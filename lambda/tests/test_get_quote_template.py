import unittest

from helpers.processQuote import get_quote_template


class TestGetQuoteTemplate(unittest.TestCase):
    
    def test_template_format(self):
        template = get_quote_template()

        # Check if the template contains expected placeholders
        self.assertIn("{{ businessName }}", template)
        self.assertIn("{{ datetime }}", template)
        self.assertIn("{{ emailAddress }}", template)
        self.assertIn("{{ formType }}", template)
        self.assertIn("{{ industryName }}", template)
        self.assertIn("{{ phoneNumber }}", template)
        self.assertIn("{{ services }}", template)
        self.assertIn("{{ zipCode }}", template)

# This allows running the tests from the command line
if __name__ == '__main__':
    unittest.main()
