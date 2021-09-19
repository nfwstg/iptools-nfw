import ipaddress
import sys
import datetime


########################################
# Exceptions
########################################
class NetworkFormatError(Exception):
    """String is not in IP address or network format.

    """
    pass


########################################
# Functions
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


########################################
# Functional Class
########################################
class Countdown():
    """Print countdown.

    Args:
        prefix(str): Prefix for printed string.
        suffix(str): Suffix for printed string.
        reportmode(str): Output target, default: stdout.
            stdout: Output progress to stdout.
            None: Output nothing.

    """
    def __init__(self, prefix='', suffix='', reportmode='stdout'):
        self.prefix = prefix
        self.suffix = suffix
        self.reportmode = reportmode

    def print(self, num):
        """Print progress.

        Args:
            num(int): Printed Number.

        """
        if self.reportmode == 'stdout':
            print('{}{}{}\033[0K\r'.format(
                self.prefix, num, self.suffix),
                end='',
                file=sys.stderr)

    def close(self, message):
        """Stop countdown.
        Print terminate string.

        Args:
            message(str): Terminate string.

        """
        if self.reportmode == 'stdout':
            sys.stdout.flush()
            print('{}{}\033[0K'.format(self.prefix, message),
                file=sys.stderr)


########################################
# Decorators
########################################
def count_time(func):
    """Decorater to count time taken for decorated func.

    """
    def wrapper(*args, **kwargs):
        start = datetime.datetime.now()

        result = func(*args, **kwargs)

        end = datetime.datetime.now()
        print('----time----')
        print(end - start)
        return result
    return wrapper
