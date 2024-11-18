import os
import sys

import pytest

# Add the parent directory to the path so we can import the latest version of the script
oom_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, oom_dir)

from oom_investigate import Printer


class TestPrinter:
    def setup_method(self):
        """Setup for each method"""
        self.printer = Printer()

    def test_spacer(self):
        """Test the spacer property."""
        expected = "\033[1m" + ("_" * 40) + "\033[0m"
        assert self.printer.spacer == expected

    def test_header(self):
        """Test the header function output and severity level impact."""
        message = "Header message"
        expected = "\033[1mHeader message\033[0m"
        assert self.printer._header(message) == expected
        assert self.printer._severity == Printer.INFO

    def test_ok(self):
        """Test the _ok function output and severity level impact."""
        message = "OK message"
        expected = "\033[1;32mOK message\033[0m"
        assert self.printer._ok(message) == expected
        assert self.printer._severity == Printer.INFO

    def test_notice(self):
        """Test the _notice function output and severity level impact."""
        message = "Notice message"
        expected = "\033[0;96mNotice message\033[0m"
        assert self.printer._notice(message) == expected
        assert self.printer._severity == Printer.NOTICE

    def test_warning(self):
        """Test the _warning function output and severity level impact."""
        message = "Warning message"
        expected = "\033[1;33mWarning message\033[0m"
        assert self.printer._warning(message) == expected
        assert self.printer._severity == Printer.WARN

    def test_critical(self):
        """Test the _critical function output and severity level impact."""
        message = "Critical message"
        expected = "\033[1;31mCritical message\033[0m"
        assert self.printer._critical(message) == expected
        assert self.printer._severity == Printer.CRIT

    def test_multiline_no_output_below_severity(self):
        """Test multiline output when severity is below the specified level."""
        self.printer._severity = Printer.NONE
        assert self.printer.multiline(minseverity=Printer.INFO) == []

    def test_multiline_with_limit(self):
        """Test multiline output with a limit on the number of lines returned."""
        self.printer._lines = ["line1", "line2", "line3", "line4", "line5"]
        self.printer._severity = Printer.INFO
        expected = ["...(4x more)...", "line5"]
        assert self.printer.multiline(minseverity=Printer.INFO, limit=1) == expected

    def test_multiline_with_header(self):
        """Test multiline with a header set."""
        self.printer.HEADER = "Test Header"
        self.printer._lines = ["line1"]
        self.printer._severity = Printer.INFO
        expected = ["\033[1mTest Header:\033[0m", "line1"]
        assert self.printer.multiline() == expected
