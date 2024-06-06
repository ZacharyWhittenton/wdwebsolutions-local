import unittest
from helpers.processQuote import QuoteData, get_quote_body, get_quote_template


class TestGetQuoteBody(unittest.TestCase):

    def test_correct_rendering(self):
        # Create a QuoteData instance with test data
        quote_data = QuoteData(
            businessName="Test Business",
            emailAddress="test@example.com",
            formType="quote",
            industryName="Technology",
            otherService="None",
            phoneNumber="1234567890",
            captchaToken="token",
            selectboxes="Service1,Service2",
            zipCode="12345"
        )

        template_string = get_quote_template()
        rendered_html = get_quote_body(quote_data, template_string)

        # Check if the result contains the expected data
        self.assertIn("Test Business", rendered_html)
        self.assertIn("test@example.com", rendered_html)
        self.assertIn("Technology", rendered_html)
        self.assertIn("1234567890", rendered_html)
        self.assertIn("Service1, Service2", rendered_html)
        self.assertIn("12345", rendered_html)

# This allows running the tests from the command line
if __name__ == '__main__':
    unittest.main()
