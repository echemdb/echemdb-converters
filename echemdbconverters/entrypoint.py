r"""
The echemdb-converter suite.

EXAMPLES::

    >>> from echemdbconverters.test.cli import invoke
    >>> invoke(cli, "--help")  # doctest: +NORMALIZE_WHITESPACE
    Usage: cli [OPTIONS] COMMAND [ARGS]...

      The echemdb-converter suite

    Options:
      --help  Show this message and exit.
    Commands:
      csv  Convert a file containing CSV data into an echemdb unitpackage.
      ec   Convert an electrochemistry file into an echemdb datapackage.

"""
# ********************************************************************
#  This file is part of echemdb-converters.
#
#        Copyright (C) 2022 Albert Engstfeld
#        Copyright (C) 2022 Johannes Hermann
#        Copyright (C) 2022 Julian Rüth
#
#  echemdb-converters is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  echemdb-converters is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with echemdb-converters. If not, see <https://www.gnu.org/licenses/>.
# ********************************************************************
import logging
import os

import click

logger = logging.getLogger("echemdb-converters")


@click.group(help=__doc__.split("EXAMPLES")[0])
def cli():
    r"""
    Entry point of the command line interface.

    This redirects to the individual commands listed below.
    """


def _outfile(template, suffix=None, outdir=None):
    r"""
    Return a file name for writing.

    The file is named like `template` but with the suffix changed to `suffix`
    if specified. The file is created in `outdir`, if specified, otherwise in
    the directory of `template`.

    EXAMPLES::

        >>> from echemdbconverters.test.cli import invoke, TemporaryData
        >>> with TemporaryData("../**/default.cvs") as directory:
        ...     outname = _outfile(os.path.join(directory, "default.csv"), suffix=".csv")
        ...     with open(outname, mode="wb") as csv:
        ...         _ = csv.write(b"...")
        ...     os.path.exists(os.path.join(directory, "default.csv"))
        True

    ::

        >>> with TemporaryData("../**/default.csv") as directory:
        ...     outname = _outfile(os.path.join(directory, "default.csv"), suffix=".csv", outdir=os.path.join(directory, "subdirectory"))
        ...     with open(outname, mode="wb") as csv:
        ...         _ = csv.write(b"...")
        ...     os.path.exists(os.path.join(directory, "subdirectory", "default.csv"))
        True

    """
    if suffix is not None:
        template = f"{os.path.splitext(template)[0]}{suffix}"

    if outdir is not None:
        template = os.path.join(outdir, os.path.basename(template))

    os.makedirs(os.path.dirname(template) or ".", exist_ok=True)

    return template


def _create_package(csvname, metadata, fields, outdir):
    r"""
    Return a data package built from a :param:`metadata` dict and tabular data
    in :param:`csvname`.

    This is a helper method for :meth:`convert`.
    """
    from frictionless import Package, Resource, Schema

    package = Package(
        resources=[
            Resource(
                path=os.path.basename(csvname),
                basepath=outdir or os.path.dirname(csvname),
            )
        ],
    )
    package.infer()

    resource = package.resources[0]

    resource.custom.setdefault("metadata", {})
    resource.custom["metadata"].setdefault("echemdb", metadata)

    resource.schema = Schema(fields=fields)

    return package


def _write_metadata(out, metadata):
    r"""
    Write `metadata` to the `out` stream in JSON format.

    This is a helper method for :meth:`digitize_cv`.
    """

    def defaultconverter(item):
        r"""
        Return `item` that Python's json package does not know how to serialize
        in a format that Python's json package does know how to serialize.
        """
        from datetime import date, datetime

        # The YAML standard knows about dates and times, so we might see these
        # in the metadata. However, standard JSON does not know about these so
        # we need to serialize them as strings explicitly.
        if isinstance(item, (datetime, date)):
            return str(item)

        raise TypeError(f"Cannot serialize ${item} of type ${type(item)} to JSON.")

    import json

    json.dump(metadata, out, default=defaultconverter, ensure_ascii=False, indent=4)
    # json.dump does not save files with a newline, which compromises the tests
    # where the output files are compared to an expected json.
    out.write("\n")


