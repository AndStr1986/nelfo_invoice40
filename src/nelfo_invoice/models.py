from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
import pycountry


class NelfoBaseLineModel(BaseModel):
    @classmethod
    def from_list(cls, data: list[str]):
        field_names = [name for name in cls.model_fields.keys()]
        if len(data) > len(field_names):
            raise ValueError(
                f"{cls.__name__}: line has {len(data)} fields, excpected at most {len(field_names)}"
            )
        field_values = [value or None for value in data]
        return cls(**dict(zip(field_names, field_values)))


class FH(NelfoBaseLineModel):
    """Faktura Sending Hodepost (FH) — file-level header.

    One per file, always the first record. Identifies the sender and the
    format version for all invoices that follow.

    Spec: EFO/NELFO Fakturaformat v4.0, Posttype FH.
    """

    post_type: str = Field(
        default="FH", init=False, max_length=2, json_schema_extra={"position": 1}
    )
    doc_format: str = Field(
        default="EFONELFO", init=False, max_length=8, json_schema_extra={"position": 2}
    )
    version: str = Field(
        default="4.0", init=False, max_length=3, json_schema_extra={"position": 3}
    )
    seller_id: str = Field(
        max_length=14,
        json_schema_extra={"position": 4},
        description="Selgers foretaksnummer, e.g. 'NO123456789MVA'",
    )
    production_date: date = Field(
        json_schema_extra={"position": 5},
        description="Produksjonsdato. Raw format: ÅÅÅÅMMDD",
    )
    seller_company_name: str = Field(
        max_length=35,
        json_schema_extra={"position": 6},
        description="Selgers firmanavn",
    )
    seller_address1: Optional[str] = Field(
        default=None,
        max_length=35,
        json_schema_extra={"position": 7},
        description="Selgers adresse1",
    )
    seller_address2: Optional[str] = Field(
        default=None,
        max_length=35,
        json_schema_extra={"position": 8},
        description="Selgers adresse2",
    )
    seller_postal_code: str = Field(
        max_length=9,
        json_schema_extra={"position": 9},
        description="Selgers postnummer",
    )
    seller_city: str = Field(
        max_length=35,
        json_schema_extra={"position": 10},
        description="Selgers poststed",
    )
    seller_country_code: Optional[str] = Field(
        default=None,
        max_length=2,
        json_schema_extra={"position": 11},
        description="Selgers landkode, ISO 3166-1 alpha-2, e.g. 'NO'",
    )

    @field_validator("production_date", mode="before")
    @classmethod
    def validate_production_date(cls, value):
        """Parse date string from ÅÅÅÅMMDD format into a date object."""
        if isinstance(value, str):
            return date(int(value[:4]), int(value[4:6]), int(value[6:8]))
        return value

    @field_validator("seller_country_code", mode="before")
    @classmethod
    def validate_country(cls, value):
        """Validate that country is a recognised ISO 3166-1 alpha-2 code."""
        if value and not pycountry.countries.get(alpha_2=value):
            raise ValueError(f"Invalid country code: {value}")
        return value


