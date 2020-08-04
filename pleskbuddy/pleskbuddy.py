#!/bin/python
# pleskbuddy.py created by Dan Hand

from __future__ import absolute_import, division, print_function

# Standard Library
import argparse
import sys
from subprocess import call, PIPE, Popen
from urllib2 import urlopen


__version__ = '1.0.0'


def options():
    psa_parser = argparse.ArgumentParser()
    psa_parser.add_argument('-v', '--version', dest='show_version',
                            action='store_true', help='Shows version information')
    psa_parser.add_argument('--sub-list', dest='subscription_list',
                            action='store_true', help='Shows a list of subscriptions')
    psa_parser.add_argument('--info', dest='info',
                            action='store_true', help='Shows a list of subscriptions')
    psa_parser.add_argument('--domain-list', dest='domain_list',
                            action='store_true', help='Shows a list of domains with their IP addresses')
    psa_parser.add_argument('--list-components', dest='show_components',
                            action='store_true', help='Creates a list of available components')
    psa_parser.add_argument('--install-component', dest='component_install', type=str,
                            help='Allows installation of available component')
    psa_parser.add_argument('--php-handler', dest='php_handler',
                            action='store_true', help='Displays a list of domains with their respective PHP handler')
    return psa_parser


class Color(object):
    RED = '\033[31m\033[1m'
    GREEN = '\033[32m\033[1m'
    YELLOW = '\033[33m\033[1m'
    BLUE = '\033[34m\033[1m'
    MAGENTA = '\033[35m\033[1m'
    CYAN = '\033[36m\033[1m'
    WHITE = '\033[37m\033[1m'
    RESET = '\033[0m'


# Variables
PSA_PARSER = options()
PSA_ARGS = PSA_PARSER.parse_args()


def show_version():
    print(Color.CYAN + r'''
           _           _    _               _     _
     _ __ | | ___  ___| | _| |__  _   _  __| | __| |_   _
    | '_ \| |/ _ \/ __| |/ / '_ \| | | |/ _` |/ _` | | | |
    | |_) | |  __/\__ \   <| |_) | |_| | (_| | (_| | |_| |
    | .__/|_|\___||___/_|\_\_.__/ \__,_|\__,_|\__,_|\__, |
    |_|                                             |___/

    version: %s ''' % (__version__), Color.RESET)


def info():
    domain_count = Popen('MYSQL_PWD=`cat /etc/psa/.psa.shadow` mysql -u admin -Dpsa -sNe \
                         "select count(*) from domains"', stdout=PIPE, shell=True).communicate()[0].strip()
    plesk_version = open('/usr/local/psa/version', "r").read().split()
    login_url = Popen('plesk login -relative-url', stdout=PIPE, shell=True).communicate()[0].strip()
    public_ip = urlopen('https://ipv4.icanhazip.com').read().strip()
    psa_info = (Color.MAGENTA + '==== Plesk Information ====\n' + Color.RESET +
                Color.MAGENTA + 'Login URL: ' + Color.RESET + 'https://{0}:8443{1}\n' + Color.MAGENTA +
                'Plesk version: ' + Color.RESET + '{2}\n' + Color.MAGENTA +
                'Domain Count: ' + Color.RESET + '{3}').format(public_ip, login_url, plesk_version[0], str(domain_count))
    print(psa_info)


def subscription_list():
    print(Color.MAGENTA + '==== Plesk Subscription List ====' + Color.RESET)
    subscription_list = 'plesk bin subscription --list'
    call(subscription_list, shell=True)


def domain_list():
    print(Color.MAGENTA + '==== Plesk Domain List ====' + Color.RESET)
    domain_list = 'MYSQL_PWD=`cat /etc/psa/.psa.shadow` mysql -u admin -Dpsa -e"SELECT dom.id, dom.name, \
                   ia.ipAddressId, iad.ip_address FROM domains dom LEFT JOIN DomainServices d ON \
                   (dom.id = d.dom_id AND d.type = \'web\') LEFT JOIN IpAddressesCollections ia ON \
                   ia.ipCollectionId = d.ipCollectionId LEFT JOIN IP_Addresses iad ON iad.id = ia.ipAddressId"'
    call(domain_list, shell=True)


def show_components():
    print(Color.MAGENTA + '==== Plesk Component List ====' + Color.RESET)
    component_list = 'plesk installer --select-release-current --show-components'
    call(component_list, shell=True)


def component_install():
    call(['plesk', 'installer', '--select-release-current',
          '--install-component', PSA_ARGS.component_install])


def php_handler():
    print(Color.MAGENTA + '==== Plesk domains and their PHP handler ====' + Color.RESET)
    domains_with_php = 'plesk db "select d.name,h.php_handler_id from domains d join hosting h on h.dom_id=d.id"'
    call(domains_with_php, shell=True)


def main():
    # Check if Plesk is installed
    try:
        _ = open('/usr/local/psa/version', 'r')
    except IOError as ex:
        sys.exit('It doesn\'t look like Plesk is installed!')
    
    if PSA_ARGS.show_version:
        show_version()
    elif PSA_ARGS.subscription_list:
        subscription_list()
    elif PSA_ARGS.domain_list:
        domain_list()
    elif PSA_ARGS.show_components:
        show_components()
    elif PSA_ARGS.component_install:
        component_install()
    elif PSA_ARGS.php_handler:
        php_handler()
    else:
        info()


if __name__ == '__main__':
    main()
