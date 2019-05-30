## Plesk Buddy

[![Build Status](https://travis-ci.org/dsgnr/pleskbuddy.svg?branch=master)](https://travis-ci.org/dsgnr/pleskbuddy)
[![Build Status](https://jenkins.handsoff.cloud/buildStatus/icon?job=pleskbuddy%2Fmaster)](https://jenkins.handsoff.cloud/job/pleskbuddy/job/master/)
![GitHub repo size](https://img.shields.io/github/repo-size/dsgnr/pleskbuddy.svg)

PleskBuddy is a script packed with useful commands to make using Plesk easier.

### Options

    -h, --help     show this help message and exit
    -v, --version  Shows version information
    --sub-list     Shows a list of subscriptions
    --domain-list  Shows a list of domains with their IP addresses
    --list-components  Creates a list of available components
    --install-component COMPONENT_INSTALL
                        Allows installation of available component
    --php-handler       Displays a list of domains with their respective PHP
                        handler

#### Info
Outputs a block of information for the user

    ➜ ./plesbuddy.py --info
    ==== Plesk Information ====
    Login URL: https://<public_ip_address>:8443/login?secret=<secret_random_login_string>
    Plesk version: 17.9.12
    Domain Count: 5

#### Listing Plesk subscriptions
Outputs a list of subscriptions

    ➜ ./plesbuddy.py --sub-list
    ==== Plesk Subscription List ====
    example1.com
    example2.com
    example3.com
    example4.com


#### Listing Plesk domains
Outputs a list of domains with their IP addresses

    ➜ ./plesbuddy.py --domain-list
    ==== Plesk Domain List ====
    +----+-------------------------------+-------------+----------------+
    | id | name                          | ipAddressId | ip_address     |
    +----+-------------------------------+-------------+----------------+
    |  1 | example1.com                  |           1 | 192.168.100.34 |
    |  2 | example2.com                  |           1 | 192.168.100.34 |
    |  3 | example3.com                  |           1 | 192.168.100.34 |
    |  4 | example4.com                  |           1 | 192.168.100.34 |
    +----+-------------------------------+-------------+----------------+

#### List available Plesk components
Creates a list of components that are either installed, updatable, or available to install

    ➜ ./plesbuddy.py --list-components
    ==== Plesk Component List ====
    Detecting installed product components.
        panel             [up2date] - Plesk
        bind              [up2date] - BIND DNS server
        postgresql        [install] - PostgreSQL server
        health-monitor    [install] - Server Health Monitor
        fail2ban          [install] - Fail2Ban
        selinux           [up2date] - SELinux policy
        l10n              [up2date] - All language localization for Plesk
        git               [up2date] - Git
        docker            [up2date] - Docker
        [...]

#### Install an available Plesk component
Allows the installation of an available component. A package highlighted as `[install]`
must be given as an argument from `--list-components`

    ➜ ./pleskbuddy.py --install-component php5.5
    [...]
    Running Transaction Check
    Installing: plesk-php55-5.5.38-centos7.17090117.x86_64 [1/30]
    Installing: plesk-php55-pdo-5.5.38-centos7.17090117.x86_64 [2/30]
    Installing: plesk-php55-cli-5.5.38-centos7.17090117.x86_64 [3/30]
    Installing: plesk-php55-xml-5.5.38-centos7.17090117.x86_64 [4/30]

    The changes were applied successfully.


#### List domain PHP handlers
Outputs a list of domains with their respective PHP handler

    ➜  ./pleskbuddy.py --php-handler
    ==== Plesk domains and their PHP handler ====
    +-------------------------------+-----------------+
    | name                          | php_handler_id  |
    +-------------------------------+-----------------+
    | 431848-pleskOnyx.racker.co.uk | fpm             |
    | example1.com                  | plesk-php70-fpm |
    | example2.com                  | plesk-php71-fpm |
    | example3.com                  | plesk-php72-fpm |
    | example4.com                  | plesk-php56-fpm |
    | rafa9006.com                  | plesk-php72-fpm |
    +-------------------------------+-----------------+
