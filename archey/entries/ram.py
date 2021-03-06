"""RAM usage detection class"""

import re

from subprocess import check_output

from archey.colors import Colors
from archey.configuration import Configuration


class RAM:
    """
    First tries to use the `free` command to retrieve RAM usage.
    If not available, falls back on the parsing of `/proc/meminfo` file.
    """
    def __init__(self):
        # Fetch the user-defined RAM limits from configuration.
        ram_limits = Configuration().get('limits')['ram']

        try:
            ram = ''.join(
                filter(
                    re.compile('Mem').search,
                    check_output(
                        ['free', '-m'],
                        env={'LANG': 'C'}, universal_newlines=True
                    ).splitlines()
                )
            ).split()
            used = float(ram[2])
            total = float(ram[1])

        except (IndexError, FileNotFoundError):
            # An in-digest one-liner to retrieve memory info into a dictionary
            with open('/proc/meminfo') as file:
                ram = {
                    i.split(':')[0]: float(i.split(':')[1].strip(' kB')) / 1024
                    for i in filter(None, file.read().splitlines())
                }

            total = ram['MemTotal']
            # Here, let's imitate Neofetch's behavior.
            # See <https://github.com/dylanaraps/neofetch/wiki/Frequently-Asked-Questions>.
            used = total + ram['Shmem'] - (
                ram['MemFree'] + ram['Cached'] + ram['SReclaimable'] + ram['Buffers'])
            # Imitates what `free` does when the obtained value happens to be incorrect.
            # See <https://gitlab.com/procps-ng/procps/blob/master/proc/sysinfo.c#L790>.
            if used < 0:
                used = total - ram['MemFree']

        # Based on the RAM percentage usage, select the corresponding level color.
        level_color = Colors.get_level_color(
            (used / total) * 100,
            ram_limits['warning'], ram_limits['danger']
        )

        self.value = '{0}{1} MiB{2} / {3} MiB'.format(
            level_color,
            int(used),
            Colors.CLEAR,
            int(total)
        )
