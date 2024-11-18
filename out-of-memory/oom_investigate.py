#!/usr/bin/env python
#
# Author:       Luke Shirnia
# Source:       https://github.com/LukeShirnia/out-of-memory/
####
# To Do:
# - Read "pages RAM" from oom incident for precise system RAM at time of incident
# - Explore adding "What file should we check next" option? (undecided if actually required)
####
from __future__ import print_function

import datetime
import errno
import fnmatch
import gzip
import itertools
import os
import re
import subprocess
import sys
import warnings
from collections import defaultdict
from optparse import OptionParser

warnings.filterwarnings(
    "ignore", category=DeprecationWarning
)  # Hide platform.dist() related deprecation warnings


__version__ = "2.0.2"


def std_exceptions(etype, value, tb):
    """
    The following exits cleanly on Ctrl-C or EPIPE
    while treating other exceptions as before.
    """
    sys.excepthook = sys.__excepthook__
    if issubclass(etype, KeyboardInterrupt):
        pass
    elif issubclass(etype, IOError) and value.errno == errno.EPIPE:
        pass
    else:
        sys.__excepthook__(etype, value, tb)


sys.excepthook = std_exceptions


# Helper functions # {{{
def open_file(file_path):
    """Handle reading of gzipped and regular files"""
    if file_path.endswith(".gz"):
        return gzip.open(file_path, "rt")
    else:
        return open(file_path, "r")


class Printer(object):
    """
    Base class for all facts

    A `fact` is a basic unit of information collection in this script. This is a base class
    providing the common functions such as output formatting.
    """

    horizontal_line = "_" * 40

    WHITE = "\033[1m"
    GREEN = "\033[1;32m"
    CYAN = "\033[0;96m"
    ORANGE = "\033[1;33m"
    RED = "\033[1;31m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

    # Fact's severity
    NONE = 0  # no useful output
    INFO = 1
    NOTICE = 2
    WARN = 3
    CRIT = 4
    _severity = NONE
    _lines = []

    HEADER = None

    @property
    def spacer(self):
        return self.WHITE + self.horizontal_line + self.RESET

    def _header(self, msg):
        self._severity = max(self._severity, self.INFO)
        return self.WHITE + msg + self.RESET

    def _ok(self, msg):
        self._severity = max(self._severity, self.INFO)
        return self.GREEN + msg + self.RESET

    def _notice(self, msg):
        self._severity = max(self._severity, self.NOTICE)
        return self.CYAN + msg + self.RESET

    def _warning(self, msg):
        self._severity = max(self._severity, self.WARN)
        return self.ORANGE + msg + self.RESET

    def _critical(self, msg):
        self._severity = max(self._severity, self.CRIT)
        return self.RED + msg + self.RESET

    def multiline(self, minseverity=INFO, limit=None):
        if self._severity < minseverity or len(self._lines) == 0:
            return []
        lines = self._lines
        if limit and len(lines) > limit:
            # pylint: disable=invalid-unary-operand-type
            lines = ["...(%dx more)..." % (len(lines) - limit)] + lines[-limit:]
        if self.HEADER:
            lines = [self.WHITE + self.HEADER + ":" + self.RESET] + lines
        return lines


# }}}


def main_header():
    """
    Disclaimer and Script Header
    """
    colours = Printer()
    analyzer_name = "Out Of Memory Analyzer"
    current_year = datetime.datetime.now().year
    author_name = "LukeShirnia"
    disclaimer_text = "If the system OOMs too viciously, there may be nothing logged!"
    warning_text = "Do NOT take this script as FACT, ALWAYS investigate further."

    print(colours.spacer)
    print("      _____ _____ _____ ")
    print("     |     |     |     |")
    print("     |  |  |  |  | | | |")
    print("     |_____|_____|_|_|_|")
    print("     {}".format(analyzer_name))
    print("")
    print("\u00A9 {} {}".format(current_year, author_name))
    print("")
    print(
        "{colours.RED}{colours.UNDERLINE}Disclaimer:{colours.RESET}".format(
            colours=colours
        )
    )
    print(
        "{colours.RED}{disclaimer_text}".format(
            colours=colours, disclaimer_text=disclaimer_text
        )
    )
    print(
        "{warning_text}{colours.RESET}".format(
            warning_text=warning_text, colours=colours
        )
    )
    print(colours.spacer)


