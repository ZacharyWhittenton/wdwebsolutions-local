import base64
import json
import os
from pathlib import Path
from typing import Any

import boto3

from helpers.contact import ContactData, ContactValidationError, render_contact_email


DEFAULT_HEADERS = {
    "Content-Type": "application/json",
}


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


def make_response(status_code: int, body: dict[str, Any]) -> dict:
    return {
        "statusCode": status_code,
        "headers": DEFAULT_HEADERS,
        "body": json.dumps(body),
    }


def parse_event_body(event: dict[str, Any]) -> dict[str, Any]:
    body = event.get("body", event)

    if event.get("isBase64Encoded") and isinstance(body, str):
        body = base64.b64decode(body).decode("utf-8")

    if isinstance(body, str):
        return json.loads(body or "{}")

    if isinstance(body, dict):
        return body

    raise ContactValidationError("Request body must be a JSON object")


def request_method(event: dict[str, Any]) -> str:
    return (
        event.get("requestContext", {})
        .get("http", {})
        .get("method", event.get("httpMethod", "POST"))
        .upper()
    )


def request_path(event: dict[str, Any]) -> str:
    return event.get("rawPath") or event.get("path") or "/contact"


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


def handle_contact(event: dict[str, Any]) -> dict:
    form_data = parse_event_body(event)
    contact = ContactData(
        name=form_data.get("name", ""),
        emailAddress=form_data.get("emailAddress", ""),
        message=form_data.get("message", ""),
        formType=form_data.get("formType", "contact"),
        company=form_data.get("company") or None,
        phone=form_data.get("phone") or None,
    )
    email_body = render_contact_email(contact)
    subject = f"New WD Web Solutions contact request from {contact.emailAddress}"
    send_email(subject, email_body, load_config(), reply_to=contact.emailAddress)
    return make_response(200, {"message": "Your request has been sent."})


def main(event, context):
    try:
        method = request_method(event)
        path = request_path(event).rstrip("/")

        if method == "OPTIONS":
            return make_response(204, {})

        if method != "POST" or path not in {"/contact", "/api/contact"}:
            return make_response(404, {"message": "Not found"})

        return handle_contact(event)
    except ContactValidationError as error:
        print(f"Contact validation error: {error}")
        return make_response(400, {"message": str(error)})
    except json.JSONDecodeError:
        return make_response(400, {"message": "Request body must be valid JSON"})
    except Exception as error:
        print(f"Unexpected contact handler error: {error}")
        return make_response(
            500,
            {"message": "An error occurred while sending your request."},
        )


handler = main
