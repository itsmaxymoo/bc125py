from ctypes import Union
from enum import Enum
from bc125py.scanner.scanner_data import _ScannerDataObject


class Backlight(_ScannerDataObject):

	class Mode(Enum):
		AlwaysOn = "AO"
		AlwaysOff = "AF"
		Keypress = "KY"
		KeySquelch = "KS"
		Squelch = "SQ"


	__backlight: Mode


	def set_backlight(self, bl: Union[Mode, str]) -> None:
		if type(bl) is str:
			bl = self.Mode(bl)
		
		self.__backlight = bl


	def get_command_name(self) -> str:
		return "BLT"


	def to_write_command(self) -> str:
		return ",".join(self.get_command_name(), self.__backlight.value)


	def import_from_command_response(self, command_response: tuple) -> None:
		self.set_backlight(command_response[0])


	def to_save_file_format(self) -> str:
		return self.__backlight.value


	def import_from_save_file_format(self, in_text: str) -> None:
		self.set_backlight(in_text)