class FF(NelfoBaseLineModel):
    """Faktura Hodepost (FF) — invoice header.

    One per invoice. Contains all invoice-level metadata including amounts,
    dates, references, and address information for delivery, buyer and
    invoice recipient.

    Spec: EFO/NELFO Fakturaformat v4.0, Posttype FF.
    """

    # --- Identity ---
    post_type: str = Field(
        default="FF", init=False, max_length=2, json_schema_extra={"position": 1}
    )
    invoice_number: str = Field(
        max_length=8,
        json_schema_extra={"position": 2},
        description="Selgers fakturanummer",
    )
    document_sign: Literal["+", "-"] = Field(
        json_schema_extra={"position": 3}, description="+ = Faktura, - = Kreditnota"
    )
    partial_invoice: Optional[str] = Field(
        default=None,
        max_length=1,
        json_schema_extra={"position": 4},
        description="1 = delfaktura, alle andre verdier = sluttfaktura",
    )
    buyer_id: Optional[str] = Field(
        default=None,
        max_length=14,
        json_schema_extra={"position": 5},
        description="Kjøpers foretaksnummer, e.g. 'NO123456789MVA'",
    )
    seller_order_number: str = Field(
        max_length=10,
        json_schema_extra={"position": 6},
        description="Selgers ordrenummer",
    )
    buyer_order_number: Optional[str] = Field(
        default=None,
        max_length=10,
        json_schema_extra={"position": 7},
        description="Kjøpers bestillingsnummer",
    )
    customer_number: str = Field(
        max_length=10,
        json_schema_extra={"position": 8},
        description="Kjøpers kundenr oppgitt av selger",
    )

    # --- Dates ---
    invoice_date: date = Field(
        json_schema_extra={"position": 9},
        description="Fakturadato. Raw format: ÅÅÅÅMMDD",
    )
    due_date: date = Field(
        json_schema_extra={"position": 10},
        description="Forfallsdato. Raw format: ÅÅÅÅMMDD",
    )

    # --- Amounts ---
    net_amount_pre_tax: int = Field(
        json_schema_extra={"position": 11},
        description="Sum netto før moms, 2 desimaler uten desimaltegn",
    )
    vat_amount: int = Field(
        json_schema_extra={"position": 12},
        description="Sum merverdiavgift, 2 desimaler uten desimaltegn",
    )
    rounding_amount: int = Field(
        json_schema_extra={"position": 13},
        description="Øreavrunding, 2 desimaler uten desimaltegn",
    )
    rounding_sign: Literal["+", "-"] = Field(
        json_schema_extra={"position": 14},
        description="+ = positiv øreavrunding, - = negativ øreavrunding",
    )
    invoice_total: int = Field(
        json_schema_extra={"position": 15},
        description="Fakturatotal inkl. mva, 2 desimaler uten desimaltegn",
    )
    currency_code: str = Field(
        max_length=3,
        json_schema_extra={"position": 16},
        description="Valutakode, ISO 4217, e.g. 'NOK'",
    )

    # --- References ---
    agreement_id_indicator: Optional[Literal["R", "T", "P"]] = Field(
        default=None,
        json_schema_extra={"position": 17},
        description="R = rabattavtale, T = tilbud, P = prosjekt",
    )
    agreement_id: Optional[str] = Field(
        default=None,
        max_length=10,
        json_schema_extra={"position": 18},
        description="Selgers rabattavtale-, tilbuds- eller prosjektnr",
    )
    customer_order_number: Optional[str] = Field(
        default=None,
        max_length=10,
        json_schema_extra={"position": 19},
        description="Kjøpers ordrenummer mot kjøpers kunde",
    )
    customer_department: Optional[str] = Field(
        default=None,
        max_length=10,
        json_schema_extra={"position": 20},
        description="Kjøpers avdeling eller kundekonto",
    )
    project_number: Optional[str] = Field(
        default=None,
        max_length=10,
        json_schema_extra={"position": 21},
        description="Kjøpers prosjektnummer",
    )
    warehouse_mark: Optional[Literal["E"]] = Field(
        default=None,
        json_schema_extra={"position": 22},
        description="E = EAN lokasjonsnummer brukt i KLager",
    )
    warehouse: Optional[str] = Field(
        default=None,
        max_length=14,
        json_schema_extra={"position": 23},
        description="Kjøpers lager",
    )
    external_reference: Optional[str] = Field(
        default=None,
        max_length=10,
        json_schema_extra={"position": 24},
        description="Ekstern referanse oppgitt av kjøper",
    )
    buyer_reference: Optional[str] = Field(
        default=None,
        max_length=25,
        json_schema_extra={"position": 25},
        description="Kjøpers øvrige referanse, fritekst",
    )
    seller_reference: Optional[str] = Field(
        default=None,
        max_length=25,
        json_schema_extra={"position": 26},
        description="Selgers referanse",
    )
    marking_text: Optional[str] = Field(
        default=None,
        max_length=25,
        json_schema_extra={"position": 27},
        description="Merkingstekst for pakke-etikett",
    )
    order_origin: Optional[str] = Field(
        default=None,
        max_length=2,
        json_schema_extra={"position": 28},
        description="Kode for bestillingens opprinnelse",
    )
    seller_id_at_buyer: Optional[str] = Field(
        default=None,
        max_length=10,
        json_schema_extra={"position": 29},
        description="Selgerens nummer hos kjøper",
    )
    packing_slip_number: Optional[str] = Field(
        default=None,
        max_length=8,
        json_schema_extra={"position": 30},
        description="Selgerens pakkseddelnummer",
    )
    kid: Optional[str] = Field(
        default=None,
        max_length=27,
        json_schema_extra={"position": 31},
        description="Selgers KID-nr for fakturaen",
    )
    account_number: Optional[str] = Field(
        default=None,
        max_length=11,
        json_schema_extra={"position": 32},
        description="Selgers kontonummer (bank/post)",
    )

    # --- Delivery address (Leveringsadresse) ---
    delivery_location_ean: Optional[str] = Field(
        default=None,
        max_length=14,
        json_schema_extra={"position": 33},
        description="EAN lokasjonsnummer for leveringsadresse",
    )
    delivery_company_name: Optional[str] = Field(
        default=None,
        max_length=35,
        json_schema_extra={"position": 34},
        description="Varemottakers navn",
    )
    delivery_address1: Optional[str] = Field(
        default=None,
        max_length=35,
        json_schema_extra={"position": 35},
        description="Varemottakers adresse1",
    )
    delivery_address2: Optional[str] = Field(
        default=None,
        max_length=35,
        json_schema_extra={"position": 36},
        description="Varemottakers adresse2",
    )
    delivery_postal_code: Optional[str] = Field(
        default=None,
        max_length=9,
        json_schema_extra={"position": 37},
        description="Varemottakers postnummer",
    )
    delivery_city: Optional[str] = Field(
        default=None,
        max_length=35,
        json_schema_extra={"position": 38},
        description="Varemottakers poststed",
    )
    delivery_country_code: Optional[str] = Field(
        default=None,
        max_length=2,
        json_schema_extra={"position": 39},
        description="Varemottakers landkode, ISO 3166-1 alpha-2",
    )

    # --- Buyer address (Kjøperadresse) ---
    buyer_company_name: Optional[str] = Field(
        default=None,
        max_length=35,
        json_schema_extra={"position": 40},
        description="Kjøpers firmanavn",
    )
    buyer_address1: Optional[str] = Field(
        default=None,
        max_length=35,
        json_schema_extra={"position": 41},
        description="Kjøpers adresse1",
    )
    buyer_address2: Optional[str] = Field(
        default=None,
        max_length=35,
        json_schema_extra={"position": 42},
        description="Kjøpers adresse2",
    )
    buyer_postal_code: Optional[str] = Field(
        default=None,
        max_length=9,
        json_schema_extra={"position": 43},
        description="Kjøpers postnummer",
    )
    buyer_city: Optional[str] = Field(
        default=None,
        max_length=35,
        json_schema_extra={"position": 44},
        description="Kjøpers poststed",
    )
    buyer_country_code: Optional[str] = Field(
        default=None,
        max_length=2,
        json_schema_extra={"position": 45},
        description="Kjøpers landkode, ISO 3166-1 alpha-2",
    )
    buyer_contact_name: Optional[str] = Field(
        default=None,
        max_length=35,
        json_schema_extra={"position": 46},
        description="Kjøpers kontaktperson navn",
    )

    # --- Invoice recipient address (Fakturamottaker) ---
    invoice_recipient_name: str = Field(
        max_length=35,
        json_schema_extra={"position": 47},
        description="Fakturamottakers navn",
    )
    invoice_recipient_address1: Optional[str] = Field(
        default=None,
        max_length=35,
        json_schema_extra={"position": 48},
        description="Fakturamottakers adresse1",
    )
    invoice_recipient_address2: Optional[str] = Field(
        default=None,
        max_length=35,
        json_schema_extra={"position": 49},
        description="Fakturamottakers adresse2",
    )
    invoice_recipient_postal_code: str = Field(
        max_length=9,
        json_schema_extra={"position": 50},
        description="Fakturamottakers postnummer",
    )
    invoice_recipient_city: str = Field(
        max_length=35,
        json_schema_extra={"position": 51},
        description="Fakturamottakers poststed",
    )
    invoice_recipient_country_code: Optional[str] = Field(
        default=None,
        max_length=2,
        json_schema_extra={"position": 52},
        description="Fakturamottakers landkode, ISO 3166-1 alpha-2",
    )
    invoice_recipient_customer_number: Optional[str] = Field(
        default=None,
        max_length=10,
        json_schema_extra={"position": 53},
        description="Fakturamottakers kundenr oppgitt av selger",
    )

    # --- Banking details ---
    iban: Optional[str] = Field(
        default=None,
        max_length=15,
        json_schema_extra={"position": 54},
        description="Selgers IBAN-kode",
    )
    swift: Optional[str] = Field(
        default=None,
        max_length=15,
        json_schema_extra={"position": 55},
        description="Selgers BIC/SWIFT-kode",
    )

    @field_validator("invoice_date", "due_date", mode="before")
    @classmethod
    def validate_date(cls, value):
        """Parse date string from ÅÅÅÅMMDD format into a date object."""
        if isinstance(value, str):
            return date(int(value[:4]), int(value[4:6]), int(value[6:8]))
        return value

    @field_validator(
        "delivery_country_code",
        "buyer_country_code",
        "invoice_recipient_country_code",
        mode="before",
    )
    @classmethod
    def validate_country(cls, value):
        """Validate that country is a recognised ISO 3166-1 alpha-2 code."""
        if value and not pycountry.countries.get(alpha_2=value):
            raise ValueError(f"Invalid country code: {value}")
        return value

    @field_validator("currency_code", mode="before")
    @classmethod
    def validate_currency(cls, value):
        """Validate that currency is a recognised ISO 4217 currency code."""
        if value and not pycountry.currencies.get(alpha_3=value):
            raise ValueError(f"Invalid currency code: {value}")
        return value


