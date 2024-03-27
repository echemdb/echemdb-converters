r"""
Loads MPT files recorded with the EC-Lab software from BioLogic for BioLogic potentiostats.

EXAMPLES:

The file can be loaded with the ECLabLoader::

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
    >>> eclab_csv = ECLabLoader(file)
    >>> eclab_csv.df
        mode  time/s Ewe/V  <I>/mA  control/V
    0     2       0   0.1       0          0
    1     2       1   1.4       5          1

The file can also be loaded from the base loader::

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
    >>> from echemdbconverters.csvloader import CSVloader
    >>> csv = CSVloader.create('eclab')(file)
    >>> csv.df
        mode  time/s Ewe/V  <I>/mA  control/V
    0     2       0   0.1       0          0
    1     2       1   1.4       5          1

    >>> csv.header
    ['EC-Lab ASCII FILE\n', 'Nb header lines : 6\n', '\n', 'Device metadata : some metadata\n', '\n']

    >>> csv.column_names
    ['mode', 'time/s', 'Ewe/V', '<I>/mA', 'control/V']

"""

# ********************************************************************
#  This file is part of echemdb-converters.
#
#        Copyright (C) 2024 Albert Engstfeld
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


from echemdbconverters.csvloader import CSVloader


class ECLabLoader(CSVloader):
    r"""
    Loads BioLogic EC-Lab MPT files.

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
        >>> from echemdbconverters.csvloader import CSVloader
        >>> csv = CSVloader.create('eclab')(file)
        >>> csv.df
           mode  time/s Ewe/V  <I>/mA  control/V
        0     2       0   0.1       0          0
        1     2       1   1.4       5          1

        >>> csv.header
        ['EC-Lab ASCII FILE\n', 'Nb header lines : 6\n', '\n', 'Device metadata : some metadata\n', '\n']

        >>> csv.column_names
        ['mode', 'time/s', 'Ewe/V', '<I>/mA', 'control/V']

    """

    @property
    def header_lines(self):
        r"""
        The number of header lines of an EC-Lab MPT file without column names.
        The number is provided in the header of the MPT file, which contains, however,
        also the line with the data column names.

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
            >>> from echemdbconverters.csvloader import CSVloader
            >>> csv = CSVloader.create('eclab')(file)
            >>> csv.header_lines
            5

        """
        matches = []

        for line in self.file.readlines():
            import re

            match = re.findall(
                r"(?P<headerlines>Nb header lines) *\: *(?P<value>-?\d+\.?\d*)",
                str(line),
                re.IGNORECASE,
            )

            if match:
                matches.append(match)

        return int(matches[0][0][1]) - 1

    @property
    def df(self):
        r"""
        A pandas dataframe with the data of the EC-Lab MPT file.

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
            >>> from echemdbconverters.csvloader import CSVloader
            >>> csv = CSVloader.create('eclab')(file)
            >>> csv.df
               mode  time/s Ewe/V  <I>/mA  control/V
            0     2       0   0.1       0          0
            1     2       1   1.4       5          1

        """
        import pandas as pd

        return pd.read_csv(
            self.file,
            sep="\t",
            header=self.header_lines,
            decimal=self.decimal,
            # encoding="latin1",
            skip_blank_lines=False,
        )

    @property
    def decimal(self):
        r"""
        Returns the decimal separator in the MPT,
        which depends on the language settings of the operating system running the software.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO('''EC-Lab ASCII FILE
            ... Nb header lines : 6
            ...
            ... Device metadata : some metadata
            ...
            ... mode\ttime/s\tEwe/V\t<I>/mA\tcontrol/V
            ... 2\t0\t0,1\t0\t0
            ... 2\t1\t1,4\t5\t1
            ... ''')
            >>> from echemdbconverters.csvloader import CSVloader
            >>> ec = CSVloader.create('eclab')(file)
            >>> ec.decimal
            ','

        """
        # The values in the MPT are always tab separated.
        # The data in the file only consist of numbers.
        # Hence we simply determine if the line contains a comma or not.
        if "," in self.data.readlines()[0]:
            return ","

        return "."
