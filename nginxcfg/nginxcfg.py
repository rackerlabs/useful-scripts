#!/usr/bin/env python
import __future__  # pylint: disable=unused-import
import re
import os
from optparse import OptionParser


__version__ = "1.0.1"


COLOURS = {
    "GREEN": '\033[1;32m',
    "RESET": '\033[0m',
    "WHITE": '\033[1m',
    "CYAN": '\033[96m',
}


class nginxCfg:
    """
    A class for nginxCfg functionalities
    """

    def _get_vhosts(self):
        """
        get vhosts
        """
        ret = []
        for f in self._get_all_config():
            ret += self._get_vhosts_info(f)
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
        path = orig_path = self._strip_line(line.split()[1])
        included_from_dir = os.path.dirname(parent)

        if not os.path.isabs(path):
            """ Path is relative - first check if path is
                relative to 'current directory' """
            path = os.path.join(included_from_dir, self._strip_line(path))
            if not os.path.exists(os.path.dirname(path)) or \
                    not os.path.isfile(path):
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
        config_file = config_file or "/etc/nginx/nginx.conf"
        ret = [config_file]

        with open(config_file, "r") as config_data:
            for line in [line.strip().strip(';') for line in config_data]:
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
            for line_num, _ in enumerate(vhost_data):
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

    def get_vhosts(self, exclude_string):
        vhosts_list = self._get_vhosts()
        print("{0}nginx vhost configuration:{1}".format(
            COLOURS["WHITE"], COLOURS["RESET"]))
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
                    except:  # pylint: disable=bare-except
                        ip = '*'
                        port = ip_port[0]
                servername = vhost.get('servername', None)
                serveralias = vhost.get('alias', None)
                line_number = vhost.get('l_num', None)
                config_file = vhost.get('config_file', None)
                try:
                    if exclude_string in servername:
                        continue
                    if any(exclude_string in x for x in serveralias):
                        serveralias = \
                            [a for a in serveralias if exclude_string not in a]
                except TypeError:  # Used to skip empty servernames
                    pass
                print("{0}:{1} is a Virtualhost".format(ip, port))
                print("\tport {0} namevhost {1} {2} {3} ({4}:{5})".format(port,
                      COLOURS["GREEN"],
                      servername,
                      COLOURS["RESET"],
                      config_file,
                      line_number))
                for alias in serveralias:
                    print("\t\talias {0} {1} {2}".format(COLOURS["CYAN"],
                          alias,
                          COLOURS["RESET"]))


def main():
    n = nginxCfg()

    parser = OptionParser(usage='usage: %prog [option]')
    parser.add_option(
        "-v", "--version",
        action="store_true",
        default=False,
        dest="version",
        help="Show script version")
    parser.add_option(
        "-e", "--exclude",
        action="store",
        dest="exclude",
        metavar="<exclude word>",
        help="Exclude items from output")

    (options, _) = parser.parse_args()
    exclude_string = None

    if options.exclude:
        exclude_string = options.exclude

    if options.version:
        print("Script Version: {0}".format(__version__))
        return

    n.get_vhosts(exclude_string)


if __name__ == "__main__":
    try:
        main()
    except IOError as ex:
        print("{0}\nIs nginx installed?".format(ex))
