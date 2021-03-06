"""Test module for `archey.processes`"""

from subprocess import CalledProcessError

import unittest
from unittest.mock import patch

from archey.processes import Processes


class TestProcessesUtil(unittest.TestCase):
    """
    Test cases for the `Processes` (singleton) class.
    To work around the singleton, we reset the internal `_instances` dictionary.
    This way, `check_output` can be mocked here.
    """
    @patch.dict(
        'archey.singleton.Singleton._instances',
        clear=True
    )
    @patch(
        'archey.processes.check_output',
        return_value="""\
what
an
awesome
processes
list
you
got
there
""")
    def test_ps_ok(self, check_output_mock):
        """Simple test with a plausible `ps` output"""
        # We'll create two `Processes` instances.
        processes_1 = Processes()
        _ = Processes()

        self.assertListEqual(
            processes_1.get(),
            ['what', 'an', 'awesome', 'processes', 'list', 'you', 'got', 'there']
        )

        # The class has been instantiated twice, but `check_output` has been called only once.
        # `unittest.mock.Mock.assert_called_once` is not available against Python < 3.6.
        self.assertEqual(check_output_mock.call_count, 1)

    @patch.dict(
        'archey.singleton.Singleton._instances',
        clear=True
    )
    @patch(
        'archey.processes.check_output',
        side_effect=[
            CalledProcessError(1, 'ps', "ps: unrecognized option: u\n"),
            """\
COMMAND
sh
top
ps
"""])
    def test_ps_failed(self, _):
        """Verifies that the program correctly handles first crashing `ps` call"""
        self.assertListEqual(
            Processes().get(),
            ['sh', 'top', 'ps']
        )

    @patch.dict(
        'archey.singleton.Singleton._instances',
        clear=True
    )
    @patch(
        'archey.processes.check_output',
        side_effect=FileNotFoundError()
    )
    @patch(
        'archey.processes.print',
        return_value=None,  # Let's nastily mute class' outputs.
        create=True
    )
    def test_ps_not_available(self, _, __):
        """Verifies that the program stops when `ps` is not available"""
        self.assertRaises(SystemExit, Processes)


if __name__ == '__main__':
    unittest.main()
