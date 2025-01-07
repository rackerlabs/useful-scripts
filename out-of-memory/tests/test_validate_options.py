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

    # Skip tests on Amazon Linux and CentOS because they don't have dmesg
    @pytest.mark.skipif(
        System().get_distro_info()[0] in ["centos"],
        reason="No dmesg in arch container",
    )
    def test_dmesg(self, capsys):
        # Test journalctl log
        options = self.values
        options.dmesg = True
        options.file = False

        system = validate_options(self.system, options)
        with pytest.raises(SystemExit) as ex:
            run(system, options)
            assert ex.code == 0

        out, _ = capsys.readouterr()
        assert "Using Dmesg: \x1b[0m\x1b[1;32mTrue" in out

    def test_too_many_options(self, capsys):
        # Test too many options
        options = self.values
        options.dmesg = True
        options.journalctl = True
        options.file = "tests/assets/logs/messages"

        with pytest.raises(SystemExit) as ex:
            validate_options(self.system, options)

        assert ex.value.code == 1

        out, _ = capsys.readouterr()
        assert (
            "Error: Please specify only a single option; a log file, dmesg or journalctl."
            in out
        )
        assert "- File: tests/assets/logs/messages" in out
        assert "- Journalctl: True" in out
        assert "- Dmesg: True" in out

    def test_invalid_file(self, capsys):
        # Test invalid file
        options = self.values
        options.dmesg = False
        options.journalctl = False
        options.file = "tests/assets/logs/invalid"

        with pytest.raises(SystemExit) as ex:
            validate_options(self.system, options)
            assert ex.code == 1

        out, _ = capsys.readouterr()
        assert "File tests/assets/logs/invalid does not exist" in out
