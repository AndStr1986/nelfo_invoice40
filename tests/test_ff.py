"""Tests for the FF (Faktura Hodepost) model.

Covers:
- Valid construction
- Fixed/immutable fields (post_type)
- Date string parsing
- document_sign and rounding_sign Literal constraints
- Currency code validation (ISO 4217)
- Country code validation (ISO 3166-1 alpha-2)
- Required field enforcement
- Optional field defaults
"""

import pytest
from pydantic import ValidationError
from nelfo_invoice.models import FF
from datetime import date


@pytest.fixture
def valid_ff_data():
    """Valid FF data parsed from a real example in Invoice.txt.

    Empty fields in the source line are omitted (they default to None).
    Numeric amount fields are integers with 2 implied decimal places
    (e.g. 40059 = 400.59 NOK).
    """
    return {
        "invoice_number":                   "11537643",
        "document_sign":                    "-",
        "buyer_id":                         "NO979538480MVA",
        "seller_order_number":              "63328410",
        "buyer_order_number":               "ES156475",
        "customer_number":                  "2004640",
        "invoice_date":                     "20250605",
        "due_date":                         "20250814",
        "net_amount_pre_tax":               40059,
        "vat_amount":                       10015,
        "rounding_amount":                  0,
        "rounding_sign":                    "+",
        "invoice_total":                    50074,
        "currency_code":                    "NOK",
        "customer_order_number":            "248873",
        "buyer_reference":                  "248873/Kirkelina",
        "seller_reference":                 "Joakim Jensen",
        "order_origin":                     "K",
        "kid":                              "241153764320046404",
        "account_number":                   "60030652269",
        "delivery_company_name":            "Arro Elektro AS",
        "delivery_address2":               "Spinderisletta 95",
        "delivery_postal_code":             "3057",
        "delivery_city":                    "Solbergelva",
        "delivery_country_code":            "NO",
        "buyer_company_name":               "Arro Elektro AS",
        "buyer_address2":                  "Spinderisletta 95",
        "buyer_postal_code":                "3057",
        "buyer_city":                       "Solbergelva",
        "buyer_country_code":               "NO",
        "buyer_contact_name":               "Stein Ullhaug",
        "invoice_recipient_name":           "Arro Elektro AS",
        "invoice_recipient_address2":      "Spinderisletta 95",
        "invoice_recipient_postal_code":    "3057",
        "invoice_recipient_city":           "Solbergelva",
        "invoice_recipient_country_code":   "NO",
        "invoice_recipient_customer_number": "2004640",
        "iban":                             "NO4160030652269",
        "swift":                            "NDEANOKK",
    }

# --- Valid construction ---

def test_valid_ff(valid_ff_data):
    """A fully valid FF can be constructed without errors."""
    ff = FF(**valid_ff_data)
    assert ff.invoice_number == "11537643"


# --- Fixed fields ---

def test_fixed_fields(valid_ff_data):
    """post_type is always 'FF' regardless of input."""
    ff = FF(**valid_ff_data)
    assert ff.post_type == "FF"


# --- Date parsing ---

def test_date_parsing(valid_ff_data):
    """Date strings in ÅÅÅÅMMDD format are parsed into date objects."""
    ff = FF(**valid_ff_data)
    assert ff.invoice_date == date(2025, 6, 5)
    assert ff.due_date == date(2025, 8, 14)

def test_date_parsing_with_date_obj(valid_ff_data):
    """A date object passed directly is accepted without conversion."""
    valid_ff_data["invoice_date"] = date(2025, 6, 5)
    ff = FF(**valid_ff_data)
    assert ff.invoice_date == date(2025, 6, 5)

def test_invalid_date(valid_ff_data):
    """A non-date string for invoice_date raises a ValidationError."""
    valid_ff_data["invoice_date"] = "not-a-date"
    with pytest.raises(ValidationError):
        FF(**valid_ff_data)


# --- Sign constraints ---

def test_invalid_document_sign(valid_ff_data):
    """document_sign only accepts '+' or '-'."""
    valid_ff_data["document_sign"] = "x"
    with pytest.raises(ValidationError):
        FF(**valid_ff_data)

def test_invalid_rounding_sign(valid_ff_data):
    """rounding_sign only accepts '+' or '-'."""
    valid_ff_data["rounding_sign"] = "x"
    with pytest.raises(ValidationError):
        FF(**valid_ff_data)


# --- Currency code validation ---

def test_invalid_currency_code(valid_ff_data):
    """An unrecognised ISO 4217 currency code raises a ValidationError."""
    valid_ff_data["currency_code"] = "INVALID"
    with pytest.raises(ValidationError):
        FF(**valid_ff_data)


# --- Country code validation ---

def test_invalid_country_code(valid_ff_data):
    """An unrecognised ISO 3166-1 alpha-2 country code raises a ValidationError."""
    valid_ff_data["buyer_country_code"] = "XX"
    with pytest.raises(ValidationError):
        FF(**valid_ff_data)


# --- Required fields ---

def test_missing_required_field(valid_ff_data):
    """Omitting invoice_number raises a ValidationError."""
    del valid_ff_data["invoice_number"]
    with pytest.raises(ValidationError):
        FF(**valid_ff_data)


# --- Optional fields ---

def test_optional_fields_default(valid_ff_data):
    """Optional fields not provided default to None."""
    ff = FF(**valid_ff_data)
    assert ff.buyer_address1 is None




