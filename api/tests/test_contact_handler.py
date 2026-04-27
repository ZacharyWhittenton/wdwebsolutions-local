import json
import unittest
from unittest.mock import patch

from helpers.contact import ContactData, ContactValidationError
import main


class ContactHandlerTests(unittest.TestCase):
    def test_valid_contact_submission_returns_success(self):
        event = {
            "rawPath": "/contact",
            "body": json.dumps(
                {
                    "name": "Derek",
                    "emailAddress": "derekd@wdwebsolutions.com",
                    "message": "I need a website.",
                    "formType": "contact",
                }
            ),
            "requestContext": {"http": {"method": "POST"}},
        }

        with patch("main.send_email") as send_email:
            response = main.main(event, None)

        self.assertEqual(response["statusCode"], 200)
        send_email.assert_called_once()

    def test_invalid_email_returns_400(self):
        event = {
            "rawPath": "/contact",
            "body": json.dumps(
                {
                    "name": "Derek",
                    "emailAddress": "not-an-email",
                    "message": "I need a website.",
                    "formType": "contact",
                }
            ),
            "requestContext": {"http": {"method": "POST"}},
        }

        response = main.main(event, None)

        self.assertEqual(response["statusCode"], 400)
        self.assertIn("emailAddress", json.loads(response["body"])["message"])

    def test_non_contact_path_returns_404(self):
        response = main.main(
            {
                "rawPath": "/health",
                "body": "{}",
                "requestContext": {"http": {"method": "POST"}},
            },
            None,
        )

        self.assertEqual(response["statusCode"], 404)

    def test_contact_data_requires_contact_form_type(self):
        with self.assertRaises(ContactValidationError):
            ContactData(
                name="Derek",
                emailAddress="derekd@wdwebsolutions.com",
                message="Hello",
                formType="quote",
            )


if __name__ == "__main__":
    unittest.main()
