import unittest

from helpers.validations import valid_formType

class TestValidFormType(unittest.TestCase):

    # Test cases where the function is expected to return True
    def test_valid_contact_formType(self):
        self.assertTrue(valid_formType({'formType': 'contact'}))

    def test_valid_quote_formType(self):
        self.assertTrue(valid_formType({'formType': 'quote'}))

    # Test cases where the function is expected to return False
    def test_invalid_formType_value(self):
        self.assertFalse(valid_formType({'formType': 'invalid'}))

    def test_formType_key_missing(self):
        self.assertFalse(valid_formType({'otherKey': 'value'}))

    def test_empty_body(self):
        self.assertFalse(valid_formType({}))

    def test_non_dict_input(self):
        self.assertFalse(valid_formType("not a dict"))

    def test_none_input(self):
        self.assertFalse(valid_formType(None))

    def test_list_input(self):
        self.assertFalse(valid_formType(["not", "a", "dict"]))

    def test_numeric_formType(self):
        self.assertFalse(valid_formType({'formType': 12345}))

    def test_null_formType(self):
        self.assertFalse(valid_formType({'formType': None}))

if __name__ == '__main__':
    unittest.main()
