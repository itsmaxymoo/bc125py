"""Test ctcss_dcs_internal and ctcss_dcs_human."""

from dataclasses import dataclass

import pytest

from bc125py.mappings import ctcss_dcs_to_human, ctcss_dcs_to_internal


@dataclass
class DataStruct:
    """Test data for ctcss_dcs_human."""
    human: str | float | int = -1
    internal: int = -1

    def __str__(self):
        """Return a string representation of the data."""
        return f"h: {self.human}, i: {self.internal}"


VALIDH2IDATA = (DataStruct(human="NONE", internal=0),
                DataStruct(human="SEARCH", internal=127),
                DataStruct(human="No Tone", internal=240),
                DataStruct(human="No_tone", internal=240),
                DataStruct(human="ctcss67.0", internal=64),
)

@pytest.mark.parametrize("data", VALIDH2IDATA, ids=str)
def test_ctcss_dcs_to_internal(data: DataStruct):
    """Ensure variations of human-friendly values are mapped to internal.
    
    Args:
        data: The test data.

    """
    assert ctcss_dcs_to_internal(data.human) == data.internal

INVALIDH2IDATA = (DataStruct(human="12345"),
                  DataStruct(human=12345),
                  DataStruct(human="123.45"),
                  DataStruct(human=123.45),
                  DataStruct(human=""),
                  DataStruct(human="67.0")
)

@pytest.mark.parametrize("data", INVALIDH2IDATA, ids=str)  
def test_ctcss_dcs_to_internal_invalid(data: DataStruct):
    """Ensure invalid human-friendly values raise ValueError.
    
    Args:
        data: The test data.
    """
    with pytest.raises(ValueError):
        ctcss_dcs_to_internal(data.human)

VALIDI2HDATA = (DataStruct(human="NONE", internal=0),
                DataStruct(human="SEARCH", internal=127),
                DataStruct(human="NO_TONE", internal=240),
                DataStruct(human="ctcss_74.4", internal=67),
                DataStruct(human="dcs_23", internal=128),
)   

@pytest.mark.parametrize("data", VALIDI2HDATA, ids=str)
def test_ctcss_dcs_to_human(data: DataStruct):
    """Ensure internal values are mapped to human-friendly values.
    
    Args:
        data: The test data.

    """
    assert ctcss_dcs_to_human(data.internal) == data.human.lower()

INVALIDI2HDATA = (DataStruct(internal=12345),)

@pytest.mark.parametrize("data", INVALIDI2HDATA, ids=str)
def test_ctcss_dcs_to_human_invalid(data: DataStruct):
    """Ensure invalid internal values raise ValueError.
    
    Args:
        data: The test data.

    """
    with pytest.raises(ValueError):
        ctcss_dcs_to_human(data.internal)
