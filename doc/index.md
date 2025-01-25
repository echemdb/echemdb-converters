---
jupytext:
  formats: md:myst,ipynb
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.5
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Welcome to echemdb-converters's documentation!

`echemdbconverters` provides a command line interface (CLI) for creating echemdb compatible [unitpackages](https://github.com/echemdb/unitpackage) from CSV or CSV like files. The module can be extended to load different kind of CSV files and/or to convert files with different structure but similar content into a standardized format. An API to the loaders and converters allows for seamless integration in existing workflows.

```{warning}
This module is still under development.
```

## Examples

```{hint}
An `!` in the following examples indicates a shell command which is executed in a jupyter cell. Remove the `!` to run the command in a shell.
```

```{note}
The input and output files for and from the following commands can be found in the [test folder](https://github.com/echemdb/echemdb-converters/tree/master/test/) of the repository.
```

A frictionless datapackage consits of a JSON, describing one or more tabular data files. With `echemdbconverters`, a frictionless datapackage can be created from a {download}`CSV <../test/data/default.csv>`  without header, where the first line contains the column names.

```{code-cell} ipython3
!echemdbconverters csv ../test/data/default.csv --outdir ../test/generated
```

By providing information on the units of the columns in a metadata file (YAML) a [unitpackage](https://github.com/echemdb/unitpackage) can be created. The units to the columns must be included in the YAML under `figure_description.fields`, according to the [frictionless field schema](https://specs.frictionlessdata.io/table-schema/#field-descriptors). See {download}`example YAML <../test/data/unit.csv.metadata>` for reference.

```{code-cell} ipython3
!echemdbconverters csv ../test/data/unit.csv --metadata ../test/data/unit.csv.metadata --outdir ../test/generated
```

Specific loaders convert non-standard CSV, which, for {download}`example <../test/data/eclab_cv.mpt>`, contain a certain number of header lines, values are separated by different separators, or have a different decimal separator. Such files are often generated from software supplied with data acquisition instruments. The header is removed in the resulting CSV to the unitpackage.

```{code-cell} ipython3
!echemdbconverters csv ../test/data/eclab_cv.mpt --device eclab --metadata ../test/data/eclab_cv.mpt.metadata --outdir ../test/generated
```

## Further usage

Use echemdbs' `unitpackage` to browse, modify and visualize the data.

```{code-cell} ipython3
from unitpackage.collection import Collection
db = Collection.from_local('../test/generated')
entry = db['eclab_cv']
entry
```

## Installation

This package is available on [PiPY](https://pypi.org/project/echemdbconverters/) and can be installed with pip:

```sh .noeval
pip install echemdbconverters
```

See the [installation instructions](installation.md) for further details.

<!--
You can cite this project as described [on our zenodo page](https://zenodo.org/badge/latestdoi/XXXXXX).
-->

## License

The contents of this repository are licensed under the [GNU General Public
License v3.0](https://www.gnu.org/licenses/gpl-3.0.html) or, at your option, any later version.

+++

```{toctree}
:maxdepth: 2
:caption: "Contents:"
:hidden:
installation.md
api.md
```
