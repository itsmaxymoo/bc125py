"""Lookup values for CTCSS and DCS codes."""

# Documented string representations of special values
NONE: str = "NONE/All"
SEARCH: str = "SEARCH"
NO_TONE: str = "NO_TONE"

# A mapping of internal special values to human-friendly values
SPECIAL_VALUES: dict[int, str] = {
    0: NONE,
    127: SEARCH,
    240: NO_TONE,
}

# A mapping of internal CTCSS values to human-friendly values
CTCSS: dict[int, str] = {
    64: "67.0",
    65: "69.3",
    66: "71.9",
    67: "74.4",
    68: "77.0",
    69: "79.7",
    70: "82.5",
    71: "85.4",
    72: "88.5",
    73: "91.5",
    74: "94.8",
    75: "97.4",
    76: "100.0",
    77: "103.5",
    78: "107.2",
    79: "110.9",
    80: "114.8",
    81: "118.8",
    82: "123.0",
    83: "127.3",
    84: "131.8",
    85: "136.5",
    86: "141.3",
    87: "146.2",
    88: "151.4",
    89: "156.7",
    90: "159.8",
    91: "162.2",
    92: "165.5",
    93: "167.9",
    94: "171.3",
    95: "173.8",
    96: "177.3",
    97: "179.9",
    98: "183.5",
    99: "186.2",
    100: "189.9",
    101: "192.8",
    102: "196.6",
    103: "199.5",
    104: "203.5",
    105: "206.5",
    106: "210.7",
    107: "218.1",
    108: "225.7",
    109: "229.1",
    110: "233.6",
    111: "241.8",
    112: "250.3",
    113: "254.1"
}

# A mapping of internal DCS values to human-friendly values
DCS: dict[int, str] = {
    128: "23",
    129: "25",
    130: "26",
    131: "31",
    132: "32",
    133: "36",
    134: "43",
    135: "47",
    136: "51",
    137: "53",
    138: "54",
    139: "65",
    140: "71",
    141: "72",
    142: "73",
    143: "74",
    144: "114",
    145: "115",
    146: "116",
    147: "122",
    148: "125",
    149: "131",
    150: "132",
    151: "134",
    152: "143",
    153: "145",
    154: "152",
    155: "155",
    156: "156",
    157: "162",
    158: "165",
    159: "172",
    160: "174",
    161: "205",
    162: "212",
    163: "223",
    164: "225",
    165: "226",
    166: "243",
    167: "244",
    168: "245",
    169: "246",
    170: "251",
    171: "252",
    172: "255",
    173: "261",
    174: "263",
    175: "265",
    176: "266",
    177: "271",
    178: "274",
    179: "306",
    180: "311",
    181: "315",
    182: "325",
    183: "331",
    184: "332",
    185: "343",
    186: "346",
    187: "351",
    188: "356",
    189: "364",
    190: "365",
    191: "371",
    192: "411",
    193: "412",
    194: "413",
    195: "423",
    196: "431",
    197: "432",
    198: "445",
    199: "446",
    200: "452",
    201: "454",
    202: "455",
    203: "462",
    204: "464",
    205: "465",
    206: "466",
    207: "503",
    208: "506",
    209: "516",
    210: "523",
    211: "526",
    212: "532",
    213: "546",
    214: "565",
    215: "606",
    216: "612",
    217: "624",
    218: "627",
    219: "631",
    220: "632",
    221: "654",
    222: "662",
    223: "664",
    224: "703",
    225: "712",
    226: "723",
    227: "731",
    228: "732",
    229: "734",
    230: "743",
    231: "754",
}

VALID_VALUES: dict[int, str] = {**SPECIAL_VALUES, **CTCSS, **DCS}


def ctcss_dcs_i2h(code: int|str) -> int | float | str:
    """Lookup CTCSS/DCS code and return a human-friendly value.

    Although multiple viable values exist for 0, 127, 240, use the value from the protocol
    documentation.

    Args:
        code: The CTCSS/DCS code to lookup.

    Returns:
        The human-friendly value of the code.

    Raises:
        ValueError: If the code is not valid.
    """
    code = int(code)
    try:
        return VALID_VALUES[code]
    except KeyError as exc:
        raise ValueError(f"invalid internal ctcss/dcs: {code}") from exc


def ctcss_dcs_h2i(provided: str | float | int) -> int:
    """Map the user provided value to the internal code.

    Allow various and case insensitve input for for 0, 127, and 240.
    Allow for the user provided value to be an str, integer or float.

    Args:
        provided: The user provided value.

    Returns:
        The internal code.
    
    Raises:
        ValueError: If the provided value is not valid.
    """
    _provided = str(provided)

    # Some convenience variations
    if _provided.lower() in ("none", "all", "noneall"):
        _provided = NONE
    if _provided.lower() in ("no tone", "notone"):
        _provided = NO_TONE

    for key, value in VALID_VALUES.items():
        if value.lower() == _provided.lower():
            return key
    _provided = _provided.lower()
    
    
    valid_values = f"Special: [{', '.join(SPECIAL_VALUES.values())}]" 
    valid_values += f" CTCSS: [{', '.join(CTCSS.values())}]"
    valid_values += f" DCS: [{', '.join(DCS.values())}]"
    raise ValueError(f"invalid provided ctcss/dcs: {provided}, valid values: {valid_values}")
