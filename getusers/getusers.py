#!/usr/bin/python


###################################
# Imports
###################################
from __future__ import print_function, with_statement
import argparse
import sys
import pwd
import os
import re
import subprocess
import time
import datetime
import pydoc
import time
import struct

__version__ = '1.0.2'

###################################
# Useful variables for the script
###################################


def options():
    '''Processes commandline arguments. Returns the argparse parser'''
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-v', '--version', dest='show_version',
                        action='store_true', help='Shows script version')

    parser.add_argument('-s', '--system-users',
                        dest='show_system_users',
                        action='store_true',
                        help='Show system users on the device'
                        )

    parser.add_argument('-u', '--users',
                        dest='show_users',
                        action='store_true',
                        help='Show users on this device. This is the default'
                        )

    parser.add_argument('-a', '--all-users',
                        dest='show_all_users',
                        action='store_true',
                        help='Show all users on this device.'
                        )

    parser.add_argument('-F', '--show-full',
                        dest='show_full_output',
                        action='store_true',
                        help='Show the full user information'
                        )

    parser.add_argument('-h', '--help',
                        dest='help',
                        action='store_true',
                        help='Show this help message and exit'
                        )
    return parser


class Color(object):
    '''
    This class contains the colors for commandline output
    Available colors:
    Red, Green, Yellow, Blue, Magenta, Cyan, White, Reset
    '''
    RED = '\033[31m\033[1m'
    GREEN = '\033[32m\033[1m'
    YELLOW = '\033[33m\033[1m'
    BLUE = '\033[34m\033[1m'
    MAGENTA = '\033[35m\033[1m'
    CYAN = '\033[36m\033[1m'
    WHITE = '\033[37m\033[1m'
    RESET = '\033[0m'


class Config(object):
    '''
    This class contains configuration variables for use in the script

    Attributes:
        DEFS_FILE:      Location of the linux defs file
        GROUP_FILE:     Location of the system groups file
        PASSWD_FILE:    Location of the local users (passwd) file
        SUDO_FILE:      Location of the sudoers file
        WTMP_FILE:      Location of the wtmp file (Containing login history)

        HEADER_STANDARD:    Header rows for the output table from the script
        HEADER_FULL:        Header rows for the output table from the script

        LAST_CMD:    Command to execute to get the login history on the device
    '''
    DEFS_FILE = '/etc/login.defs'
    GROUP_FILE = '/etc/group'
    PASSWD_FILE = '/etc/passwd'
    SUDO_FILE = '/etc/sudoers'
    WTMP_FILE = '/var/log/wtmp'
    LAST_FILE = '/var/log/lastlog'
    # Headers for table output
    HEADER_STANDARD = ['ID', 'User', 'Home', 'Shell', 'Sudo', 'Last Login']
    HEADER_FULL = ['ID', 'User', 'Group ID', 'GECOS',
                   'Home', 'Shell', 'Sudo', 'Last Login']

    # Other configurations
    LAST_CMD = 'last -w -i -f '


class Users(object):
    '''
    This class stores runtime data for the script

    Attributes:
        UID_MIN:        The minimum ID of users
        UID_MAX:        The maximum ID of users
        SYS_UID_MIN:    The minimum ID of system users
        SYS_UID_MAX:    The maximum ID of system users

        SUDO_CONTENT:   An array of the content from the sudoers file
        GROUP_CONTENT:  An array of the content from the groups file

        USERS:          The output from the pwd module with all users
        LOGINS:         Contains the login history of users
    '''
    UID_MIN = 1000
    UID_MAX = 60000
    SYS_UID_MIN = 0
    SYS_UID_MAX = 999

    SUDO_CONTENT = None
    GROUP_CONTENT = None
    USERS = None
    LOGINS = []

###################################
# Non-Display functions for the script
###################################


