"""Tests for the FH (Faktura Sending Hodepost) model.

Covers:
- Valid construction
- Fixed/immutable fields (post_type, doc_format, version)
- Field max length constraints
- Date string parsing
- Country code validation (ISO 3166-1 alpha-2)
- Required field enforcement
- Optional field defaults
"""

import pytest
from pydantic import ValidationError
from nelfo_invoice.models import FH
from datetime import date


@pytest.fixture
def valid_fh_data():
    """Minimal valid FH data based on a real example from Invoice.txt.

    seller_address1 is intentionally omitted to verify optional fields work.
    """
    return {
        "seller_id": "NO980672891MVA",
        "production_date": "20250606",
        "seller_company_name": "Solar Norge AS",
        "seller_address2": "Postboks 23",
        "seller_postal_code": "2051",
        "seller_city": "Jessheim",
        "seller_country_code": "NO",
    }


# --- Valid construction ---

def test_valid_fh(valid_fh_data):
    """A fully valid FH can be constructed without errors."""
    fh = FH(**valid_fh_data)
    assert fh.seller_id == "NO980672891MVA"

# --- Fixed fields ---

def test_fixed_fields(valid_fh_data):
    """Fixed fields always have their expected default values."""
    fh = FH(**valid_fh_data)
    assert fh.post_type == "FH"
    assert fh.doc_format == "EFONELFO"
    assert fh.version == "4.0"

# --- Max length constraints ---

def test_sellers_id_max_length(valid_fh_data):
    """seller_id longer than 14 chars raises a ValidationError."""
    valid_fh_data["seller_id"] = "NO" + "1" * 14 + "MVA"  # 19 chars, exceeds max of 14
    with pytest.raises(ValidationError):
        FH(**valid_fh_data)

# --- Date parsing ---

def test_date_parsing(valid_fh_data):
    """production_date string in ÅÅÅÅMMDD format is parsed into a date object."""
    fh = FH(**valid_fh_data)
    assert fh.production_date == date(2025, 6, 6)

def test_valid_date_obj(valid_fh_data):
    valid_fh_data["production_date"] = date(2025, 6, 6)
    fh = FH(**valid_fh_data)
    assert fh.production_date == date(2025, 6, 6)

def test_invalid_date(valid_fh_data):
    """A non-date string for production_date raises a ValidationError."""
    valid_fh_data["production_date"] = "not-a-date"
    with pytest.raises(ValidationError):
        FH(**valid_fh_data)


# --- Country code validation ---

def test_valid_country_code(valid_fh_data):
    """A valid ISO 3166-1 alpha-2 country code is accepted."""
    valid_fh_data["seller_country_code"] = "US"
    fh = FH(**valid_fh_data)
    assert fh.seller_country_code == "US"


def test_invalid_country_code(valid_fh_data):
    """An unrecognised country code raises a ValidationError."""
    valid_fh_data["seller_country_code"] = "XX"
    with pytest.raises(ValidationError):
        FH(**valid_fh_data)


# --- Required fields ---

def test_missing_sellers_id(valid_fh_data):
    """Omitting seller_id raises a ValidationError."""
    del valid_fh_data["seller_id"]
    with pytest.raises(ValidationError):
        FH(**valid_fh_data)


def test_missing_prod_date(valid_fh_data):
    """Omitting production_date raises a ValidationError."""
    del valid_fh_data["production_date"]
    with pytest.raises(ValidationError):
        FH(**valid_fh_data)


def test_missing_company_name(valid_fh_data):
    """Omitting seller_company_name raises a ValidationError."""
    del valid_fh_data["seller_company_name"]
    with pytest.raises(ValidationError):
        FH(**valid_fh_data)


def test_missing_postnr(valid_fh_data):
    """Omitting seller_postal_code raises a ValidationError."""
    del valid_fh_data["seller_postal_code"]
    with pytest.raises(ValidationError):
        FH(**valid_fh_data)


def test_missing_post_place(valid_fh_data):
    """Omitting seller_city raises a ValidationError."""
    del valid_fh_data["seller_city"]
    with pytest.raises(ValidationError):
        FH(**valid_fh_data)


# --- Optional fields ---

def test_optional_fields_default_to_none(valid_fh_data):
    """Optional fields default to None if not provided."""
    del valid_fh_data["seller_country_code"]
    del valid_fh_data["seller_address2"]
    fh = FH(**valid_fh_data)
    assert fh.seller_country_code is None
    assert fh.seller_address1 is None
    assert fh.seller_address2 is None
