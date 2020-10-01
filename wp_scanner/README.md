# wp_version_scanner
Wordpress Version Scanner 

Now with 9000% more status so you know whats going on!

```
usage example:

$ perl wpscan.pl /var/www --verbose
|--| Latest wordpress version is: 4.9.8 (August 2, 2018)
|--| Searching /var/www for any wordpress installations, please wait...
|!!|     *  (2.0.4) [ PLEASE UPDATE (July 29, 2006) ] /var/www/wordpresstest/version.php
|--| Summary Report for /var/www:
|--| Found 1 'potential' wordpress installations:
|!!|  -> None up to date.
|!!|  -> 1 require updating.
|--| List of wordpress versions I looked up, by release date:
2.0.4 => July 29, 2006
4.9.8 => August 2, 2018 (Latest)
Done.

# perl wpscan.pl --help
Usage: wpscan.pl [space delimited list of directories] [OPTIONS]
If no options are specified, the basic tests will be run.
        -b, --bbcode            Print output in BBCODE style (useful for forums or ticketing systems that support bbcode)
        -h, --help              Print this help message
        -L, --light-term        Show colours for a light background terminal.
        -n, --nocolor           Use default terminal color, dont try to be all fancy!
        -v, --verbose           Use verbose output (display list of wordpress versions found and where, and what version)

default to /var/www if no argument found
default to ANSI colors unless --bbcode option is used
```
