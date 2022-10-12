r"""
Converts ECLab MPT files into an echemdb datapackage compatible CSV object.
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

from .ec_unit_package_adapter import ECUnitPackageAdapter


class ECLabAdapter(ECUnitPackageAdapter):
    r"""
    Some description.

    EXAMPLES::

        >>> from io import StringIO
        >>> file = StringIO('''EC-Lab ASCII FILE
        ... Nb header lines : 6
        ...
        ... Device metadata : some metadata
        ...
        ... mode\ttime/s\tEwe/V\t<I>/mA\tcontrol/V
        ... 1\t2\t3\t4\t5
        ... 1\t2.1\t3.1\t4.1\t5.1
        ... ''')
        >>> device = 'eclab'
        >>> from .csvloader import CSVloader
        >>> from .ec_unit_package_adapter import ECUnitPackageAdapter
        >>> ec = ECUnitPackageAdapter.create(device=device)(CSVloader.create(device)(file))
        >>> ec.loader.df
           mode  time/s  Ewe/V  <I>/mA  control/V
        0     1     2.0    3.0     4.0        5.0
        1     1     2.1    3.1     4.1        5.1

        >>> ec.df
           mode    t    E    I  control/V
        0     1  2.0  3.0  4.0        5.0
        1     1  2.1  3.1  4.1        5.1

        >>> ec.fields()  # doctest: +NORMALIZE_WHITESPACE
        [{'name': 'mode'},
        {'description': 'relative time', 'dimension': 't', 'name': 't', 'unit': 's'},
        {'description': 'working electrode potential', 'dimension': 'E', 'name': 'E', 'unit': 'V'},
        {'description': 'working electrode current', 'dimension': 'I', 'name': 'I', 'unit': 'mA'},
        {'description': 'control voltage', 'dimension': 'E', 'name': 'control/V', 'unit': 'V'}]

    """

    @property
    def field_name_conversion(self):

        return {
            "time/s": "t",
            "Ewe/V": "E",
            "<I>/mA": "I",
        }
