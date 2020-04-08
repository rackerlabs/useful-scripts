# Nginxcfg

# ![Build Status](https://github.com/LukeShirnia/nginxcfg/workflows/nginxcfg/badge.svg)

The nginxcfg allows to control some of the functionlities of nginx daemon.
This tool is similar to apachectl and which main feature is to list
domains configured on a nginx webserver.

### Download/Installation
```
clone repo
cd nginxcfg
python nginxcfg.py
```

### Usage
```
Usage: nginxcfg.py [option]

Options:
  -h, --help            show this help message and exit
  -v, --version         Show script version
  -e <exclude word>, --exclude=<exclude word>
                        Exclude items from output
```

Here is an example of running the option to discover virtual hosts:
```
# python nginxctl.py -S
nginx vhost configuration:
*:8080 is a Virtualhost
	port 8080 namevhost  example.com  (/etc/nginx/sites-enabled/example.com:5)
[::]:80 is a Virtualhost
	port 80 namevhost  example.com  (/etc/nginx/sites-enabled/example.com:5)
```
