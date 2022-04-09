from bc125py.scanner.scanner_data import _ScannerDataObject


class DeviceModel(_ScannerDataObject):

	__model: str

	def get_command_name(self) -> str:
		return "MDL"


	def import_from_command_response(self, command_response: tuple) -> None:
		self.__model = command_response[0]


	def to_save_file_format(self) -> str:
		return self.__model


	def import_from_save_file_format(self, in_text: str) -> None:
		self.__model = in_text


	def get_model(self):
		return self.__model


class FirmwareVersion(_ScannerDataObject):

	__ver: str

	def get_command_name(self) -> str:
		return "VER"


	def import_from_command_response(self, command_response: tuple) -> None:
		self.__ver = command_response[0]


	def to_save_file_format(self) -> str:
		return self.__ver


	def import_from_save_file_format(self, in_text: str) -> None:
		self.__ver = in_text


	def get_version(self):
		return self.__ver
