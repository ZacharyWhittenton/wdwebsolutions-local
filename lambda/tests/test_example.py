import unittest

from helpers.add_numbers import add_two_numbers

class TestExample(unittest.TestCase):

    # Passing Test Cases

    def test_with_body(self):
        self.assertTrue(True)
        
    def test_add_two_numbers(self):
        self.assertTrue(add_two_numbers(1, 2) == 3)
if __name__ == '__main__':
    unittest.main()
