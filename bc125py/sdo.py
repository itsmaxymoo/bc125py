from enum import Enum
import bc125py


# --- GLOBAL FUNCTIONS ---

def freq_to_scanner(freq: str) -> str:
	"""Convert a frequency in MHz to the scanner format

	Args:
		freq (str): Input frequency, in MHz

	Returns:
		str: Frequency in scanner format
	"""

	return str(
		round(
			float(freq) * 10000
		)
	)


def freq_to_mhz(freq: str) -> str:
	"""Convert a frequency from the scanner format to MHz

	Args:
		freq (str): The input frequency, in scanner format

	Returns:
		str: The output frequency, MHz (padded).
	"""

	return f"{float(freq) / 10000:08.4f}"


def is_valid_freq_scanner(freq: str) -> bool:
	"""Determines if the given frequency is valid on a BC125AT.

	Args:
		freq (str): The frequency to test, IN SCANNER FORMAT

	Returns:
		bool: True if the frequency is valid
	"""

	val = int(freq)

	if val == 0:
		return True
	if 250000 <= val <= 540000:
		return True
	if 1080000 <= val <= 1740000:
		return True
	if 2250000 <= val <= 3800000:
		return True
	if 4000000 <= val <= 5120000:
		return True
	
	return False


def is_valid_freq_mhz(freq: str) -> bool:
	"""Determines if the given frequency is valid on a BC125AT.

	Args:
		freq (str): The frequency to test, IN MHz

	Returns:
		bool: True if the frequency is valid
	"""

	return is_valid_freq_scanner(freq_to_scanner(freq))


# --- ENUMS ---

class E_TrueFalse(Enum):
	T: str = "0"
	F: str = "1"


class E_LockState(Enum):
	Unlocked: str = "0"
	Locked: str = "1"


class E_BacklightMode(Enum):
	AlwaysOn: str = "AO"
	AlwaysOff: str = "AF"
	Keypress: str = "KY"
	Squelch: str = "SQ"
	KeypressSquelch: str = "KS"


class E_BeepLevel(Enum):
	Auto: str = "0"
	Off: str = "99"


class E_Modulation(Enum):
	Auto: str = "AUTO"
	FM: str = "FM"
	NFM: str = "NFM"
	AM: str = "AM"


class E_PriorityMode(Enum):
	Off: str = "0"
	On: str = "1"
	PlusOn: str = "2"
	DoNotDisturb: str = "3"


