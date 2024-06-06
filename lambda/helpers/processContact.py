from dataclasses import dataclass, field
import re
from datetime import datetime
from jinja2 import Template

def validate_name(name: str) -> None:
    if not isinstance(name, str):
        raise TypeError("Name must be a string")
    if len(name) == 0 or len(name) > 200:
        raise ValueError("Name must be non-empty and less than 200 characters")

def validate_email_address(email: str) -> None:
    if not isinstance(email, str):
        raise TypeError("Email address must be a string")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Invalid email address")

def validate_message(message: str) -> None:
    if not isinstance(message, str):
        raise TypeError("Message must be a string")
    if len(message) > 4000:
        raise ValueError("Message must be 4000 characters or less")

def validate_form_type(form_type: str) -> None:
    if form_type != "contact":
        raise ValueError("Form type must be 'contact'")

# ContactData class using the validation functions
@dataclass
class ContactData:
    name: str
    emailAddress: str
    formType: str
    message: str
    captchaToken: str
    _datetime: datetime = field(init=False, repr=False)

    def __post_init__(self):
        self._datetime = datetime.now() 
        validate_name(self.name)
        validate_email_address(self.emailAddress)
        validate_form_type(self.formType)
        validate_message(self.message)

    @property
    def datetime(self):
        return self._datetime

def get_contact_template():
    return """<!DOCTYPE html>
    <html>
    <head>
        <title>Contact Form Submission</title>
    </head>
    <body>
        <h1>New Contact Request</h1>
        <p><strong>Name:</strong> {{ name }}</p>
        <p><strong>Time:</strong> {{ datetime }}</p>
        <p><strong>Email Address:</strong> {{ emailAddress }}</p>
        <p><strong>Form Type:</strong> {{ formType }}</p>
        <p><strong>Message:</strong> {{ message }}</p>
    </body>
    </html>
    """
    
def get_contact_body(contact_data: ContactData, template_string: str) -> str:
    template = Template(template_string)
    rendered_html = template.render(
        name=contact_data.name,
        datetime=contact_data.datetime.strftime("%Y-%m-%d %H:%M:%S"),
        emailAddress=contact_data.emailAddress,
        formType=contact_data.formType,
        message=contact_data.message
    )
    
    return rendered_html
