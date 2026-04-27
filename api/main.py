import json
import os
from pathlib import Path
from typing import Any

import boto3
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum
from pydantic import BaseModel, ConfigDict

from helpers.contact import ContactData, ContactValidationError, render_contact_email


DEFAULT_CORS_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "https://dev.wdwebsolutions.com",
    "https://wdwebsolutions.com",
    "https://www.wdwebsolutions.com",
]


def load_cors_origins() -> list[str]:
    configured_origins = os.environ.get("CONTACT_ALLOWED_ORIGINS")
    if configured_origins:
        return [
            origin.strip()
            for origin in configured_origins.split(",")
            if origin.strip()
        ]

    return DEFAULT_CORS_ORIGINS


class ContactRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = ""
    emailAddress: str = ""
    message: str = ""
    formType: str = "contact"
    company: str | None = None
    phone: str | None = None


class ContactResponse(BaseModel):
    message: str


app = FastAPI(
    title="WD Web Solutions Contact API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=load_cors_origins(),
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


def load_config() -> dict:
    config_file = os.environ.get("ENVIRONMENT_CONFIG", "prod.config.json")
    config_path = Path(__file__).with_name(config_file)

    if config_path.exists():
        with config_path.open() as file:
            config = json.load(file)
    else:
        config = {}

    source_email = os.environ.get("CONTACT_SOURCE_EMAIL")
    recipients = os.environ.get("CONTACT_RECIPIENTS")

    if source_email:
        config["source_email"] = source_email

    if recipients:
        config["output_emails"] = [
            email.strip() for email in recipients.split(",") if email.strip()
        ]

    config.setdefault("source_email", "no-reply@wdwebsolutions.com")
    config.setdefault("output_emails", ["derekd@wdwebsolutions.com"])
    config.setdefault("ses_region", os.environ.get("AWS_REGION", "us-east-1"))
    config.setdefault("send_email", True)
    return config


def send_email(
    subject: str,
    email_body: str,
    config: dict,
    reply_to: str | None = None,
) -> None:
    if not config.get("send_email", True):
        print(f"Skipping SES send in local mode. Subject: {subject}")
        return

    recipients = config["output_emails"]
    if isinstance(recipients, str):
        recipients = [recipients]

    ses_client = boto3.client("ses", region_name=config["ses_region"])
    response = ses_client.send_email(
        Source=config["source_email"],
        Destination={"ToAddresses": recipients},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Html": {"Data": email_body}},
        },
        ReplyToAddresses=[reply_to or config["source_email"]],
    )
    print("Contact email sent", response.get("MessageId"))


def contact_from_payload(payload: ContactRequest | dict[str, Any]) -> ContactData:
    form_data = payload.model_dump() if isinstance(payload, ContactRequest) else payload

    if not isinstance(form_data, dict):
        raise ContactValidationError("Request body must be a JSON object")

    return ContactData(
        name=form_data.get("name", ""),
        emailAddress=form_data.get("emailAddress", ""),
        message=form_data.get("message", ""),
        formType=form_data.get("formType", "contact"),
        company=form_data.get("company") or None,
        phone=form_data.get("phone") or None,
    )


def process_contact_payload(payload: ContactRequest | dict[str, Any]) -> dict[str, str]:
    contact = contact_from_payload(payload)
    email_body = render_contact_email(contact)
    subject = f"New WD Web Solutions contact request from {contact.emailAddress}"
    send_email(subject, email_body, load_config(), reply_to=contact.emailAddress)
    return {"message": "Your request has been sent."}


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    print(f"Request validation error on {request.url.path}: {error}")
    return JSONResponse(
        status_code=400,
        content={"message": "Request body must be a JSON object"},
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


def submit_contact_payload(payload: ContactRequest) -> ContactResponse | JSONResponse:
    try:
        return ContactResponse(**process_contact_payload(payload))
    except ContactValidationError as error:
        print(f"Contact validation error: {error}")
        return JSONResponse(status_code=400, content={"message": str(error)})
    except Exception as error:
        print(f"Unexpected contact handler error: {error}")
        return JSONResponse(
            status_code=500,
            content={"message": "An error occurred while sending your request."},
        )


@app.post("/contact", response_model=ContactResponse)
def submit_contact(payload: ContactRequest) -> ContactResponse | JSONResponse:
    return submit_contact_payload(payload)


@app.post("/api/contact", response_model=ContactResponse)
def submit_api_contact(payload: ContactRequest) -> ContactResponse | JSONResponse:
    return submit_contact_payload(payload)


handler = Mangum(app)
main = handler
