import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from helpers.contact import ContactData, ContactValidationError
import main


client = TestClient(main.app)


def api_gateway_event(method: str, path: str, body: dict | None = None) -> dict:
    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": path,
        "rawQueryString": "",
        "headers": {
            "content-type": "application/json",
            "host": "api.wdwebsolutions.com",
        },
        "requestContext": {
            "accountId": "123",
            "apiId": "api",
            "domainName": "api.wdwebsolutions.com",
            "domainPrefix": "api",
            "http": {
                "method": method,
                "path": path,
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "test",
            },
            "requestId": "request",
            "routeKey": "$default",
            "stage": "$default",
            "time": "27/Apr/2026:00:00:00 +0000",
            "timeEpoch": 0,
        },
        "isBase64Encoded": False,
        "body": json.dumps(body) if body is not None else None,
    }


def lambda_context() -> SimpleNamespace:
    return SimpleNamespace(
        function_name="test",
        function_version="$LATEST",
        invoked_function_arn="arn:aws:lambda:us-east-1:123:function:test",
        memory_limit_in_mb=128,
        aws_request_id="test-request",
        log_group_name="/aws/lambda/test",
        log_stream_name="test",
    )


class ContactHandlerTests(unittest.TestCase):
    def test_valid_contact_submission_returns_success(self):
        with patch("main.send_email") as send_email:
            response = client.post(
                "/contact",
                json={
                    "name": "Derek",
                    "emailAddress": "derekd@wdwebsolutions.com",
                    "message": "I need a website.",
                    "formType": "contact",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Your request has been sent.")
        send_email.assert_called_once()

    def test_api_contact_route_returns_success(self):
        with patch("main.send_email") as send_email:
            response = client.post(
                "/api/contact",
                json={
                    "name": "Derek",
                    "emailAddress": "derekd@wdwebsolutions.com",
                    "message": "I need a website.",
                    "formType": "contact",
                },
            )

        self.assertEqual(response.status_code, 200)
        send_email.assert_called_once()

    def test_invalid_email_returns_400(self):
        response = client.post(
            "/contact",
            json={
                "name": "Derek",
                "emailAddress": "not-an-email",
                "message": "I need a website.",
                "formType": "contact",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("emailAddress", response.json()["message"])

    def test_non_contact_path_returns_404(self):
        response = client.post("/not-found", json={})

        self.assertEqual(response.status_code, 404)

    def test_health_route_returns_ok(self):
        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_lambda_handler_remains_compatible_with_pulumi_config(self):
        response = main.main(
            api_gateway_event(
                "POST",
                "/contact",
                {
                    "name": "Derek",
                    "emailAddress": "not-an-email",
                    "message": "I need a website.",
                    "formType": "contact",
                },
            ),
            lambda_context(),
        )

        self.assertEqual(response["statusCode"], 400)
        self.assertIn("emailAddress", json.loads(response["body"])["message"])

    def test_contact_data_requires_contact_form_type(self):
        with self.assertRaises(ContactValidationError):
            ContactData(
                name="Derek",
                emailAddress="derekd@wdwebsolutions.com",
                message="Hello",
                formType="support",
            )


if __name__ == "__main__":
    unittest.main()
