from datetime import datetime
import unittest

from helpers.processQuote import QuoteData

class TestQuoteData(unittest.TestCase):

    def test_quote_data_valid(self):
        """Test QuoteData with valid data."""
        try:
            valid_quote = QuoteData(
                businessName="Valid Business",
                emailAddress="valid@example.com",
                formType="quote",
                industryName="Retail",
                otherService="Additional Service",
                phoneNumber="+1234567890",
                captchaToken="valid_token",
                selectboxes="Service1,Service2",
                zipCode="12345"
            )
            self.assertIsInstance(valid_quote, QuoteData)
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")

    def test_invalid_business_name(self):
        """Test QuoteData with invalid business names."""
        with self.assertRaises(Exception):
            QuoteData(
                businessName="",
                # ... other valid fields
            )
        with self.assertRaises(Exception):
            QuoteData(
                businessName=123,
                # ... other valid fields
            )
        # ... further test cases

    def test_invalid_email_address(self):
        """Test QuoteData with invalid email addresses."""
        with self.assertRaises(Exception):
            QuoteData(
                emailAddress="invalidemail",
                # ... other valid fields
            )
        # ... further test cases

    # Add similar tests for other fields (formType, industryName, phoneNumber, etc.)

if __name__ == '__main__':
    unittest.main()