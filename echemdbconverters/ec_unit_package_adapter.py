r"""
Creates standardized echemdb datapackage compatible CSV.

The file loaded must have the columns t, U/E, and I/j.
Other columns are not included in the output data.

EXAMPLES::

    >>> from io import StringIO
    >>> file = StringIO(r'''t,E,j,x
    ... 0,0,0,0
    ... 1,1,1,1''')
    >>> from .csvloader import CSVloader
    >>> metadata = {'figure description': {'schema': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'}]}}}
    >>> ec = ECUnitPackageAdapter(CSVloader(file=file), fields=metadata['figure description']['schema']['fields'])
    >>> ec.df
       t  E  j  x
    0  0  0  0  0
    1  1  1  1  1

The original dataframe is still accessible from the loader::

    >>> ec.loader.df
       t  E  j  x
    0  0  0  0  0
    1  1  1  1  1

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

logger = logging.getLogger("ECUnitPackageAdapter")


class ECUnitPackageAdapter:
    r"""
    Creates standardized echemdb datapackage compatible CSV.

    The file loaded must have the columns t, U/E, and I/j.
    Any other columns will be discarded.

    EXAMPLES::

        >>> from io import StringIO
        >>> file = StringIO(r'''t,E,j,x
        ... 0,0,0,0
        ... 1,1,1,1''')
        >>> from .csvloader import CSVloader
        >>> metadata = {'figure description': {'schema': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'}]}}}
        >>> ec = ECUnitPackageAdapter(CSVloader(file=file), fields=metadata['figure description']['schema']['fields'])
        >>> ec.df
           t  E  j  x
        0  0  0  0  0
        1  1  1  1  1

    A list of names describing the columns::

        >>> ec.column_names
        ['t', 'E', 'j', 'x']

        >>> ec.fields()
        [{'name': 't', 'unit': 's'}, {'name': 'E', 'reference': 'RHE', 'unit': 'V'}, {'name': 'j', 'unit': 'uA / cm2'}, {'name': 'x', 'unit': 'm'}]

    """
    core_dimensions = {"time": ["t"], "voltage": ["E", "U"], "current": ["I", "j"]}

    def __init__(self, loader, fields=None):
        self.loader = loader
        self._fields = self.loader.derive_fields(fields=fields)

    @staticmethod
    def create(device=None):
        r"""
        Calls a specific `converter` based on a given device.
        """
        from .eclab_adapater import ECLabAdapter

        devices = {
            "eclab": ECLabAdapter,  # Biologic-EClab device
        }

        if device in devices:
            return devices[device]

        raise KeyError(f"Device wth name '{device}' is unknown to the converter'.")

    @property
    def field_name_conversion(self):
        """
        A dictionary which defines new names for column names of the loaded CSV.
        For example the loaded CSV could contain a column with name `time/s`.
        In the converted CSV that column should be named `t` instead.
        In that case {'time/s':'t'} should be returned.
        The property should be adapted in the respective device converters.


        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from .csvloader import CSVloader
            >>> ec = ECUnitPackageAdapter(CSVloader(file))
            >>> ec.field_name_conversion
            {}
        """
        return {}

    @classmethod
    def _validate_core_dimensions(cls, column_names):
        """
        Validates that the column names contain a time, voltage and current axis.

        EXAMPLES::

            >>> ECUnitPackageAdapter.core_dimensions
            {'time': ['t'], 'voltage': ['E', 'U'], 'current': ['I', 'j']}

            >>> ECUnitPackageAdapter._validate_core_dimensions(column_names=['t','U','I','cycle','comment'])
            True

            >>> ECUnitPackageAdapter._validate_core_dimensions(column_names=['t','U'])
            Traceback (most recent call last):
            ...
            KeyError: "No column with a 'current' axis."

        """
        for key, item in cls.core_dimensions.items():
            if not set(item).intersection(set(column_names)):
                raise KeyError(f"No column with a '{key}' axis.")
        return True

    def fields(self):
        r"""
        A frictionless `Schema` object, including a `Fields` object
        describing the columns of the converted electrochemical data.

        In case the field names were not changed in property:name_conversion:
        the resulting schema is identical to that of the loader.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from .csvloader import CSVloader
            >>> metadata = {'figure description': {'schema': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'}]}}}
            >>> ec = ECUnitPackageAdapter(CSVloader(file=file), fields=metadata['figure description']['schema']['fields'])
            >>> ec.fields() # doctest: +NORMALIZE_WHITESPACE
            [{'name': 't', 'unit': 's'},
            {'name': 'E', 'reference': 'RHE', 'unit': 'V'},
            {'name': 'j', 'unit': 'uA / cm2'},
            {'name': 'x', 'unit': 'm'}]

        A CVS with incomplete field information.::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from .csvloader import CSVloader
            >>> metadata2 = {'figure description': {'schema': {'fields': [{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'t', 'unit':'s'}]}}}
            >>> ec = ECUnitPackageAdapter(CSVloader(file=file), fields=metadata2['figure description']['schema']['fields'])
            >>> ec.fields() # doctest: +NORMALIZE_WHITESPACE
            [{'name': 't', 'unit': 's'},
            {'name': 'E', 'reference': 'RHE', 'unit': 'V'},
            {'name': 'j', 'unit': 'uA / cm2'},
            {'comment': 'Created by echemdb-converters.', 'name': 'x'}]

        A CVS with a missing potential axis which is, however, defined in the field description.::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,j,x
            ... 0,0,0
            ... 1,1,1''')
            >>> from .csvloader import CSVloader
            >>> metadata = {'figure description': {'schema': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'}]}}}
            >>> ec = ECUnitPackageAdapter(CSVloader(file=file), fields=metadata['figure description']['schema']['fields'])
            >>> ec.fields()
            Traceback (most recent call last):
            ...
            KeyError: "No column with a 'voltage' axis."


        """
        from frictionless import Schema

        schema = Schema(fields=self._fields)

        for name in schema.field_names:
            if name in self.field_name_conversion:
                schema.get_field(name)["name"] = self.field_name_conversion[name]

        self._validate_core_dimensions(schema.field_names)

        return schema["fields"]

    @property
    def column_names(self):
        """
        The EC file must have at least three dimensions, including time, voltage and current.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from .csvloader import CSVloader
            >>> metadata = {'figure description': {'schema': {'fields': [{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'},{'name':'t', 'unit':'s'}]}}}
            >>> ec = ECUnitPackageAdapter(CSVloader(file), fields=metadata['figure description']['schema']['fields'])
            >>> ec.column_names
            ['t', 'E', 'j', 'x']

        """
        from frictionless import Schema

        return Schema(fields=self.fields()).field_names

    @property
    def df(self):
        """
        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from .csvloader import CSVloader
            >>> metadata = {'figure description': {'schema': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'}]}}}
            >>> ec = ECUnitPackageAdapter(CSVloader(file), fields=metadata['figure description']['schema']['fields'])
            >>> ec.df
               t  E  j  x
            0  0  0  0  0
            1  1  1  1  1

        """
        df = self.loader.df.copy()
        df.columns = self.column_names
        return df

    def augment(self, metadata=None):
        r"""
        Returns metadata associated with the CSV.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from .csvloader import CSVloader
            >>> metadata = {'figure description': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'}]}}
            >>> ec = ECUnitPackageAdapter(CSVloader(file))
            >>> ec.augment(metadata)  # doctest: +NORMALIZE_WHITESPACE
            {'figure description': {'fields': [{'name': 't', 'unit': 's'},
            {'name': 'E', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'unit': 'uA / cm2'}, {'name': 'x', 'unit': 'm'}]}}

        """
        return self.loader.augment(metadata)
