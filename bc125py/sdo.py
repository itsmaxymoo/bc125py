from enum import Enum


class _ScannerDataObject:
	"""An object to represent a data object on the scanner, eg: channel, volume, backlight, etc...
	"""

	def __init__(self) -> None:
		"""Data object constructor

		Raises:
			NotImplementedError: if sdo._ScannerDataObject is instantiated directly
		"""

		if type(self) == _ScannerDataObject:
			raise NotImplementedError(type(self).__name__ + " cannot be instantiated directly (abstract)")


	def to_write_command(self) -> tuple:
		"""Get the scanner command to write this object to the device

		Raises:
			NotImplementedError: if this function is not implemented in a child class

		Returns:
			tuple: scanner command to write this data object to the scanner
		"""

		raise NotImplementedError(type(self).__name__ + " must implement to_write_command()")


	def to_fetch_command(self) -> str:
		"""Get the scanner command to fetch the data for this object

		Raises:
			NotImplementedError: if this function is not implemented in a child class

		Returns:
			str, tuple: scanner command to read this object
		"""

		raise NotImplementedError(type(self).__name__ + " must implement to_fetch_command()")


	def from_command_response(self, command_response: tuple) -> None:
		"""From a command response tuple, import the values into this object

		Args:
			command_response (tuple): command response data

		Raises:
			NotImplementedError: if this function is not implemented in a child class
		"""

		raise NotImplementedError(type(self).__name__ + " must implement from_command_response()")


	def to_dict(self) -> dict:
		"""Convert this object to a dict

		Raises:
			NotImplementedError: if this function is not implemented in a child class

		Returns:
			dict: dict representing this object
		"""

		raise NotImplementedError(type(self).__name__ + " must implement to_dict()")


	def from_dict(self, data: dict) -> None:
		"""From a dict, import the values to this object

		Args:
			data (dict): The data to import to this object

		Raises:
			NotImplementedError: if this function is not implemented in a child class
		"""

		raise NotImplementedError(type(self).__name__ + " must implement from_dict()")


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


	def to_write_command(self) -> tuple:
		return (self.to_fetch_command(), self.attrib)


	def to_fetch_command(self) -> str:
		return "EXX"


	def from_command_response(self, command_response: tuple) -> None:
		(self.attrib,) = command_response


	def to_dict(self) -> dict:
		return {"attrib": self.attrib}


	def from_dict(self, data) -> None:
		self.attrib = data.attrib


# PRG Program Mode
class EnterProgramMode(_ScannerDataObject):
	"""Enter program mode (command only)

	Attributes:
		None
	
	Notes:
		No attributes. Write command only.
	"""

	def to_write_command(self) -> tuple:
		return ("PRG",)


# EPG Exit Program Mode
class ExitProgramMode(_ScannerDataObject):
	"""Exit program mode (command only)

	Attributes:
		None
	
	Notes:
		No attributes. Write command only.
	"""

	def to_write_command(self) -> tuple:
		return ("EPG",)


# MDL Device Model
class DeviceModel(_ScannerDataObject):
	"""Scanner device model

	Attributes:
		model (str): The scanner device mode
	
	Notes:
		Read only
	"""

	# Defaults
	model: str = "NO MDL"

	def to_fetch_command(self) -> str:
		return "MDL"


	def from_command_response(self, command_response: tuple) -> None:
		(self.model,) = command_response


	def to_dict(self) -> dict:
		return {"model": self.model}


	def from_dict(self, data: dict) -> None:
		self.model = data.model


# VER Firmware version
class FirmwareVersion(_ScannerDataObject):
	"""Scanner firmware version

	Attributes:
		version (str): The firmware version of the scanner
	
	Notes:
		Read only
	"""

	# Defaults
	version: str = "NO VER"

	def to_fetch_command(self) -> str:
		return "VER"


	def from_command_response(self, command_response: tuple) -> None:
		(self.version,) = command_response


	def to_dict(self) -> dict:
		return {"version": self.version}


	def from_dict(self, data: dict = {}) -> None:
		self.version = data.version


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

	def to_write_command(self) -> tuple:
		return (self.to_fetch_command(), self.backlight)


	def to_fetch_command(self) -> str:
		return "BLT"


	def from_command_response(self, command_response: tuple) -> None:
		(self.backlight,) = command_response


	def to_dict(self) -> dict:
		return {"backlight": self.backlight}


	def from_dict(self, data: dict) -> None:
		self.backlight = data.backlight


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

	def to_write_command(self) -> tuple:
		return (self.to_fetch_command(), self.hours)


	def to_fetch_command(self) -> str:
		return "BSV"


	def from_command_response(self, command_response: tuple) -> None:
		self.hours = int(command_response[0])


	def to_dict(self) -> dict:
		return {"hours": self.hours}


	def from_dict(self, data: dict) -> None:
		self.hours = data.hours


# CLR Clear Scanner Memory
class ClearScannerMemory(_ScannerDataObject):
	"""Clear all scanner memory, settings, and channels (command only)

	Attributes:
		None
	
	Notes:
		No attributes. Write command only.
		Takes some time to complete
	"""

	def to_write_command(self) -> tuple:
		return ("CLR",)


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

	def to_write_command(self) -> tuple:
		return (self.to_fetch_command(), self.beep_level, self.key_lock)


	def to_fetch_command(self) -> str:
		return "KBP"


	def from_command_response(self, command_response: tuple) -> None:
		self.beep_level = int(command_response[0])
		self.key_lock = int(command_response[1])


	def to_dict(self) -> dict:
		return {
			"beep_level": self.beep_level,
			"key_lock": self.key_lock
		}


	def from_dict(self, data: dict) -> None:
		self.beep_level = data.beep_level
		self.key_lock = data.key_lock


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

	def to_write_command(self) -> tuple:
		return (self.to_fetch_command(), self.mode)


	def to_fetch_command(self) -> str:
		return "PRI"


	def from_command_response(self, command_response: tuple) -> None:
		(self.mode,) = command_response


	def to_dict(self) -> dict:
		return {"mode": self.mode}


	def from_dict(self, data: dict) -> None:
		self.mode = data.mode


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

	def to_write_command(self) -> tuple:
		cmd_str = "".join(map(lambda n: "1" if n else "0", self.banks))
		return (self.to_fetch_command(), cmd_str)


	def to_fetch_command(self) -> str:
		return "SCG"


	def from_command_response(self, command_response: tuple) -> None:
		cmd_str: str
		(cmd_str,) = command_response
		self.banks = map(lambda n: n == "1", cmd_str.split(""))


	def to_dict(self) -> dict:
		return {"banks": self.banks}


	def from_dict(self, data: dict) -> None:
		self.banks = data.banks


# DCH Delete Channel
class DeleteChannel(_ScannerDataObject):
	"""Delete a channel from the scanner

	Attributes:
		index (int): the index to delete

	Notes:
		index must be in range [1-500]
	"""

	index: int = 1

	def __init__(self, index: int = 1) -> None:
		self.index = index


	def to_write_command(self) -> tuple:
		return ("DCH", self.index)