class FL(NelfoBaseLineModel):
    """Faktura Linjepost (FL) — invoice line item.

    One or more per invoice, following the FF header. Each line represents
    a product or service delivered.

    Spec: EFO/NELFO Fakturaformat v4.0, Posttype FL.
    """

    post_type: str = Field(
        default="FL", init=False, max_length=2, json_schema_extra={"position": 1}
    )
    line_number: Optional[int] = Field(
        default=None,
        json_schema_extra={"position": 2},
        description="Linjenummer på faktura",
    )
    buyer_order_number: Optional[str] = Field(
        default=None,
        max_length=10,
        json_schema_extra={"position": 3},
        description="Kjøpers bestillingsnr, kun hvis avvik fra FF",
    )
    order_line_number: Optional[str] = Field(
        default=None,
        max_length=4,
        json_schema_extra={"position": 4},
        description="Referanse til linjenummer på bestilling",
    )
    item_type: int = Field(
        json_schema_extra={"position": 5},
        description="0=Ukjent, 1=Elnummer, 2=EAN, 3=Produsentnr, 4=NRF, 9=Tilleggsvare",
    )
    item_number: str = Field(
        max_length=14, json_schema_extra={"position": 6}, description="Produktnummer"
    )
    quantity: int = Field(
        json_schema_extra={"position": 7},
        description="Levert antall, alltid positivt, 2 desimaler uten desimaltegn",
    )
    price_unit: str = Field(
        max_length=3,
        json_schema_extra={"position": 8},
        description="Varens prisenhet, UN Common Code, e.g. 'EA', 'MTR'",
    )
    unit_price: int = Field(
        json_schema_extra={"position": 9},
        description="Pris pr. prisenhet, 2 desimaler uten desimaltegn",
    )
    vat_rate: int = Field(
        json_schema_extra={"position": 10},
        description="Mva-prosentsats, 2 desimaler uten desimaltegn, e.g. 2500 = 25.00%",
    )
    discount1_percent: Optional[int] = Field(
        default=None,
        json_schema_extra={"position": 11},
        description="Rabattsats 1 i prosent, 2 desimaler uten desimaltegn",
    )
    discount1_amount: Optional[int] = Field(
        default=None,
        json_schema_extra={"position": 12},
        description="Rabatt 1 i beløp, 2 desimaler uten desimaltegn",
    )
    discount2_percent: Optional[int] = Field(
        default=None,
        json_schema_extra={"position": 13},
        description="Rabattsats 2 i prosent, 2 desimaler uten desimaltegn",
    )
    discount2_amount: Optional[int] = Field(
        default=None,
        json_schema_extra={"position": 14},
        description="Rabatt 2 i beløp, 2 desimaler uten desimaltegn",
    )
    surcharge_percent: Optional[int] = Field(
        default=None,
        json_schema_extra={"position": 15},
        description="Tillegg i prosent, 2 desimaler uten desimaltegn",
    )
    surcharge_amount: Optional[int] = Field(
        default=None,
        json_schema_extra={"position": 16},
        description="Tilleggsbeløp, 2 desimaler uten desimaltegn",
    )
    tax_percent: Optional[int] = Field(
        default=None,
        json_schema_extra={"position": 17},
        description="Avgift i prosent, 2 desimaler uten desimaltegn",
    )
    tax_amount: Optional[int] = Field(
        default=None,
        json_schema_extra={"position": 18},
        description="Avgiftsbeløp, 2 desimaler uten desimaltegn",
    )
    line_amount: int = Field(
        json_schema_extra={"position": 19},
        description="Netto varelinjebeløp inkl. rabatter og tillegg, 2 desimaler uten desimaltegn",
    )
    buyer_item_number: Optional[str] = Field(
        default=None,
        max_length=25,
        json_schema_extra={"position": 20},
        description="Kjøpers varenummer",
    )
    item_description: Optional[str] = Field(
        default=None,
        max_length=30,
        json_schema_extra={"position": 21},
        description="Varebetegnelse",
    )
    item_description2: Optional[str] = Field(
        default=None,
        max_length=30,
        json_schema_extra={"position": 22},
        description="Utfyllende varetekst",
    )
    sign: Optional[Literal["+", "-"]] = Field(
        default=None,
        json_schema_extra={"position": 23},
        description="+ = positivt beløp, - = negativt beløp",
    )
    buyer_reference: Optional[str] = Field(
        default=None,
        max_length=25,
        json_schema_extra={"position": 24},
        description="Kjøpers referanse, kun hvis avvik fra FF",
    )
    packing_slip_number: Optional[str] = Field(
        default=None,
        max_length=8,
        json_schema_extra={"position": 25},
        description="Selgerens pakkseddelnummer, kun hvis avvik fra FF",
    )
    seller_warehouse_mark: Optional[Literal["E"]] = Field(
        default=None,
        json_schema_extra={"position": 26},
        description="E = EAN lokasjonsnummer brukt i SLager",
    )
    seller_warehouse: Optional[str] = Field(
        default=None,
        max_length=14,
        json_schema_extra={"position": 27},
        description="Selgers lager varen leveres fra",
    )

    @field_validator("item_type", mode="before")
    @classmethod
    def validate_item_type(cls, value):
        """Parse item_type from string and validate against allowed values."""
        if isinstance(value, str):
            value = int(value)
        if value not in (0, 1, 2, 3, 4, 9):
            raise ValueError(f"item_type must be one of 0, 1, 2, 3, 4, 9, got {value}")
        return value

    @field_validator(
        "line_number",
        "quantity",
        "unit_price",
        "vat_rate",
        "line_amount",
        "discount1_percent",
        "discount1_amount",
        "discount2_percent",
        "discount2_amount",
        "surcharge_percent",
        "surcharge_amount",
        "tax_percent",
        "tax_amount",
        mode="before",
    )
    @classmethod
    def parse_int_fields(cls, value):
        """Parse numeric fields from string to int."""
        if isinstance(value, str) and value:
            return int(value)
        return value


