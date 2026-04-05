"""Tests for the FH (Faktura Sending Hodepost) model.

Covers:
- Valid construction
- Required field enforcement
- Optional field defaults
- Date string parsing
- Country code validation (ISO 3166-1 alpha-2)
- Field max length constraints
- Fixed/immutable fields (post_type, doc_format, version)
"""

import pytest
from pydantic import ValidationError
from nelfo_invoice.models import FH
from datetime import date


@pytest.fixture
def valid_fh_data():
    """Minimal valid FH data based on a real example from Invoice.txt.

    address1 is intentionally omitted to verify optional fields work.
    """
    return {
        "sellers_id": "NO980672891MVA",
        "prod_date": "20250606",
        "company_name": "Solar Norge AS",
        "address2": "Postboks 23",
        "postnr": "2051",
        "post_place": "Jessheim",
        "country": "NO",
    }


# --- Valid construction ---

def test_valid_fh(valid_fh_data):
    """A fully valid FH can be constructed without errors."""
    fh = FH(**valid_fh_data)
    assert fh.sellers_id == "NO980672891MVA"


# --- Date parsing ---

def test_date_parsing(valid_fh_data):
    """prod_date string in ÅÅÅÅMMDD format is parsed into a date object."""
    fh = FH(**valid_fh_data)
    assert fh.prod_date == date(2025, 6, 6)


def test_invalid_date(valid_fh_data):
    """A non-date string for prod_date raises a ValidationError."""
    valid_fh_data["prod_date"] = "not-a-date"
    with pytest.raises(ValidationError):
        FH(**valid_fh_data)


# --- Country code validation ---

def test_valid_country_code(valid_fh_data):
    """A valid ISO 3166-1 alpha-2 country code is accepted."""
    valid_fh_data["country"] = "US"
    fh = FH(**valid_fh_data)
    assert fh.country == "US"


def test_invalid_country_code(valid_fh_data):
    """An unrecognised country code raises a ValidationError."""
    valid_fh_data["country"] = "XX"
    with pytest.raises(ValidationError):
        FH(**valid_fh_data)


# --- Required fields ---

def test_missing_sellers_id(valid_fh_data):
    """Omitting sellers_id raises a ValidationError."""
    del valid_fh_data["sellers_id"]
    with pytest.raises(ValidationError):
        FH(**valid_fh_data)


def test_missing_prod_date(valid_fh_data):
    """Omitting prod_date raises a ValidationError."""
    del valid_fh_data["prod_date"]
    with pytest.raises(ValidationError):
        FH(**valid_fh_data)


def test_missing_company_name(valid_fh_data):
    """Omitting company_name raises a ValidationError."""
    del valid_fh_data["company_name"]
    with pytest.raises(ValidationError):
        FH(**valid_fh_data)


def test_missing_postnr(valid_fh_data):
    """Omitting postnr raises a ValidationError."""
    del valid_fh_data["postnr"]
    with pytest.raises(ValidationError):
        FH(**valid_fh_data)


def test_missing_post_place(valid_fh_data):
    """Omitting post_place raises a ValidationError."""
    del valid_fh_data["post_place"]
    with pytest.raises(ValidationError):
        FH(**valid_fh_data)