class System(Printer):
    """System information"""

    def __init__(self):
        self.python_version = None
        self.distro, self.version, _ = self.get_distro_info()
        self.log_files = []
        self.log_to_use = None
        self.journalctl = False
        self.ram = self.get_ram_info()
        self.find_system_logs()
        self.use_journalctl = False
        self.use_dmesg = False

    def __str__(self):
        return self._system

    def parse_os_release(self):
        """
        This is a fallback, fallback method to get the distro and version information for OS's we
        can't get from the platform or distro modules.
        """
        distro = version = None
        release_id_map = {
            "ol": "oracle",
            "rhel": "redhat",
            "centos": "centos",
            "almalinux": "almalinux",
            "rocky": "rocky",
        }

        if os.path.isfile("/etc/os-release"):
            with open_file("/etc/os-release") as f:
                for line in f:
                    if line.startswith("VERSION_ID="):
                        version = line.split("=")[1].strip('" \n')
                    if line.startswith("ID="):
                        distro = line.split("=")[1].strip('" \n')
                        distro = release_id_map.get(distro, distro)

        return distro, version, None

    def get_distro_info(self):
        """Method to get the distro and version information for the system"""
        python_version = sys.version_info
        self.python_version = "{}.{}.{}".format(
            python_version.major, python_version.minor, python_version.micro
        )
        # pylint: disable=deprecated-method
        # pylint: disable=import-outside-toplevel
        try:
            # First we attempt to use platform.dist() for compatibility reasons.
            # This function however has been deprecated in py > 3.7, so we catch the AttributeError
            # and then attempt to use the distro module instead
            # Standard Library
            import platform as platform_info

            platform_info_tuple = platform_info.dist()
            # If the tuple is empty, it's probably AWS, so let's expand the supported distro list
            # If the tuple's last element is "Green Obsidian", it's Rocky Linux so let's expand
            # the supported distros
            if (
                not any(platform_info_tuple)
                or platform_info_tuple[-1] == "Green Obsidian"
            ):
                dists = platform_info._supported_dists + (
                    "system",
                )  # pylint: disable=protected-access
                # Added to include Amazon and Rocky Linux Support
                return platform_info.linux_distribution(supported_dists=dists)
            return platform_info_tuple
        except AttributeError:
            try:
                # Third Party
                import distro as platform_info  # pylint: disable=import-error

                return platform_info.linux_distribution(full_distribution_name=False)
            # If the distro module does not exist, gracefully handle htLook exit
            except ModuleNotFoundError:  # pylint: disable=undefined-variable
                return self.parse_os_release()

    def parse_file(self, file_path, patterns):
        if os.path.isfile(file_path):
            with open_file(file_path) as f:
                for line in f:
                    for pattern, extractor in patterns:
                        if pattern in line:
                            path = extractor(line)
                            if not os.path.isfile(path):
                                path = file_path
                            self.log_files.append(path)

    def find_system_logs(self):
        # Check for rsyslog.conf on Linux systems
        self.parse_file(
            "/etc/rsyslog.conf", [("*.info", lambda line: line.split()[-1])]
        )

        # Check for journald.conf on newer Linux systems
        self.parse_file(
            "/etc/systemd/journald.conf",
            [("Storage=", lambda line: line.split("=")[-1].strip())],
        )

        # Check for syslog.conf on older Linux systems and older macOS systems
        self.parse_file(
            "/etc/syslog.conf",
            [
                ("*.info", lambda line: line.split()[-1]),
                ("/var/log/system.log", lambda line: line.split()[-1]),
            ],
        )

        # Check for asl.conf on newer macOS systems
        self.parse_file(
            "/etc/asl.conf",
            [
                (
                    "? [= Sender kernel] file (.+)",
                    lambda line: "/var/log/" + line.split()[-1],
                )
            ],
        )

        # Adding log info to the lines list
        if self.log_files:
            self.log_to_use = self.log_files[0]

    @property
    def default_system_log(self):
        # Only default to journalctl if there is only one log file and it is journald config file
        if len(self.log_files) == 1 and "journald" in self.log_files[0]:
            self.journalctl = True
            return "journald"
        if not self.log_files:
            return (
                "No log files found on system. You might need to manually specify one."
            )
        return self.log_files[0]

    def search_log_dir(self, log_file):
        """
        This function finds all log files in the directory of
        default log file (or specified log file)
        """
        log_directory = os.path.dirname(log_file)
        log_file_pattern = os.path.basename(log_file) + "*"

        log_files = [
            os.path.join(root, name)
            for root, _, files in os.walk(log_directory)
            for name in files
            if fnmatch.fnmatch(name, log_file_pattern)
        ]
        return sorted(log_files)

    def get_ram_info(self):
        try:
            mem_bytes = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
            mem_mib = mem_bytes / (1024.0**2)
            return round(mem_mib)
        except ValueError:
            return None

    def populate_lines(self):
        # Only populate lines if they haven't been populated already
        if self._lines:
            return

        distro_version = "{} {}".format(self.distro, self.version)
        self._lines.append(self._header("OS: ") + self._notice(distro_version))
        self._lines.append(
            self._header("Python Version: ") + self._notice(self.python_version)
        )
        self._lines.append(
            self._header("RAM: ")
            + self._notice("{} GiB".format(round(self.ram / 1024)))
        )
        self._lines += [
            self._header("Default System Log: ") + self._notice(self.default_system_log)
        ]
        self._lines.append("")

    def print_pretty(self):
        self.populate_lines()

        print()
        for line in self._lines:
            print(line)


