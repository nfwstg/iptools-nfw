import sys
import ipaddress
import os
import glob
import re


class Countdown():
    """Print countdown.

    Attributes:
        prefix(str): Prefix for printed string.
        suffix(str): Suffix for printed string.

    """
    def __init__(self, prefix='', suffix=''):
        self.prefix = prefix
        self.suffix = suffix

    def print(self, num):
        print('{}{}{}\033[0K\r'.format(
            self.prefix, num, self.suffix),
            end='',
            file=sys.stderr)

    def close(self, message):
        sys.stdout.flush()
        print('{}{}\033[0K'.format(self.prefix, message),
            file=sys.stderr)


def str2network(iprange_str):
    network = None

    if not network:
        try:
            network = ipaddress.IPv4Network(iprange_str)
        except:
            network = None
    if not network:
        try:
            ipaddr = ipaddress.IPv4Address(iprange_str)
            network = ipaddress.IPv4Network(ipaddr)
        except:
            network = None
    if not network:
        try:
            network = ipaddress.IPv6Network(iprange_str)
        except:
            network = None
    if not network:
        try:
            ipaddr = ipaddress.IPv6Address(iprange_str)
            network = ipaddress.IPv6Network(ipaddr)
        except:
            network = None
    if not network:
        raise Exception("Range format error, {}".format(iprange_str))

    return network


class CompiledFiles():
    """Group of CompiledFile.

    Attributes:
        compiledfiles(list): List of CompiledFiles.

    Args:
        filenames(list): List of target filenames and directory names.

    """
    def __init__(self, filenames):
        self.compiledfiles = self._compile(filenames)

    def _compile(self, filenames):
        """ Compile filenames.

        Args:
            filenames(list): List of target filenames and directory names.

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
            compiledfiles.append(CompiledFile(candidate))

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


class CompiledFile():
    """Compiled iprange data from target file.

    Attributes:
        finemane(str): Target file name.

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
    def __init__(self, filename):
        self.filename = filename
        compiled = self._compile(filename)

        if compiled:
            self.readable = True
            self._network_attrs_ipv4 = compiled[0]
            self._network_attrs_ipv6 = compiled[1]
        else:
            self.readable = False
            self._network_attrs_ipv4 = []
            self._network_attrs_ipv6 = []

    def _compile(self, filename):
        try:
            fd = open(filename, 'r')
        except:
            return None

        network_attrs_ipv4 = []
        network_attrs_ipv6 = []
        regex_ip = '[\d\.:]+(/\d{1,3}){0,1}'
        for row, line in enumerate(fd, 1):
            candidates = re.finditer(regex_ip, line)
            for candidate in candidates:
                try:
                    network = str2network(candidate.group())
                except:
                    continue

                if isinstance(network, ipaddress.IPv4Network):
                    network_attrs_ipv4.append({
                        'network': network,
                        'row': row,
                        'col': candidate.span()[0],
                        'string': candidate.string})

                if isinstance(network, ipaddress.IPv6Network):
                    network_attrs_ipv6.append({
                        'network': network,
                        'row': row,
                        'col': candidate.span()[0],
                        'string': candidate.string})
        return (network_attrs_ipv4, network_attrs_ipv6)

    def grep(self, keyword):
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
                result['finename'] = self.filename
                results.append(result)

        return results


if __name__ == '__main__':
    import argparse

    # Parser
    parser = argparse.ArgumentParser()
    parser.add_argument('network',
                        default=None,
                        help='Netwrok to searh, ex.) 192.168.1.1/32')
    parser.add_argument('filenames',
                        nargs='*',
                        default=[],
                        help='Target files and directories to search.')
    parser.add_argument('-m',
                        default=None,
                        help='Match type, <match, included, include>')
    args = parser.parse_args()

    # Run
    compiledfiles = CompiledFiles(args.filenames)
    print(compiledfiles.grep(args.network, match_type=args.m))
