from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import re

from jinja2 import Environment, FileSystemLoader, select_autoescape


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ContactValidationError(ValueError):
    pass


def _validate_text(name: str, value: str, max_length: int) -> str:
    if not isinstance(value, str):
        raise ContactValidationError(f"{name} must be a string")

    clean_value = value.strip()
    if not clean_value:
        raise ContactValidationError(f"{name} is required")

    if len(clean_value) > max_length:
        raise ContactValidationError(f"{name} must be {max_length} characters or less")

    return clean_value


def validate_email_address(email_address: str) -> str:
    clean_email = _validate_text("emailAddress", email_address, 254)
    if not EMAIL_PATTERN.match(clean_email):
        raise ContactValidationError("emailAddress must be a valid email address")
    return clean_email


@dataclass
class ContactData:
    name: str
    emailAddress: str
    message: str
    formType: str = "contact"
    company: str | None = None
    phone: str | None = None
    _submitted_at: datetime = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._submitted_at = datetime.now(timezone.utc)
        self.name = _validate_text("name", self.name, 200)
        self.emailAddress = validate_email_address(self.emailAddress)
        self.message = _validate_text("message", self.message, 4000)

        if self.formType != "contact":
            raise ContactValidationError("formType must be contact")

        if self.company:
            self.company = _validate_text("company", self.company, 200)

        if self.phone:
            self.phone = _validate_text("phone", self.phone, 40)

    @property
    def submitted_at(self) -> datetime:
        return self._submitted_at


def render_contact_email(contact_data: ContactData) -> str:
    templates_dir = Path(__file__).resolve().parents[1] / "templates"
    environment = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = environment.get_template("contact_email.html")
    return template.render(contact=contact_data)
