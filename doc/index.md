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

A frictionless datapackage consits of a JSON, describing one or more tabular data files. With `echemdbconverters`, a frictionless datapackage can be created from a {download}`CSV <../test/csv/default.csv>`  without header, where the first line contains the column names.

```{code-cell} ipython3
!echemdbconverters csv ../test/csv/default.csv --outdir ../test/generated
```

By providing information on the units of the columns in a metadata file (YAML) a [unitpackage](https://github.com/echemdb/unitpackage) can be created. The units to the columns must be included in the YAML under `figure_description.schema.fields`, according to the [frictionless field schema](https://specs.frictionlessdata.io/table-schema/#field-descriptors). See {download}`example YAML <../test/csv/unit.csv.metadata>` for reference.

```{code-cell} ipython3
!echemdbconverters csv ../test/csv/unit.csv --metadata ../test/csv/unit.csv.metadata --outdir ../test/generated
```

Specific loaders convert non-standard CSV, which, for {download}`example <../test/csv/eclab_cv_csv.mpt>`, contain a certain number of header lines, values are separated by different separators, or have a different decimal separator. Such files are often generated from software supplied with data acquisition instruments. The header is removed in the resulting CSV to the unitpackage.

```{code-cell} ipython3
!echemdbconverters csv ../test/csv/eclab_cv_csv.mpt --device eclab --metadata ../test/csv/eclab_cv_csv.mpt.metadata --outdir ../test/generated
```

Unitpackages with specific metadata standards can be created. For example `echemdb`'s unitpackages for electrochemical data, require a time, potential and current axis labelled `t`, `U` or `E`, and `j` or `I`. The CLI provides special commands (here `ec`).

```{code-cell} ipython3
!echemdbconverters ec ../test/csv/eclab_cv_ec.mpt --device eclab --metadata ../test/csv/eclab_cv_ec.mpt.metadata --outdir ../test/generated
```

## Further usage

Use echemdbs' `unitpackage` to browse, modify and visualize the data.

```{code-cell} ipython3
from unitpackage.collection import Collection
from unitpackage.local import collect_datapackages
db = Collection(collect_datapackages('../test/generated'))
entry = db['eclab_cv_ec']
entry.rescale({'t':'h', 'E':'mV'}).plot('t', 'E')
```



<!--
You can cite this project as described [on our zenodo page](https://zenodo.org/badge/latestdoi/637997870).

## Installation

This package is available on [PiPY](https://pypi.org/project/unitpackage/) and can be installed with pip:

```sh .noeval
pip install unitpackage
```

The package is also available on [conda-forge](https://github.com/conda-forge/unitpackage-feedstock) an can be installed with conda

```sh .noeval
conda install -c conda-forge unitpackage
```

or mamba

```sh .noeval
mamba install -c conda-forge unitpackage
```

See the [installation instructions](installation.md) for further details.
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