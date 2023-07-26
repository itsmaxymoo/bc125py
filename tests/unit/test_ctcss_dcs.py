"""Test ctcss_dcs_internal and ctcss_dcs_human."""

from dataclasses import dataclass

import pytest

from bc125py.mappings import ctcss_dcs_h2i, ctcss_dcs_i2h


@dataclass
class DataStruct:
    """Test data for ctcss_dcs_human."""
    human: str | float | int = -1
    internal: int = -1

    def __str__(self):
        """Return a string representation of the data."""
        return f"h: {self.human}, i: {self.internal}"


VALIDH2IDATA = (DataStruct(human="NONE", internal=0),
                DataStruct(human="All", internal=0),
                DataStruct(human="None/All", internal=0),
                DataStruct(human="SEARCH", internal=127),
                DataStruct(human="No Tone", internal=240),
                DataStruct(human="No_tone", internal=240),
                DataStruct(human="67.0", internal=64),
                DataStruct(human=67.0, internal=64),
                DataStruct(human="23", internal=128),
                DataStruct(human=23, internal=128),
)

@pytest.mark.parametrize("data", VALIDH2IDATA, ids=str)
def test_ctcss_dcs_h2i(data: DataStruct):
    """Ensure variations of human-friendly values are mapped to internal.
    
    Args:
        data: The test data.

    """
    assert ctcss_dcs_h2i(data.human) == data.internal

INVALIDH2IDATA = (DataStruct(human="12345"),
                  DataStruct(human=12345),
                  DataStruct(human="123.45"),
                  DataStruct(human=123.45),
                  DataStruct(human="")
)

@pytest.mark.parametrize("data", INVALIDH2IDATA, ids=str)  
def test_ctcss_dcs_h2i_invalid(data: DataStruct):
    """Ensure invalid human-friendly values raise ValueError.
    
    Args:
        data: The test data.
    """
    with pytest.raises(ValueError):
        ctcss_dcs_h2i(data.human)

VALIDI2HDATA = (DataStruct(human="NONE/All", internal=0),
                DataStruct(human="SEARCH", internal=127),
                DataStruct(human="NO_TONE", internal=240),
                DataStruct(human="67.0", internal=64),
                DataStruct(human="23", internal=128),
)   

@pytest.mark.parametrize("data", VALIDI2HDATA, ids=str)
def test_ctcss_dcs_i2h(data: DataStruct):
    """Ensure internal values are mapped to human-friendly values.
    
    Args:
        data: The test data.

    """
    assert ctcss_dcs_i2h(data.internal) == data.human

INVALIDI2HDATA = (DataStruct(internal=12345),)

@pytest.mark.parametrize("data", INVALIDI2HDATA, ids=str)
def test_ctcss_dcs_i2h_invalid(data: DataStruct):
    """Ensure invalid internal values raise ValueError.
    
    Args:
        data: The test data.

    """
    with pytest.raises(ValueError):
        ctcss_dcs_i2h(data.internal)
