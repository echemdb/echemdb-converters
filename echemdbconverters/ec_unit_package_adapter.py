r"""
Creates standardized echemdb datapackage compatible CSV.

The file loaded must have the columns t, U/E, and I/j.
In addition, the fields to these columns must have a unit.

EXAMPLES::

    >>> from io import StringIO
    >>> file = StringIO(r'''t,E,j,x
    ... 0,0,0,0
    ... 1,1,1,1''')
    >>> from echemdbconverters.csvloader import CSVloader
    >>> metadata = {'figure description': {'schema': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'}]}}}
    >>> ec = ECUnitPackageAdapter(CSVloader(file=file), fields=metadata['figure description']['schema']['fields'])
    >>> ec.df
       t  E  j  x
    0  0  0  0  0
    1  1  1  1  1

The original dataframe can be accessed from the loader::

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

    The file loaded must have the columns t, U or E, and I or j.
    In addition, the fields to these columns must have a unit.

    EXAMPLES::

        >>> from io import StringIO
        >>> file = StringIO(r'''t,E,j,x
        ... 0,0,0,0
        ... 1,1,1,1''')
        >>> from echemdbconverters.csvloader import CSVloader
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
        [{'name': 't', 'type': 'integer', 'unit': 's'},
        {'name': 'E', 'type': 'integer', 'unit': 'V', 'reference': 'RHE'},
        {'name': 'j', 'type': 'integer', 'unit': 'uA / cm2'},
        {'name': 'x', 'type': 'integer', 'unit': 'm'}]

    """
    core_dimensions = {"time": ["t"], "voltage": ["E", "U"], "current": ["I", "j"]}

    def __init__(self, loader, fields=None, metadata=None):
        self.loader = loader
        self._fields = self.loader.derive_fields(fields=fields)
        self._metadata = metadata

    @staticmethod
    def create(device=None):
        r"""
        Calls a specific `EC adapter` based on a given device.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from echemdbconverters.csvloader import CSVloader
            >>> metadata = {'figure description': {'schema': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'}]}}}
            >>> ec = ECUnitPackageAdapter.create('eclab')(CSVloader(file=file), fields=metadata['figure description']['schema']['fields'])
            >>> ec.df
            t  E  j  x
            0  0  0  0  0
            1  1  1  1  1

        """
        if device == "eclab":
            from echemdbconverters.eclab_adapter import ECLabAdapter

            return ECLabAdapter

        raise KeyError(
            f"Device wth name '{device}' is unknown to the ECUnitPackageAdapter."
        )

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
            >>> from echemdbconverters.csvloader import CSVloader
            >>> ec = ECUnitPackageAdapter(CSVloader(file))
            >>> ec.field_name_conversion
            {}
        """
        return {}

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
            >>> from echemdbconverters.csvloader import CSVloader
            >>> metadata = {'figure description': {'schema': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'}]}}}
            >>> ec = ECUnitPackageAdapter(CSVloader(file=file), fields=metadata['figure description']['schema']['fields'])
            >>> ec.fields() # doctest: +NORMALIZE_WHITESPACE
            [{'name': 't', 'type': 'integer', 'unit': 's'},
            {'name': 'E', 'type': 'integer', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'integer', 'unit': 'uA / cm2'},
            {'name': 'x', 'type': 'integer', 'unit': 'm'}]

        A CSV with incomplete field information.::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from echemdbconverters.csvloader import CSVloader
            >>> metadata = {'figure description': {'schema': {'fields': [{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'t', 'unit':'s'}]}}}
            >>> ec = ECUnitPackageAdapter(CSVloader(file=file), fields=metadata['figure description']['schema']['fields'])
            >>> ec.fields() # doctest: +NORMALIZE_WHITESPACE
            [{'name': 't', 'type': 'integer', 'unit': 's'},
            {'name': 'E', 'type': 'integer', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'type': 'integer', 'unit': 'uA / cm2'},
            {'name': 'x', 'type': 'integer'}]

        A CSV with a missing potential axis which is, however, defined in the field description.::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,j,x
            ... 0,0,0
            ... 1,1,1''')
            >>> from echemdbconverters.csvloader import CSVloader
            >>> metadata = {'figure description': {'schema': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'}]}}}
            >>> ec = ECUnitPackageAdapter(CSVloader(file=file), fields=metadata['figure description']['schema']['fields'])
            >>> ec.fields()
            Traceback (most recent call last):
            ...
            KeyError: "No column with a 'voltage' axis."


        Fields with missing units in one o the core dimension fields.::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from echemdbconverters.csvloader import CSVloader
            >>> metadata = {'figure description': {'schema': {'fields': [{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'t'}]}}}
            >>> ec = ECUnitPackageAdapter(CSVloader(file=file), fields=metadata['figure description']['schema']['fields'])
            >>> ec.fields()
            Traceback (most recent call last):
            ...
            KeyError: "No unit associated with the field named 't'"

        """
        import itertools

        from frictionless import Schema

        schema = Schema(fields=self._fields)

        for name in schema.field_names:
            # Change the name of specific fields.
            if name in self.field_name_conversion:
                schema.update_field(name, {"original name": name})
                schema.update_field(name, {"name": self.field_name_conversion[name]})
            # Validate that each field with a core dimension has a unit.
            if name in list(
                itertools.chain.from_iterable(list(self.core_dimensions.values()))
            ):
                try:
                    schema.get_field(name).custom["unit"]
                except KeyError as exc:
                    raise KeyError(
                        f"No unit associated with the field named '{name}'"
                    ) from exc

        # Validates that the column names contain a time, voltage and current axis.
        for key, item in self.core_dimensions.items():
            if not set(item).intersection(set(schema.field_names)):
                raise KeyError(f"No column with a '{key}' axis.")

        return schema.fields

    @property
    def column_names(self):
        """
        The EC file must have at least three dimensions, including time, voltage and current.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from echemdbconverters.csvloader import CSVloader
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
            >>> from echemdbconverters.csvloader import CSVloader
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

    @property
    def metadata(self):
        r"""
        Returns metadata associated with the CSV.

        EXAMPLES::

            >>> from io import StringIO
            >>> file = StringIO(r'''t,E,j,x
            ... 0,0,0,0
            ... 1,1,1,1''')
            >>> from echemdbconverters.csvloader import CSVloader
            >>> metadata = {'figure description': {'fields': [{'name':'t', 'unit':'s'},{'name':'E', 'unit':'V', 'reference':'RHE'},{'name':'j', 'unit':'uA / cm2'},{'name':'x', 'unit':'m'}]}}
            >>> ec = ECUnitPackageAdapter(CSVloader(file), metadata=metadata)
            >>> ec.metadata  # doctest: +NORMALIZE_WHITESPACE
            {'figure description': {'fields': [{'name': 't', 'unit': 's'},
            {'name': 'E', 'unit': 'V', 'reference': 'RHE'},
            {'name': 'j', 'unit': 'uA / cm2'}, {'name': 'x', 'unit': 'm'}]}}

        """
        return self._metadata or self.loader.metadata