class OOMAnalyzer(Printer):
    """Class to analyze OOM logs"""

    def __init__(self, system):
        self.system = system
        self.log_file = self.system.log_to_use
        self.oom_instances = []
        self.current_instance = None
        self.rss_column = 7
        self.log_start_time = None
        self.log_end_time = None
        self.oom_counter = 0
        self._get_log_source = None
        self._system_ram = None
        self._last_instance_system_ram = None

    def get_log_source(self, log_file=None, journalctl=None, dmesg=None):
        """Method to get the log source, allowing for manual override"""
        if self._get_log_source:
            return self._get_log_source

        log_sources = [
            ("dmesg", dmesg, self.system.use_dmesg),
            ("journalctl", journalctl, self.system.use_journalctl),
            ("file", log_file, self.log_file),
        ]

        chosen_source = None

        for source, manual, attribute in log_sources:
            if manual is True:
                if chosen_source is not None:
                    print("Please specify only one log source")
                    sys.exit(1)
                chosen_source = source
            elif manual is None and attribute and chosen_source is None:
                # Let's use journalctl if the log file is a journald config file
                if source == "file" and "journald" in self.log_file:
                    chosen_source = "journalctl"
                else:
                    chosen_source = source

        self._get_log_source = chosen_source or "file"
        return self._get_log_source

    def log_lines(self, source, log_file=None):
        """Method to return log lines from different sources"""
        # If log file is specified, read from that file
        if source == "file":
            log_file_to_read = log_file or self.log_file
            with open_file(log_file_to_read) as file:
                for line in file:
                    yield line.strip()
        # If system.use_journalctl is True, read from journalctl
        elif source == "journalctl":
            cmd = "journalctl -o short-iso --no-pager --boot=-0 -k"
            p = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            for line in p.stdout:
                yield line.decode("utf-8")
        # If system.dmsg is True, read from dmesg
        elif source == "dmesg":
            cmd = "dmesg"
            p = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            for line in p.stdout:
                yield line.decode("utf-8")

    def analyze(self):
        """Method to parse the log and analyze OOM incidents"""

        # Prevent errors if log file is empty
        log_generator = self.log_lines(self.get_log_source())
        try:
            first_line = next(log_generator)
        except StopIteration:
            return

        state = {"found_killed": False}

        # Extract the start timestamp from the line
        if self.log_start_time is None:
            self.log_start_time = self.extract_timestamp(first_line)

        def generator():
            current_instance = None
            line = None
            for line in log_generator:
                # Extract the ram from the system logs if possible
                if not self._system_ram:
                    ram = self.get_ram_from_logs(line)
                    if ram:
                        self._system_ram = round(ram)
                # This is both the start of a new oom incident and the end of the previous one.
                if self.is_oom_start(line):
                    line = self.strip_brackets_pid(line)
                    self.oom_counter += 1
                    timestamp = self.extract_timestamp(line)
                    self.rss_column = line.split().index("rss")
                    # If we've already started an OOM incident, yield it and start a new one
                    if current_instance:
                        current_instance["system_ram"] = "{:,.0f}".format(
                            self._system_ram if self._system_ram else self.system.ram
                        )
                        yield current_instance
                        self._last_instance_system_ram = self._system_ram
                        self._system_ram = None
                        state["found_killed"] = False
                    current_instance = {
                        "total_mb": 0,
                        "processes": [],
                        "killed": [],
                        "start_time": timestamp,
                        "incident_number": self.oom_counter,
                    }
                # Processing the new OOM incident
                elif (
                    not state["found_killed"]
                    and not self.is_killed_process(line)
                    and self.is_process_line(line)
                    and current_instance is not None
                ):
                    try:
                        processed_line = self.parse_process_line(line)
                        current_instance["processes"].append(processed_line)
                        current_instance["total_mb"] += processed_line["rss"]
                    except ValueError:
                        continue
                elif self.is_killed_process(line) and current_instance is not None:
                    state["found_killed"] = True
                    current_instance["killed"].append(
                        self.parse_killed_process_line(line)
                    )

            if line:
                self.log_end_time = self.extract_timestamp(line)

            # Yield the last OOM incident
            if current_instance:
                current_instance["system_ram"] = "{:,.0f}".format(
                    self._last_instance_system_ram
                    if self._last_instance_system_ram
                    else self.system.ram
                )
                yield current_instance

        return generator()

    def strip_brackets_pid(self, log_line):
        return log_line.replace("[", "").replace("]", "")

    def is_oom_start(self, line):
        """Check if the line is the start of a new OOM incident"""
        return bool(re.search(r"\[\s*pid\s*\]", line))

    def is_process_line(self, line):
        return re.match(r".*\[\s*\d+\]\s*\d+\s+\d+\s+\d+\s+.*", line)

    def parse_process_line(self, line):
        """Parse the line and obtain the pid, rss and name of the process"""
        # When we get the rss column and store it, we've stripped the brackets. So we need to
        # strip them here too to make sure we get the right column
        line = self.strip_brackets_pid(line)
        fields = line.split()
        rss = int(fields[self.rss_column])
        rss_mb = rss * 4 // 1024
        name = fields[-1]
        return {"rss": rss_mb, "name": name}

    def get_ram_from_logs(self, line):
        """Method to return the RAM indicated in the logs, rather than the host machine"""
        # total RAM printed in preable before each OOM-killer event
        # as count of 4K pages.
        m = re.search("([0-9]+) pages RAM", line)
        if m:
            return int(m.group(1)) * 4 / 1024.0
        # Alternatively if running inside a cgroup then use the configured
        # memory limit.
        m = re.search("memory: usage [0-9]+kB, limit ([0-9]+)kB", line)
        if m:
            return int(m.group(1)) / 1024
        return None

    def is_killed_process(self, line):
        """Check if the line is a killed process line"""
        return "killed process" in line.lower()

    def parse_killed_process_line(self, line):
        """Extract the name of the killed process"""
        match = re.search(
            r"Killed process \d+(?:, UID \d+)?, \((\S+)\)|Killed process \d+ \((\S+)\)",
            line,
            re.IGNORECASE,
        )
        if match:
            return match.group(1) or match.group(2)
        return None

    def extract_timestamp(self, line):
        syslog_pattern = r"(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})"
        dmesg_pattern = r"^\[?\s*(\d+\.\d+)\]?"
        journalctl_pattern = (
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{6})?(?:\+|-)\d{4})"
        )

        syslog_match = re.search(syslog_pattern, line)
        dmesg_match = re.search(dmesg_pattern, line)
        journalctl_match = re.search(journalctl_pattern, line)

        time = None
        if syslog_match:
            timestamp_str = syslog_match.group(1)
            time = datetime.datetime.strptime(timestamp_str, "%b %d %H:%M:%S")
        elif dmesg_match:
            timestamp_str = dmesg_match.group(1)
            time = datetime.datetime.fromtimestamp(float(timestamp_str))
        elif journalctl_match:
            timestamp_str = journalctl_match.group(1)
            try:
                time = datetime.datetime.strptime(
                    timestamp_str, "%Y-%m-%dT%H:%M:%S.%f%z"
                )
            except ValueError:
                time = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S%z")

        return time

    def sorted_results(self, oom_processes_list):
        """Method to sort the OOM processes by RSS"""
        result = {}
        count = {}
        for item in oom_processes_list:
            process = item["name"]
            rss = item["rss"]
            if process in result:
                result[process] += rss
                count[process] += 1
            else:
                result[process] = rss
                count[process] = 1
        return sorted(result.items(), key=lambda x: x[1], reverse=True), count

    def quick_check(self):
        """Check how many oom incidents a log (or all logs) have...quickly"""
        source = self.get_log_source()

        all_log_files = []
        if source in ["journalctl", "dmesg"]:
            all_log_files.append((source, None))
        else:
            all_log_files.extend(
                ("file", log) for log in self.system.search_log_dir(self.log_file)
            )

        all_logs = {}
        for src, log in all_log_files:
            count = 0
            generator = self.log_lines(src, log_file=log)

            # Prevent errors if log file is empty
            try:
                _ = next(generator)
            except StopIteration:
                all_logs[log] = count
                continue

            for line in generator:
                if self.is_oom_start(line):
                    count += 1
            all_logs[log] = count
        return all_logs

    def print_pretty_oom_instance(self, oom_instance):
        """Method to print the OOM incident in a pretty format"""
        lines = []
        lines.append(
            self._warning("OOM Incident: ")
            + self._notice(str(oom_instance["incident_number"]))
        )
        # Don't hard fail if we are unable to extract the date/time from the log files
        start_time = (
            self._ok(oom_instance["start_time"].strftime("%a %b %d %X"))
            if oom_instance.get("start_time")
            else self._critical("Unable to extract datetime")
        )
        lines.append("Start Time: " + start_time)
        lines.append("System RAM: " + self._ok(str(oom_instance["system_ram"]) + " MB"))
        lines.append(
            "Total RAM at Incident: "
            + self._critical(str(format(oom_instance["total_mb"], ",")) + " MB")
        )

        lines.append(self._warning("The following processes were killed:"))
        for killed in oom_instance["killed"]:
            lines.append("  " + self._critical(killed))

        sorted_result, count = self.sorted_results(oom_instance["processes"])

        # Calculate column widths dynamically
        process_width = max(len(process) for process, _ in sorted_result) + 2
        count_width = max(len(str(count[process])) for process, _ in sorted_result) + 2
        rss_width = max(len(str(rss)) for _, rss in sorted_result) + 7

        # Print header row
        lines.append(self._header("Processes (showing top 10 processes):"))
        header_row = (
            "{process:<{process_width}}{count:<{count_width}}{rss:<{rss_width}}".format(
                process="PROCESS",
                process_width=process_width - 3,
                count="COUNT",
                count_width=count_width + 3,
                rss="RSS (MB)",
                rss_width=rss_width,
            )
        )
        lines.append(self._header("  " + header_row.rstrip()))

        # Print data rows
        for process, rss in sorted_result[:10]:
            data_row = "{process:<{process_width}}{count:<{count_width}}{rss:<{rss_width}}".format(
                process=process,
                process_width=process_width,
                count=count[process],
                count_width=count_width,
                rss=format(rss, ",") + " MB",
                rss_width=rss_width,
            )
            lines.append("  " + self._notice(data_row.rstrip()))

        lines.append("")
        return lines

    def print_pretty_log_info(self):
        """Method to print the OOM incident in a pretty format"""
        source = self.get_log_source()

        lines = []
        if source == "journalctl":
            lines.append(self._header("Using Journalctl: ") + self._ok("True"))
        elif source == "dmesg":
            lines.append(self._header("Using Dmesg: ") + self._ok("True"))
        else:
            lines.append(self._header("Using Log File: ") + self._ok(self.log_file))

        # Exit early if log file is empty
        if not self.log_start_time and not self.log_end_time:
            lines.append("")
            lines.append(self._warning("Log file appears to be empty"))
            lines.append("")
            print("\n".join(lines))
            sys.exit(0)

        lines.append(
            self._header("Log Start Time: ")
            + self._notice(self.log_start_time.strftime("%a %b %d %X"))
        )
        lines.append(
            self._header("Log End Time: ")
            + self._notice(self.log_end_time.strftime("%a %b %d %X"))
        )
        lines.append("")
        return lines


