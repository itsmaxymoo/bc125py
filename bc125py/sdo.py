from enum import Enum
import bc125py


#region Global Functions

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

#endregion


#region Enums

class E_TrueFalse(Enum):
	true: str = "1"
	false: str = "0"


class E_LockState(Enum):
	unlocked: str = "0"
	locked: str = "1"


class E_BacklightMode(Enum):
	always_on: str = "AO"
	always_off: str = "AF"
	keypress: str = "KY"
	squelch: str = "SQ"
	keypress_squelch: str = "KS"


class E_BeepLevel(Enum):
	auto: str = "0"
	off: str = "99"


class E_Modulation(Enum):
	auto: str = "AUTO"
	fm: str = "FM"
	nfm: str = "NFM"
	am: str = "AM"


class E_PriorityMode(Enum):
	off: str = "0"
	on: str = "1"
	plus_on: str = "2"
	do_not_disturb: str = "3"


class E_CloseCallMode(Enum):
	off: str = "0"
	priority: str = "1"
	do_not_disturb = "2"


#endregion


#region Helper Classes

class BankListManager:
	"""An object to represent a list of related banks and their state.
	This is NOT an SDO.
	"""

	banks: list
	__chr_bnk_enabled: str
	__chr_bnk_disabled: str
	__require_enabled: bool


	def __init__(self, size: int, invert: bool = False, require_enabled: bool = True) -> None:
		"""Constructor

		Args:
			size (int): How many banks in this list?
			invert (bool, optional): Should 1 be considered enabled? Defaults to False.
			require_enabled (bool, optional): Should the manager require at least one bank enabled? Defaults to True.
		"""

		if size < 1:
			raise ValueError("BankManager size must be >= 1!")

		self.banks = [True] * size

		# Recall that 1 typically means "locked out"
		self.__chr_bnk_enabled = "1" if invert else "0"
		self.__chr_bnk_disabled = "0" if invert else "1"

		self.__require_enabled = require_enabled


	def to_write_command(self) -> str:
		return "".join(map(lambda n: self.__chr_bnk_enabled if n else self.__chr_bnk_disabled, self.banks))


	def from_command_response(self, command_response: str) -> None:
		self.banks = list(map(lambda n: n == self.__chr_bnk_enabled, list(command_response)))


	def to_dict(self) -> list:
		return self.banks


	def from_dict(self, banks: list) -> None:
		self.banks = banks


	def validate(self) -> None:
		if self.__require_enabled:
			if not any(self.banks):
				raise ValueError("At least one bank must be enabled!")


#endregion


#region SDO

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


	def validate(self) -> None:
		"""Allow an SDO to validate its data.

		Raises:
			ValueError: if any data validation error is encountered.
		"""

		return None


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
		self.attrib = data["attrib"]


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
		self.model = data["model"]


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
		self.version = data["version"]


# BLT Backlight Settings
class Backlight(_ScannerDataObject):
	"""Scanner backlight settings

	Attributes:
		backlight (E_BacklightMode): The backlight state of the scanner
	
	Notes:
		Backlight value expects specific code
	"""

	# Defaults
	backlight: E_BacklightMode = E_BacklightMode.always_off

	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (self.backlight.value,)


	def to_fetch_command(self) -> tuple:
		return ("BLT",)


	def from_command_response(self, command_response: tuple) -> None:
		self.backlight = E_BacklightMode(command_response[0])


	def to_dict(self) -> dict:
		return {"backlight": self.backlight.name}


	def from_dict(self, data: dict) -> None:
		self.backlight = E_BacklightMode[data["backlight"]]


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
		self.hours = data["hours"]


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
	beep_level: E_BeepLevel = E_BeepLevel.auto
	key_lock: E_LockState = E_LockState.unlocked

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
		self.beep_level = E_BeepLevel[data["beep_level"]]
		self.key_lock = E_LockState[data["key_lock"]]