class FT(NelfoBaseLineModel):
    """Faktura Fritekstlinje (FT) — free text line.

    Optional free text associated with the preceding FL line, or with the
    entire invoice if placed directly after FF. Multiple FT records can
    follow a single FL.

    Spec: EFO/NELFO Fakturaformat v4.0, Posttype FT.
    """

    post_type: str = Field(
        default="FT", init=False, max_length=2, json_schema_extra={"position": 1}
    )
    free_text: Optional[str] = Field(
        default=None,
        max_length=30,
        json_schema_extra={"position": 2},
        description="Fri tekst",
    )


class FA(NelfoBaseLineModel):
    """Faktura Avslutningspost (FA) — invoice footer.

    One per invoice, always the last record before the next FF or FS.
    Contains the invoice number and optional record count for verification.

    Spec: EFO/NELFO Fakturaformat v4.0, Posttype FA.
    """

    post_type: str = Field(
        default="FA", init=False, max_length=2, json_schema_extra={"position": 1}
    )
    invoice_number: str = Field(
        max_length=8,
        json_schema_extra={"position": 2},
        description="Selgerens fakturanummer",
    )
    record_count: Optional[int] = Field(
        default=None,
        json_schema_extra={"position": 3},
        description="Sum poster i fakturaen inkl. fritekstlinjer og avslutningspost",
    )

    @field_validator("record_count", mode="before")
    @classmethod
    def parse_record_count(cls, value):
        """Parse record_count from string to int."""
        if isinstance(value, str) and value:
            return int(value)
        return value


