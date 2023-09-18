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

```{note}
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
!echemdbconverters csv ../test/csv/eclab_cv_csv.mpt --device eclab --metadata ../test/csv/eclab_cv_csv.mpt.metadata --outdir ../test/generated
```

Finally use echemdbs' `unitpackage` to browse, modify and visualize the data.

```{code-cell} ipython3
from unitpackage.collection import Collection
from unitpackage.local import collect_datapackages
db = Collection(collect_datapackages('../test/generated'))
entry = db['eclab_cv_ec']
entry.rescale({'t':'h', 'E':'mV'}).plot('t', 'E')
```
<!--
Annotation of scientific data plays a crucial role in research data management workflows to ensure that the data is stored according to the FAIR principles. A simple CSV file recorded during an experiment usually does, for example, not provide any information on the units of the values within the CSV, nor does it provide information on what system has been investigated, or who performed the experiment. Such information can be stored in [frictionless datapackages](https://frictionlessdata.io/), which consist of a CSV (data) file which is annotated with a JSON file.
The `unitpackage` module provides a Python library to interact with such datapackages which have a very [specific structure](usage/unitpackage.md).
An example demonstrating the usage of a collection of datapackages along with the `unitpackage` Python library is found on [echemdb.org](https://www.echemdb.org/cv). The website shows a collection of electrochemical data, stored following the [echemdb's metadata schema](https://github.com/echemdb/metadata-schema).

## Examples

A collection of datapackages can be generated from [local files](usage/local_collection.md) or from a remote repository, such as [echemdb.org](https://www.echemdb.org). To illustrate the usage of `unitpackage` we use in the following examples the data available on [echemdb.org](https://www.echemdb.org/cv). The data is downloaded by default when the `Collection` class does not receive the argument `data_packages=collect_datapackages('./files_folder)`.

```{note}
We denote the collection as `db` (database), even thought it is not a database in that sense.
```

```{code-cell} ipython3
from unitpackage.collection import Collection
db = Collection()
```

A single entry can be retrieved with an identifiers available in the database

```{code-cell} ipython3
entry = db['engstfeld_2018_polycrystalline_17743_f4b_1']
```

The metadata of the datapackage is available from `entry.package`.

The data related to an entry can be returned as a [pandas](https://pandas.pydata.org/) dataframe.

```{code-cell} ipython3
entry.df.head()
```

The units of the columns can be retrieved.

```{code-cell} ipython3
entry.field_unit('j')
```

The values in the dataframe can be changed to other compatible units.

```{code-cell} ipython3
rescaled_entry = entry.rescale({'E' : 'mV', 'j' : 'uA / m2'})
rescaled_entry.df.head()
```

The data can be visualized in a plotly figure:

```{code-cell} ipython3
entry.plot('E', 'j')
```

## Specific Collections

For certain datasets, unitpackage can be extended by additional modules. Such a module is the `CVCollection` class which loads a collection of packages containing cyclic voltammograms which are stored according to the echemdb metadata schema. Such data is usually found in the field of electrochemistry as illustrated on [echemdb.org](https://www.echemdb.org/cv).

```{code-cell} ipython3
from unitpackage.cv.cv_collection import CVCollection
db = CVCollection()
db.describe()
```

Filtering the collection for entries having specific properties, e.g., containing Pt as working electrode material, returns a new collection.

```{code-cell} ipython3
db_filtered = db.filter(lambda entry: entry.get_electrode('WE').material == 'Pt')
db_filtered.describe()
```

```{note}
The filtering method is also available to the base class `Collection`.
```

## Further Usage

Frictionless datapackages or unitpackges are perfectly machine readable making the underling data and metadata reusable in many ways.

* The `unitpackage` API can be used to filter collections of similar data for certain properties, thus allowing for simple comparison of different data sets. For example, you could think of comparing local files recorded in the laboratory with data published in a repository.
* The content of datapackages can be included in other applications or the generation of a website. The latter has been demonstrated for electrochemical data on [echemdb.org](https://www.echemdb.org/cv). The datapackages could also be published with the [frictionless Livemark](https://livemark.frictionlessdata.io/) data presentation framework.

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
