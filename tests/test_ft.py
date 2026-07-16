"""Tests for the FT (Faktura Fritekstlinje) model.

Covers:
- Valid construction with free text
- Valid construction without free text
- Fixed/immutable fields (post_type)
- max_length constraint on free_text
"""

import pytest
from pydantic import ValidationError
from nelfo_invoice.models import FT


# --- Valid construction ---


def test_valid_ft_with_text():
    """FT can be constructed with free text."""
    ft = FT(free_text="Material disc. group 49.7300")
    assert ft.free_text == "Material disc. group 49.7300"


def test_valid_ft_without_text():
    """FT can be constructed without free text."""
    ft = FT()
    assert ft.free_text is None


# --- Fixed fields ---


def test_fixed_fields():
    """post_type is always 'FT' regardless of input."""
    ft = FT(free_text="some text")
    assert ft.post_type == "FT"


# --- Max length ---


def test_free_text_max_length():
    """free_text longer than 30 chars raises a ValidationError."""
    with pytest.raises(ValidationError):
        FT(free_text="A" * 31)
