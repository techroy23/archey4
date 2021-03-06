"""Test module for Archey's disks usage detection module"""

from subprocess import CalledProcessError

import unittest
from unittest.mock import patch

from archey.colors import Colors
from archey.entries.disk import Disk


class TestDiskEntry(unittest.TestCase):
    """
    Here, we mock `check_output` calls to disk utility tools.
    """
    @patch(
        'archey.entries.disk.check_output',
        side_effect=[
            """\
Filesystem       1000000-blocks    Used Available Capacity Mounted on
/dev/mapper/root        39101MB 14216MB   22870MB      39% /
/dev/sda1                 967MB    91MB     810MB      11% /boot
/dev/mapper/home       265741MB 32700MB  219471MB      13% /home
total                  305809MB 47006MB  243149MB      17% -
""",
            # Second `df` call will fail.
            CalledProcessError(1, 'df', "df: no file systems processed\n")
        ]
    )
    @patch(
        'archey.entries.disk.Configuration.get',
        return_value={
            'disk': {
                'warning': 50,
                'danger': 75
            }
        }
    )
    def test_df_only(self, _, __):
        """Test computations around `df` output at disk regular level"""
        disk = Disk().value
        self.assertTrue(all(i in disk for i in [str(Colors.GREEN_NORMAL), '45.9', '298.6']))

    @patch(
        'archey.entries.disk.check_output',
        side_effect=[
            """\
Filesystem       1000000-blocks     Used Available Capacity Mounted on
/dev/mapper/root        39101MB  14216MB   22870MB      39% /
/dev/sda1                 967MB     91MB     810MB      11% /boot
/dev/mapper/home       265741MB 243291MB   22450MB      92% /home
total                  305809MB 257598MB   46130MB      84% -
""",
            # Second `df` call will fail.
            CalledProcessError(1, 'df', "df: no file systems processed\n")
        ]
    )
    @patch(
        'archey.entries.disk.Configuration.get',
        return_value={
            'disk': {
                'warning': 80,
                'danger': 90
            }
        }
    )
    def test_df_only_warning(self, _, __):
        """Test computations around `df` output at disk warning level"""
        disk = Disk().value
        self.assertTrue(all(i in disk for i in [str(Colors.YELLOW_NORMAL), '251.6', '298.6']))

    @patch(
        'archey.entries.disk.check_output',
        side_effect=[
            """\
Filesystem       1000000-blocks    Used Available Capacity Mounted on
/dev/mapper/root        39101MB 14216MB   22870MB      39% /
/dev/sda1                 967MB    91MB     810MB      11% /boot
/dev/mapper/home       265741MB 32700MB  219471MB      13% /home
total                  305809MB 47006MB  243149MB      17% -
""",
            """\
Mounted on
/
/vol
""",
            """\
/dev/nvme0n1p1, ID: 1
   Device size:               0.00B
   Device slack:              0.00B
   Unallocated:           476.44GiB

""",
            """\
/dev/sda1, ID: 1
   Device size:               0.00B
   Device slack:              0.00B
   Unallocated:             3.64TiB

""",
            """\
Overall:
    Device size:                         476.44GiB
    Device allocated:                    432.02GiB
    Device unallocated:                   44.42GiB
    Device missing:                      476.44GiB
    Used:                                352.13GiB
    Free (estimated):                    122.57GiB      (min: 122.57GiB)
    Data ratio:                               1.00
    Metadata ratio:                           1.00
    Global reserve:                        0.43GiB      (used: 0.00GiB)

Data,single: Size:429.01GiB, Used:350.85GiB (81.78%)

Metadata,single: Size:3.01GiB, Used:1.28GiB (42.56%)

System,single: Size:0.00GiB, Used:0.00GiB (1.95%)


Overall:
    Device size:                        3726.02GiB
    Device allocated:                    592.01GiB
    Device unallocated:                 3134.02GiB
    Device missing:                     3726.02GiB
    Used:                                591.27GiB
    Free (estimated):                   1567.03GiB      (min: 1567.03GiB)
    Data ratio:                               1.00
    Metadata ratio:                           1.00
    Global reserve:                        0.50GiB      (used: 0.00GiB)

Data,single: Size:590.00GiB, Used:589.95GiB (99.99%)

Metadata,single: Size:2.00GiB, Used:1.32GiB (66.16%)

System,single: Size:0.01GiB, Used:0.00GiB (1.03%)

"""
        ]
    )
    @patch(
        'archey.entries.disk.Configuration.get',
        return_value={
            'disk': {
                'warning': 50,
                'danger': 75
            }
        }
    )
    def test_df_and_btrfs(self, _, __):
        """Test computations around `df` and `btrfs` outputs"""
        disk = Disk().value
        self.assertTrue(all(i in disk for i in [str(Colors.GREEN_NORMAL), '989.3', '4501.1']))

    @patch(
        'archey.entries.disk.check_output',
        side_effect=[
            CalledProcessError(1, 'df', "df: no file systems processed\n"),
            """\
Mounted on
/
/vol
""",
            """\
/dev/nvme0n1p1, ID: 1
   Device size:               0.00B
   Device slack:              0.00B
   Unallocated:           476.44GiB

""",
            """\
/dev/sda1, ID: 1
   Device size:               0.00B
   Device slack:              0.00B
   Unallocated:             3.64TiB

/dev/sdb1, ID: 2
   Device size:               0.00B
   Device slack:              0.00B
   Unallocated:             3.64TiB

""",
            """\
Overall:
    Device size:                         476.44GiB
    Device allocated:                    432.02GiB
    Device unallocated:                   44.42GiB
    Device missing:                      476.44GiB
    Used:                                352.13GiB
    Free (estimated):                    122.57GiB      (min: 122.57GiB)
    Data ratio:                               1.00
    Metadata ratio:                           1.00
    Global reserve:                        0.43GiB      (used: 0.00GiB)

Data,single: Size:429.01GiB, Used:350.85GiB (81.78%)

Metadata,single: Size:3.01GiB, Used:1.28GiB (42.56%)

System,single: Size:0.00GiB, Used:0.00GiB (1.95%)


Overall:
    Device size:                        7452.04GiB
    Device allocated:                   1184.02GiB
    Device unallocated:                 6268.03GiB
    Device missing:                     7452.04GiB
    Used:                               1182.54GiB
    Free (estimated):                   3134.06GiB      (min: 3134.06GiB)
    Data ratio:                               2.00
    Metadata ratio:                           2.00
    Global reserve:                        0.50GiB      (used: 0.00GiB)

Data,RAID1: Size:590.00GiB, Used:589.95GiB

Metadata,RAID1: Size:2.00GiB, Used:1.32GiB

System,RAID1: Size:0.01GiB, Used:0.00GiB

"""
        ]
    )
    @patch(
        'archey.entries.disk.Configuration.get',
        return_value={
            'disk': {
                'warning': 50,
                'danger': 75
            }
        }
    )
    def test_btrfs_only_with_raid_configuration(self, _, __):
        """Test computations around `btrfs` outputs with a RAID-1 setup"""
        disk = Disk().value
        self.assertTrue(all(i in disk for i in [str(Colors.GREEN_NORMAL), '943.4', '4202.5']))

    @patch(
        'archey.entries.disk.check_output',
        side_effect=[
            CalledProcessError(1, 'df', "df: unrecognized option: l\n"),
            CalledProcessError(1, 'df', "df: unrecognized option: l\n")
        ]
    )
    @patch(
        'archey.entries.disk.Configuration.get',
        return_value={'not_detected': 'Not detected'}
    )
    def test_df_failing(self, _, __):
        """Test df call failing against the BusyBox implementation"""
        self.assertEqual(Disk().value, 'Not detected')

    @patch(
        'archey.entries.disk.check_output',
        side_effect=[
            CalledProcessError(1, 'df', "df: no file systems processed\n"),
            CalledProcessError(1, 'df', "df: no file systems processed\n")
        ]
    )
    @patch(
        'archey.entries.disk.Configuration.get',
        return_value={'not_detected': 'Not detected'}
    )
    def test_no_recognised_disks(self, _, __):
        """Test df failing to detect any valid file-systems"""
        self.assertEqual(Disk().value, 'Not detected')


if __name__ == '__main__':
    unittest.main()
