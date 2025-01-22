r"""
Loads DAT files recorded with the Gamry Instruments Framework software
from Gamry for Gamry potentiostats.

EXAMPLES:

The file can be loaded with the GamryLoader::

    >>> from io import StringIO
    >>> file = StringIO('''EXPLAIN
    ... TAG\tCV
    ... TITLE\tLABEL\tCyclic Voltammetry\tTest &Identifier
    ... CURVE\tTABLE\t3597
    ... \tPt\tT\tVf\tIm\tVu\tSig\tAch\tIERange\tOver\tCycle\tTemp
    ... \t#\ts\tV vs. Ref.\tA\tV\tV\tV\t#\tbits\t#\tdeg C
    ... \t0\t0,06\t2,00054E-001\t1,72821E-005\t0,00000E+000\t2,00000E-001\t6,45222E-004\t9\t..........a\t0\t-327,75
    ... \t1\t0,12\t1,97170E-001\t1,04547E-005\t0,00000E+000\t1,97000E-001\t-1,17889E-003\t9\t..........a\t0\t-327,75
    ... ''')
    >>> from echemdbconverters.gamryloader import GamryLoader
    >>> csv = GamryLoader(file)
    >>> csv.df # doctest: +NORMALIZE_WHITESPACE
       Pt / #  T / s  Vf / V vs. Ref.  ...  Over / bits  Cycle / #  Temp / deg C
    0       0   0.06         0.200054  ...  ..........a          0       -327.75
    1       1   0.12         0.197170  ...  ..........a          0       -327.75
    ...

The file can also be loaded from the base loader::

    >>> from io import StringIO
    >>> file = StringIO('''EXPLAIN
    ... TAG\tCV
    ... TITLE\tLABEL\tCyclic Voltammetry\tTest &Identifier
    ... CURVE\tTABLE\t3597
    ... \tPt\tT\tVf\tIm\tVu\tSig\tAch\tIERange\tOver\tCycle\tTemp
    ... \t#\ts\tV vs. Ref.\tA\tV\tV\tV\t#\tbits\t#\tdeg C
    ... \t0\t0,06\t2,00054E-001\t1,72821E-005\t0,00000E+000\t2,00000E-001\t6,45222E-004\t9\t..........a\t0\t-327,75
    ... \t1\t0,12\t1,97170E-001\t1,04547E-005\t0,00000E+000\t1,97000E-001\t-1,17889E-003\t9\t..........a\t0\t-327,75
    ... ''')
    >>> from echemdbconverters.csvloader import CSVloader
    >>> csv = CSVloader.create('gamry')(file)
    >>> csv.df
       Pt / #  T / s  Vf / V vs. Ref.  ...  Over / bits  Cycle / #  Temp / deg C
    0       0   0.06         0.200054  ...  ..........a          0       -327.75
    1       1   0.12         0.197170  ...  ..........a          0       -327.75
    ...

    >>> csv.header
    ['EXPLAIN\n', 'TAG\tCV\n', 'TITLE\tLABEL\tCyclic Voltammetry\tTest &Identifier\n', 'CURVE\tTABLE\t3597\n']

    >>> csv.column_names
    ['Pt / #', 'T / s', 'Vf / V vs. Ref.', 'Im / A', 'Vu / V', 'Sig / V', 'Ach / V', 'IERange / #', 'Over / bits', 'Cycle / #', 'Temp / deg C']

"""

# ********************************************************************
#  This file is part of echemdb-converters.
#
#        Copyright (C) 2025 Albert Engstfeld
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