# --- SDO ---

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


	def to_fetch_command(self) -> tuple:
		"""Get the scanner command to fetch the data for this object

		Raises:
			NotImplementedError: if this function is not implemented in a child class

		Returns:
			tuple: scanner command to read this object
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


	def write_to(self, scanner_con: bc125py.ScannerConnection) -> None:
		"""Writes this SDO to the scanner.

		Args:
			scanner_con (bc125py.ScannerConnection): An active scanner connection
		"""

		scanner_con.exec(self.to_write_command())


	def read_from(self, scanner_con: bc125py.ScannerConnection) -> None:
		"""Reads this object from the scanner.
		Populates the SDO's attributes with scanner data.

		Args:
			scanner_con (bc125py.ScannerConnection): An active scanner connection
		"""

		self.from_command_response(
			scanner_con.exec(self.to_fetch_command())
		)


	def __str__(self) -> str:
		"""Attempts to return dict representation of SDO.
		Otherwise, returns SDO write command
		"""

		try:
			return str(self.to_dict())
		except NotImplementedError:
			return ",".join(self.to_write_command())


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
		return self.to_fetch_command() + (self.attrib,)


	def to_fetch_command(self) -> tuple:
		return ("EXX",)


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

	def to_fetch_command(self) -> tuple:
		return ("MDL",)


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

	def to_fetch_command(self) -> tuple:
		return ("VER",)


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
		backlight (E_BacklightMode): The backlight state of the scanner
	
	Notes:
		Backlight value expects specific code
	"""

	# Defaults
	backlight: E_BacklightMode = E_BacklightMode.AlwaysOff

	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (self.backlight.value,)


	def to_fetch_command(self) -> tuple:
		return ("BLT",)


	def from_command_response(self, command_response: tuple) -> None:
		self.backlight = E_BacklightMode(command_response[0])


	def to_dict(self) -> dict:
		return {"backlight": self.backlight.name}


	def from_dict(self, data: dict) -> None:
		self.backlight = E_BacklightMode[data.backlight]


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
		return self.to_fetch_command() + (self.hours,)


	def to_fetch_command(self) -> tuple:
		return ("BSV",)


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
		beep_level (E_BeepLevel): Key beep level, 0: Auto, 99: Off
		key_lock (E_LockState): Keypad lock status, 0: Unlocked, 1: Locked
	"""

	# Defaults
	beep_level: E_BeepLevel = E_BeepLevel.Auto
	key_lock: E_LockState = E_LockState.Unlocked

	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (self.beep_level.value, self.key_lock.value)


	def to_fetch_command(self) -> tuple:
		return ("KBP",)


	def from_command_response(self, command_response: tuple) -> None:
		self.beep_level = E_BeepLevel(command_response[0])
		self.key_lock = E_LockState(command_response[1])


	def to_dict(self) -> dict:
		return {
			"beep_level": self.beep_level.name,
			"key_lock": self.key_lock.name
		}


	def from_dict(self, data: dict) -> None:
		self.beep_level = E_BeepLevel[data.beep_level]
		self.key_lock = E_LockState[data.key_lock]


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
	mode: int = PrioritySetting.Off.value

	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (self.mode,)


	def to_fetch_command(self) -> tuple:
		return ("PRI",)


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
		return self.to_fetch_command() + (cmd_str,)


	def to_fetch_command(self) -> tuple:
		return ("SCG",)


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


# CIN Channel Info
class Channel(_ScannerDataObject):
	"""Represents a channel on the scanner

	Attributes:
		index (int): The index of the channel. [1-500]
		name (str): The name of the channel
		frequency (str): The frequency of the channel, in MHz
		modulation (str): The modulation to be used for this channel
		ctcss (int): The CTCSS/DCS tone for this channel
		delay (int): How long to stay on this channel after rx
		locked_out (int): Should we skip this channel when scanning?
		priority (int): Should this channel get priority in pri-scans?

	Notes:
		Explore included enums.
	"""

	class Modulation(Enum):
		Auto = "AUTO"
		AM = "AM"
		FM = "FM"
		NarrowFM = "NFM"


	class LockoutMode(Enum):
		Unlocked = 0
		Locked = 1


	class PriorityStatus(Enum):
		Normal = 0
		IsPriority = 1


	index: int = 1
	name: str = "NoName"
	frequency: str = "146.4"
	modulation: str = Modulation.Auto.value
	ctcss: int = 0
	delay: int = 2
	locked_out: int = LockoutMode.Unlocked.value
	priority: int = PriorityStatus.Normal.value


	def __init__(self, index: int = 1) -> None:
		self.index = index


	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (
			self.name,
			self.frequency,
			self.modulation,
			self.ctcss,
			self.delay,
			self.locked_out,
			self.priority
		)


	def to_fetch_command(self) -> tuple:
		return ("CIN", self.index)


	def from_command_response(self, command_response: tuple) -> None:
		self.index = int(command_response[0])
		self.name = command_response[1]
		self.frequency = command_response[2]
		self.modulation = command_response[3]
		self.ctcss = int(command_response[4])
		self.delay = int(command_response[5])
		self.locked_out = int(command_response[6])
		self.priority = int(command_response[7])


	def to_dict(self) -> dict:
		return {
			"index": self.index,
			"name": self.name,
			"frequency": freq_to_mhz(self.frequency),
			"modulation": self.modulation,
			"ctcss": self.ctcss,
			"delay": self.delay,
			"locked_out": self.locked_out,
			"priority": self.priority
		}


	def from_dict(self, data) -> None:
		self.index = data.index
		self.name = data.name
		self.frequency = freq_to_scanner(data.frequency)
		self.modulation = data.modulation
		self.ctcss = data.ctcss
		self.delay = data.delay
		self.locked_out = data.locked_out
		self.priority = data.priority


# SCO Close Call Delay/CTCSS Settings
class CloseCallDelayCTCSSSettings(_ScannerDataObject):
	"""Close Call delay and ctcss settings

	Attributes:
		delay (int): seconds to stay on CC after rx end
		ctcss (int): whether the scanner should search for a CTCSS/DCS tone in CC's

	Notes:
		ctcss default is 1 (on)
		It's not clear why this isn't a part of CLC
		Explore CloseCallCTCSSMode enum
	"""

	class CloseCallCTCSSMode(Enum):
		Off = 0
		On = 1


	# Defaults
	delay: int = 2
	ctcss: int = CloseCallCTCSSMode.On.value

	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (self.delay, self.ctcss)


	def to_fetch_command(self) -> tuple:
		return ("SCO",)


	def from_command_response(self, command_response: tuple) -> None:
		self.delay = int(command_response[0])
		self.ctcss = int(command_response[1])


	def to_dict(self) -> dict:
		return {"delay": self.delay, "ctcss": self.ctcss}


	def from_dict(self, data: dict) -> None:
		self.delay = data.delay
		self.ctcss = data.ctcss