def run(system, options):
    reverse, quick = options.reverse, options.quick

    # Account for --all flag
    show_counter = -1 if options.show_all else options.show_counter

    # Parse the log file and extract OOM incidents
    analyzer = OOMAnalyzer(system)

    # Print system and log overview
    system.print_pretty()

    lines = []
    # Quick check
    if quick:
        all_results = analyzer.quick_check()
        lines.append(system.spacer)
        lines.append("")
        lines.append(system._warning("Performing a quick check..."))
        for log, count in all_results.items():
            lines.append(
                system._header("File {}: {} OOM incidents").format(
                    log, system._critical(str(count))
                )
            )
        lines.append("")
        lines.append(system.spacer)
        lines.append("")
        print("\n".join(lines))

        return sys.exit(0)

    # Find the largest incident
    largest_incident = None
    oom_instances = analyzer.analyze()

    # Exit early if no OOM incidents were found
    try:
        first_item = next(oom_instances)
    except (StopIteration, TypeError):
        source = analyzer.get_log_source()
        if source == "journalctl":
            msg = "No OOM incidents found! Journalctl has no OOM incidents."
        elif source == "dmesg":
            msg = "No OOM incidents found! Dmesg has no OOM incidents."
        else:
            msg = (
                "No OOM incidents found! "
                + analyzer.log_file
                + " has no OOM incidents."
            )
        lines.extend(analyzer.print_pretty_log_info())
        lines.append(system._ok(msg))
        lines.append("")
        print("\n".join(lines))
        return sys.exit(0)

    # Add the first item back to the iterator
    oom_instances = itertools.chain([first_item], oom_instances)

    # Handle the reverse flag and obtain the last incident
    if reverse:
        oom_instances = iter(reversed(list(oom_instances)))

    last_incident = None
    sliced_oom_instance_numbers = []
    oom_lines = []

    killed_services_count = defaultdict(int)
    for index, oom_instance in enumerate(oom_instances or []):
        # If reverse is set, we need to get the last incident, which is actually the first incident
        if reverse and last_incident is None:
            last_incident = oom_instance
        elif not reverse:
            last_incident = oom_instance

        if show_counter == -1 or index < show_counter:
            sliced_oom_instance_numbers.append(oom_instance["incident_number"])
            oom_lines.extend(analyzer.print_pretty_oom_instance(oom_instance))
        # Find the largest incident
        if (
            largest_incident is None
            or oom_instance["total_mb"] > largest_incident["total_mb"]
        ):
            largest_incident = oom_instance
        # Count killed services
        for killed_service in oom_instance["killed"]:
            killed_services_count[killed_service] += 1

    sorted_killed_service_count = sorted(
        killed_services_count.items(), key=lambda x: x[1], reverse=True
    )

    total_incidents = last_incident["incident_number"]

    # OOM Overview
    lines.extend(analyzer.print_pretty_log_info())
    lines.append(system.spacer)
    lines.append("")
    lines.append("")
    lines.append(
        system._critical(
            "WARNING: This device has run out of memory at least once in this log file."
        )
    )
    lines.append("")
    lines.append(system.spacer)
    lines.append("")
    lines.append(system._header("      Incident Overview"))
    lines.append(system.spacer)
    lines.append("")
    lines.append(
        system._header("OOM Incidents: ") + system._critical(str(total_incidents))
    )
    lines.append("Killed Services across all incidents: ")
    for service, count in sorted_killed_service_count:
        lines.append(
            "- "
            + system._warning(service)
            + ": killed "
            + system._critical(str(count))
            + " times"
        )
    lines.append("")
    lines.append(
        "Highest OOM Incident: "
        + system._warning("Incident Number " + str(largest_incident["incident_number"]))
    )
    lines.append(
        "Available RAM: " + system._warning(str(largest_incident["system_ram"]) + " MB")
    )
    lines.append(
        "Memory Used In Incident: "
        + system._critical(str(largest_incident["total_mb"]) + " MB")
    )
    lines.append("")
    lines.append(system.spacer)

    # Lets ALWAYS display the largest OOM incident. If it is not in the show_instances list,
    # display it.
    if largest_incident["incident_number"] not in sliced_oom_instance_numbers:
        lines.append("")
        lines.append(system.spacer)
        lines.append("")
        lines.append(system._critical("      Largest Incident"))
        lines.append(system.spacer)
        lines.append("")
        lines.append(system._header("The largest OOM incident in this log file was:"))
        lines.append("")
        lines.extend(analyzer.print_pretty_oom_instance(largest_incident))
        lines.append(system.spacer)

    lines.append("")
    lines.append(system._header("         OOM Incidents"))
    lines.append(system.spacer)
    lines.append("")
    show = "all" if show_counter == -1 else show_counter
    lines.append("Displaying {} OOM incidents:".format(show))
    lines.append("")

    # Display OOM incidents based on the show_counter and reverse (if provided)
    lines.extend(oom_lines)
    lines.append(system.spacer)
    lines.append("")

    # Only display this message if there are more oom incidents than the show_counter
    if total_incidents > show_counter and show_counter != -1:
        lines.append("")
        lines.append(
            system._warning(
                "(To increase the number of OOM incidents displayed, use the -s flag)"
            )
        )
        lines.append("")

    lines.append("")
    print("\n".join(lines))

    return sys.exit(0)


