import unittest

from helpers.validations import body_in_event


class TestBodyInEvent(unittest.TestCase):

    # Passing Test Cases

    def test_with_body(self):
        event = {"body": "some data"}
        self.assertTrue(body_in_event(event))

    def test_empty_body(self):
        event = {"body": ""}
        self.assertTrue(body_in_event(event))

    def test_with_body_and_other_keys(self):
        event = {"body": "data", "other_key": "value"}
        self.assertTrue(body_in_event(event))

    def test_with_null_body(self):
        event = {"body": None}
        self.assertTrue(body_in_event(event))
        
    def test_with_numeric_body(self):
        event = {"body": 12345}
        self.assertTrue(body_in_event(event))

    # Failing Test Cases

    def test_with_no_body(self):
        event = {"no_body": "data"}
        self.assertFalse(body_in_event(event))

    def test_non_dict_input(self):
        event = "not a dict"
        self.assertFalse(body_in_event(event))

    def test_none_input(self):
        event = None
        self.assertFalse(body_in_event(event))

    def test_list_input(self):
        event = ["not", "a", "dict"]
        self.assertFalse(body_in_event(event))
        
    def test_empty_event(self):
        event = {}
        self.assertFalse(body_in_event(event))

    

if __name__ == '__main__':
    unittest.main()
