r"""Fields describing specific csv data, such as biologic MPT files."""

biologic_fields = [
    {
        "name": "mode",
    },
    {
        "name": "ox/red",
    },
    {
        "name": "error",
    },
    {
        "name": "control changes",
    },
    {
        "name": "counter inc.",
    },
    {"name": "time/s", "unit": "s", "dimension": "t", "description": "relative time"},
    {
        "name": "control/V",
        "unit": "V",
        "dimension": "E",
        "description": "control voltage",
    },
    {
        "name": "Ewe/V",
        "unit": "V",
        "dimension": "E",
        "description": "working electrode potential",
    },
    {
        "name": "<I>/mA",
        "unit": "mA",
        "dimension": "I",
        "description": "working electrode current",
    },
    {"name": "cycle number", "description": "cycle number"},
    {
        "name": "(Q-Qo)/C",
        "unit": "C",
    },
    {"name": "I Range", "description": "current range"},
    {"name": "P/W", "unit": "W", "dimension": "P", "description": "power"},
]

biologic_fields_alt_names = {
    "<I>/mA": "I",
    "Ewe/V": "E",
    "<Ewe>/V": "E",
    "time/s": "t",
    "Re(Z)/Ohm": "Re(Z)",
    "-Im(Z)/Ohm": "-Im(Z)",
    "freq/Hz": "f",
    "Phase(Z)/deg": "Phase(Z)",
}
