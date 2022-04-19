from bc125py.scanner.scanner_data import _ScannerDataObject


class EnterProgramMode(_ScannerDataObject):

	def to_get_command(self) -> str:
		return "PRG"


class ExitProgramMode(_ScannerDataObject):

	def to_get_command(self) -> str:
		return "EPG"


class ClearAllMemory(_ScannerDataObject):
	def to_get_command(self) -> str:
		return "CLR"
