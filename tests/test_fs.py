"""Tests for the FS (Faktura Sending Sluttpost) model.

Covers:
- Valid construction
- Fixed/immutable fields (post_type)
- production_date string parsing (ÅÅÅÅMMDD)
- production_date accepts date object directly
- invoice_count string-to-int parsing
- Missing required field enforcement
- Optional invoice_count defaults to None
"""

import pytest
from pydantic import ValidationError
from nelfo_invoice.models import FS
from datetime import date


@pytest.fixture
def valid_fs_data():
    """Valid FS data based on a real example in Invoice.txt.

    Based on: FS;20250606;4
    """
    return {
        "production_date": "20250606",
        "invoice_count":   4,
    }


# --- Valid construction ---

def test_valid_fs(valid_fs_data):
    """A fully valid FS can be constructed without errors."""
    fs = FS(**valid_fs_data)
    assert fs.production_date == date(2025, 6, 6)
    assert fs.invoice_count == 4


# --- Fixed fields ---

def test_fixed_fields(valid_fs_data):
    """post_type is always 'FS' regardless of input."""
    fs = FS(**valid_fs_data)
    assert fs.post_type == "FS"


# --- Date parsing ---

def test_date_parsed_from_string(valid_fs_data):
    """production_date string in ÅÅÅÅMMDD format is parsed into a date object."""
    fs = FS(**valid_fs_data)
    assert fs.production_date == date(2025, 6, 6)

def test_date_accepts_date_object(valid_fs_data):
    """A date object passed directly is accepted without conversion."""
    valid_fs_data["production_date"] = date(2025, 6, 6)
    fs = FS(**valid_fs_data)
    assert fs.production_date == date(2025, 6, 6)

def test_invalid_date(valid_fs_data):
    """A non-date string for production_date raises a ValidationError."""
    valid_fs_data["production_date"] = "not-a-date"
    with pytest.raises(ValidationError):
        FS(**valid_fs_data)


# --- invoice_count parsing ---

def test_invoice_count_parsed_from_string(valid_fs_data):
    """invoice_count is parsed from a string to an int."""
    valid_fs_data["invoice_count"] = "4"
    fs = FS(**valid_fs_data)
    assert fs.invoice_count == 4


# --- Required fields ---

def test_missing_production_date(valid_fs_data):
    """Omitting production_date raises a ValidationError."""
    del valid_fs_data["production_date"]
    with pytest.raises(ValidationError):
        FS(**valid_fs_data)


# --- Optional fields ---

def test_invoice_count_defaults_to_none():
    """invoice_count defaults to None when not provided."""
    fs = FS(production_date=date(2025, 6, 6))
    assert fs.invoice_count is None