def init_variables():
    '''Initialises and retrives data for later use in the script'''
    # First test we can open all the required files, exit if not
    # Check access to passwd
    try:
        open(Config.PASSWD_FILE, 'r')
    except IOError:
        sys.exit('Unable to open ' + Config.PASSWD_FILE)

    # Check access to groups
    try:
        GROUP_CONTENT = open(Config.GROUP_FILE, 'r')
        Users.GROUP_CONTENT = GROUP_CONTENT.readlines()
    except IOError:
        sys.exit('Unable to open ' + Config.GROUP_FILE)

    # Get values from defs
    try:
        with open(Config.DEFS_FILE, 'r') as f:
            lines = list(line for line in (l.strip() for l in f) if line)
    except IOError:
        sys.exit('Unable to open ' + Config.DEFS_FILE)

    for l in lines:
        fields = l.strip().split()
        if fields[0] == "UID_MIN":
            Users.UID_MIN = int(fields[1])
            continue
        elif fields[0] == "UID_MAX":
            Users.UID_MAX = int(fields[1])
            continue
        elif fields[0] == "SYS_UID_MIN":
            Users.SYS_UID_MIN = int(fields[1])
            continue
        elif fields[0] == "SYS_UID_MAX":
            Users.SYS_UID_MAX = int(fields[1])
            continue
        else:
            continue

    # Check access to sudoers
    try:
        CHECK_SUDO = open(Config.SUDO_FILE, 'r')
        Users.SUDO_CONTENT = CHECK_SUDO.readlines()
    except IOError:
        sys.exit('Unable to open ' + Config.SUDO_FILE)

    # Get all users from the system into a table
    Users.USERS = pwd.getpwall()

    # Get all of the logins from lastlog
    try:
        last_file = open(Config.LAST_FILE, 'rb')
    except IOError:
        sys.exit("Unable to open " + Config.LAST_FILE)

    uid = 0
    chunk_size = struct.calcsize('=L32s256s')
    for chunk in read_in_chunks(last_file, chunk_size):
        # Unpack the binary data
        row = list(struct.unpack('=L32s256s', chunk))
        timestamp = row[0]
        if(timestamp == 0):
            # If there is no login, continue
            uid = uid + 1
            continue
        # Convert the timestamp
        datetime = time.ctime(timestamp)
        # Strip trailing null characters
        terminal = row[1].rstrip('\x00'.encode())
        host = row[2].rstrip('\x00'.encode())

        login = [uid, datetime, host, terminal]
        Users.LOGINS.append(login)
        uid = uid + 1

    last_file.close()


def get_system_users():
    '''Get system users. Returns array'''
    users_table = []
    for x in Users.USERS:
        if(x[2] <= Users.SYS_UID_MAX):
            if is_sudo(x[0]):
                sudo = "yes"
            else:
                sudo = "no"
            last_login = get_last_login(x[2])
            users_table.append([x[2], x[0], x[5], x[6], sudo, last_login])
    return users_table


def get_system_full():
    '''Get system users and GECOS and group ID. Returns array'''
    users_table = []
    for x in Users.USERS:
        if(x[2] <= Users.SYS_UID_MAX):
            if is_sudo(x[0]):
                sudo = "yes"
            else:
                sudo = "no"
            last_login = get_last_login(x[2])
            gecos = x[4]
            # Truncate comment field to stop output being huge
            gecos = (gecos[:16] + "..") if len(gecos) > 18 else gecos
            if(gecos == ""):
                gecos = "None"
            users_table.append(
                [x[2], x[0], x[3], gecos, x[5], x[6], sudo, last_login])
    return users_table


def get_users():
    '''Get non system users. Returns array'''
    users_table = []
    for x in Users.USERS:
        if(Users.UID_MIN <= x[2] <= Users.UID_MAX):
            if is_sudo(x[0]):
                sudo = "yes"
            else:
                sudo = "no"
            last_login = get_last_login(x[2])
            users_table.append([x[2], x[0], x[5], x[6], sudo, last_login])
    return users_table


def get_users_full():
    '''Get non system users and GECOS and group ID. Returns array'''
    users_table = []
    for x in Users.USERS:
        if(Users.UID_MIN <= x[2] <= Users.UID_MAX):
            if is_sudo(x[0]):
                sudo = "yes"
            else:
                sudo = "no"
            last_login = get_last_login(x[2])
            gecos = x[4]
            # Truncate comment field to stop output being huge
            gecos = (gecos[:16] + "..") if len(gecos) > 18 else gecos
            if(gecos == ""):
                gecos = "None"
            users_table.append(
                [x[2], x[0], x[3], gecos, x[5], x[6], sudo, last_login])
    return users_table


def get_all_users():
    '''Gets all users. Returns array'''
    users_table = []
    for x in Users.USERS:
        if is_sudo(x[0]):
            sudo = "yes"
        else:
            sudo = "no"
        last_login = get_last_login(x[2])
        users_table.append([x[2], x[0], x[5], x[6], sudo, last_login])
    return users_table


def get_all_users_full():
    '''Gets all users and GECOS and Group ID. Returns array'''
    users_table = []
    for x in Users.USERS:
        if is_sudo(x[0]):
            sudo = "yes"
        else:
            sudo = "no"
        last_login = get_last_login(x[2])
        gecos = x[4]
        # Truncate comment field to stop output being huge
        gecos = (gecos[:16] + "..") if len(gecos) > 18 else gecos
        if(gecos == ""):
            gecos = "None"
        users_table.append(
            [x[2], x[0], x[3], gecos, x[5], x[6], sudo, last_login])
    return users_table


def is_sudo(user):
    '''
    Checks if a provided username has sudo privileges.

    Parameters:
        user (string):     The username to be checked

    Returns:
        boolean:    True / False whether the user is sudo or not
    '''
    # If they are in the sudo file (Just checks if their name is listed)
    for line in Users.SUDO_CONTENT:
        if user+" " in line:
            return True

    for line in Users.GROUP_CONTENT:
        fields = line.strip().split(':')
        try:
            fields[0]
        except IndexError:
            continue
        if (
            fields[0] == "wheel"
            or fields[0] == "admin"
            or fields[0] == "sudo"
        ):
            groupusers = fields[3].split(',')
            for groupuser in groupusers:
                if groupuser == user:
                    return True

    return False


