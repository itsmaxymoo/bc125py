from bc125py.scanner.scanner_data import _ScannerDataObject


class EnterProgramMode(_ScannerDataObject):

	def get_command_name(self) -> str:
		return "PRG"


class ExitProgramMode(_ScannerDataObject):

	def get_command_name(self) -> str:
		return "EPG"
