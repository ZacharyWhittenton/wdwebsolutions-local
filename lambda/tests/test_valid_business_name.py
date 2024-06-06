import unittest

from helpers.processQuote import validate_business_name


class TestValidateBusinessName(unittest.TestCase):

    # Passing Test 1: Test with a valid name
    def test_valid_name(self):
        self.assertIsNone(validate_business_name("My Business"))

    # Passing Test 2: Test with a valid name exactly 75 characters long
    def test_valid_name_exact_length(self):
        self.assertIsNone(validate_business_name("a" * 75))

    # Passing Test 3: Test with a valid name that is not empty
    def test_valid_name_non_empty(self):
        self.assertIsNone(validate_business_name("B"))

    # Failing Test 1: Test with an empty string
    def test_invalid_name_empty(self):
        with self.assertRaises(ValueError):
            validate_business_name("")

    # Failing Test 2: Test with a name longer than 75 characters
    def test_invalid_name_long(self):
        with self.assertRaises(ValueError):
            validate_business_name("a" * 76)

    # Failing Test 3: Test with a non-string input
    def test_invalid_type(self):
        with self.assertRaises(TypeError):
            validate_business_name(12345)
            
    # Failing Test 4: Test with a non-string input
    def test_invalid_type_list(self):
        with self.assertRaises(TypeError):
            validate_business_name(["12345","hello 123"])