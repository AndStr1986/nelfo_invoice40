# nelfo-invoice

A Python parser for the **EFO/NELFO invoice format** (v4.0) — a semicolon-delimited EDI format used in the Norwegian electrical wholesale industry.

## Installation

```bash
pip install git+https://github.com/AndStr1986/nelfo_invoice40
```

Or with uv:

```bash
uv add git+https://github.com/AndStr1986/nelfo_invoice40
```

## Usage

```python
from nelfo_invoice import NelfoInvoiceParser
from pathlib import Path

invoice_file = NelfoInvoiceParser.from_path(Path("invoice.txt"))

print(invoice_file.header.seller_company_name)   # e.g. "Solar Norge AS"
print(invoice_file.file_invoice_count)            # number of invoices in the file

for invoice in invoice_file.body:
    print(invoice.header.invoice_number)
    print(invoice.header.invoice_total)           # total incl. VAT, 2 implied decimals
    for line in invoice.lines:
        print(line.line.item_number, line.line.line_amount)
```

## File structure

A NELFO file is a sequence of semicolon-separated records, one per line. Each record starts with a type code:

| Record | Model | Description |
|--------|-------|-------------|
| `FH` | `FH` | File header — sender identity and format version. One per file. |
| `FF` | `FF` | Invoice header — amounts, dates, and address information. One per invoice. |
| `FL` | `FL` | Invoice line item — product, quantity, price, discounts. One or more per invoice. |
| `FT` | `FT` | Free text line — optional text attached to the preceding `FL`. |
| `FA` | `FA` | Invoice footer — closes each invoice, includes optional record count. |
| `FS` | `FS` | File trailer — closes the file, includes optional invoice count. |

The parsed result is a `NelfoFile` object:

```
NelfoFile
├── header: FH
├── body: list[NelfoInvoice]
│   ├── header: FF
│   ├── lines: list[NelfoInvoiceLine]
│   │   ├── line: FL
│   │   └── free_texts: list[FT]
│   └── trailer: FA
└── trailer: FS
```

## Validation

The parser validates:

- Dates parsed from `ÅÅÅÅMMDD` format
- Country codes against ISO 3166-1 alpha-2
- Currency codes against ISO 4217
- Invoice number consistency between `FF` and `FA` records
- Record counts in `FA` and invoice counts in `FS` (when present)

## Requirements

- Python 3.14+
- [pydantic](https://docs.pydantic.dev/) >= 2.12
- [pycountry](https://pypi.org/project/pycountry/) >= 26.2
