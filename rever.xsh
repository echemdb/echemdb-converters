# ********************************************************************
#  This file is part of echemdb-converters.
#
#        Copyright (C) 2022-2025 Albert Engstfeld
#        Copyright (C) 2022      Johannes Hermann
#        Copyright (C) 2022      Julian Rüth
#        Copyright (C) 2022      Nicolas Hörmann
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ********************************************************************

import re

# Check that we are on the main branch
branch=$(git branch --show-current)
if branch.strip() != "main":
  raise Exception("You must be on the main branch to release.")
# and that it is up to date with origin/main
git fetch https://github.com/echemdb/echemdb-converters.git
git reset FETCH_HEAD
git diff --exit-code
git diff --cached --exit-code

$PROJECT = 'echemdb-converters'

from rever.activities.command import command

command('build', 'python -m build')
command('twine', 'twine upload dist/echemdbconverters-' + $VERSION + '.tar.gz')
# run a pixi task to update lock file
command('update_pixi_lock', 'pixi run black')


$ACTIVITIES = [
    'version_bump',
    'changelog',
    'update_pixi_lock',
    'build',
    'twine',
    'tag',
    'push_tag',
    'ghrelease',
]

$VERSION_BUMP_PATTERNS = [
    ('pyproject.toml', r'version =', 'version = "$VERSION"'),
    ('doc/conf.py', r"release = ", r"release = '$VERSION'"),
    ('pixi.lock', r'(name:\s*echemdbconverters\s*\n\s*version:\s*)[\d\.]+', r'\1$VERSION'),
]

$CHANGELOG_FILENAME = 'ChangeLog'
$CHANGELOG_TEMPLATE = 'TEMPLATE.rst'
$CHANGELOG_NEWS = 'doc/news'
$PUSH_TAG_REMOTE = 'git@github.com:echemdb/echemdb-converters.git'

$GITHUB_ORG = 'echemdb'
$GITHUB_REPO = 'echemdb-converters'

$CHANGELOG_CATEGORIES = ('Added', 'Changed', 'Deprecated', 'Removed', 'Fixed', 'Performance')
