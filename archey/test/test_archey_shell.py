"""Test module for Archey's shell detection module"""

from subprocess import CalledProcessError

import unittest
from unittest.mock import patch

from archey.entries.shell import Shell


class TestShellEntry(unittest.TestCase):
    """
    For this entry, we'll just verify that the output is non-null.
    """
    @patch(
        'archey.entries.shell.os.getenv',
        return_value='SHELL'
    )
    def test_getenv(self, _):
        """Simple mock, simple test"""
        self.assertEqual(Shell().value, 'SHELL')

    @patch(
        'archey.entries.shell.os.getenv',
        return_value=None
    )
    @patch(
        'archey.entries.shell.os.getuid',  # We DO NOT HAVE TO mock this call.
        return_value=1000
    )
    @patch(
        'archey.entries.shell.check_output',
        return_value="USERNAME:x:1000:1000:User Name,,,:/home/user:/bin/bash\n"
    )
    def test_getent_call(self, _, __, ___):
        """Mock `getent` returned value and check the correct assignment"""
        self.assertEqual(Shell().value, '/bin/bash')

    @patch(
        'archey.entries.shell.os.getenv',
        return_value=None
    )
    @patch(
        'archey.entries.shell.check_output',
        side_effect=CalledProcessError(2, 'getent')
    )
    @patch(
        'archey.entries.shell.Configuration.get',
        return_value={'not_detected': 'Not detected'}
    )
    def test_config_fall_back(self, _, __, ___):
        """`id` fails, but Archey must not !"""
        self.assertEqual(Shell().value, 'Not detected')

if __name__ == '__main__':
    unittest.main()
