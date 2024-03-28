Installation
============

Install with pip from PyPI
--------------------------

The latest stable version of the echemdbconverters is available on
[PyPI](https://pypi.org/project/echemdbconverters/) for all platforms and can be
installed if you have Python and pip installed already:

```sh
pip install echemdbconverters
```

This command downloads and installs the echemdbconverters and its dependencies into
your local Python installation.

If the above command fails because you do not have permission to modify your
Python installation, you can install the echemdbconverters into your user account:

```sh
pip install --user echemdbconverters
```

You can instead also install the latest unreleased version of the echemdbconverters
from our [GitHub Repository](https://github.com/echemdb/echemdbconverters) with

```sh
pip install git+https://github.com/echemdb/echemdbconverters@main
```

Install with pip for development
--------------------------------

If you want to work on the echemdbconverters itself, get a copy of the latest
unreleased version of the echemdbconverters:

```sh
git clone https://github.com/echemdb/echemdbconverters.git
```

Move to the directory and install the dependencies

```sh
conda activate echemdbconverters
conda env create --file environment.yaml
```

Create an [editable](https://pip.pypa.io/en/stable/cli/pip_install/#editable-installs) install of the echemdbconverters:

```sh
pip install -e echemdbconverters
```

Any changes you make to the files in your local copy of the echemdbconverters should
now be available in your next Python session.

We would love to see your contribution to the echemdbconverters.
