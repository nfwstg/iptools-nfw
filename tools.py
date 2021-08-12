import ipaddress
import os
import sys
import pickle
import hashlib
import datetime


########################################
# Variables
########################################
cachedirname = ".ipgrep"


########################################
# Exceptions
########################################
class CacheArgmentError(Exception):
    pass


class CacheFileNotExistError(Exception):
    pass


class NetworkFormatError(Exception):
    pass


########################################
# Functions and Classes
########################################
def str2network(iprange_str_in):
    """Generate IPv4Network or IPv6Network inscance.

    """
    network = None

    iprange_str = iprange_str_in.strip()
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
        raise NetworkFormatError(iprange_str)

    return network


def cache(is_method=False, enable=True):
    """Decorator to cache compiled data.

    Note:
        Args of function must be filename string only.
    """
    def deco(func):
        def check_hash(filename):
            fd = open(filename, 'rb')
            md5 = hashlib.md5(fd.read()).hexdigest()
            return md5

        def wrapper(*args, **kwargs):
            if is_method:
                if len(args) != 2 or kwargs:
                    raise CacheArgmentError()
                filename = args[1]
            else:
                if len(args) != 1 or kwargs:
                    raise CacheArgmentError()
                filename = args[0]

            if not os.path.isfile(filename):
                raise CacheFileNotExistError(filename)

            md5 = check_hash(filename)
            cachedir = os.path.expanduser(
                    os.path.join('~', cachedirname))
            cachepath = os.path.expanduser(
                    os.path.join(cachedir, md5))

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

    return deco
def tt(func):
    def wrapper(*args, **kwargs):
        start = datetime.datetime.now()

        result = func(*args, **kwargs)

        end = datetime.datetime.now()
        print('----time----')
        print(end - start)
        return result
    return wrapper


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

