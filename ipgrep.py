import ipaddress
import os
import glob
import re
import pickle
import hashlib
from tools import str2network


class CompiledFiles():
    """Group of CompiledFile.

    Attributes:
        compiledfiles(list): List of CompiledFiles.

    Args:
        filenames(list): List of target filenames and directory names.

    """
    def __init__(self, filenames, cachedir="~/.ipgrep"):
        self.compiledfiles = self._compile(filenames, cachedir)

    def _compile(self, filenames, cachedir):
        """ Compile filenames.

        Args:
            filenames(list): List of target filenames and directory names.
            cachedir(str): File path to save cached data.

        Returns:
            list: List of CompiledFile.

        """
        candidates = []
        for filename in filenames:
            if os.path.isdir(filename):
                candidates += [filename for filename in
                        glob.glob(os.path.join(filename, '**'),
                                recursive=True)
                        if os.path.isfile(filename)]
            elif os.path.isfile(filename):
                candidates += [filename]

        compiledfiles = []
        for candidate in candidates:
            compiledfiles.append(CompiledFile(candidate, cachedir))

        return compiledfiles

    def grep(self, iprange_str, match_type=None):
        """ Find input ipaddress in compiled files.

        Args:
            iprange_str(str): String format ip address.

        Output:
            list: List of found points in target files.

        """

        results = []
        network = str2network(iprange_str)

        for compiledfile in self.compiledfiles:
            results += compiledfile.grep(network)

        if match_type:
            results = [result for result in results
                        if result['match_type'] == match_type]

        return results

    def print(self, keyword, verbose=False, match_type=None):
        """Print grep result on stdout.

        Args:
            keyword(str): Network to search.
            verbose(bool): Show verbose or not, default: False.
            match_type(str): Show specific type only.
                match: Show exact matched IP string only.
                included: Show IP string which include keyword range.
                include: Show IP string which is included in kyeword range.
                Default: None

        """
        results = self.grep(keyword)
        for result in results:
            if match_type:
                if result['match_type'] != match_type:
                    continue
            if verbose:
                print('{}:{},{}:{}'.format(
                    result['filename'],
                    result['row'], result['col'],
                    result['string']
                    ))
            else:
                print('{}:{},{}'.format(
                    result['filename'],
                    result['row'], result['col']))


class CompiledFile():
    """Compiled iprange data from target file.

    Attributes:
        filename(str): Target file name.

        readable(bool): True for compiled, False for not compiled by format unmatch.

        _network_attrs_ipv4(list): List of dict format network instance.
           Dict format:
             {
                 'network': <ipaddress.IPv4Network or IPv6Network instance>,
                 'raw': <int> # Raw string at 'line'.
                 'col': <int> # Raw string at 'line'.
                 'string': <str> #Raw string of line.
             }

        _network_attrs_ipv6(list): List of dict format network instance.
           Format is same as v4

    Args:
        filename(str): Search target file name.

    """
    def __init__(self, filename, cachedir):
        self.filename = filename
        self.cachedir = cachedir
        compiled = self._compile(filename)

        if compiled:
            self.readable = True
            self._network_attrs_ipv4 = compiled[0]
            self._network_attrs_ipv6 = compiled[1]
        else:
            self.readable = False
            self._network_attrs_ipv4 = []
            self._network_attrs_ipv6 = []

    def cache(func):
        """Decorator to cache compiled data.

        Note:
            Args of function must be filename string only.
        """
        def check_hash(filename):
            fd = open(filename, 'rb')
            md5 = hashlib.md5(fd.read()).hexdigest()
            return md5

        def wrapper(*args, **kwargs):
            if len(args) != 2 or kwargs:
                raise Exception("Invalid apply for cache decorator.")

            self = args[0]
            filename = args[1]

            cachedir = os.path.expanduser(self.cachedir)
            if not os.path.isdir(cachedir):
                if os.path.exists(cachedir):
                    raise Exception("Cache dir name is already used.")
                os.mkdir(cachedir)


            md5 = check_hash(filename)
            cachepath = os.path.join(cachedir, md5)

            data = None
            if os.path.isfile(cachepath):
                with open(cachepath, 'rb') as fd:
                    data = pickle.load(fd)
            else:
                data = func(*args)
                if not os.path.isdir(cachedir):
                    os.makedirs(cachedir)
                with open(cachepath, 'wb') as fd:
                    pickle.dump(data, fd)
            return data

        return wrapper

    @cache
    def _compile(self, filename):
        try:
            fd = open(filename, 'r')
        except:
            return None

        network_attrs_ipv4 = []
        network_attrs_ipv6 = []
        regex_ip = r'[\d\.:]+(/\d{1,3}){0,1}'
        for row, line in enumerate(fd, 1):
            line = line.strip()
            candidates = re.finditer(regex_ip, line)
            for candidate in candidates:
                try:
                    network = str2network(candidate.group())
                except:
                    continue

                if isinstance(network, ipaddress.IPv4Network):
                    network_attrs_ipv4.append({
                        'filename': filename,
                        'network': network,
                        'row': row,
                        'col': candidate.span()[0],
                        'string': candidate.string})

                if isinstance(network, ipaddress.IPv6Network):
                    network_attrs_ipv6.append({
                        'filename': filename,
                        'network': network,
                        'row': row,
                        'col': candidate.span()[0],
                        'string': candidate.string})
        return (network_attrs_ipv4, network_attrs_ipv6)

    def grep(self, keyword):
        """Search keyword ip address or network in self.

        Args:
            keyword(IPv4Network or IPv6Network): Search keyword.

        Output:
            list: List of found location of keyword.

        """
        network_attrs = []
        if isinstance(keyword, ipaddress.IPv4Network):
            network_attrs = self._network_attrs_ipv4
        elif isinstance(keyword, ipaddress.IPv6Network):
            network_attrs = self._network_attrs_ipv6

        results = []
        for network_attr in network_attrs:
            match_type = None
            target = network_attr['network']
            if keyword == target:
                match_type = "match"
            elif keyword.subnet_of(target):
                match_type = "included"
            elif target.subnet_of(keyword):
                match_type = "include"

            if match_type:
                result = network_attr.copy()
                result['match_type'] = match_type
                results.append(result)

        return results


if __name__ == '__main__':
    import argparse

    # Parser
    parser = argparse.ArgumentParser()
    parser.add_argument('network',
                        default=None,
                        help='Network to searh, ex.) 192.168.1.1/32')
    parser.add_argument('filenames',
                        nargs='*',
                        default=[],
                        help='Target files and directories to search.')
    parser.add_argument('-m',
                        default=None,
                        help='Match type, <match, included, include>')
    parser.add_argument('-v',
                        action='store_true',
                        help='Show result details')
    args = parser.parse_args()

    # Run
    compiledfiles = CompiledFiles(args.filenames)
    compiledfiles.print(args.network, match_type=args.m, verbose=args.v)
