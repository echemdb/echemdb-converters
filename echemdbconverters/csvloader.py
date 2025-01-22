r"""
Loader for CSV files (https://datatracker.ietf.org/doc/html/rfc4180)
which consist of a single header line containing the column (field)
names and rows with comma separated values.

In pandas the names of the columns are referred to as `column_names`,
whereas in a frictionless datapackage the column names are called `fields`.
The datapackage contains information about, i.e.,
the type of data, a title and a set of descriptors.

The CSV object has the following properties:

TODO:: Add examples for the following functions
    * a DataFrame
    * the column names
    * the header contents
    * the number of header lines

Loaders for non standard CSV files can be called:

TODO:: Add example

"""

# ********************************************************************
#  This file is part of echemdb-converters.
#
#        Copyright (C) 2025 Albert Engstfeld
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

logger = logging.getLogger("loader")


class CSVloader:
    r"""
    Loads a CSV, where the first line must contain the column (field) names
    and the following lines comma separated values.

    EXAMPLES::

        >>> from io import StringIO
        >>> file = StringIO(r'''a,b
        ... 0,0
        ... 1,1''')
        >>> csv = CSVloader(file)
        >>> csv.df
           a  b
        0  0  0
        1  1  1

    A list of column names::

        >>> csv.column_names
        ['a', 'b']

    More specific converters can be selected:

    TODO:: Add example with csv.get_device('device')(file)

    """

    def __init__(self, file, header_lines=None, column_header_lines=None):
        self._file = file.read()
        self._header_lines = header_lines
        self._column_header_lines = column_header_lines

    @property
    def file(self):
        r"""
        A file like object of the loaded CSV.

        EXAMPLES::
            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = CSVloader(file)
            >>> type(csv.file)
            <class '_io.StringIO'>

        """
        from io import StringIO

        return StringIO(self._file)

    def augment(self, metadata=None):
        r"""
        Metadata constructed from input metadata and the CSV header.
        A simple CSV does not have any metadata in the header.

        EXAMPLES:

        Without metadata::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j
            ... 0,0,0
            ... 1,1,1''')
            >>> from echemdbconverters.csvloader import CSVloader
            >>> csv = CSVloader(file)
            >>> csv.augment()
            {}

        Without metadata provided to the loader::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j
            ... 0,0,0
            ... 1,1,1''')
            >>> from echemdbconverters.csvloader import CSVloader
            >>> csv = CSVloader(file)
            >>> csv.augment(metadata={'foo':'bar'})
            {'foo': 'bar'}

        """
        return metadata or {}

    @staticmethod
    def create(device=None):
        r"""
        Calls a specific `loader` based on a given device.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO('''EC-Lab ASCII FILE
            ... Nb header lines : 6
            ...
            ... Device metadata : some metadata
            ...
            ... mode\ttime/s\tEwe/V\t<I>/mA\tcontrol/V
            ... 2\t0\t0.1\t0\t0
            ... 2\t1\t1.4\t5\t1
            ... ''')
            >>> csv = CSVloader.create('eclab')(file)
            >>> csv.df
               mode  time/s  Ewe/V  <I>/mA  control/V
            0     2       0    0.1       0          0
            1     2       1    1.4       5          1

        """
        if device == "eclab":
            from echemdbconverters.eclabloader import ECLabLoader

            return ECLabLoader

        if device == "gamry":
            from echemdbconverters.gamryloader import GamryLoader

            return GamryLoader

        raise KeyError(f"Device wth name '{device}' is unknown to the loader'.")

    @property
    def header_lines(self):
        r"""
        The number of header lines in a CSV excluding the line with the column names.

        EXAMPLES:

        Files for the base loader do not have a header::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = CSVloader(file)
            >>> csv.header_lines
            0

        Implementation in a specific device loader::

            >>> file = StringIO('''EC-Lab ASCII FILE
            ... Nb header lines : 6
            ...
            ... Device metadata : some metadata
            ...
            ... mode\ttime/s\tEwe/V\t<I>/mA\tcontrol/V
            ... 2\t0\t0,1\t0\t0
            ... 2\t1\t1,4\t5\t1
            ... ''')
            >>> csv = CSVloader.create('eclab')(file)
            >>> csv.header_lines
            5

        """
        return self._header_lines or 0

    @property
    def header(self):
        r"""
        The header of the CSV (excluding column names).

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = CSVloader(file)
            >>> csv.header
            []

        """
        lines = self.file.readlines()

        return [lines[_] for _ in range(self.header_lines)]

    @property
    def column_header_lines(self):
        r"""
        The number of lines containing the descriptive information of the data
        for each column.

        EXAMPLES:

        A file with a single column header line::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = CSVloader(file)
            >>> csv.column_header_lines
            1

        A file with a two column header lines::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... x,y
            ... 0,0
            ... 1,1''')
            >>> csv = CSVloader(file, column_header_lines=2)
            >>> csv.column_header_lines
            2

        """
        return self._column_header_lines or 1

    @property
    def column_headers(self):
        r"""
        The lines in the file containing the descriptive information of the data
        for each column.

        EXAMPLES:

        A file with a single column header line::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = CSVloader(file)
            >>> csv.column_headers.readlines()
            ['a,b\n']

        A file with two column header lines, which is sometimes, for example,
        used for storing units to the values::

            >>> from io import StringIO
            >>> file = StringIO(r'''T,v
            ... K,m/s
            ... 0,0
            ... 1,1''')
            >>> csv = CSVloader(file, column_header_lines=2)
            >>> csv.column_headers.readlines()
            ['T,v\n', 'K,m/s\n']

        """
        from io import StringIO

        return StringIO(
            "".join(
                line
                for line in self.file.readlines()[
                    self.header_lines : self.header_lines + self.column_header_lines
                ]
            )
        )

    @property
    def column_header_names(self):
        r"""
        A list of column header names constructed from the lines
        containing the column head names.

        EXAMPLES:

        A file with a single column header line::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = CSVloader(file)
            >>> csv.column_header_names
            ['a', 'b']

        For a file containing two or more column header lines,
        we create a single name for each column including the information
        from the following lines and separating those with a ``/``.::

            >>> from io import StringIO
            >>> file = StringIO(r'''T,v
            ... K,m/s
            ... 0,0
            ... 1,1''')
            >>> csv = CSVloader(file, column_header_lines=2)
            >>> csv.column_header_names
            ['T / K', 'v / m/s']

        """

        headers = [
            line.strip().split(self.delimiter)
            for line in self.column_headers.getvalue().splitlines()
        ]

        # If there's only one line, return it as is
        if len(headers) == 1:
            return headers[0]

        # If there are multiple lines, combine them column-wise
        return [" / ".join(items) for items in zip(*headers)]

    @property
    def data(self):
        r"""
        A file like object with the data of the CSV without header lines.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = CSVloader(file)
            >>> type(csv.data)
            <class '_io.StringIO'>

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = CSVloader(file)
            >>> csv.data.readlines()
            ['0,0\n', '1,1']

        """
        from io import StringIO

        return StringIO(
            "".join(
                line
                for line in self.file.readlines()[
                    self.header_lines + self.column_header_lines :
                ]
            )
        )

    @property
    def df(self):
        r"""
        A pandas dataframe of the data in the CSV.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = CSVloader(file)
            >>> csv.df
               a  b
            0  0  0
            1  1  1

        """
        import pandas as pd

        return pd.read_csv(
            self.data,
            #    header=self.header_lines + self.column_header_lines,
            names=self.column_header_names,
        )

    @property
    def column_names(self):
        r"""
        List of column (field) names describing the tabulated data.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = CSVloader(file)
            >>> csv.column_names
            ['a', 'b']

        """
        return self.df.columns.to_list()

    @property
    def delimiter(self):
        r"""
        The delimiter in the CSV, which is extracted from
        the first two lines of the CSV data.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = CSVloader(file)
            >>> csv.delimiter
            ','

        """
        import clevercsv

        # Only two lines are used to detect the delimiter,
        # since clevercsv is slow with files containing many columns.
        return clevercsv.detect.Detector().detect(self.data.read()[:2]).delimiter

    @property
    def decimal(self):
        r"""
        The decimal separator in the floats in the CSV data.

        EXAMPLES:

        Not implemented in the base loader::

            >>> from io import StringIO
            >>> file = StringIO(r'''a,b
            ... 0,0
            ... 1,1''')
            >>> csv = CSVloader(file)
            >>> csv.decimal
            Traceback (most recent call last):
            ...
            NotImplementedError

        Implementation in a specific device loader::

            >>> file = StringIO('''EC-Lab ASCII FILE
            ... Nb header lines : 6
            ...
            ... Device metadata : some metadata
            ...
            ... mode\ttime/s\tEwe/V\t<I>/mA\tcontrol/V
            ... 2\t0\t0,1\t0\t0
            ... 2\t1\t1,4\t5\t1
            ... ''')
            >>> csv = CSVloader.create('eclab')(file)
            >>> csv.decimal
            ','

        """
        raise NotImplementedError
