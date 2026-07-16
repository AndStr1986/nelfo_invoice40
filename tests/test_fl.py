"""Tests for the FL (Faktura Linjepost) model.

Covers:
- Valid construction
- Fixed/immutable fields (post_type)
- item_type validation
- sign and seller_warehouse_mark Literal constraints
- Numeric field string-to-int parsing
- Required field enforcement
- Optional field defaults
"""

import pytest
from pydantic import ValidationError
from nelfo_invoice.models import FL


@pytest.fixture
def valid_fl_data():
    """Valid FL data parsed from a real example in Invoice.txt.

    Based on: FL;10;;;1;3242919;100;EA;40059;2500;;;;;;;;;40059;;GLOW ECO 8W 750LM 3000K;;-;248873/Kirkelina;63328410;E;7080001003395
    Optional discount/surcharge/tax fields are omitted (default to None).
    """
    return {
        "line_number": 10,
        "item_type": 1,
        "item_number": "3242919",
        "quantity": 100,
        "price_unit": "EA",
        "unit_price": 40059,
        "vat_rate": 2500,
        "line_amount": 40059,
        "item_description": "GLOW ECO 8W 750LM 3000K",
        "sign": "-",
        "buyer_reference": "248873/Kirkelina",
        "packing_slip_number": "63328410",
        "seller_warehouse_mark": "E",
        "seller_warehouse": "7080001003395",
    }


# --- Valid construction ---


def test_valid_fl(valid_fl_data):
    """A fully valid FL can be constructed without errors."""
    fl = FL(**valid_fl_data)
    assert fl.item_number == "3242919"


# --- Fixed fields ---


def test_fixed_fields(valid_fl_data):
    """post_type is always 'FL' regardless of input."""
    fl = FL(**valid_fl_data)
    assert fl.post_type == "FL"


# --- item_type validation ---


def test_valid_item_types(valid_fl_data):
    """All valid item_type values (0, 1, 2, 3, 4, 9) are accepted."""
    for valid_type in (0, 1, 2, 3, 4, 9):
        valid_fl_data["item_type"] = valid_type
        fl = FL(**valid_fl_data)
        assert fl.item_type == valid_type


def test_invalid_item_type(valid_fl_data):
    """An item_type not in (0, 1, 2, 3, 4, 9) raises a ValidationError."""
    valid_fl_data["item_type"] = 5
    with pytest.raises(ValidationError):
        FL(**valid_fl_data)


def test_item_type_parsed_from_string(valid_fl_data):
    """item_type is parsed from a string to an int."""
    valid_fl_data["item_type"] = "1"
    fl = FL(**valid_fl_data)
    assert fl.item_type == 1


# --- Numeric field parsing ---


def test_int_fields_parsed_from_string(valid_fl_data):
    """Numeric fields are parsed from strings to ints."""
    valid_fl_data["quantity"] = "100"
    valid_fl_data["unit_price"] = "40059"
    valid_fl_data["line_amount"] = "40059"
    fl = FL(**valid_fl_data)
    assert fl.quantity == 100
    assert fl.unit_price == 40059
    assert fl.line_amount == 40059


# --- Sign constraint ---


def test_invalid_sign(valid_fl_data):
    """sign only accepts '+' or '-'."""
    valid_fl_data["sign"] = "x"
    with pytest.raises(ValidationError):
        FL(**valid_fl_data)


# --- seller_warehouse_mark constraint ---


def test_invalid_seller_warehouse_mark(valid_fl_data):
    """seller_warehouse_mark only accepts 'E'."""
    valid_fl_data["seller_warehouse_mark"] = "X"
    with pytest.raises(ValidationError):
        FL(**valid_fl_data)


# --- Required fields ---


def test_missing_item_type(valid_fl_data):
    """Omitting item_type raises a ValidationError."""
    del valid_fl_data["item_type"]
    with pytest.raises(ValidationError):
        FL(**valid_fl_data)


def test_missing_item_number(valid_fl_data):
    """Omitting item_number raises a ValidationError."""
    del valid_fl_data["item_number"]
    with pytest.raises(ValidationError):
        FL(**valid_fl_data)


def test_missing_quantity(valid_fl_data):
    """Omitting quantity raises a ValidationError."""
    del valid_fl_data["quantity"]
    with pytest.raises(ValidationError):
        FL(**valid_fl_data)


def test_missing_price_unit(valid_fl_data):
    """Omitting price_unit raises a ValidationError."""
    del valid_fl_data["price_unit"]
    with pytest.raises(ValidationError):
        FL(**valid_fl_data)


def test_missing_unit_price(valid_fl_data):
    """Omitting unit_price raises a ValidationError."""
    del valid_fl_data["unit_price"]
    with pytest.raises(ValidationError):
        FL(**valid_fl_data)


def test_missing_vat_rate(valid_fl_data):
    """Omitting vat_rate raises a ValidationError."""
    del valid_fl_data["vat_rate"]
    with pytest.raises(ValidationError):
        FL(**valid_fl_data)


def test_missing_line_amount(valid_fl_data):
    """Omitting line_amount raises a ValidationError."""
    del valid_fl_data["line_amount"]
    with pytest.raises(ValidationError):
        FL(**valid_fl_data)


# --- Optional fields ---


def test_optional_fields_default_to_none(valid_fl_data):
    """Optional fields not provided default to None."""
    fl = FL(**valid_fl_data)
    assert fl.buyer_order_number is None
    assert fl.order_line_number is None
    assert fl.discount1_percent is None
    assert fl.discount1_amount is None
    assert fl.item_description2 is None
