from dataclasses import dataclass, field
import re
from datetime import datetime
from typing import List, Tuple
from jinja2 import Template
import os


def validate_business_name(name: str) -> None:
    if not isinstance(name, str):
        raise TypeError("Business name must be a string")
    if len(name) == 0 or len(name) > 75:
        raise ValueError("Business name must be non-empty and less than 75 characters")

def validate_email_address(email: str) -> None:
    if not isinstance(email, str):
        raise TypeError("Email address must be a string")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Invalid email address")

def validate_form_type(form_type: str) -> None:
    if form_type != "quote":
        raise ValueError("Form type must be 'quote'")

def validate_industry_name(name: str) -> None:
    if len(name) > 100:
        raise ValueError("Industry name must be less than 50 characters")

def validate_phone_number(number: str) -> None:
    if not re.match(r"\+?\d[\d -]{8,}\d", number):
        raise ValueError("Invalid phone number")

def validate_selectboxes_and_other_service(selectboxes: str, other_service: str) -> List[str]:
    services = []
    if selectboxes:
        if selectboxes.split(',') != "":
            services.extend(selectboxes.split(','))
        if other_service:

            services.append(other_service)
        if not (0 < len(services) <= 6) or any(len(s) > 50 for s in services):
            raise ValueError("Selectboxes must have 1 to 6 items, each up to 30 characters")
    else:
        services = []
        if other_service:
            services.append(other_service)

    
    return services


def validate_zip_code(zip_code: str) -> None:
    if not re.match(r"^\d{5}(?:[-\s]\d{4})?$", zip_code):
        raise ValueError("Invalid zip code")

# Updated QuoteData class using the validation functions
@dataclass
class QuoteData:
    businessName: str
    emailAddress: str
    formType: str
    industryName: str
    otherService: str
    phoneNumber: str
    captchaToken: str
    selectboxes: str
    zipCode: str
    _services: List[str] = field(init=False, repr=False)
    _datetime: datetime = field(init=False, repr=False)

    def __post_init__(self):
        self._datetime = datetime.now() 
        validate_business_name(self.businessName)
        validate_email_address(self.emailAddress)
        validate_form_type(self.formType)
        validate_industry_name(self.industryName)
        validate_phone_number(self.phoneNumber)
        self._services = validate_selectboxes_and_other_service(self.selectboxes, self.otherService)
        validate_zip_code(self.zipCode)

    @property
    def datetime(self):
        return self._datetime

    @property
    def services(self):
        return self._services

def get_quote_template():
    return """<!DOCTYPE html>
    <html>
    <head>
        <title>Quote Form Submission</title>
    </head>
    <body>
        <h1>New Quote Request</h1>
        <p><strong>Business Name:</strong> {{ businessName }}</p>
        <p><strong>Time:</strong> {{ datetime }}</p>
        <p><strong>Email Address:</strong> {{ emailAddress }}</p>
        <p><strong>Form Type:</strong> {{ formType }}</p>
        <p><strong>Industry:</strong> {{ industryName }}</p>
        <p><strong>Phone Number:</strong> {{ phoneNumber }}</p>
        <p><strong>Services:</strong> {{ services }}</p>
        <p><strong>Zip Code:</strong> {{ zipCode }}</p>
    </body>
    </html>
    """
    
    
def get_quote_body(quote_data: QuoteData, template_string: str) -> str:
    # Use the template string directly
    template = Template(template_string)

    # Render the template with your class instance
    rendered_html = template.render(
        businessName=quote_data.businessName,
        datetime=quote_data.datetime.strftime("%Y-%m-%d %H:%M:%S"),
        emailAddress=quote_data.emailAddress,
        formType=quote_data.formType,
        industryName=quote_data.industryName,
        phoneNumber=quote_data.phoneNumber,
        services=', '.join(quote_data.services),
        zipCode=quote_data.zipCode
    )
    
    return rendered_html
