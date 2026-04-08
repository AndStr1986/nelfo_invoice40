"""Tests for the FA (Faktura Avslutningspost) model.

Covers:
- Valid construction
- Fixed/immutable fields (post_type)
- record_count string-to-int parsing
- Missing required field enforcement
- Optional record_count defaults to None
"""

import pytest
from pydantic import ValidationError
from nelfo_invoice.models import FA


@pytest.fixture
def valid_fa_data():
    """Valid FA data based on a real example in Invoice.txt.

    Based on: FA;11537643;4
    """
    return {
        "invoice_number": "11537643",
        "record_count":   4,
    }


# --- Valid construction ---

def test_valid_fa(valid_fa_data):
    """A fully valid FA can be constructed without errors."""
    fa = FA(**valid_fa_data)
    assert fa.invoice_number == "11537643"
    assert fa.record_count == 4


# --- Fixed fields ---

def test_fixed_fields(valid_fa_data):
    """post_type is always 'FA' regardless of input."""
    fa = FA(**valid_fa_data)
    assert fa.post_type == "FA"


# --- record_count parsing ---

def test_record_count_parsed_from_string(valid_fa_data):
    """record_count is parsed from a string to an int."""
    valid_fa_data["record_count"] = "4"
    fa = FA(**valid_fa_data)
    assert fa.record_count == 4


# --- Required fields ---

def test_missing_invoice_number(valid_fa_data):
    """Omitting invoice_number raises a ValidationError."""
    del valid_fa_data["invoice_number"]
    with pytest.raises(ValidationError):
        FA(**valid_fa_data)


# --- Optional fields ---

def test_record_count_defaults_to_none():
    """record_count defaults to None when not provided."""
    fa = FA(invoice_number="11537643")
    assert fa.record_count is None
