import unittest

from helpers.processQuote import validate_email_address

class TestValidateEmailAddress(unittest.TestCase):

    # Passing Test 1: Valid email
    def test_valid_email(self):
        self.assertIsNone(validate_email_address("example@example.com"))

    # Passing Test 2: Another valid email
    def test_another_valid_email(self):
        self.assertIsNone(validate_email_address("user123@domain.co.uk"))

    # Passing Test 3: Email with subdomain
    def test_email_with_subdomain(self):
        self.assertIsNone(validate_email_address("user.name@sub.domain.com"))

    # Failing Test 1: Email without @ symbol
    def test_email_without_at(self):
        with self.assertRaises(ValueError):
            validate_email_address("example.com")

    # Failing Test 2: Email without domain part
    def test_email_without_domain(self):
        with self.assertRaises(ValueError):
            validate_email_address("user123@")

    # Failing Test 3: Non-string input
    def test_non_string_email(self):
        with self.assertRaises(TypeError):
            validate_email_address(12345)

    # Failing Test 4: Empty string
    def test_empty_string(self):
        with self.assertRaises(ValueError):
            validate_email_address("")

if __name__ == "__main__":
    unittest.main()
