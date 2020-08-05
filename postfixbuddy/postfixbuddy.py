#!/usr/bin/env python
# postfixbuddy.py created by Daniel Hand (daniel.hand@rackspace.co.uk)
# This is a recreation of pfHandle.perl but in Python.

from __future__ import absolute_import, division, print_function

# Standard Library
import argparse
import os
from os.path import join
import sys
import subprocess
from subprocess import call


__version__ = '0.2.0'


def get_options():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list', dest='list_queues',
                        action='store_true',
                        help='List all the current mail queues')
    parser.add_argument('-p', '--purge', dest='purge_queues', type=str,
                        choices=['active', 'bounce', 'corrupt',
                                 'deferred', 'hold', 'incoming'],
                        help='Purge messages from specific queues.')
    parser.add_argument('-m', '--message', dest='delete_mail', type=str,
                        help='Delete specific email based on mailq ID.')
    parser.add_argument('-c', '--clean', dest='clean_queues',
                        action='store_true',
                        help='Purge messages from all queues.')
    parser.add_argument('-H', '--hold', dest='hold_queues',
                        action='store_true',
                        help='Hold all mail queues.')
    parser.add_argument('-r', '--release', dest='release_queues',
                        action='store_true',
                        help='Release all mail queues from held state.')
    parser.add_argument('-f', '--flush', dest='process_queues',
                        action='store_true', help='Flush mail queues')
    parser.add_argument('-D', '--delete', dest='delete_by_search', type=str,
                        help='Delete based on subject or email address')
    parser.add_argument('-s', '--show', dest='show_message', type=str,
                        help='Show message from queue ID')
    parser.add_argument('-v', '--version', dest='show_version',
                        action='store_true',
                        help='Shows version information')
    return parser


