import unittest
from unittest.mock import MagicMock
from setup.configuration import Configuration

# Create your tests here.


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        self.recursion_counter = 0

    def testInput(self, input_tuple):
        config = Configuration()
        config.getInput = MagicMock(return_value=input_tuple[0])

        result = config.question("test")

        config.getInput.assert_called_with("test (y/n): ")
        self.assertEqual(result, input_tuple[1])

    def test_valid_inputs(self):
        inputs = [['yes', True], ['ye', True], ['y', True], ['no', False], ['n', False]]

        for input_tuple in inputs:
            self.testInput(input_tuple)
