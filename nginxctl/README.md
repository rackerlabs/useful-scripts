<h1>NginxCtl</h1>

### Jenkins ###

[![Build Status](https://jenkins.lukeslinux.com/buildStatus/icon?job=nginxCtl)](https://jenkins.lukeslinux.com/job/nginxCtl/)

### Travis ###

[![Build Status](https://travis-ci.org/LukeShirnia/nginxctl.svg?branch=master)](https://travis-ci.org/LukeShirnia/nginxctl)

This tool is a simplification of the tool: https://github.com/rackerlabs/nginxctl
Functionaility has been stripped, now it simply gathers all nginx server blocks and a summary of the information

<h2>Download/Installation</h2>

```
wget https://raw.githubusercontent.com/LukeShirnia/nginxctl/master/nginxctl.py -O nginxctl.py 
python nginxctl.py
```

Here is an example of running the script to discover virtual hosts

```
# python nginxctl.py
nginx vhost configuration:
*:8080 is a Virtualhost
	port 8080 namevhost  example.com  (/etc/nginx/sites-enabled/example.com:5)
[::]:80 is a Virtualhost
	port 80 namevhost  example.com  (/etc/nginx/sites-enabled/example.com:5)

```
