from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import pycountry

class FH(BaseModel):
    """Faktura Sending Hodepost (FH) — file-level header.

    One per file, always the first record. Identifies the sender and the
    format version for all invoices that follow.

    Spec: EFO/NELFO Fakturaformat v4.0, Posttype FH.
    """

    post_type: str = Field(default="FH", init=False, max_length=2)
    doc_format: str = Field(default="EFONELFO", init=False, max_length=8)
    version: str = Field(default="4.0", init=False, max_length=3)
    sellers_id: str = Field(max_length=14, description="Selgers foretaksnummer, e.g. 'NO123456789MVA'")
    prod_date: date = Field(description="Produksjonsdato. Raw format: ÅÅÅÅMMDD")
    company_name: str = Field(max_length=35, description="Selgers firmanavn")
    address1: Optional[str] = Field(default=None, max_length=35, description="Selgers adresse1")
    address2: Optional[str] = Field(default=None, max_length=35, description="Selgers adresse2")
    postnr: str = Field(max_length=9, description="Selgers postnummer")
    post_place: str = Field(max_length=35, description="Selgers poststed")
    country: Optional[str] = Field(default=None, max_length=2, description="Selgers landkode, ISO 3166-1 alpha-2, e.g. 'NO'")

    @field_validator("prod_date", mode="before")
    @classmethod
    def validate_prod_date(cls, value):
        """Parse date string from ÅÅÅÅMMDD format into a date object."""
        if isinstance(value, str):
            return date(int(value[:4]), int(value[4:6]), int(value[6:8]))
        return value

    @field_validator("country", mode="before")
    @classmethod
    def validate_country(cls, value):
        """Validate that country is a recognised ISO 3166-1 alpha-2 code."""
        if value and not pycountry.countries.get(alpha_2=value):
            raise ValueError(f"Invalid country code: {value}")
        return value