def get_last_login(user):
    '''
    Gets the last login time for a user.

    Parameters:
        user (string): The user id to be checked

    Returns:
        string:    The last login found (None found, if none)
    '''
    # Loop over the array we earlier stored from wtmp
    for x in Users.LOGINS:
        if(x[0] == user):
            login = x[1]
            return login

    return "None found"


def get_column_widths(table):
    '''
    Gets the maximum widths for each column

    Parameters:
        table (array):  The table to check the widths for

    Returns:
        columns (list): The coulumn widths for the table
    '''
    column_widths = []
    for x in table:
        for i in range(len(x)):
            # The length of this field
            length = len(str(x[i]))
            # If a lengnth is already in the table, compare
            if len(x) == len(column_widths):
                if length > column_widths[i]:
                    column_widths[i] = length
            else:
                column_widths.append(length)
    return column_widths


def read_in_chunks(file, chunk_size=1024*64):
    '''
    Reads the provided file in specified chunks

    Parameters:
        file: The open file handler
        chumk_size: The chunk size to be read

    Return:
        chunk: The read chunk from the file
    '''
    while True:
        chunk = file.read(chunk_size)
        if chunk:
            yield chunk
        else:
            # The chunk was empty, which means we're at the end
            # of the file
            return

###################################
# Display functions for the script
###################################


def show_header():
    '''Prints the header for the script (ASCII Art)'''
    print(Color.GREEN + r'''
   ______     __     __  __
  / ____/__  / /_   / / / /_______  __________
 / / __/ _ \/ __/  / / / / ___/ _ \/ ___/ ___/
/ /_/ /  __/ /_   / /_/ (__  )  __/ /  (__  )
\____/\___/\__/   \____/____/\___/_/  /____/
    ''', Color.RESET)


def show_version():
    '''Prints the version number of the script'''
    print(Color.GREEN + r'''Version: %s ''' % (__version__), Color.RESET)


def print_table(headers, table):
    '''
    Prints a formatted table with the provided headers and table content

    Parameters:
        headers (array):    The row of headers to go at the top of the table
        table (array):      The table content

    Returns: None
    '''
    if(len(table) == 0):
        print(Color.RED + "No users found!" + Color.RESET)
        return

    column_widths = get_column_widths(table)

    print(Color.GREEN, end='')

    for i in range(len(headers)):
        row = headers[i]
        width = column_widths[i] + 3
        print("".join(str(row).ljust(width)), end="")

    print(Color.RESET)
    print(Color.CYAN, end='')

    for x in table:
        for i in range(len(x)):
            row = x[i]
            width = column_widths[i] + 3
            print("".join(str(row).ljust(width)), end="")
        print("")

    print(Color.RESET)
    return

###################################
# Main features
###################################


def show_system_users(ARGS):
    '''Main Feature: Retreives and prints system users'''
    if ARGS.show_full_output:
        users_table = get_system_full()
        print_table(Config.HEADER_FULL, users_table)

    else:
        users_table = get_system_users()
        print_table(Config.HEADER_STANDARD, users_table)
    return


def show_users(ARGS):
    '''Main Feature: Retreives and prints standard users'''
    if ARGS.show_full_output:
        users_table = get_users_full()
        print_table(Config.HEADER_FULL, users_table)

    else:
        users_table = get_users()
        print_table(Config.HEADER_STANDARD, users_table)
    return


def show_all_users(ARGS):
    '''Main Feature: Retreives and prints all users'''
    if ARGS.show_full_output:
        users_table = get_all_users_full()
        print_table(Config.HEADER_FULL, users_table)
    else:
        users_table = get_all_users()
        print_table(Config.HEADER_STANDARD, users_table)
    return

###################################
# Main execution for the script
###################################


def main():
    PARSER = options()
    ARGS = PARSER.parse_args()

    if ARGS.help:
        PARSER.print_help()
        sys.exit()

    if ARGS.show_version:
        show_version()
        sys.exit()

    '''Main script execution'''
    show_header()
    init_variables()

    if ARGS.show_system_users:
        print(Color.MAGENTA + r"Showing system users", Color.RESET)
        print("")
        show_system_users(ARGS)
        sys.exit()

    if ARGS.show_users:
        print(Color.MAGENTA + r"Showing standard users", Color.RESET)
        print("")
        show_users(ARGS)
        sys.exit()

    if ARGS.show_all_users:
        print(Color.MAGENTA + r"Showing all users", Color.RESET)
        print("")
        show_all_users(ARGS)
        sys.exit()

    # Catch all, but default just show additional users
    print(Color.MAGENTA + r"Default: Showing standard users", Color.RESET)
    print("")
    show_users(ARGS)
    sys.exit()


if __name__ == '__main__':
    main()