class FS(NelfoBaseLineModel):
    """Faktura Sending Sluttpost (FS) — file trailer.

    One per file, always the last record. Contains the production date and
    optional invoice count for verification.

    Spec: EFO/NELFO Fakturaformat v4.0, Posttype FS.
    """

    post_type: str = Field(
        default="FS", init=False, max_length=2, json_schema_extra={"position": 1}
    )
    production_date: date = Field(
        json_schema_extra={"position": 2},
        description="Produksjonsdato for fil. Raw format: ÅÅÅÅMMDD",
    )
    invoice_count: Optional[int] = Field(
        default=None,
        json_schema_extra={"position": 3},
        description="Sum antall fakturaer i sendingen",
    )

    @field_validator("production_date", mode="before")
    @classmethod
    def validate_production_date(cls, value):
        """Parse date string from ÅÅÅÅMMDD format into a date object."""
        if isinstance(value, str):
            return date(int(value[:4]), int(value[4:6]), int(value[6:8]))
        return value

    @field_validator("invoice_count", mode="before")
    @classmethod
    def parse_invoice_count(cls, value):
        """Parse invoice_count from string to int."""
        if isinstance(value, str) and value:
            return int(value)
        return value


class NelfoInvoiceLine(BaseModel):
    "Represents a single line item in a Nelfo invoice, including optional free text lines."

    line: FL
    free_texts: list[FT] = Field(default_factory=list)

    @property
    def description(self) -> str | None:
        return self.line.item_description

    @property
    def quantity(self) -> Decimal:
        return Decimal(self.line.quantity) / 100

    @property
    def price(self) -> Decimal:
        return Decimal(self.line.unit_price) / 100

    @property
    def total(self) -> Decimal:
        return Decimal(self.line.line_amount) / 100


