import os
import sys
from optparse import Values

import pytest

# Add the parent directory to the path so we can import the latest version of the script
oom_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, oom_dir)

from oom_investigate import System, run, validate_options

# Ignore DeprecationWarning and PendingDeprecationWarning warnings
pytest.mark.filterwarnings("ignore::DeprecationWarning")
pytest.mark.filterwarnings("ignore::PendingDeprecationWarning")


class TestSystem:
    system = System()
    values = Values(
        {
            "file": False,
            "show_counter": 5,
            "reverse": False,
            "journalctl": False,
            "dmesg": False,
            "quick": False,
            "version": None,
            "show_all": False,
        }
    )

    @pytest.mark.parametrize(
        "log_file, expected_oom_count, expected_oom_incident, system_ram, start_time, end_time",
        [
            (
                "tests/assets/logs/messages",
                19,
                19,
                "32,768 MB",
                "Mon Jun 18 02:23:48",
                "Wed Jun 20 20:33:22",
            ),
            (
                "tests/assets/logs/messages.1",
                1,
                1,
                "31,496 MB",
                "Sat Sep 29 08:12:34",
                "Sat Sep 29 08:12:34",
            ),
        ],
    )
    def test_file_processing(
        self,
        log_file,
        expected_oom_count,
        expected_oom_incident,
        system_ram,
        start_time,
        end_time,
        capsys,
    ):
        # Test functionality with different log files and expected results
        options = self.values
        options.file = log_file
        options.show_all = True

        with pytest.raises(SystemExit) as ex:
            self.system.log_to_use = options.file
            run(self.system, options)
            assert ex.code == 0

        out, _ = capsys.readouterr()
        assert "Using Log File: \x1b[0m\x1b[1;32m{0}".format(log_file) in out
        assert (
            "OOM Incidents: \x1b[0m\x1b[1;31m{0}\x1b[0m".format(expected_oom_count)
            in out
        )
        assert (
            "OOM Incident: \x1b[0m\x1b[0;96m{0}\x1b[0m".format(expected_oom_incident)
            in out
        )
        assert "Displaying all OOM incidents:" in out
        assert "System RAM: \x1b[1;32m{0}".format(system_ram) in out
        assert "Log Start Time: \x1b[0m\x1b[0;96m{0}".format(start_time) in out
        assert "Log End Time: \x1b[0m\x1b[0;96m{0}".format(end_time) in out
