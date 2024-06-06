import unittest
from helpers.processQuote import validate_selectboxes_and_other_service

class TestValidateSelectboxesAndOtherService(unittest.TestCase):

    def test_single_valid_selectbox(self):
        self.assertEqual(validate_selectboxes_and_other_service("Service1", ""), ["Service1"])

    def test_multiple_valid_selectboxes(self):
        self.assertEqual(validate_selectboxes_and_other_service("Service1,Service2,Service3", ""), ["Service1", "Service2", "Service3"])

    def test_max_allowed_selectboxes(self):
        self.assertEqual(validate_selectboxes_and_other_service("S1,S2,S3,S4,S5,S6", ""), ["S1", "S2", "S3", "S4", "S5", "S6"])

    def test_valid_selectboxes_with_other_service(self):
        self.assertEqual(validate_selectboxes_and_other_service("Service1,Service2", "Service3"), ["Service1", "Service2", "Service3"])

    def test_more_than_six_selectboxes(self):
        with self.assertRaises(ValueError):
            validate_selectboxes_and_other_service("S1,S2,S3,S4,S5,S6,S7", "")

    def test_selectbox_exceeds_max_length(self):
        with self.assertRaises(ValueError):
            validate_selectboxes_and_other_service("a" * 51, "")

    def test_multiple_selectboxes_with_one_exceeding_max_length(self):
        with self.assertRaises(ValueError):
            validate_selectboxes_and_other_service("Service1,Service2," + "a" * 51, "")

    def test_single_selectbox_with_empty_other_service(self):
        self.assertEqual(validate_selectboxes_and_other_service("Service1", ""), ["Service1"])

    def test_empty_selectboxes_with_valid_other_service(self):
        self.assertEqual(validate_selectboxes_and_other_service("", "Service1"), ["Service1"])

    def test_valid_selectbox_with_exceeding_other_service(self):
        with self.assertRaises(ValueError):
            validate_selectboxes_and_other_service("Service1", "a" * 51)

if __name__ == '__main__':
    unittest.main()