# PRI Priority Mode
class PriorityMode(_ScannerDataObject):
	"""Scanner priority mode

	Attributes:
		mode (E_PriorityMode): Mode setting
	"""

	# Defaults
	mode: E_PriorityMode = E_PriorityMode.off

	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (self.mode.value,)


	def to_fetch_command(self) -> tuple:
		return ("PRI",)


	def from_command_response(self, command_response: tuple) -> None:
		self.mode = E_PriorityMode(command_response[0])


	def to_dict(self) -> dict:
		return {"mode": self.mode.name}


	def from_dict(self, data: dict) -> None:
		self.mode = E_PriorityMode[data["mode"]]


# SCG Set active scanner banks
class EnabledChannelBanks(_ScannerDataObject):
	"""Control which scanning banks are enabled on the scanner
	Disabled banks will be skipped when in "Scan" mode

	Attributes:
		banks (bool list, length 10): An array representing each bank and whether or not it's enabled
	
	Notes:
		banks[] length must be 10
		At least one bank must be enabled
	"""

	# Defaults
	bank_list_manager: BankListManager = BankListManager(size=10)

	def to_write_command(self) -> tuple:

		return self.to_fetch_command() + (self.bank_list_manager.to_write_command(),)


	def to_fetch_command(self) -> tuple:
		return ("SCG",)


	def from_command_response(self, command_response: tuple) -> None:
		self.banks = self.bank_list_manager.from_command_response(command_response[0])


	def to_dict(self) -> dict:
		return {"banks": self.bank_list_manager.to_dict()}


	def from_dict(self, data: dict) -> None:
		self.bank_list_manager.from_dict(data["banks"])


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
		modulation (E_Modulation): The modulation to be used for this channel
		ctcss (int): The CTCSS/DCS tone for this channel
		delay (int): How long to stay on this channel after rx
		locked_out (E_LockState): Should we skip this channel when scanning?
		priority (E_TrueFalse): Should this channel get priority in pri-scans?

	Notes:
		name may not be > 16 chars.
		name should avoid special characters
	"""

	index: int = 1
	name: str = "NoName"
	frequency: str = "146.4"
	modulation: E_Modulation = E_Modulation.auto
	ctcss: int = 0
	delay: int = 2
	locked_out: E_LockState = E_LockState.unlocked
	priority: E_TrueFalse = E_TrueFalse.false


	def __init__(self, index: int = 1) -> None:
		self.index = index


	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (
			self.name,
			freq_to_scanner(self.frequency),
			self.modulation.value,
			self.ctcss,
			self.delay,
			self.locked_out.value,
			self.priority.value
		)


	def to_fetch_command(self) -> tuple:
		return ("CIN", self.index)


	def from_command_response(self, command_response: tuple) -> None:
		self.index = int(command_response[0])
		self.name = command_response[1]
		self.frequency = freq_to_mhz(command_response[2])
		self.modulation = E_Modulation(command_response[3])
		self.ctcss = int(command_response[4])
		self.delay = int(command_response[5])
		self.locked_out = E_LockState(command_response[6])
		self.priority = E_PriorityMode(command_response[7])


	def to_dict(self) -> dict:
		return {
			"index": self.index,
			"name": self.name,
			"frequency": self.frequency,
			"modulation": self.modulation.name,
			"ctcss": self.ctcss,
			"delay": self.delay,
			"locked_out": self.locked_out.name,
			"priority": self.priority.name
		}


	def from_dict(self, data) -> None:
		self.index = data["index"]
		self.name = data["name"]
		self.frequency = data["frequency"]
		self.modulation = E_Modulation[data["modulation"]]
		self.ctcss = data["ctcss"]
		self.delay = data["delay"]
		self.locked_out = E_LockState[data["locked_out"]]
		self.priority = E_PriorityMode[data["priority"]]


# SCO Close Call Delay/CTCSS Settings
class CloseCallDelayCTCSSSettings(_ScannerDataObject):
	"""Close Call delay and ctcss settings

	Attributes:
		delay (int): seconds to stay on CC after rx end
		ctcss (E_TrueFalse): whether the scanner should search for a CTCSS/DCS tone in CC's

	Notes:
		ctcss default is 1 (on)
		It's not clear why this isn't a part of CLC
	"""

	# Defaults
	delay: int = 2
	ctcss: E_TrueFalse = E_TrueFalse.false

	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (self.delay, self.ctcss.value)


	def to_fetch_command(self) -> tuple:
		return ("SCO",)


	def from_command_response(self, command_response: tuple) -> None:
		self.delay = int(command_response[0])
		self.ctcss = E_TrueFalse(command_response[1])


	def to_dict(self) -> dict:
		return {"delay": self.delay, "ctcss": self.ctcss.name}


	def from_dict(self, data: dict) -> None:
		self.delay = data["delay"]
		self.ctcss = E_TrueFalse[data["ctcss"]]


# GLF / ULF / LOF Locked Out Channels Bank
class LockedFrequencies(_ScannerDataObject):
	"""Locked out channels bank.

	Attributes:
		frequencies (string list): A list of all locked out frequencies, in MHz
	
	Notes:
		Object behavior does not translate directly to a scanner command.
		Directly overrides write_to() and read_from.
		Most traditional SDO functions not implemented. Use write_to() and read_from().
	"""

	# Defaults
	frequencies: list = []


	def to_fetch_command(self) -> tuple:
		return ("GLF",)


	def to_dict(self) -> dict:
		return {"freqs": self.frequencies}


	def from_dict(self, data: dict) -> None:
		self.frequencies = data["freqs"]
	

	def write_to(self, scanner_con: bc125py.ScannerConnection) -> None:
		"""Writes this SDO to the scanner.

		Args:
			scanner_con (bc125py.ScannerConnection): An active scanner connection
		"""

		# --- First we must get the locked out freqs to delete.
		delete_freqs: list = []

		# EPG, PRG necessary to reset the lockout frequency tracker (dumb uniden design)
		ExitProgramMode().write_to(scanner_con)
		EnterProgramMode().write_to(scanner_con)

		# Get first lock out freq (LOF)
		lof: str = scanner_con.exec("GLF")[0]

		# Ensure we aren't at the end of locked out freqs and this isn't a simulated write
		while lof not in ["-1", "GLF"]:
			# Add freq to list
			delete_freqs.append(freq_to_mhz(lof))

			# Get next
			lof = scanner_con.exec("GLF")[0]
		
		# EPG, PRG necessary to reset the lockout frequency tracker (dumb uniden design)
		ExitProgramMode().write_to(scanner_con)
		EnterProgramMode().write_to(scanner_con)

		# Unlock all locked frequencies
		for f in delete_freqs:
			UnlockFrequency(f).write_to(scanner_con)
		
		# Now, lock appropriate freqs
		for f in self.frequencies:
			LockFrequency(f).write_to(scanner_con)


	def read_from(self, scanner_con: bc125py.ScannerConnection) -> None:
		"""Reads this object from the scanner.
		Populates the SDO's attributes with scanner data.

		Args:
			scanner_con (bc125py.ScannerConnection): An active scanner connection
		"""

		# EPG, PRG necessary to reset the lockout frequency tracker (dumb uniden design)
		ExitProgramMode().write_to(scanner_con)
		EnterProgramMode().write_to(scanner_con)

		# Get first lock out freq (LOF)
		lof: str = scanner_con.exec("GLF")[0]

		# Ensure we aren't at the end of locked out freqs
		while lof != "-1":
			# Add freq to list
			self.frequencies.append(freq_to_mhz(lof))

			# Get next
			lof = scanner_con.exec("GLF")[0]


# ULF Unlock Locked Frequency
class UnlockFrequency(_ScannerDataObject):
	"""Unlock a locked frequency

	Attributes:
		frequency (str): The frequency to unlock, in MHz.

	Notes:
		May set frequency via constructor
	"""

	frequency: str

	def __init__(self, frequency: str = "0") -> None:
		self.frequency = frequency


	def to_write_command(self) -> tuple:
		return ("ULF", freq_to_scanner(self.frequency))


# LOF Lockout Frequency
class LockFrequency(_ScannerDataObject):
	"""Lock a frequency

	Attributes:
		frequency (str): The frequency to lock, in MHz.

	Notes:
		May set frequency via constructor
	"""

	frequency: str

	def __init__(self, frequency: str = "0") -> None:
		self.frequency = frequency


	def to_write_command(self) -> tuple:
		return ("LOF", freq_to_scanner(self.frequency))


# CLC Close Call Main Settings
class CloseCallSettings(_ScannerDataObject):
	"""Close call main settings

	Attributes:
		mode (E_CloseCallMode): The mode of close call operation
		alert_beep (E_TrueFalse): Should the scanner beep when CC is found
		alert_light (E_TrueFalse): Should the scanner backlight flash when CC is found
		cc_bands (bool list, length 5): Which CC bands are enabled
		lockout (E_LockState): Unknown
	
	Notes:
		cc_bands length must be 5
	"""

	# Defaults
	mode: E_CloseCallMode = E_CloseCallMode.off
	alert_beep: E_TrueFalse = E_TrueFalse.true
	alert_light: E_TrueFalse = E_TrueFalse.true
	cc_bands: list = [True] * 5
	lockout: E_LockState = E_LockState.unlocked


	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (
			self.mode.value,
			self.alert_beep.value,
			self.alert_light.value,
			"".join(map(lambda n: "1" if n else "0", self.cc_bands)),
			self.lockout.value
		)


	def to_fetch_command(self) -> tuple:
		return ("CLC",)


	def from_command_response(self, command_response: tuple) -> None:
		self.mode = E_CloseCallMode(command_response[0])
		self.alert_beep = E_TrueFalse(command_response[1])
		self.alert_light = E_TrueFalse(command_response[2])
		self.cc_bands = list(map(lambda n: n == "1", list(command_response[3])))
		self.lockout = E_LockState(command_response[4])


	def to_dict(self) -> dict:
		return {
			"mode": self.mode.name,
			"alert_beep": self.alert_beep.name,
			"alert_light": self.alert_light.name,
			"enabled_cc_bands": self.cc_bands,
			"lockout": self.lockout.name
		}


	def from_dict(self, data) -> None:
		self.mode = E_CloseCallMode[data["mode"]]
		self.alert_beep = E_TrueFalse[data["alert_beep"]]
		self.alert_light = E_TrueFalse[data["alert_light"]]
		self.cc_bands = data["enabled_cc_bands"]
		self.lockout = E_LockState[data["lockout"]]


# SSG Enabled Search Banks
class EnabledServiceSearchBanks(_ScannerDataObject):
	"""Control which SERVICE search banks are enabled on the scanner
	Disabled banks will be skipped when in "Srch/Svc" mode

	Attributes:
		banks (bool list, length 10): An array representing each bank and whether or not it's enabled
	
	Notes:
		banks[] length must be 10
		At least one bank must be enabled
	"""

	# Defaults
	banks: list = [True] * 10


	def to_write_command(self) -> tuple:
		cmd_str = "".join(map(lambda n: "0" if n else "1", self.banks))

		if "0" not in cmd_str:
			raise ValueError("At least one channel bank must be enabled!")

		return self.to_fetch_command() + (cmd_str,)


	def to_fetch_command(self) -> tuple:
		return ("SSG",)


	def from_command_response(self, command_response: tuple) -> None:
		cmd_str: str
		(cmd_str,) = command_response
		self.banks = list(map(lambda n: n == "0", list(cmd_str)))


	def to_dict(self) -> dict:
		return {"banks": self.banks}


	def from_dict(self, data: dict) -> None:
		self.banks = data["banks"]


# CSG Enabled Custom Search Banks
class EnabledCustomSearchBanks(_ScannerDataObject):
	"""Control which custom search banks are enabled on the scanner
	Disabled banks will be skipped when in "Srch" mode

	Attributes:
		banks (bool list, length 10): An array representing each bank and whether or not it's enabled
	
	Notes:
		banks[] length must be 10
		At least one bank must be enabled
	"""

	# Defaults
	banks: list = [True] * 10


	def to_write_command(self) -> tuple:
		cmd_str = "".join(map(lambda n: "0" if n else "1", self.banks))

		if "0" not in cmd_str:
			raise ValueError("At least one channel bank must be enabled!")

		return self.to_fetch_command() + (cmd_str,)


	def to_fetch_command(self) -> tuple:
		return ("CSG",)


	def from_command_response(self, command_response: tuple) -> None:
		cmd_str: str
		(cmd_str,) = command_response
		self.banks = list(map(lambda n: n == "0", list(cmd_str)))


	def to_dict(self) -> dict:
		return {"banks": self.banks}


	def from_dict(self, data: dict) -> None:
		self.banks = data["banks"]


# CSP Custom Search Bank
class CustomSearchBank(_ScannerDataObject):
	"""A custom search bank.

	Attributes:
		index (int): Custom search bank index
		lower_limit (str): The lower limit frequency, in MHz
		upper_limit (str): The upper limit frequency, in MHz
	
	Notes:
		Frequencies must be valid
		index MUST be in range [1-10]
	"""

	# Defaults
	index: int = 1
	lower_limit: str = "25.000"
	upper_limit: str = "512.000"


	def __init__(self, index: int = 1) -> None:
		self.index = index


	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (
			freq_to_scanner(self.lower_limit),
			freq_to_scanner(self.upper_limit)
		)


	def to_fetch_command(self) -> tuple:
		return ("CSP", self.index)


	def from_command_response(self, command_response: tuple) -> None:
		self.index = int(command_response[0])
		self.lower_limit = freq_to_mhz(command_response[1])
		self.upper_limit = freq_to_mhz(command_response[2])


	def to_dict(self) -> dict:
		return {
			"index": self.index,
			"lower_limit": self.lower_limit,
			"upper_limit": self.upper_limit
		}


	def from_dict(self, data) -> None:
		self.index = data["index"]
		self.lower_limit = data["lower_limit"]
		self.upper_limit = data["upper_limit"]


# WXS Weather Alert Settings
class WeatherAlertSettings(_ScannerDataObject):
	"""Scanner weather WX settings

	Attributes:
		alert_priority (E_TrueFalse): Should the scanner interrupt when WX alert detected. Default false.
	"""

	# Defaults
	alert_priority: E_TrueFalse = E_TrueFalse.false


	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (self.alert_priority.value,)


	def to_fetch_command(self) -> tuple:
		return ("WXS",)


	def from_command_response(self, command_response: tuple) -> None:
		self.alert_priority = E_TrueFalse(command_response[0])


	def to_dict(self) -> dict:
		return {"alert_priority": self.alert_priority.name}


	def from_dict(self, data: dict) -> None:
		self.alert_priority = E_TrueFalse[data["alert_priority"]]


# CNT Contrast
class DisplayContrast(_ScannerDataObject):
	"""Scanner display contrast

	Attributes:
		contrast (int): Contrast. Default 8
	
	Notes:
		contrast range must be in [1-15]
	"""

	# Defaults
	contrast: int = 8


	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (self.contrast,)


	def to_fetch_command(self) -> tuple:
		return ("CNT",)


	def from_command_response(self, command_response: tuple) -> None:
		self.contrast = int(command_response[0])


	def to_dict(self) -> dict:
		return {"contrast": self.contrast}


	def from_dict(self, data) -> None:
		self.contrast = data["contrast"]


# VOL Volume
class DeviceVolume(_ScannerDataObject):
	"""Device volume.

	Attributes:
		volume (int): The device volume
	
	Notes:
		volume range must be in [0-15]
		0 is mute
		15 is maximum and quite loud
	"""

	# Defaults
	volume: int = 8


	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (self.volume,)


	def to_fetch_command(self) -> tuple:
		return ("VOL",)


	def from_command_response(self, command_response: tuple) -> None:
		self.volume = int(command_response[0])


	def to_dict(self) -> dict:
		return {"volume": self.volume}


	def from_dict(self, data) -> None:
		self.volume = data["volume"]


# SQL Squelch
class Squelch(_ScannerDataObject):
	"""Rx squelch

	Attributes:
		squelch (int): The Rx squelch. Default is 2
	
	Notes:
		squelch must be in range [0-15]
		0 is off
		15 is closed
		2 appears to be optimal value, 1 in some situations.
	"""

	# Defaults
	squelch: int = 2


	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (self.squelch,)


	def to_fetch_command(self) -> tuple:
		return ("SQL",)


	def from_command_response(self, command_response: tuple) -> None:
		self.squelch = int(command_response[0])


	def to_dict(self) -> dict:
		return {"squelch": self.squelch}


	def from_dict(self, data) -> None:
		self.squelch = data["squelch"]


#endregion


#region Scanner

class Scanner:

	bc125py_version: str = bc125py.MODULE_VERSION

	model: DeviceModel
	firmware: FirmwareVersion
	backlight: Backlight
	battery_charge_timer: BatteryChargeTimer
	keypad: KeypadSettings
	priority_mode: PriorityMode
	enabled_channel_banks: EnabledChannelBanks
	channels: list
	cc_ctcss_delay: CloseCallDelayCTCSSSettings
	locked_frequencies: LockedFrequencies
	cc_main_settings: CloseCallSettings
	enabled_service_search_banks: EnabledServiceSearchBanks
	enabled_custom_search_banks: EnabledCustomSearchBanks
	custom_search_banks: list
	weather_alert_settings: WeatherAlertSettings
	display_contrast: DisplayContrast
	device_volume: DeviceVolume
	squelch: Squelch

	def __init__(self) -> None:
		self.model = DeviceModel()
		self.firmware = FirmwareVersion()
		self.backlight = Backlight()
		self.battery_charge_timer = BatteryChargeTimer()
		self.keypad = KeypadSettings()
		self.priority_mode = PriorityMode()
		self.enabled_channel_banks = EnabledChannelBanks()

		self.channels = []
		for i in range(1, 501):
			self.channels.append(Channel(i))

		self.cc_ctcss_delay = CloseCallDelayCTCSSSettings()
		self.locked_frequencies = LockedFrequencies()
		self.cc_main_settings = CloseCallSettings()
		self.enabled_service_search_banks = EnabledServiceSearchBanks()
		self.enabled_custom_search_banks = EnabledCustomSearchBanks()

		self.custom_search_banks = []
		for i in range(1, 11):
			self.custom_search_banks.append(CustomSearchBank(i))
		
		self.weather_alert_settings = WeatherAlertSettings()
		self.display_contrast = DisplayContrast()
		self.device_volume = DeviceVolume()
		self.squelch = Squelch()


	def write_to(self, scanner_con: bc125py.ScannerConnection) -> None:
		"""Writes this scanner to the scanner

		Args:
			scanner_con (bc125py.ScannerConnection): An active scanner connection
		"""

		EnterProgramMode().write_to(scanner_con)

		self.backlight.write_to(scanner_con)
		self.battery_charge_timer.write_to(scanner_con)
		self.keypad.write_to(scanner_con)
		self.priority_mode.write_to(scanner_con)
		self.enabled_channel_banks.write_to(scanner_con)

		for c in self.channels:
			c.write_to(scanner_con)
		
		self.cc_ctcss_delay.write_to(scanner_con)
		self.locked_frequencies.write_to(scanner_con)
		self.cc_main_settings.write_to(scanner_con)
		self.enabled_service_search_banks.write_to(scanner_con)
		self.enabled_custom_search_banks.write_to(scanner_con)

		for c in self.custom_search_banks:
			c.write_to(scanner_con)
		
		self.weather_alert_settings.write_to(scanner_con)
		self.display_contrast.write_to(scanner_con)
		self.device_volume.write_to(scanner_con)
		self.squelch.write_to(scanner_con)

		ExitProgramMode().write_to(scanner_con)


	def read_from(self, scanner_con: bc125py.ScannerConnection) -> None:
		"""Reads this scanner from the scanner.

		Args:
			scanner_con (bc125py.ScannerConnection): An active scanner connection
		"""

		EnterProgramMode().write_to(scanner_con)

		self.model.read_from(scanner_con)
		self.firmware.read_from(scanner_con)
		self.backlight.read_from(scanner_con)
		self.battery_charge_timer.read_from(scanner_con)
		self.keypad.read_from(scanner_con)
		self.priority_mode.read_from(scanner_con)
		self.enabled_channel_banks.read_from(scanner_con)

		for c in self.channels:
			c.read_from(scanner_con)
		
		self.cc_ctcss_delay.read_from(scanner_con)
		self.locked_frequencies.read_from(scanner_con)
		self.cc_main_settings.read_from(scanner_con)
		self.enabled_service_search_banks.read_from(scanner_con)
		self.enabled_custom_search_banks.read_from(scanner_con)

		for c in self.custom_search_banks:
			c.read_from(scanner_con)
		
		self.weather_alert_settings.read_from(scanner_con)
		self.display_contrast.read_from(scanner_con)
		self.device_volume.read_from(scanner_con)
		self.squelch.read_from(scanner_con)

		ExitProgramMode().write_to(scanner_con)


	def to_dict(self) -> dict:
		# Dict shall have channels last; for ease of editing
		return {
			"bc125py_version": self.bc125py_version,

			"model": self.model.to_dict(),
			"firmware": self.firmware.to_dict(),
			"backlight": self.backlight.to_dict(),
			"battery_charge_timer": self.battery_charge_timer.to_dict(),
			"keypad": self.keypad.to_dict(),
			"priority_mode": self.priority_mode.to_dict(),
			"enabled_channel_banks": self.enabled_channel_banks.to_dict(),
			"cc_main_settings": self.cc_main_settings.to_dict(),
			"cc_ctcss_delay": self.cc_ctcss_delay.to_dict(),
			"locked_frequencies": self.locked_frequencies.to_dict(),
			"enabled_service_search_banks": self.enabled_service_search_banks.to_dict(),
			"enabled_custom_search_banks": self.enabled_custom_search_banks.to_dict(),
			"custom_search_banks": list(map(lambda c : c.to_dict(), self.custom_search_banks)),
			"weather_alert_settings": self.weather_alert_settings.to_dict(),
			"display_contrast": self.display_contrast.to_dict(),
			"device_volume": self.device_volume.to_dict(),
			"squelch": self.squelch.to_dict(),

			"channels": list(map(lambda c : c.to_dict(), self.channels))
		}


	def from_dict(self, data: dict) -> None:
		self.bc125py_version = data.get("bc125py_version", "error")

		self.model.from_dict(data["model"])
		self.firmware.from_dict(data["firmware"])
		self.backlight.from_dict(data["backlight"])
		self.battery_charge_timer.from_dict(data["battery_charge_timer"])
		self.keypad.from_dict(data["keypad"])
		self.priority_mode.from_dict(data["priority_mode"])
		self.enabled_channel_banks.from_dict(data["enabled_channel_banks"])

		self.channels = []
		for cd in data["channels"]:
			c: Channel = Channel()
			c.from_dict(cd)
			self.channels.append(c)

		self.cc_ctcss_delay.from_dict(data["cc_ctcss_delay"])
		self.locked_frequencies.from_dict(data["locked_frequencies"])
		self.cc_main_settings.from_dict(data["cc_main_settings"])
		self.enabled_service_search_banks.from_dict(data["enabled_service_search_banks"])
		self.enabled_custom_search_banks.from_dict(data["enabled_custom_search_banks"])

		self.custom_search_banks = []
		for csb in data["custom_search_banks"]:
			c: CustomSearchBank = CustomSearchBank()
			c.from_dict(csb)
		
		self.weather_alert_settings.from_dict(data["weather_alert_settings"])
		self.display_contrast.from_dict(data["display_contrast"])
		self.device_volume.from_dict(data["device_volume"])
		self.squelch.from_dict(data["squelch"])


	def __str__(self) -> str:
		"""Attempts to return dict representation of SDO.
		Otherwise, returns SDO write command
		"""

		return str(self.to_dict())

#endregion