class NelfoInvoice(BaseModel):
    "Nelfo Faktura — represents a single invoice with header, lines, and optional free text and footer."

    header: FF
    lines: list[NelfoInvoiceLine] = Field(default_factory=list)
    trailer: Optional[FA] = None

    @property
    def total(self) -> Decimal:
        return Decimal(self.header.invoice_total) / 100

    @property
    def net_amount(self) -> Decimal:
        return Decimal(self.header.net_amount_pre_tax) / 100

    @property
    def vat_amount(self) -> Decimal:
        return Decimal(self.header.vat_amount) / 100

    @property
    def invoice_number(self) -> str:
        return str(self.header.invoice_number)

    @property
    def is_credit_note(self) -> bool:
        return self.header.document_sign == "-"

    @property
    def line_count(self) -> int:
        return int(len(self.lines))

    def __repr__(self):
        return f"NelfoInvoice({self.header.invoice_number})"


class NelfoFile(BaseModel):
    "Nelfo Fakturafil — represents an entire invoice file with header, lines, and trailer."

    header: FH
    body: list[NelfoInvoice]
    trailer: FS

    def to_json(self, filename):
        with open(filename, "w") as f:
            f.write(self.model_dump_json(indent=2))

    @property
    def invoice_numbers(self) -> list[str]:
        return [invoice.invoice_number for invoice in self.body]

    @property
    def invoices(self) -> list[NelfoInvoice]:
        return self.body

    @property
    def file_invoice_count(self):
        return len(self.body)

    @property
    def regular_invoices(self) -> list[NelfoInvoice]:
        return [inv for inv in self.body if not inv.is_credit_note]

    @property
    def credit_notes(self) -> list[NelfoInvoice]:
        return [inv for inv in self.body if inv.is_credit_note]

    def get_invoice(self, invoice_number: str) -> NelfoInvoice | None:
        return next(
            (
                invoice
                for invoice in self.body
                if invoice.invoice_number == invoice_number
            ),
            None,
        )