def validate_options(system, options):
    """Function to validate the options provided by the user"""
    valid_options = [options.file, options.journalctl, options.dmesg]
    active_options = [opt for opt in valid_options if opt]

    # Ensure only one logging option is specified
    if len(active_options) > 1:
        print(
            "Error: Please specify only a single option; a log file, dmesg or journalctl.\n"
            "You provided:\n- File: {}\n- Journalctl: {}\n- Dmesg: {}".format(
                options.file, options.journalctl, options.dmesg
            )
        )
        sys.exit(1)

    if options.journalctl:
        system.use_journalctl = options.journalctl
    elif options.dmesg:
        system.use_dmesg = options.dmesg
    elif options.file:
        # Check if the user has specified a valid log file
        if not os.path.isfile(options.file):
            print("File {} does not exist".format(options.file))
            sys.exit(1)
        system.log_to_use = options.file

    if not active_options:
        if not system.log_files:
            print(
                "Error: Unable to find log file for this Operating System. "
                "Please specify a log file with the -f option."
            )
            sys.exit(1)
        system.log_to_use = system.log_files[0]

    return system


def main():
    parser = OptionParser(usage="usage: %prog [option]")
    parser.add_option(
        "-f",
        "--file",
        dest="file",
        default=False,
        type="string",
        metavar="File",
        help="Specify a log to check. The default is to use the system default, "
        "which could also be journalctl.",
    )
    parser.add_option(
        "-s",
        "--show",
        dest="show_counter",
        type=int,
        metavar="Show",
        default=5,
        help="Override the default number of OOM incidents to show",
    )
    parser.add_option(
        "-a",
        "--all",
        dest="show_all",
        default=False,
        action="store_true",
        help="Show all OOM incidents found in the log file. If both -a and -s are provided, "
        "-a will take precedence.",
    )
    parser.add_option(
        "-r",
        "--reverse",
        dest="reverse",
        default=False,
        action="store_true",
        help="Show the most recent OOM incidents first. "
        "By default we show the fist OOM incidents found in the file, "
        "which are located at the beginning of the file.",
    )
    parser.add_option(
        "-j",
        "--journalctl",
        dest="journalctl",
        default=False,
        action="store_true",
        help="Investigate possible oom instances in the journalctl log file. ",
    )
    parser.add_option(
        "-d",
        "--dmesg",
        dest="dmesg",
        default=False,
        action="store_true",
        help="Investigate possible oom instances in the dmesg log file. ",
    )
    parser.add_option(
        "-q",
        "--quick",
        dest="quick",
        default=False,
        action="store_true",
        help="Display the scripts version number",
    )
    parser.add_option(
        "-V",
        "--version",
        dest="version",
        action="store_true",
        help="Display the scripts version number",
    )

    (options, _) = parser.parse_args()

    # Show the version number and exit
    if options.version:
        print("OOM Analyzer Version: {}".format(__version__))
        return sys.exit(0)

    system = System()

    # Validate the options provided by the user and the log file
    system = validate_options(system, options)

    # Print the script header
    main_header()

    return run(system, options)


if __name__ == "__main__":
    main()
