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

	val: int = 0

	try:
		val = int(freq)
	except Exception:
		return False

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

	try:
		float(freq)
	except ValueError:
		return False

	return is_valid_freq_scanner(freq_to_scanner(freq))


def is_valid_delay(delay: int) -> bool:
	return delay in [-10, -5, 0, 1, 2, 3, 4, 5]


def is_valid_ctcss(tone: int) -> bool:
	if tone == 0:
		return True
	elif (tone >= 64 and tone <= 113):
		return True
	elif (tone >= 127 and tone <= 231):
		return True
	elif tone == 240:
		return True
	else: return False


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


	def write_to(self, scanner_con) -> None:
		"""Writes this SDO to the scanner.

		Args:
			scanner_con (bc125py.con.ScannerConnection): An active scanner connection
		"""

		scanner_con.exec(self.to_write_command())


	def read_from(self, scanner_con) -> None:
		"""Reads this object from the scanner.
		Populates the SDO's attributes with scanner data.

		Args:
			scanner_con (bc125py.con.ScannerConnection): An active scanner connection
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


	def validate(self) -> None:
		if self.attrib < 0:
			raise ValueError("Attrib must be >= 0!")


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


	def validate(self) -> None:
		if not (self.hours >= 1 and self.hours <= 16):
			raise ValueError("Battery charge time hours must be in range [1-16], given " + str(self.hours))


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
		banks (BankListManager): Bank manager
	
	Notes:
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


	def validate(self) -> None:
		try:
			self.bank_list_manager.validate()
		except ValueError as e:
			raise ValueError("Channel banks: " + str(e))


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


	def validate(self) -> None:
		if not (self.index >= 1 and self.index <= 500):
			raise ValueError("DCH: index must be in range [1-500], given " + str(self.index))


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
	name: str = ""
	frequency: str = "000.0000"
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


	def validate(self) -> None:
		err_message: str = "channel: " + str(self.index)
		err_found: bool = False

		if not (self.index >= 1 and self.index <= 500):
			err_found = True
			err_message += ", index must be in range [1-500]"

		if self.name == None or len(self.name) > 16:
			err_found = True
			err_message += ", channel name must be [0-16] characters"

		if not is_valid_freq_mhz(self.frequency):
			err_found = True
			err_message += ", invalid frequency (" + self.frequency + " MHz)"
		
		if not is_valid_delay(self.delay):
			err_found = True
			err_message += ", invalid delay: " + str(self.delay)
		
		if not is_valid_ctcss(self.ctcss):
			err_found = True
			err_message += ", invalid ctcss/dcs: " + str(self.ctcss)
		
		if err_found:
			raise ValueError(err_message)


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


	def validate(self) -> None:
		if not is_valid_delay(self.delay):
			raise ValueError("cc_ctcss_settings: invalid delay: " + str(self.delay))


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
	

	def write_to(self, scanner_con) -> None:
		"""Writes this SDO to the scanner.

		Args:
			scanner_con (bc125py.con.ScannerConnection): An active scanner connection
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


	def read_from(self, scanner_con) -> None:
		"""Reads this object from the scanner.
		Populates the SDO's attributes with scanner data.

		Args:
			scanner_con (bc125py.con.ScannerConnection): An active scanner connection
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
	

	def validate(self) -> None:
		invalid_freqs: list = []

		for f in self.frequencies:
			if not is_valid_freq_mhz(f):
				invalid_freqs.append(f)

		if len(invalid_freqs) > 0:
			raise ValueError("invalid global L/O freqs: " + ", ".join(invalid_freqs))


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
	

	def validate(self) -> None:
		if not is_valid_freq_mhz(self.frequency):
			raise ValueError("ulf: invalid freq: " + self.frequency)


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
	

	def validate(self) -> None:
		if not is_valid_freq_mhz(self.frequency):
			raise ValueError("lof: invalid freq: " + self.frequency)


# CLC Close Call Main Settings
class CloseCallSettings(_ScannerDataObject):
	"""Close call main settings

	Attributes:
		mode (E_CloseCallMode): The mode of close call operation
		alert_beep (E_TrueFalse): Should the scanner beep when CC is found
		alert_light (E_TrueFalse): Should the scanner backlight flash when CC is found
		cc_bands (BankListManager): Which CC bands are enabled
		lockout (E_LockState): Unknown
	
	Notes:
		cc_bands length must be 5
	"""

	# Defaults
	mode: E_CloseCallMode = E_CloseCallMode.off
	alert_beep: E_TrueFalse = E_TrueFalse.true
	alert_light: E_TrueFalse = E_TrueFalse.true
	cc_bands: BankListManager = BankListManager(size=5, invert=True, require_enabled=False)
	lockout: E_LockState = E_LockState.unlocked


	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (
			self.mode.value,
			self.alert_beep.value,
			self.alert_light.value,
			self.cc_bands.to_write_command(),
			self.lockout.value
		)


	def to_fetch_command(self) -> tuple:
		return ("CLC",)


	def from_command_response(self, command_response: tuple) -> None:
		self.mode = E_CloseCallMode(command_response[0])
		self.alert_beep = E_TrueFalse(command_response[1])
		self.alert_light = E_TrueFalse(command_response[2])
		self.cc_bands.from_command_response(command_response[3])
		self.lockout = E_LockState(command_response[4])


	def to_dict(self) -> dict:
		return {
			"mode": self.mode.name,
			"alert_beep": self.alert_beep.name,
			"alert_light": self.alert_light.name,
			"enabled_cc_bands": self.cc_bands.to_dict(),
			"lockout": self.lockout.name
		}


	def from_dict(self, data) -> None:
		self.mode = E_CloseCallMode[data["mode"]]
		self.alert_beep = E_TrueFalse[data["alert_beep"]]
		self.alert_light = E_TrueFalse[data["alert_light"]]
		self.cc_bands.from_dict(data["enabled_cc_bands"])
		self.lockout = E_LockState[data["lockout"]]


	def validate(self) -> None:
		self.cc_bands.validate()


# SSG Enabled Search Banks
class EnabledServiceSearchBanks(_ScannerDataObject):
	"""Control which SERVICE search banks are enabled on the scanner
	Disabled banks will be skipped when in "Srch/Svc" mode

	Attributes:
		bank_list_manager (BankListManager): Bank list manager
	
	Notes:
		banks length must be 10
		At least one bank must be enabled
	"""

	# Defaults
	bank_list_manager: BankListManager = BankListManager(size=10)


	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (self.bank_list_manager.to_write_command(),)


	def to_fetch_command(self) -> tuple:
		return ("SSG",)


	def from_command_response(self, command_response: tuple) -> None:
		self.bank_list_manager.from_command_response(command_response[0])


	def to_dict(self) -> dict:
		return {"banks": self.bank_list_manager.to_dict()}


	def from_dict(self, data: dict) -> None:
		self.bank_list_manager.from_dict(data["banks"])


	def validate(self) -> None:
		self.bank_list_manager.validate()


# CSG Enabled Custom Search Banks
class EnabledCustomSearchBanks(_ScannerDataObject):
	"""Control which custom search banks are enabled on the scanner
	Disabled banks will be skipped when in "Srch" mode

	Attributes:
		bank_list_manager (BankListManager): Bank list manager
	
	Notes:
		banks length must be 10
		At least one bank must be enabled
	"""

	# Defaults
	bank_list_manager: BankListManager = BankListManager(size=10)


	def to_write_command(self) -> tuple:
		return self.to_fetch_command() + (self.bank_list_manager.to_write_command(),)


	def to_fetch_command(self) -> tuple:
		return ("CSG",)


	def from_command_response(self, command_response: tuple) -> None:
		self.bank_list_manager.from_command_response(command_response[0])


	def to_dict(self) -> dict:
		return {"banks": self.bank_list_manager.to_dict()}


	def from_dict(self, data: dict) -> None:
		self.bank_list_manager.from_dict(data["banks"])


	def validate(self) -> None:
		self.bank_list_manager.validate()


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


	def validate(self) -> None:
		err_found = False
		err_message = "search bnk: " + str(self.index)

		if not (self.index >= 1 and self.index <= 10):
			err_found = True
			err_message += ", index must be in range [1-10]"
		
		if not is_valid_freq_mhz(self.lower_limit):
			err_found = True
			err_message += ", invalid lower_limit: " + self.lower_limit + " MHz"
		
		if not is_valid_freq_mhz(self.upper_limit):
			err_found = True
			err_message += ", invalid upper_limit: " + self.upper_limit + " MHz"
		
		if err_found:
			raise ValueError(err_message)


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


	def validate(self) -> None:
		if not (self.contrast >= 1 and self.contrast <= 15):
			raise ValueError("screen contrast must be in range [1-15]")


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


	def validate(self) -> None:
		if not (self.volume >= 0 and self.volume <= 15):
			raise ValueError("device volume must be in range [0-15]")


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


	def validate(self) -> None:
		if not (self.squelch >= 0 and self.squelch <= 15):
			raise ValueError("squelch must be in range [0-15]")


#endregion


#region Scanner

class Scanner:

	bc125py_version: str = bc125py.PACKAGE_VERSION

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

		# Create default 10 CSBs
		self.custom_search_banks = []
		for i in range(1, 11):
			self.custom_search_banks.append(CustomSearchBank(i))
		
		# Populate CSBs with default ranges
		self.custom_search_banks[0].lower_limit = "025.0000"
		self.custom_search_banks[0].upper_limit = "027.9950"
		self.custom_search_banks[1].lower_limit = "028.0000"
		self.custom_search_banks[1].upper_limit = "029.6950"
		self.custom_search_banks[2].lower_limit = "029.7000"
		self.custom_search_banks[2].upper_limit = "049.9950"
		self.custom_search_banks[3].lower_limit = "050.0000"
		self.custom_search_banks[3].upper_limit = "054.0000"
		self.custom_search_banks[4].lower_limit = "108.0000"
		self.custom_search_banks[4].upper_limit = "136.9916"
		self.custom_search_banks[5].lower_limit = "137.0000"
		self.custom_search_banks[5].upper_limit = "143.9950"
		self.custom_search_banks[6].lower_limit = "144.0000"
		self.custom_search_banks[6].upper_limit = "147.9950"
		self.custom_search_banks[7].lower_limit = "225.0000"
		self.custom_search_banks[7].upper_limit = "380.0000"
		self.custom_search_banks[8].lower_limit = "400.0000"
		self.custom_search_banks[8].upper_limit = "449.9937"
		self.custom_search_banks[9].lower_limit = "450.0000"
		self.custom_search_banks[9].upper_limit = "469.9937"
		
		self.weather_alert_settings = WeatherAlertSettings()
		self.display_contrast = DisplayContrast()
		self.device_volume = DeviceVolume()
		self.squelch = Squelch()


	def write_to(self, scanner_con) -> None:
		"""Writes this scanner to the scanner

		Args:
			scanner_con (bc125py.con.ScannerConnection): An active scanner connection
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


	def read_from(self, scanner_con) -> None:
		"""Reads this scanner from the scanner.

		Args:
			scanner_con (bc125py.con.ScannerConnection): An active scanner connection
		"""

		EnterProgramMode().write_to(scanner_con)

		self.model.read_from(scanner_con)
		self.firmware.read_from(scanner_con)
		self.backlight.read_from(scanner_con)
		self.battery_charge_timer.read_from(scanner_con)
		self.keypad.read_from(scanner_con)
		self.priority_mode.read_from(scanner_con)
		self.enabled_channel_banks.read_from(scanner_con)

		# Reset channels, in case some are missing from array
		self.channels = []
		for i in range(1, 501):
			self.channels.append(Channel(i))

		# Read ALL channels from scanner
		for c in self.channels:
			c.read_from(scanner_con)
		
		self.cc_ctcss_delay.read_from(scanner_con)
		self.locked_frequencies.read_from(scanner_con)
		self.cc_main_settings.read_from(scanner_con)
		self.enabled_service_search_banks.read_from(scanner_con)
		self.enabled_custom_search_banks.read_from(scanner_con)

		# Reset csb, in case some are missing from array
		self.custom_search_banks = []
		for i in range(1, 11):
			self.custom_search_banks.append(CustomSearchBank(i))

		# Read ALL CSBs
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
			self.custom_search_banks.append(c)

		self.weather_alert_settings.from_dict(data["weather_alert_settings"])
		self.display_contrast.from_dict(data["display_contrast"])
		self.device_volume.from_dict(data["device_volume"])
		self.squelch.from_dict(data["squelch"])


	def validate(self) -> None:
		# Create list of every SDO comprising this scanner
		sdo_list: list = [
			self.model,
			self.firmware,
			self.backlight,
			self.battery_charge_timer,
			self.keypad,
			self.priority_mode,
			self.enabled_channel_banks,
			self.cc_ctcss_delay,
			self.locked_frequencies,
			self.cc_main_settings,
			self.enabled_service_search_banks,
			self.enabled_custom_search_banks,
			self.weather_alert_settings,
			self.display_contrast,
			self.device_volume,
			self.squelch,
		]
		sdo_list.extend(self.channels)
		sdo_list.extend(self.custom_search_banks)

		err_messages: list = []

		for sdo in sdo_list:
			try:
				sdo.validate()
			except ValueError as e:
				err_messages.append(str(e))

		# Make sure there aren't duplicate channels
		# Loop through each channel
		for i in range(0, len(self.channels)):

			# Compare to each other channel
			for j in range(0, len(self.channels)):

				# As long as these aren't the same channels
				# AND the channel.index's are the same (bad)
				if i != j and self.channels[i].index == self.channels[j].index:

					# Create channel conflict message
					cin_conflict: str = "duplicate channel index: " + str(self.channels[i].index)

					# AND we haven't already logged this conflict
					if cin_conflict not in err_messages:

						# Log conflict
						err_messages.append(cin_conflict)

		# Make sure there aren't duplicate CSBs
		# Loop through each CSB
		for i in range(0, len(self.custom_search_banks)):

			# Compare to each other channel
			for j in range(0, len(self.custom_search_banks)):

				# As long as these aren't the same channels
				# AND the channel.index's are the same (bad)
				if i != j and self.custom_search_banks[i].index == self.custom_search_banks[j].index:

					# Create channel conflict message
					csb_conflict: str = "duplicate custom search bank index: " + str(self.custom_search_banks[i].index)

					# AND we haven't already logged this conflict
					if csb_conflict not in err_messages:

						# Log conflict
						err_messages.append(csb_conflict)

		if len(err_messages) > 0:
			raise ValueError("\n".join(err_messages))


	def __str__(self) -> str:
		"""Attempts to return dict representation of SDO.
		Otherwise, returns SDO write command
		"""

		return str(self.to_dict())

#endregion
