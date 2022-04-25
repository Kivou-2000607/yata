import unittest
from unittest.mock import MagicMock

from setup import configuration

# Create your tests here.

class ConfigurationTests(unittest.TestCase):
    config = configuration.Configuration()

    def givenQuestion_WhenAnsweredWithValidInput_ThenResponseCorrespondsToInput(self):
        inputs = [ ['yes', True], ['ye', True], ['y', True], ['no', False], ['n', False] ]

        for input in inputs:
            self.assertEqual(self.config.question(input[0]), input[1])

    def givenQuestion_WhenAnsweredWithInvalidInput_ThenMethodCalledAgain(self):
        config = self.config
        config.question = MagicMock()
        
        config.question(0)

        assert config.question.called

if __name__ == '__main__':
    unittest.main()