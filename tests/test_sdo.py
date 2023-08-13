"""Tests for SDO structures and global functions"""

import pytest
from bc125py.sdo import *


# region Global Functions

# --- test freq_to_scanner()
def test_freq_to_scanner():
	assert freq_to_scanner(145.5855) == "1455855"


# --- test freq_to_mhz()
def test_freq_to_mhz():
	assert freq_to_mhz("1455855") == "145.5855"


# --- test is_valid_freq_scanner() and is_valid_freq_mhz()
FREQ_SCANNER_VALIDITY = (
	(95.6, False),
	(-1, False),
	(0, True),
	(25, False),
	(250000, True),
	(250001, True),
	(540000, True),
	(1080000, True),
	(1095570, True),
	(1740000, True),
	(2240000, False),
	(2250000, True),
	(3800000, True),
	(3900000, False),
	(4000000, True),
	(5120000, True),
	(5130000, False)
)


@pytest.mark.parametrize("freq_validity_pair", FREQ_SCANNER_VALIDITY, ids=tuple)
def test_is_valid_freq_scanner(freq_validity_pair: tuple):
	assert is_valid_freq_scanner(freq_validity_pair[0]) == freq_validity_pair[1]


@pytest.mark.parametrize("freq_validity_pair", FREQ_SCANNER_VALIDITY, ids=tuple)
def test_is_valid_freq_mhz(freq_validity_pair: tuple):
	assert is_valid_freq_mhz(str(freq_validity_pair[0] / 10000)) == freq_validity_pair[1]


del FREQ_SCANNER_VALIDITY


# --- test is_valid_delay
DELAY_VALIDITY = (
	("-10", False),
	(-10, True),
	(-5.6, False),
	(-5, True),
	(-1, False),
	(0, True),
	(0.5, False),
	(1, True),
	(6, False)
)

@pytest.mark.parametrize("delay_validity_pair", DELAY_VALIDITY, ids=tuple)
def test_is_valid_delay(delay_validity_pair: tuple):
	assert is_valid_delay(delay_validity_pair[0]) == delay_validity_pair[1]

del DELAY_VALIDITY

# endregion


# region Helper Classes


# --- test BankListManager
def test_BankListManager_constructor():
	with pytest.raises(ValueError):
		BankListManager(0)


BANK_MANAGER_FROM_DICT = (
	# (size, require_enabled, data, should_pass)
	(3, True, [True, False, False], True),
	(3, True, [False, False, False], False),
	(4, True, [False, False, False], False),
	(3, False, [False, False, False], True)
)

@pytest.mark.parametrize("bank_manager_data", BANK_MANAGER_FROM_DICT, ids=tuple)
def test_BankListManager_from_dict(bank_manager_data: tuple):
	should_pass: bool = bank_manager_data[3]
	data = bank_manager_data[2]

	bm: BankListManager = BankListManager(
		bank_manager_data[0],
		require_enabled=bank_manager_data[1]
	)

	if should_pass:
		bm.from_dict(data)
	else:
		with pytest.raises(InputValidationError):
			bm.from_dict(data)

# TODO: Test to_write_command

del BANK_MANAGER_FROM_DICT


# endregion


# region SDO

# --- This section in order relative to source
# Please note that "dumb" SDOs with no validation may be omitted

# PRG Program Mode
def test_EnterProgramMode():
	with pytest.raises(NotImplementedError):
		EnterProgramMode().to_dict()


# BSV Battery Charge Timer
BATTERY_CHARGE_VALIDITY = (
	(0, False),
	(1, True),
	(5, True),
	(16, True),
	(17, False)
)

@pytest.mark.parametrize("battery_charge_validity_pair", BATTERY_CHARGE_VALIDITY, ids=tuple)
def test_BatteryChargeTimer(battery_charge_validity_pair: tuple):
	d = {"hours": battery_charge_validity_pair[0]}

	if battery_charge_validity_pair[1]:
		BatteryChargeTimer().from_dict(d)
	else:
		with pytest.raises(InputValidationError):
			BatteryChargeTimer().from_dict(d)

del BATTERY_CHARGE_VALIDITY


# TODO: SCG and onward


# endregion