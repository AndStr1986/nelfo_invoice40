from pathlib import Path
from typing import IO

from nelfo_invoice.models import (
    NelfoFile,
    NelfoInvoice,
    NelfoInvoiceLine,
    FH,
    FF,
    FL,
    FT,
    FA,
    FS,
)


class NelfoInvoiceParser:
    def __init__(self, source: IO[str]) -> None:

        self._source = source

        # --- File-level state ---
        self._file_header: FH | None = None
        self._file_invoices: list[NelfoInvoice] = []

        # --- Per-invoice state, reset after each FA ---
        self._current_invoice_header: FF | None = None
        self._current_invoice_lines: list[NelfoInvoiceLine] = []

        # --- Per-line state, reset after each FL and FA ---
        self._current_invoice_line: FL | None = None
        self._current_invoice_line_free_text: list[FT] = []
        # --- record count ---
        self._current_record_count: int = 0

    @classmethod
    def from_path(cls, path: Path) -> "NelfoFile":
        with open(path, encoding="utf-8") as f:
            return cls(f).parse_invoice_file()

    def parse_invoice_file(self) -> NelfoFile:

        handlers = {
            "FH": self._handle_file_head,
            "FF": self._handle_invoice_head,
            "FL": self._handle_invoice_line,
            "FT": self._handle_invoice_line_free_text,
            "FA": self._handle_invoice_tail,
            "FS": self._handle_file_tail,
        }

        for raw_line in self._source:
            line_data = raw_line.rstrip("\n").split(";")
            line_handler_type = line_data[0]

            if handler := handlers.get(line_handler_type):
                result = handler(line_data)
                if isinstance(result, NelfoFile):
                    return result

        raise ValueError("File ended without an FS record")

    def _handle_file_head(self, line_data: list[str]) -> None:
        self._file_header = FH.from_list(line_data)

    def _handle_invoice_head(self, line_data: list[str]) -> None:
        self._current_invoice_header = FF.from_list(line_data)
        self._current_record_count += 1
        self._current_invoice_lines = []

    def _handle_invoice_line(self, line_data: list[str]) -> None:
        if self._current_invoice_line is not None:
            self._current_invoice_lines.append(
                NelfoInvoiceLine(
                    line=self._current_invoice_line,
                    free_texts=self._current_invoice_line_free_text,
                )
            )
        self._current_record_count += 1
        self._current_invoice_line = FL.from_list(line_data)
        self._current_invoice_line_free_text = []

    def _handle_invoice_line_free_text(self, line_data: list[str]) -> None:
        self._current_invoice_line_free_text.append(FT.from_list(line_data))
        self._current_record_count += 1

    def _handle_invoice_tail(self, line_data: list[str]) -> None:

        if not self._current_invoice_lines and self._current_invoice_line is None:
            raise ValueError("Invoice has no line items (FL)")
        if self._current_invoice_header is None or self._current_invoice_line is None:
            raise ValueError(
                "FA record (invoice closing) encountered before FF (invoice head) or FL (invoice line)"
            )
        fa = FA.from_list(line_data)
        self._current_record_count += 1
        if (
            fa.record_count is not None
            and self._current_record_count != fa.record_count
        ):
            raise ValueError("Line count does not match FS record line count")
        if fa.invoice_number != self._current_invoice_header.invoice_number:
            raise ValueError(
                f"FA invoice_number '{fa.invoice_number}' does not match "
                f"FF invoice_number '{self._current_invoice_header.invoice_number}'"
            )
        self._current_invoice_lines.append(
            NelfoInvoiceLine(
                line=self._current_invoice_line,
                free_texts=self._current_invoice_line_free_text,
            )
        )
        self._file_invoices.append(
            NelfoInvoice(
                header=self._current_invoice_header,
                lines=self._current_invoice_lines,
                trailer=fa,
            )
        )

        # --- Reset per-Invoice and per-line state for the next invoice ---
        self._current_invoice_header = None
        self._current_invoice_lines = []
        self._current_invoice_line = None
        self._current_invoice_line_free_text = []
        self._current_record_count = 0

    def _validate_invoice_line_count(
        self, fs_line_count: int | None, file_invoice_count: int
    ) -> None:
        if fs_line_count is not None and fs_line_count != file_invoice_count:
            raise ValueError(
                "Line count from FS and and read invoice lines does not match up"
            )

    def _handle_file_tail(self, line_data: list[str]) -> NelfoFile:
        if self._file_header is None:
            raise ValueError(
                "Encountered FS (file closing) record before FH (file head)"
            )

        result = NelfoFile(
            header=self._file_header,
            body=self._file_invoices,
            trailer=FS.from_list(line_data),
        )
        self._validate_invoice_line_count(
            result.trailer.invoice_count, result.file_invoice_count
        )
        return result
