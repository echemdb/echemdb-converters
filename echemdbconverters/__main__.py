r"""
The echemdb-converter suite.

EXAMPLES::

    # >>> from svgdigitizer.test.cli import invoke
    # >>> invoke(cli, "--help")  # doctest: +NORMALIZE_WHITESPACE
    # Usage: cli [OPTIONS] COMMAND [ARGS]...
    #   The svgdigitizer suite.
    # Options:
    #   --help  Show this message and exit.
    # Commands:
    #   cv        Digitize a cylic voltammogram.
    #   digitize  Digitize a plot.
    #   paginate  Render PDF pages as individual SVG files with linked PNG images.
    #   plot      Display a plot of the data traced in an SVG.

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
import os

import click


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

        >>> from svgdigitizer.test.cli import invoke, TemporaryData
        >>> with TemporaryData("**/xy.svg") as directory:
        ...     outname = _outfile(os.path.join(directory, "xy.svg"), suffix=".csv")
        ...     with open(outname, mode="wb") as csv:
        ...         _ = csv.write(b"...")
        ...     os.path.exists(os.path.join(directory, "xy.csv"))
        True

    ::

        >>> with TemporaryData("**/xy.svg") as directory:
        ...     outname = _outfile(os.path.join(directory, "xy.svg"), suffix=".csv", outdir=os.path.join(directory, "subdirectory"))
        ...     with open(outname, mode="wb") as csv:
        ...         _ = csv.write(b"...")
        ...     os.path.exists(os.path.join(directory, "subdirectory", "xy.csv"))
        True

    """
    if suffix is not None:
        template = f"{os.path.splitext(template)[0]}{suffix}"

    if outdir is not None:
        template = os.path.join(outdir, os.path.basename(template))

    os.makedirs(os.path.dirname(template) or ".", exist_ok=True)

    return template

def _create_package(converter, csvname, outdir):
    r"""
    Return a data package built from a :param:`metadata` dict and tabular data
    in :param:`csvname`.

    This is a helper method for :meth:`convert`.
    """
    from frictionless import Package, Resource, Schema

    package = Package(
        converter.metadata,
        resources=[
            Resource(
                path=os.path.basename(csvname),
                basepath=outdir or os.path.dirname(csvname),
            )
        ],
    )
    package.infer()

    package["resources"][0]["schema"] = converter.schema

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
            return item.__str__()

        raise TypeError(f"Cannot serialize ${item} of type ${type(item)} to JSON.")

    import json

    json.dump(metadata, out, default=defaultconverter)


@click.command(name='ec')
@click.argument("csv", type=click.Path(exists=True))
@click.option("--device", type=str, default=None, help='selects a specific CSVloader')
@click.option(
    "--outdir",
    type=click.Path(file_okay=False),
    default=None,
    help="write output files to this directory",
)
@click.option("--metadata", type=click.File("rb"), default=None, help="yaml file with metadata"
)
@click.option("--package", is_flag=True, help="create .json in data package format")
def convert(csv, device, outdir, metadata, package):
    r"""
    Convert an electrochemistry file into an echemdb datapackage.

    EXAMPLES::

        >>> from svgdigitizer.test.cli import invoke, TemporaryData
        >>> with TemporaryData("**/xy_rate.svg") as directory:
        ...     invoke(cli, "cv", os.path.join(directory, "xy_rate.svg"))

    TESTS:

    The command can be invoked on files in the current directory::

        >>> from svgdigitizer.test.cli import invoke, TemporaryData
        >>> cwd = os.getcwd()
        >>> with TemporaryData("**/xy_rate.svg") as directory:
        ...     os.chdir(directory)
        ...     try:
        ...         invoke(cli, "cv", "xy_rate.svg")
        ...     finally:
        ...         os.chdir(cwd)

    The command can be invoked without sampling when data is not given in volts::

        >>> from svgdigitizer.test.cli import invoke, TemporaryData
        >>> from svgdigitizer.svg import SVG
        >>> from svgdigitizer.svgplot import SVGPlot
        >>> from svgdigitizer.electrochemistry.cv import CV
        >>> with TemporaryData("**/xy_rate.svg") as directory:
        ...     print(CV(SVGPlot(SVG(open(os.path.join(directory, "xy_rate.svg"))))).figure_schema.get_field("E")["unit"])
        mV
        >>> with TemporaryData("**/xy_rate.svg") as directory:
        ...     invoke(cli, "cv", os.path.join(directory, "xy_rate.svg"))

    """
    from .csvloader import CSVloader
    from .ecconverter import ECConverter
    import yaml

    if metadata:
        metadata = yaml.load(metadata, Loader=yaml.SafeLoader)

    if device:
        converter = ECConverter.get_converter(device)(CSVloader.get_loader(device)(open(csv, 'r'), metadata))
    else:
        converter = ECConverter(open(csv, 'r'), metadata)

    csvname = _outfile(csv, suffix=".csv", outdir=outdir)
    converter.df.to_csv(csvname, index=False)

    if package:
        package = _create_package(converter, csvname, outdir)

        with open(
            _outfile(csv, suffix=".json", outdir=outdir),
            mode="w",
            encoding="utf-8",
        ) as json:
            _write_metadata(json, package.to_dict() if package else converter.metadata)
    pass


cli.add_command(convert)

# Register command docstrings for doctesting.
# Since commands are not functions anymore due to their decorator, their
# docstrings would otherwise be ignored.
__test__ = {
    name: command.__doc__ for (name, command) in cli.commands.items() if command.__doc__
}

if __name__ == "__main__":
    cli()
