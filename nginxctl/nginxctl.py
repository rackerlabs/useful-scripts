#!/usr/bin/env python
import subprocess
import re
import sys
import os
import urllib2


class bcolors:
    """
    This class is to display differnet colour fonts
    """
    GREEN = '\033[1;32m'
    RESET = '\033[0m'
    WHITE = '\033[1m'
    CYAN = '\033[96m'


class nginxCtl:
    """
    A class for nginxCtl functionalities
    """


    def _get_vhosts(self):
        """
        get vhosts
        """
        ret = []
        for f in self._get_all_config():
            ret += self._get_vhosts_info(f)
        #print ret
        return ret


    def _strip_line(self, path, remove=None):
        """ Removes any trailing semicolons, and all quotes from a string
        """
        if remove is None:
            remove = ['"', "'", ';']
        for c in remove:
            if c in path:
                path = path.replace(c, '')
        return path


    def _get_includes_line(self, line, parent, root):
        """ Reads a config line, starting with 'include', and returns a list
            of files this include corresponds to. Expands relative paths,
            unglobs globs etc.
        """
        path = self._strip_line(line.split()[1])
        orig_path = path
        included_from_dir = os.path.dirname(parent)

        if not os.path.isabs(path):
            """ Path is relative - first check if path is
                relative to 'current directory' """
            path = os.path.join(included_from_dir, self._strip_line(path))
            if not os.path.exists(os.path.dirname(path)) or not os.path.isfile(path):
                """ If not, it might be relative to the root """
                path = os.path.join(root, orig_path)

        if os.path.isfile(path):
            return [path]
        elif '/*' not in path and not os.path.exists(path):
            """ File doesn't actually exist - probably IncludeOptional """
            return []

        """ At this point we have an absolute path to a basedir which
            exists, which is globbed
        """
        basedir, extension = path.split('/*')
        try:
            if extension:
                return [
                    os.path.join(basedir, f) for f in os.listdir(
                        basedir) if f.endswith(extension)]

            return [os.path.join(basedir, f) for f in os.listdir(basedir)]
        except OSError:
            return []


    def _get_all_config(self, config_file=None):
        """
        Reads all config files, starting from the main one, expands all
        includes and returns all config in the correct order as a list.
        """
        if config_file is None:
            config_file = "/etc/nginx/nginx.conf"
        else:
            config_file
        ret = [config_file]

        config_data = open(config_file, 'r').readlines()

        for line in [line.strip().strip(';') for line in config_data]:
            if line.startswith('#'):
                continue
            line = line.split('#')[0]
            if line.startswith('include'):
                includes = self._get_includes_line(line,
                                                   config_file,
                                                   "/etc/nginx/")
                for include in includes:
                    try:
                        ret += self._get_all_config(include)
                    except IOError:
                        pass
        return ret


    def _get_vhosts_info(self, config_file):
        server_block_boundry = []
        server_block_boundry_list = []
        vhost_data = open(config_file, "r").readlines()
        open_brackets = 0
        found_server_block = False
        for line_number, line in enumerate(vhost_data):
            if line.startswith('#'):
                continue
            line = line.split('#')[0]
            line = line.strip().strip(';')
            if re.match(r"server.*{", line):
                server_block_boundry.append(line_number)
                found_server_block = True
            if '{' in line:
                open_brackets += 1
            if '}' in line:
                open_brackets -= 1
            if open_brackets == 0 and found_server_block:
                server_block_boundry.append(line_number)
                server_block_boundry_list.append(server_block_boundry)
                server_block_boundry = []
                found_server_block = False

        server_dict_ret = []
        for server_block in server_block_boundry_list:
            alias = []
            ip_port = []
            server_name_found = False
            server_dict = {}
            stored = ''
            for line_num, li in enumerate(vhost_data):
                if line_num >= server_block[0]:
                    l = vhost_data[line_num]
                    if line_num >= server_block[1]:
                        server_dict['alias'] = alias
                        server_dict['l_num'] = server_block[0]
                        server_dict['config_file'] = config_file
                        server_dict['ip_port'] = ip_port
                        server_dict_ret.append(server_dict)
                        server_name_found = False
                        break
    
                    if l.startswith('#'):
                        continue
                    l = l.split('#')[0]
    
                    if not l.strip().endswith(';'):
                        if line_num != server_block[0]:
                            stored += l.strip() + ' '
                        continue
                    else:
                        l = stored + l
                        l = l.strip().strip(';')
                        stored = ''

                    if l.startswith('server_name') and server_name_found:
                        alias += l.split()[1:]
    
                    if l.startswith('server_name'):
                        if l.split()[1] == "_":
                            server_dict['servername'] = "default_server_name"
                        else:
                            server_dict['servername'] = l.split()[1]
                        server_name_found = True
                        if len(l.split()) >= 2:
                            alias += l.split()[2:]
                    if l.startswith('listen'):
                        ip_port.append(l.split()[1])
        return server_dict_ret


    def get_vhosts(self):
        vhosts_list = self._get_vhosts()
        print "%snginx vhost configuration:%s" % (bcolors.WHITE, bcolors.RESET)
        for vhost in vhosts_list:
            ip_ports = vhost['ip_port']
            for ip_port_x in ip_ports:
                if '[::]' in ip_port_x:
                    pattern = re.compile(r'(\[::\]):(\d{2,5})')
                    pattern_res = re.match(pattern, ip_port_x)
                    ip = pattern_res.groups()[0]
                    port = pattern_res.groups()[1]
                else:
                    ip_port = ip_port_x.split(':')
                    try:
                        ip = ip_port[0]
                        port = ip_port[1]
                    except:
                        ip = '*'
                        port = ip_port[0]
                servername = vhost.get('servername', None)
                serveralias = vhost.get('alias', None)
                line_number = vhost.get('l_num', None)
                config_file = vhost.get('config_file', None)
                print "%s:%s is a Virtualhost" % (ip, port)
                print "\tport %s namevhost %s %s %s (%s:%s)" % (port,
                                                                bcolors.GREEN,
                                                                servername,
                                                                bcolors.RESET,
                                                                config_file,
                                                                line_number)
                for alias in serveralias:
                    print "\t\talias %s %s %s" % (bcolors.CYAN,
                                                  alias,
                                                  bcolors.RESET)


def main():
    n = nginxCtl()
	
    if len(sys.argv) == 1:
        n.get_vhosts()
    else:
	print "No options available"
	print "Re-run script with NO options"
if __name__ == "__main__":
    main()
