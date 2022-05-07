from enum import Enum


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


	def import_from_command_response(self, command_response: tuple) -> None:
		(self.attrib) = command_response


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


	def import_from_command_response(self, command_response: tuple) -> None:
		(self.model) = command_response


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


	def import_from_command_response(self, command_response: tuple) -> None:
		(self.version) = command_response


	def to_dict(self) -> str:
		return {"version": self.version}


# BLT Backlight Settings
class Backlight(_ScannerDataObject):
	"""Scanner backlight settings

	Attributes:
		backlight (str): The backlight state of the scanner
	
	Notes:
		Backlight value expects specific code
		Explore BacklightMode(Enum) to see valid modes
	"""

	# Backlight value enum
	class BacklightMode(Enum):
		AlwaysOn = "AO"
		AlwaysOff = "AF"
		Keypress = "KY"
		Squelch = "SQ"
		KeypressSquelch = "KS"


	# Defaults
	backlight: str = "AF"


	def __init__(self, data: dict = {}) -> None:
		if data:
			self.backlight = data.backlight


	def get_fetch_command(self, *args, **kwargs) -> str:
		return "BLT"


	def to_write_command(self) -> tuple:
		return (self.get_fetch_command, self.backlight)

	def import_from_command_response(self, command_response: tuple) -> None:
		(self.backlight) = command_response


	def to_dict(self) -> str:
		return {"backlight": self.backlight}


# BSV Battery Charge Timer
class BatteryChargeTimer(_ScannerDataObject):
	"""Scanner battery charge timer. Controls how long
	(in hours) the scanner will charge its batteries for
	when plugged into USB.

	Attributes:
		hours (int): The maximum charge time, in hours [1-16]
	
	Notes:
		level must be in range [1-16]
		level is in hours

		Recommended charge time for Ni-MH:
			1500 mAh - 9
			1800 mAh - 11
			2000 mAh - 12
			2100 mAh - 13
			2200 mAh - 13
			2300 mAh - 14
			2500 mAh - 15
			2700 mAh - 16
	"""

	# Defaults
	hours: int = 9


	def __init__(self, data: dict = {}) -> None:
		if data:
			self.hours = data.hours


	def get_fetch_command(self, *args, **kwargs) -> str:
		return "BSV"


	def to_write_command(self) -> tuple:
		return (self.get_fetch_command, self.hours)
	

	def import_from_command_response(self, command_response: tuple) -> None:
		self.hours = int(command_response[0])


	def to_dict(self) -> str:
		return {"hours": self.hours}


# CLR Clear Scanner Memory
class ClearScannerMemory(_ScannerDataObject):
	"""Clear all scanner memory, settings, and channels (command only)

	Attributes:
		None
	
	Notes:
		No attributes. Command only. Use get_fetch_command()
		Takes some time to complete
	"""

	def __init__(self, data: dict = {}) -> None:
		pass


	def get_fetch_command(self) -> str:
		return "CLR"


# KBP Keypad/Beep settings
class KeypadSettings(_ScannerDataObject):
	"""Keypad/beep settings

	Attributes:
		beep_level (int): Key beep level, 0: Auto, 99: Off
		key_lock (int): Keypad lock status, 0: Unlocked, 1: Locked
	
	Notes:
		Explore the BeepLevel and KeypadLock enums
	"""

	# Key beep level enum
	class BeepLevel(Enum):
		Auto = 0
		Off = 99
	

	# Keypad lock enum
	class KeypadLock:
		Unlocked = 0
		Locked = 1


	# Defaults
	beep_level: int = 0
	key_lock: int = 0


	def __init__(self, data: dict = {}) -> None:
		if data:
			self.beep_level = data.beep_level
			self.key_lock = data.key_lock


	def get_fetch_command(self, *args, **kwargs) -> str:
		return "KBP"


	def to_write_command(self) -> tuple:
		return (self.get_fetch_command, self.beep_level, self.key_lock)


	def import_from_command_response(self, command_response: tuple) -> None:
		self.beep_level = int(command_response[0])
		self.key_lock = int(command_response[1])


	def to_dict(self) -> str:
		return {
			"beep_level": self.beep_level,
			"key_lock": self.key_lock
		}


# PRI Priority Mode
class PriorityMode(_ScannerDataObject):
	"""Scanner priority mode

	Attributes:
		mode (int): Mode setting [0-3]
	
	Notes:
		Explore the PrioritySetting enum
	"""

	# Priority Setting enum
	class PrioritySetting(Enum):
		Off = 0
		On = 1
		PlusOn = 2
		DoNotDisturb = 3


	# Defaults
	mode: int = 0


	def __init__(self, data: dict = {}) -> None:
		if data:
			self.mode = data.mode


	def get_fetch_command(self, *args, **kwargs) -> str:
		return "PRI"


	def to_write_command(self) -> tuple:
		return (self.get_fetch_command, self.mode)


	def import_from_command_response(self, command_response: tuple) -> None:
		(self.mode) = command_response


	def to_dict(self) -> str:
		return {"mode": self.mode}


# SCG Set active scanner banks
class EnabledChannelBanks(_ScannerDataObject):
	"""Control which scanning banks are enabled on the scanner
	Disabled banks will be skipped when in "Scan" mode

	Attributes:
		banks (bool list, length 10): An array represeting each bank and whether or not it's enabled
	
	Notes:
		banks[] length must be 10
	"""

	# Defaults
	banks: list = [True] * 10


	def __init__(self, data: dict = {}) -> None:
		if data:
			self.banks = data.banks


	def get_fetch_command(self, *args, **kwargs) -> str:
		return "SCG"


	def to_write_command(self) -> tuple:
		cmd_str = "".join(map(lambda n: "1" if n else "0", self.banks))
		return (self.get_fetch_command, cmd_str)


	def import_from_command_response(self, command_response: tuple) -> None:
		cmd_str: str
		(cmd_str) = command_response
		self.banks = map(lambda n: n == "1", cmd_str.split(""))


	def to_dict(self) -> str:
		return {"banks": self.banks}
