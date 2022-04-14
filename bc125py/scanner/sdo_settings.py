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


	__backlight: Mode = Mode.AlwaysOff

	def set(self, bl: Union[Mode, str]) -> None:
		if type(bl) is str:
			try:
				bl = self.Mode(bl)
			except ValueError:
				bl = self.Mode[bl]

		self.__backlight = bl


	def get(self) -> str:
		return self.__backlight.name


	def to_get_command(self) -> str:
		return "BLT"


	def to_write_command(self) -> str:
		return ",".join(self.to_get_command(), self.__backlight.value)


	def import_from_command_response(self, command_response: tuple) -> None:
		self.set(command_response[0])


	def to_save_file_format(self) -> str:
		return self.__backlight.name


	def import_from_save_file_format(self, in_text: str) -> None:
		self.set(in_text)


class BatteryChargeTime(_ScannerDataObject):

	MAX_CHARGE_TIME: int = 16
	__battery_charge_time: int = 14

	def set(self, bct: Union[int, str]) -> None:
		if type(bct) is str:
			bct = int(bct)

		if type(bct) is not int:
			raise TypeError()

		if bct not in range(1, self.MAX_CHARGE_TIME + 1):
			raise ValueError("Charge time must be within range [1-16]")

		self.__battery_charge_time = bct


	def get(self) -> int:
		return self.__battery_charge_time


	def to_get_command(self) -> str:
		return "BSV"


	def to_write_command(self) -> str:
		return ",".join(self.to_get_command(), str(self.__battery_charge_time))


	def import_from_command_response(self, command_response: tuple) -> None:
		self.set_battery_charge_time(command_response[0])


	def to_save_file_format(self) -> str:
		return str(self.__battery_charge_time)


	def import_from_save_file_format(self, in_text: str) -> None:
		self.set_battery_charge_time(in_text)
