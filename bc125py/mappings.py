"""More complex mappings for human readable values to scanner data"""


import re


# region CTCSS/DCS


# A mapping of internal special values to human-friendly values
SPECIAL_CTCSS_DCS_VALUES: dict[int, str] = {
	0: "none",
	127: "search",
	240: "no_tone",
}

# A mapping of internal CTCSS values to human-friendly values
CTCSS: dict[int, str] = {
	64: "ctcss_67.0",
	65: "ctcss_69.3",
	66: "ctcss_71.9",
	67: "ctcss_74.4",
	68: "ctcss_77.0",
	69: "ctcss_79.7",
	70: "ctcss_82.5",
	71: "ctcss_85.4",
	72: "ctcss_88.5",
	73: "ctcss_91.5",
	74: "ctcss_94.8",
	75: "ctcss_97.4",
	76: "ctcss_100.0",
	77: "ctcss_103.5",
	78: "ctcss_107.2",
	79: "ctcss_110.9",
	80: "ctcss_114.8",
	81: "ctcss_118.8",
	82: "ctcss_123.0",
	83: "ctcss_127.3",
	84: "ctcss_131.8",
	85: "ctcss_136.5",
	86: "ctcss_141.3",
	87: "ctcss_146.2",
	88: "ctcss_151.4",
	89: "ctcss_156.7",
	90: "ctcss_159.8",
	91: "ctcss_162.2",
	92: "ctcss_165.5",
	93: "ctcss_167.9",
	94: "ctcss_171.3",
	95: "ctcss_173.8",
	96: "ctcss_177.3",
	97: "ctcss_179.9",
	98: "ctcss_183.5",
	99: "ctcss_186.2",
	100: "ctcss_189.9",
	101: "ctcss_192.8",
	102: "ctcss_196.6",
	103: "ctcss_199.5",
	104: "ctcss_203.5",
	105: "ctcss_206.5",
	106: "ctcss_210.7",
	107: "ctcss_218.1",
	108: "ctcss_225.7",
	109: "ctcss_229.1",
	110: "ctcss_233.6",
	111: "ctcss_241.8",
	112: "ctcss_250.3",
	113: "ctcss_254.1"
}

# A mapping of internal DCS values to human-friendly values
DCS: dict[int, str] = {
	128: "dcs_23",
	129: "dcs_25",
	130: "dcs_26",
	131: "dcs_31",
	132: "dcs_32",
	133: "dcs_36",
	134: "dcs_43",
	135: "dcs_47",
	136: "dcs_51",
	137: "dcs_53",
	138: "dcs_54",
	139: "dcs_65",
	140: "dcs_71",
	141: "dcs_72",
	142: "dcs_73",
	143: "dcs_74",
	144: "dcs_114",
	145: "dcs_115",
	146: "dcs_116",
	147: "dcs_122",
	148: "dcs_125",
	149: "dcs_131",
	150: "dcs_132",
	151: "dcs_134",
	152: "dcs_143",
	153: "dcs_145",
	154: "dcs_152",
	155: "dcs_155",
	156: "dcs_156",
	157: "dcs_162",
	158: "dcs_165",
	159: "dcs_172",
	160: "dcs_174",
	161: "dcs_205",
	162: "dcs_212",
	163: "dcs_223",
	164: "dcs_225",
	165: "dcs_226",
	166: "dcs_243",
	167: "dcs_244",
	168: "dcs_245",
	169: "dcs_246",
	170: "dcs_251",
	171: "dcs_252",
	172: "dcs_255",
	173: "dcs_261",
	174: "dcs_263",
	175: "dcs_265",
	176: "dcs_266",
	177: "dcs_271",
	178: "dcs_274",
	179: "dcs_306",
	180: "dcs_311",
	181: "dcs_315",
	182: "dcs_325",
	183: "dcs_331",
	184: "dcs_332",
	185: "dcs_343",
	186: "dcs_346",
	187: "dcs_351",
	188: "dcs_356",
	189: "dcs_364",
	190: "dcs_365",
	191: "dcs_371",
	192: "dcs_411",
	193: "dcs_412",
	194: "dcs_413",
	195: "dcs_423",
	196: "dcs_431",
	197: "dcs_432",
	198: "dcs_445",
	199: "dcs_446",
	200: "dcs_452",
	201: "dcs_454",
	202: "dcs_455",
	203: "dcs_462",
	204: "dcs_464",
	205: "dcs_465",
	206: "dcs_466",
	207: "dcs_503",
	208: "dcs_506",
	209: "dcs_516",
	210: "dcs_523",
	211: "dcs_526",
	212: "dcs_532",
	213: "dcs_546",
	214: "dcs_565",
	215: "dcs_606",
	216: "dcs_612",
	217: "dcs_624",
	218: "dcs_627",
	219: "dcs_631",
	220: "dcs_632",
	221: "dcs_654",
	222: "dcs_662",
	223: "dcs_664",
	224: "dcs_703",
	225: "dcs_712",
	226: "dcs_723",
	227: "dcs_731",
	228: "dcs_732",
	229: "dcs_734",
	230: "dcs_743",
	231: "dcs_754",
}

VALID_CTCSS_DCS_VALUES: dict[int, str] = {**SPECIAL_CTCSS_DCS_VALUES, **CTCSS, **DCS}


def ctcss_dcs_to_human(code: int) -> str:
	"""Lookup CTCSS/DCS code and return a human-friendly value.

	Args:
		code: The CTCSS/DCS code to lookup.

	Returns:
		The human-friendly value of the code.

	Raises:
		ValueError: If the code is not valid.
	"""

	try:
		return VALID_CTCSS_DCS_VALUES[code]
	except KeyError as exc:
		raise ValueError(f"invalid internal ctcss/dcs: {code}") from exc


def ctcss_dcs_to_internal(provided: str) -> int:
	"""Map the user provided value to the internal code.

	Allow various and case insensitve input for for 0, 127, and 240.

	Args:
		provided: The user provided value.

	Returns:
		The internal code.

	Raises:
		ValueError: If the provided value is not valid.
	"""

	minimize_regex = r"[^0-9a-z]"

	provided = str(provided).lower()
	provided = re.sub(minimize_regex, "", provided)

	for key, value in VALID_CTCSS_DCS_VALUES.items():
		value = re.sub(minimize_regex, "", value)
		if value == provided:
			return key

	raise ValueError("Invalid input value: " + str(provided))


# endregion