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

    def test_distro_info_imports(self):
        # very basic test to check if the distro info is returned
        # Designed to run on docker containers for python 2.7, 3.6, 3.10
        distro_info = self.system.get_distro_info()
        assert distro_info[0] is not None
        assert distro_info[1] is not None

    def test_default_system_log(self):
        # Test default system log file
        options = self.values

        system = validate_options(self.system, options)
        with pytest.raises(SystemExit) as ex:
            run(system, options)
            assert ex.code == 0
