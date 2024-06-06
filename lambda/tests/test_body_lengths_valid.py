import unittest

from helpers.validations import body_lengths_valid


class TestBodyLengthsValid(unittest.TestCase):

    def test_empty_dict(self):
        self.assertTrue(body_lengths_valid({}))

    def test_valid_string(self):
        self.assertTrue(body_lengths_valid({"key": "short string"}))

    def test_valid_list(self):
        self.assertTrue(body_lengths_valid({"key": ["one", "two", "three", "four", "five"]}))

    def test_string_too_long(self):
        self.assertFalse(body_lengths_valid({"key": "a" * 200}))

    def test_list_too_long(self):
        self.assertFalse(body_lengths_valid({"key": ["a"] * 6}))

    def test_item_in_list_too_long(self):
        self.assertFalse(body_lengths_valid({"key": ["a" * 50]}))

    def test_invalid_non_string_key(self):
        self.assertFalse(body_lengths_valid({123: "valid string"}))

    def test_key_too_long(self):
        self.assertFalse(body_lengths_valid({"a" * 50: "valid string"}))

    def test_invalid_value_type(self):
        self.assertFalse(body_lengths_valid({"key": 123}))

    def test_mixed_valid_invalid(self):
        self.assertFalse(body_lengths_valid({"validKey": "valid string", "invalidKey": 123}))

    def test_all_valid_conditions(self):
        self.assertTrue(body_lengths_valid({
            "key1": "valid string",
            "key2": ["one", "two"],
            "key3": "another valid string"
        }))

if __name__ == '__main__':
    unittest.main()