@click.command(name="csv")
@click.argument("csv", type=click.Path(exists=True))
@click.option("--device", type=str, default=None, help="selects a specific CSVloader")
@click.option(
    "--outdir",
    type=click.Path(file_okay=False),
    default=None,
    help="write output files to this directory",
)
@click.option(
    "--metadata", type=click.File("rb"), default=None, help="yaml file with metadata"
)
def convert(csv, device, outdir, metadata):
    """
    Convert a file containing CSV data into an echemdb unitpackage.
    \f

    EXAMPLES::

        >>> from echemdbconverters.test.cli import invoke, TemporaryData
        >>> with TemporaryData("../**/default.csv") as directory:
        ...     invoke(cli, "csv", os.path.join(directory, "default.csv"))

    TESTS:

    The command can be invoked on files in the current directory::

        >>> from echemdbconverters.test.cli import invoke, TemporaryData
        >>> cwd = os.getcwd()
        >>> with TemporaryData("../**/default.csv") as directory:
        ...     os.chdir(directory)
        ...     try:
        ...         invoke(cli, "csv", "default.csv")
        ...     finally:
        ...         os.chdir(cwd)

    """
    import yaml

    from echemdbconverters.csvloader import CSVloader

    fields = None

    if metadata:
        metadata = yaml.load(metadata, Loader=yaml.SafeLoader)
        try:
            fields = metadata["figure description"]["schema"]["fields"]
        except (KeyError, AttributeError):
            logger.warning("No units to the fields provided in the metadata")

    if device:
        with open(csv, "r") as file:  # pylint: disable=unspecified-encoding
            loader = CSVloader.create(device)(file)
    else:
        with open(csv, "r") as file:  # pylint: disable=unspecified-encoding
            loader = CSVloader(file)

    # if metadata:
    #     metadata = yaml.load(metadata, Loader=yaml.SafeLoader)

    fields = loader.derive_fields(fields=fields)

    _create_outfiles(csv, loader, fields, metadata, outdir)


def _create_outfiles(csv, loader, fields, metadata, outdir):
    # write new csv
    csvname = _outfile(csv, suffix=".csv", outdir=outdir)
    loader.df.to_csv(csvname, index=False, decimal='.', sep=',')

    # write package
    package = _create_package(csvname, metadata, fields, outdir)

    with open(
        _outfile(csv, suffix=".json", outdir=outdir),
        mode="w",
        encoding="utf-8",
    ) as json:
        _write_metadata(json, package.to_dict())


@click.command(name="ec")
@click.argument("csv", type=click.Path(exists=True))
@click.option("--device", type=str, default=None, help="selects a specific CSVloader")
@click.option(
    "--outdir",
    type=click.Path(file_okay=False),
    default=None,
    help="write output files to this directory",
)
@click.option(
    "--metadata", type=click.File("rb"), default=None, help="yaml file with metadata"
)
def electrochemistry(csv, device, outdir, metadata):
    r"""
    Convert an electrochemistry file into an echemdb datapackage.

    EXAMPLES::

        >>> from echemdbconverters.test.cli import invoke, TemporaryData
        >>> with TemporaryData("unit.csv") as directory:
        ...     with TemporaryData("unit.csv.metadata") as directory2:
        ...         invoke(cli, "ec", os.path.join(directory, "unit.csv"), '--outdir', os.path.join(directory, "generated"), '--metadata', os.path.join(directory2, "unit.csv.metadata"))

    TESTS:

    The command can be invoked on files in the current directory::

        >>> from echemdbconverters.test.cli import invoke, TemporaryData
        >>> cwd = os.getcwd()
        >>> with TemporaryData("unit.csv") as directory:
        ...     with TemporaryData("unit.csv.metadata") as directory2:
        ...         os.chdir(directory)
        ...         try:
        ...             invoke(cli, "ec", os.path.join(directory, "unit.csv"), '--outdir', os.path.join(directory, "generated"), '--metadata', os.path.join(directory2, "unit.csv.metadata"))
        ...         finally:
        ...             os.chdir(cwd)

    """
    import yaml

    from echemdbconverters.csvloader import CSVloader
    from echemdbconverters.ec_unit_package_adapter import ECUnitPackageAdapter

    fields = None

    if metadata:
        metadata = yaml.load(metadata, Loader=yaml.SafeLoader)
        try:
            fields = metadata["figure description"]["schema"]["fields"]
        except (KeyError, AttributeError):
            logger.warning("No units to the fields provided in the metadata")

    if device:
        with open(csv, "r") as file:  # pylint: disable=unspecified-encoding
            loader = ECUnitPackageAdapter.create(device=device)(
                CSVloader.create(device)(file), fields=fields
            )
    else:
        with open(csv, "r") as file:  # pylint: disable=unspecified-encoding
            loader = ECUnitPackageAdapter(CSVloader(file), fields=fields)

    fields = loader.fields()

    _create_outfiles(csv, loader, fields, metadata, outdir)


cli.add_command(convert)
cli.add_command(electrochemistry)

# Register command docstrings for doctesting.
# Since commands are not functions anymore due to their decorator, their
# docstrings would otherwise be ignored.
__test__ = {
    name: command.__doc__ for (name, command) in cli.commands.items() if command.__doc__
}
