import pytest
from io import StringIO
from nelfo_invoice import NelfoInvoiceParser
from nelfo_invoice.models import NelfoFile
from pathlib import Path

INVOICE_PATH = Path(__file__).parent / "fixtures" / "sample_invoice.txt"


def test_parse_returns_neflo_file():
    result = NelfoInvoiceParser.from_path(INVOICE_PATH)
    assert isinstance(result, NelfoFile)


def test_parse_invoice_count():
    result = NelfoInvoiceParser.from_path(INVOICE_PATH)
    assert result.file_invoice_count == 4


def test_parse_invoice_numbers():
    result = NelfoInvoiceParser.from_path(INVOICE_PATH)
    assert result.invoice_numbers == ["11537643", "11538382", "11538385", "11538388"]


# --- Error-path tests ---------------------------------------------------
#
# Built from a single, known-valid invoice sliced out of Invoice.txt
# (its first FH/FF/FL/FT/FA block), with one field mutated per test.


def _base_single_invoice_lines() -> list[str]:
    raw_lines = INVOICE_PATH.read_text(encoding="utf-8").splitlines()
    fh, ff, fl, ft, fa = raw_lines[:5]
    fs = "FS;20250606;1"
    return [fh, ff, fl, ft, fa, fs]


def _set_field(line: str, index: int, value: str) -> str:
    fields = line.split(";")
    fields[index] = value
    return ";".join(fields)


def _to_source(lines: list[str]) -> StringIO:
    return StringIO("\n".join(lines) + "\n")


def test_base_fixture_is_valid():
    result = NelfoInvoiceParser(
        _to_source(_base_single_invoice_lines())
    ).parse_invoice_file()
    assert result.file_invoice_count == 1


def test_fa_invoice_number_mismatch():
    lines = _base_single_invoice_lines()
    lines[4] = _set_field(lines[4], 1, "99999999")  # FA.invoice_number
    with pytest.raises(ValueError, match="does not match"):
        NelfoInvoiceParser(_to_source(lines)).parse_invoice_file()


def test_fa_record_count_mismatch():
    lines = _base_single_invoice_lines()
    lines[4] = _set_field(lines[4], 2, "99")  # FA.record_count
    with pytest.raises(ValueError, match="Line count does not match"):
        NelfoInvoiceParser(_to_source(lines)).parse_invoice_file()

def test_fa_without_line_items():
    fh, ff, fl, ft, fa, fs = _base_single_invoice_lines()
    with pytest.raises(ValueError, match="no line items"):
        NelfoInvoiceParser(_to_source([fh, ff, fa, fs])).parse_invoice_file()


def test_fa_before_ff():
    fh, ff, fl, ft, fa, fs = _base_single_invoice_lines()
    with pytest.raises(ValueError, match="encountered before FF"):
        NelfoInvoiceParser(_to_source([fh, fl, fa, fs])).parse_invoice_file()


def test_file_ends_without_fs():
    fh, ff, fl, ft, fa, fs = _base_single_invoice_lines()
    with pytest.raises(ValueError) as exc_info:
        NelfoInvoiceParser(_to_source([fh, ff, fl, ft, fa])).parse_invoice_file()
    # Raised outside the per-line loop, so unlike every other error here,
    # it does NOT get a "Line N:" prefix.
    assert str(exc_info.value) == "File ended without an FS record"


def test_fs_before_fh():
    fh, ff, fl, ft, fa, fs = _base_single_invoice_lines()
    with pytest.raises(ValueError, match="before FH"):
        NelfoInvoiceParser(_to_source([ff, fl, ft, fa, fs])).parse_invoice_file()


def test_fs_invoice_count_mismatch():
    fh, ff, fl, ft, fa, fs = _base_single_invoice_lines()
    fs = _set_field(fs, 2, "5")  # FS.invoice_count
    with pytest.raises(ValueError, match="Line count from FS and read invoice lines"):
        NelfoInvoiceParser(_to_source([fh, ff, fl, ft, fa, fs])).parse_invoice_file()


def test_error_message_includes_line_number():
    lines = _base_single_invoice_lines()
    lines[4] = _set_field(lines[4], 2, "99")  # FA is the 5th line in the fixture
    with pytest.raises(ValueError, match=r"^Line 5:"):
        NelfoInvoiceParser(_to_source(lines)).parse_invoice_file()


def test_sum_of_line_amounts():
    lines = _base_single_invoice_lines()
    lines[1] = _set_field(lines[1], 10, "999999")  # FF.invoice_total_amount
    with pytest.raises(ValueError, match="does not match"):
        NelfoInvoiceParser(_to_source(lines)).parse_invoice_file()

def test_invoice_total_not_match_net_amount_pluss_vat_amount():
    lines = _base_single_invoice_lines()
    lines[1] = _set_field(lines[1], 14, "999999")
    with pytest.raises(ValueError, match="does not match"):
         NelfoInvoiceParser(_to_source(lines)).parse_invoice_file()