# All variables defined in this script reply on finding the queue_directory.
# This defines the PF_DIR variable which is called later on.
PF_DIR = ""
try:
    GET_QUEUE_DIR = subprocess.Popen(['/usr/sbin/postconf',
                                      '-h', 'queue_directory'],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
    OUTPUT, ERROR = GET_QUEUE_DIR.communicate()
    if OUTPUT:
        PF_DIR = OUTPUT.split()[0]
except OSError:
    pass


class COLOR:
    RED = '\033[31m\033[1m'
    GREEN = '\033[32m\033[1m'
    YELLOW = '\033[33m\033[1m'
    BLUE = '\033[34m\033[1m'
    MAGENTA = '\033[35m\033[1m'
    CYAN = '\033[36m\033[1m'
    WHITE = '\033[37m\033[1m'
    RESET = '\033[0m'


# Variables
ACTIVE_QUEUE = PF_DIR + '/active'
BOUNCE_QUEUE = PF_DIR + '/bounce'
CORRUPT_QUEUE = PF_DIR + '/corrupt'
DEFERRED_QUEUE = PF_DIR + '/deferred'
HOLD_QUEUE = PF_DIR + '/hold'
INCOMING_QUEUE = PF_DIR + '/incoming'
QUEUE_LIST = ['Active', 'Bounce', 'Corrupt',
              'Deferred', 'Hold', 'Incoming']
QUEUE_TYPES = [ACTIVE_QUEUE, BOUNCE_QUEUE, CORRUPT_QUEUE,
               DEFERRED_QUEUE, HOLD_QUEUE, INCOMING_QUEUE]
PARSER = get_options()
ARGS = PARSER.parse_args()


def show_version():
    print(COLOR.GREEN + r'''
                    _    __ _      _               _     _
    _ __   ___  ___| |_ / _(_)_  _| |__  _   _  __| | __| |_   _
    | '_ \ / _ \/ __| __| |_| \ \/ / '_ \| | | |/ _` |/ _` | | | |
    | |_) | (_) \__ \ |_|  _| |>  <| |_) | |_| | (_| | (_| | |_| |
    | .__/ \___/|___/\__|_| |_/_/\_\_.__/ \__,_|\__,_|\__,_|\__, |
    |_|                                                     |___/

    version: ''' + __version__, COLOR.RESET)


def list_queues():
    print(COLOR.MAGENTA + '==== Mail Queue Summary ====' +
          COLOR.RESET)
    for index in range(len(QUEUE_LIST)):
        file_count = sum(len(files) for _, _, files in
                         os.walk(QUEUE_TYPES[index]))
        print(COLOR.YELLOW + QUEUE_LIST[index], 'Queue Count:' +
              COLOR.BLUE, file_count, COLOR.RESET)
    print


def purge_queues():
    print(COLOR.RED + 'Do you really want to purge the ' +
          ARGS.purge_queues + ' queue? (y/n): ' + COLOR.RESET)
    tty = open('/dev/tty')
    option_answer = tty.readline().strip()
    tty.close()
    if option_answer.lower() == 'y':
        call(['postsuper', '-d', 'ALL', ARGS.purge_queues])
        print(COLOR.GREEN + 'Purged all mail from the ' +
              ARGS.purge_queues + ' queue!' + COLOR.RESET)
    if option_answer.lower() != 'y':
        print(COLOR.RED + 'Exiting...' + COLOR.RESET)
        sys.exit(1)


def clean_queues():
    print(COLOR.RED + 'Do you really want to purge '
          'ALL mail queues? (y/n): ' + COLOR.RESET)
    tty = open('/dev/tty')
    option_answer = tty.readline().strip()
    tty.close()
    if option_answer.lower() == 'y':
        call(['postsuper', '-d', 'ALL'])
        print(COLOR.GREEN + 'Purged all mail queues!' + COLOR.RESET)
    if option_answer.lower() != 'y':
        print(COLOR.RED + 'Exiting...' + COLOR.RESET)
        sys.exit(1)


def delete_mail():
    print(COLOR.RED + 'Do you really want to delete mail ' +
          ARGS.delete_mail + '? (y/n): ' +
          COLOR.RESET)
    tty = open('/dev/tty')
    option_answer = tty.readline().strip()
    tty.close()
    if option_answer.lower() == 'y':
        call(['postsuper', '-d', ARGS.delete_mail])
        print(COLOR.GREEN + 'Deleted mail ID: ' + COLOR.YELLOW +
              ARGS.delete_mail + COLOR.GREEN + '!' + COLOR.RESET)
    if option_answer.lower() != 'y':
        print(COLOR.RED + 'Exiting...' + COLOR.RESET)
        sys.exit(1)


def hold_queues():
    call(['postsuper', '-h', 'ALL'])
    print(COLOR.GREEN + 'All mail queues now on hold!' + COLOR.RESET)


def release_queues():
    call(['postsuper', '-H', 'ALL'])
    print(COLOR.GREEN + 'Queues no longer in a held state!' + COLOR.RESET)


def process_queues():
    call(['postqueue', '-f'])
    print(COLOR.GREEN + 'Flushed all queues!' + COLOR.RESET)


def show_message():
    call(['postcat', '-q', ARGS.show_message])


def delete_by_search():
    count = 0
    for index in range(len(QUEUE_LIST)):
        for (dirname, dirs, files) in os.walk(QUEUE_TYPES[index]):
            for mail_id in files:
                thefile = os.path.join(dirname, mail_id)
                for line in open(thefile):
                    if ARGS.delete_by_search in line:
                        subprocess.Popen(['/usr/sbin/postsuper',
                                          '-d', mail_id],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
                        count += 1
    print(COLOR.BLUE + 'Looking for mail containing: \"' +
          ARGS.delete_by_search + '\"...' + COLOR.RESET)
    if count == 0:
        print(COLOR.RED + '\"' + ARGS.delete_by_search +
              '\" not found in search.' + COLOR.RESET)
    if count != 0:
        print(COLOR.GREEN + 'Total deleted: {0}'.format(count) + COLOR.RESET)


def main():
    # If the PF_DIR is empty, Postfix is either not installed, or broke'd
    if not PF_DIR:
        sys.exit('Unable to find Postfix queue directory!')

    if ARGS.show_version:
        return show_version()
    if ARGS.list_queues:
        return list_queues()
    if ARGS.purge_queues:
        return purge_queues()
    if ARGS.clean_queues:
        return clean_queues()
    if ARGS.delete_mail:
        return delete_mail()
    if ARGS.hold_queues:
        return hold_queues()
    if ARGS.release_queues:
        return release_queues()
    if ARGS.process_queues:
        return process_queues()
    if ARGS.show_message:
        return show_message()
    if ARGS.delete_by_search:
        return delete_by_search()
    return list_queues()


if __name__ == '__main__':
    main()
