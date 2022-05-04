class _ScannerDataObject:
	"""An object to represent a data object on the scanner, eg: channel, volume, backlight, etc...
	"""

	def __init__(self, data: dict = {}) -> None:
		"""Data object constructor

		Args:
			data (dict, optional): Object's values. Default if empty. Defaults to {}.

		Raises:
			NotImplementedError: if sdo._ScannerDataObject is instantiated directly
		"""

		if type(self) == _ScannerDataObject:
			raise NotImplementedError(type(self).__name__ + " cannot be instantiated directly (abstract)")


	def get_fetch_command(self, *args, **kwargs) -> str:
		"""Get the scanner command to fetch the data for this object

		Raises:
			NotImplementedError: if this function is not implemented in a child class

		Returns:
			str, tuple: scanner command
		"""

		raise NotImplementedError(type(self).__name__ + " must implement get_fetch_command()")


	def to_write_command(self) -> tuple:
		"""Get the scanner command to write this object to the device

		Raises:
			NotImplementedError: if this function is not implemented in a child class

		Returns:
			tuple: scanner command to write this data object to the scanner
		"""

		raise NotImplementedError(type(self).__name__ + " must implement to_write_command()")


	def import_from_command_response(self, command_response: tuple) -> None:
		"""From a command response tuple, import the values into this object

		Args:
			command_response (tuple): command response data

		Raises:
			NotImplementedError: if this function is not implemented in a child class
		"""

		raise NotImplementedError(type(self).__name__ + " must implement import_from_command_response()")


	def to_dict(self) -> str:
		"""Convert this object to a dict

		Raises:
			NotImplementedError: if this function is not implemented in a child class

		Returns:
			str: dict representing this object
		"""

		raise NotImplementedError(type(self).__name__ + " must implement to_dict()")


# Example SDO to copy & paste
class _E(_ScannerDataObject):
	"""Example SDO to copy & paste (describe SDO)

	Attributes:
		List all
	
	Notes:
		List all
	"""

	# Defaults
	attrib = 0

	def __init__(self, data: dict = {}) -> None:
		if data:
			self.attrib = data.attrib


	def get_fetch_command(self, *args, **kwargs) -> str:
		return "EXX"


	def to_write_command(self) -> tuple:
		return (self.get_fetch_command, self.attrib)


	def to_dict(self) -> str:
		return {"attrib": self.attrib}


# PRG Program Mode
class EnterProgramMode(_ScannerDataObject):
	"""Enter program mode (command only)

	Attributes:
		None
	
	Notes:
		No attributes. Command only. Use get_fetch_command()
	"""

	def __init__(self, data: dict = {}) -> None:
		pass


	def get_fetch_command(self) -> str:
		return "PRG"


# EPG Exit Program Mode
class ExitProgramMode(_ScannerDataObject):
	"""Exit program mode (command only)

	Attributes:
		None
	
	Notes:
		No attributes. Command only. Use get_fetch_command()
	"""

	def __init__(self, data: dict = {}) -> None:
		pass


	def get_fetch_command(self) -> str:
		return "EPG"


# MDL Device Model
class DeviceModel(_ScannerDataObject):
	"""Scanner device model

	Attributes:
		model (str): The scanner device mode
	
	Notes:
		Read only
	"""

	# Defaults
	model: str

	def __init__(self, data: dict = {}) -> None:
		if data:
			self.model = data.model


	def get_fetch_command(self, *args, **kwargs) -> str:
		return "MDL"


	def to_dict(self) -> str:
		return {"model": self.model}


# VER Firmware version
class FirmwareVersion(_ScannerDataObject):
	"""Scanner firmware version

	Attributes:
		version (str): The firmware version of the scanner
	
	Notes:
		Read only
	"""

	# Defaults
	version: str

	def __init__(self, data: dict = {}) -> None:
		if data:
			self.version = data.version


	def get_fetch_command(self, *args, **kwargs) -> str:
		return "VER"


	def to_dict(self) -> str:
		return {"version": self.version}