class GamryLoader(CSVloader):
    r"""
    Loads Gamry Instruments Framework DAT files.

    EXAMPLES::

        >>> from io import StringIO
        >>> file = StringIO('''EXPLAIN
        ... TAG\tCV
        ... TITLE\tLABEL\tCyclic Voltammetry\tTest &Identifier
        ... CURVE\tTABLE\t3597
        ... \tPt\tT\tVf\tIm\tVu\tSig\tAch\tIERange\tOver\tCycle\tTemp
        ... \t#\ts\tV vs. Ref.\tA\tV\tV\tV\t#\tbits\t#\tdeg C
        ... \t0\t0,06\t2,00054E-001\t1,72821E-005\t0,00000E+000\t2,00000E-001\t6,45222E-004\t9\t..........a\t0\t-327,75
        ... \t1\t0,12\t1,97170E-001\t1,04547E-005\t0,00000E+000\t1,97000E-001\t-1,17889E-003\t9\t..........a\t0\t-327,75
        ... ''')
        >>> from echemdbconverters.csvloader import CSVloader
        >>> csv = CSVloader.create('gamry')(file)
        >>> csv.df
           Pt / #  T / s  Vf / V vs. Ref.  ...  Over / bits  Cycle / #  Temp / deg C
        0       0   0.06         0.200054  ...  ..........a          0       -327.75
        1       1   0.12         0.197170  ...  ..........a          0       -327.75
        ...

        >>> csv.header
        ['EXPLAIN\n', 'TAG\tCV\n', 'TITLE\tLABEL\tCyclic Voltammetry\tTest &Identifier\n', 'CURVE\tTABLE\t3597\n']

        >>> csv.column_names
        ['Pt / #', 'T / s', 'Vf / V vs. Ref.', 'Im / A', 'Vu / V', 'Sig / V', 'Ach / V', 'IERange / #', 'Over / bits', 'Cycle / #', 'Temp / deg C']

    """

    def _included_files(self):
        r"""
        Some Gamry files contain several files, e.g., cycles of a CV which are split
        by lines containing ``CURVE  TABLE   <SomeNumber>``.

        We search for all those instances to construct a common df with meth df.

        """
        return NotImplementedError

    @property
    def header_lines(self):
        r"""
        The number of header lines of an EC-Lab MPT file without column names.
        The number is provided in the header of the MPT file, which contains, however,
        also the line with the data column names.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO('''EXPLAIN
            ... TAG\tCV
            ... TITLE\tLABEL\tCyclic Voltammetry\tTest &Identifier
            ... CURVE\tTABLE\t3597
            ... \tPt\tT\tVf\tIm\tVu\tSig\tAch\tIERange\tOver\tCycle\tTemp
            ... \t#\ts\tV vs. Ref.\tA\tV\tV\tV\t#\tbits\t#\tdeg C
            ... \t0\t0,06\t2,00054E-001\t1,72821E-005\t0,00000E+000\t2,00000E-001\t6,45222E-004\t9\t..........a\t0\t-327,75
            ... \t1\t0,12\t1,97170E-001\t1,04547E-005\t0,00000E+000\t1,97000E-001\t-1,17889E-003\t9\t..........a\t0\t-327,75
            ... ''')
            >>> from echemdbconverters.csvloader import CSVloader
            >>> csv = CSVloader.create('gamry')(file)
            >>> csv.header_lines
            4

        """

        import re

        expression = re.compile(r"CURVE\tTABLE\t(\d+)")

        for idx, line in enumerate(self.file.readlines()):
            if expression.match(line):
                return idx + 1

        raise KeyError("Could not find a line containing `Curve Label` in the file.")

    @property
    def column_header_lines(self):
        r"""The number of lines containing descriptive information
        on the columns of Gamry DAT files is 2.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO('''EXPLAIN
            ... TAG\tCV
            ... TITLE\tLABEL\tCyclic Voltammetry\tTest &Identifier
            ... CURVE\tTABLE\t3597
            ... \tPt\tT\tVf\tIm\tVu\tSig\tAch\tIERange\tOver\tCycle\tTemp
            ... \t#\ts\tV vs. Ref.\tA\tV\tV\tV\t#\tbits\t#\tdeg C
            ... \t0\t0,06\t2,00054E-001\t1,72821E-005\t0,00000E+000\t2,00000E-001\t6,45222E-004\t9\t..........a\t0\t-327,75
            ... \t1\t0,12\t1,97170E-001\t1,04547E-005\t0,00000E+000\t1,97000E-001\t-1,17889E-003\t9\t..........a\t0\t-327,75
            ... ''')
            >>> from echemdbconverters.csvloader import CSVloader
            >>> csv = CSVloader.create('gamry')(file)
            >>> csv.column_header_lines
            2

        """
        return 2

    @property
    def df_original(self):
        r"""A pandas dataframe of the original data in the file.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO('''EXPLAIN
            ... TAG\tCV
            ... TITLE\tLABEL\tCyclic Voltammetry\tTest &Identifier
            ... CURVE\tTABLE\t3597
            ... \tPt\tT\tVf\tIm\tVu\tSig\tAch\tIERange\tOver\tCycle\tTemp
            ... \t#\ts\tV vs. Ref.\tA\tV\tV\tV\t#\tbits\t#\tdeg C
            ... \t0\t0,06\t2,00054E-001\t1,72821E-005\t0,00000E+000\t2,00000E-001\t6,45222E-004\t9\t..........a\t0\t-327,75
            ... \t1\t0,12\t1,97170E-001\t1,04547E-005\t0,00000E+000\t1,97000E-001\t-1,17889E-003\t9\t..........a\t0\t-327,75
            ... ''')
            >>> from echemdbconverters.csvloader import CSVloader
            >>> csv = CSVloader.create('gamry')(file)
            >>> csv.df_original
               Pt / #  T / s  Vf / V vs. Ref.  ...  Over / bits  Cycle / #  Temp / deg C
            0       0   0.06         0.200054  ...  ..........a          0       -327.75
            1       1   0.12         0.197170  ...  ..........a          0       -327.75
            ...

        """
        import pandas as pd

        return pd.read_csv(
            self.data,
            sep="\t",
            #  TODO: set manually for now
            # decimal=',',
            decimal=self.decimal,
            names=self.column_header_names,
        ).reset_index(drop=True)

    @property
    def _unnecessary_columns(self):
        return ["Unnamed", "Pt", "Over", "IERange"]

    @property
    def df(self):
        r"""
        A pandas dataframe with the data of the EC-Lab MPT file.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO('''EXPLAIN
            ... TAG\tCV
            ... TITLE\tLABEL\tCyclic Voltammetry\tTest &Identifier
            ... CURVE\tTABLE\t3597
            ... \tPt\tT\tVf\tIm\tVu\tSig\tAch\tIERange\tOver\tCycle\tTemp
            ... \t#\ts\tV vs. Ref.\tA\tV\tV\tV\t#\tbits\t#\tdeg C
            ... \t0\t0,06\t2,00054E-001\t1,72821E-005\t0,00000E+000\t2,00000E-001\t6,45222E-004\t9\t..........a\t0\t-327,75
            ... \t1\t0,12\t1,97170E-001\t1,04547E-005\t0,00000E+000\t1,97000E-001\t-1,17889E-003\t9\t..........a\t0\t-327,75
            ... ''')
            >>> from echemdbconverters.csvloader import CSVloader
            >>> csv = CSVloader.create('gamry')(file)
            >>> csv.df
               Pt / #  T / s  Vf / V vs. Ref.  ...  Over / bits  Cycle / #  Temp / deg C
            0       0   0.06         0.200054  ...  ..........a          0       -327.75
            1       1   0.12         0.197170  ...  ..........a          0       -327.75
            ...

        """
        import pandas as pd

        df = pd.read_csv(
            self.data, sep="\t", decimal=self.decimal, names=self.column_header_names
        ).reset_index(drop=True)

        return df

        # df = self.df_original

        # df.columns = [f"{col} / {df.iloc[0, i]}" for i, col in enumerate(df.columns)]

        # # Remove the first row to clean up
        # df = df.iloc[1:].reset_index(drop=True)

        # for column in df.columns:
        #     for unnecessary_colum in self._unnecessary_columns:
        #         if unnecessary_colum in column:
        #             del df[column]

        # return df

    @property
    def decimal(self):
        r"""
        Returns the decimal separator in the MPT,
        which depends on the language settings of the operating system running the software.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO('''EXPLAIN
            ... TAG\tCV
            ... TITLE\tLABEL\tCyclic Voltammetry\tTest &Identifier
            ... CURVE\tTABLE\t3597
            ... \tPt\tT\tVf\tIm\tVu\tSig\tAch\tIERange\tOver\tCycle\tTemp
            ... \t#\ts\tV vs. Ref.\tA\tV\tV\tV\t#\tbits\t#\tdeg C
            ... \t0\t0,06\t2,00054E-001\t1,72821E-005\t0,00000E+000\t2,00000E-001\t6,45222E-004\t9\t..........a\t0\t-327,75
            ... \t1\t0,12\t1,97170E-001\t1,04547E-005\t0,00000E+000\t1,97000E-001\t-1,17889E-003\t9\t..........a\t0\t-327,75
            ... ''')
            >>> from echemdbconverters.csvloader import CSVloader
            >>> csv = CSVloader.create('gamry')(file)
            >>> csv.decimal
            ','

        """
        # The values in the DAT files are possibly always tab separated.
        # The data in the file only consist of numbers.
        # Hence we simply determine if the line contains a comma or not.
        # Since the first row in the date contains the units to the header
        # we validate the second wor of the data.
        if "," in self.data.readlines()[1]:
            return ","

        return "."
