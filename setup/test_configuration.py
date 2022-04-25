import unittest
from unittest.mock import MagicMock
from setup.configuration import Configuration

# Create your tests here.


class TestConfiguration(unittest.TestCase):
    def assertValidInput(self, input_tuple):
        config = Configuration()
        config.getInput = MagicMock(return_value=input_tuple[0])

        result = config.question("test")

        config.getInput.assert_called_with("test (y/n): ")
        self.assertEqual(result, input_tuple[1])

    def assertInvalidInput(self, input_tuple):
        config = Configuration()
        config.getInput = MagicMock(side_effect=input_tuple[0])

        result = config.question("test")

        self.assertEqual(config.getInput.call_count, len(input_tuple[0]))
        self.assertEqual(result, input_tuple[1])

    def test_valid_inputs(self):
        inputs = [['yes', True], ['ye', True], ['y', True], ['no', False], ['n', False]]

        for input_tuple in inputs:
            self.assertValidInput(input_tuple)

    def test_invalid_inputs(self): 
        inputs = [[['invalid', 'maybe', 'uncertain', 'no'], False], [['a', 'yes'], True]]

        for input_tuple in inputs:
            self.assertInvalidInput(input_tuple)
