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
from rever.activity import activity

@activity
def update_pixi_lock():
    import hashlib
    from pathlib import Path
    import re

    # Get version from Rever
    version = $VERSION
    tarball = Path(f"dist/echemdbconverters-{version}.tar.gz")

    if not tarball.exists():
        raise FileNotFoundError(f"Expected file {tarball} not found. Did you run 'build'?")

    # Compute SHA256
    sha256_hash = hashlib.sha256()
    with tarball.open("rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    sha256sum = sha256_hash.hexdigest()

    # Update pixi.lock
    lockfile_path = Path("pixi.lock")
    lockfile_content = lockfile_path.read_text()

    lockfile_content = re.sub(
        r"(name:\s*echemdbconverters\s*\n\s*version:\s*)[\d\.]+",
        rf"\g<1>{version}",
        lockfile_content,
    )

    lockfile_content = re.sub(
      r"(name:\s*echemdbconverters\s*\n\s*version:\s*)[\d\.]+(\s*\n\s*sha256:\s*)[a-fA-F0-9]+",
      rf"\g<1>{version}\2{sha256sum}",
      lockfile_content,
    )

    lockfile_path.write_text(lockfile_content)

    print(f"Updated pixi.lock to version {version} with sha256 {sha256sum}")

@activity
def commit_pixi_lock():
    from rever.activities.command import command

    # Commit pixi.lock with a message
    command('commit', 'git add pixi.lock')
    command('commit', 'git commit -m "Update pixi.lock to version $VERSION with sha256"')

command('build', 'python -m build')
command('twine', 'twine upload dist/echemdbconverters-' + $VERSION + '.tar.gz')


$ACTIVITIES = [
    'version_bump',
    'changelog',
    'build',
    'update_pixi_lock',
    'commit_pixi_lock',
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
