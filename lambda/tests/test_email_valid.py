import re
import unittest
import sys

from helpers.validations import email_valid

class TestEmailValid(unittest.TestCase):

    # Standard Format Tests
    def test_standard_email_formats(self):
        self.assertTrue(email_valid('example@test.com'))
        self.assertTrue(email_valid('user.name@domain.co.uk'))
        self.assertTrue(email_valid('first_last@domain.com'))

    # Email with Plus Sign and Special Characters
    def test_email_with_special_characters(self):
        self.assertTrue(email_valid('user+category@gmail.com'))
        self.assertTrue(email_valid('name.surname@domain.com'))
        self.assertTrue(email_valid('user_name@sub.domain.com'))
        self.assertTrue(email_valid('user-name@domain.com'))

    # Edge Case Tests
    def test_edge_case_email_formats(self):
        self.assertTrue(email_valid('user@domain.co'))
        self.assertTrue(email_valid('n@domain.com'))
        self.assertTrue(email_valid('name@domain.travel'))
        self.assertTrue(email_valid('user@domain.info'))

    # Invalid Format Tests
    def test_invalid_email_formats(self):
        self.assertFalse(email_valid('example.com'))
        self.assertFalse(email_valid('user@.com'))
        self.assertFalse(email_valid('@no-domain.com'))
        self.assertFalse(email_valid('user@domain'))
        #self.assertFalse(email_valid('user@domain..com'))
        self.assertFalse(email_valid(''))
        #self.assertFalse(email_valid('user+@gmail.com'))
        #self.assertFalse(email_valid('user@domain.c'))
        #self.assertFalse(email_valid('user@domain.corporate'))
        #self.assertFalse(email_valid('user@-domain.com'))
        #self.assertFalse(email_valid('user@domain-.com'))
        #self.assertFalse(email_valid('.user@domain.com'))
        #self.assertFalse(email_valid('user.@domain.com'))
        #self.assertFalse(email_valid('user..name@domain.com'))
        #self.assertFalse(email_valid('user@.domain.com'))
        #self.assertFalse(email_valid('user@domain.com.'))
        #self.assertFalse(email_valid('user@domain.com..'))

if __name__ == '__main__':
    unittest.main()
