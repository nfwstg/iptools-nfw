import ipaddress
import os
import glob
import ipaddress
import tqdm

import sys

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
            end='')

    def close(self, message):
        sys.stdout.flush()
        print('{}{}\033[0K'.format(self.prefix, message))


class IPRangeAggregation():
    """Aggregate IP ranges.

    Attributes:
        iprangelist_ipv4 (list): List of ipaddress format data for ipv4.
        iprangelist_ipv6 (list): List of ipaddress format data for ipv6.
        aggregatedlist_ipv4 (list): Aggregated list of ipaddress.
        aggregatedlist_ipv6 (list): Aggregated list of ipaddress.

    Args:
        ipranges_str (list): List of IP ranges to aggregate.
            IP range must be string like "XXX.XXX.XXX.XXX/24".
    """

    def __init__(self, iprangelist_str):
        (list_ipv4, list_ipv6) = self._generate_iprange(iprangelist_str)
        self.iprangelist_ipv4 = list_ipv4
        self.iprangelist_ipv6 = list_ipv6

        (aggr_ipv4, aggr_ipv6) = self._aggregate_iprange(list_ipv4, list_ipv6)
        self.aggregatelist_ipv4 = aggr_ipv4
        self.aggregatelist_ipv6 = aggr_ipv6

    def _generate_iprange(self, iprangelist_str):
        list_ipv4 = []
        list_ipv6 = []

        for iprange_str in iprangelist_str:
            iprange = None
            iprange_str = iprange_str.rstrip()
            try:
                iprange = ipaddress.IPv4Network(iprange_str)
                list_ipv4.append(iprange)
                continue
            except:
                pass

            try:
                ipaddr = ipaddress.IPv4Address(iprange_str)
                iprange = ipaddress.IPv4Network(ipaddr)
                list_ipv4.append(iprange)
                continue
            except:
                pass

            try:
                iprange = ipaddress.IPv6Network(iprange_str)
                list_ipv6.append(iprange)
                continue
            except:
                pass

            try:
                ipaddr = ipaddress.IPv6Address(iprange_str)
                iprange = ipaddress.IPv6Network(ipaddr)
                list_ipv6.append(iprange)
                continue
            except:
                pass

            raise Exception("Range format error, {}".format(iprange_str))

        return (list_ipv4, list_ipv6)

    def _aggregate_iprange(self, list_ipv4, list_ipv6):
        uniq_ipv4 = self._uniq_iprange(list_ipv4)
        uniq_ipv6 = self._uniq_iprange(list_ipv6)
        aggr_ipv4 = self._do_aggregate(uniq_ipv4)
        aggr_ipv6 = self._do_aggregate(uniq_ipv6)

        return (aggr_ipv4, aggr_ipv6)

    def _uniq_iprange(self, list_ip):
        uniq_list = []
        sorted_list = sorted(
                set(list_ip),
                key=lambda x: x.prefixlen, reverse=True)

        countdown = Countdown(prefix='Unification: ', suffix=' left.')
        while sorted_list:
            countdown.print(len(sorted_list))
            base = sorted_list.pop()

            for compared in sorted_list:
                if (compared.network_address <= base.network_address and
                    base.broadcast_address <= compared.broadcast_address):
                    break
            else:
                uniq_list.append(base)

        countdown.close('Done')
        return uniq_list

    def _do_aggregate(self, uniq_ip):
        aggr_list = []
        sorted_list = sorted(uniq_ip, key=lambda x: x.prefixlen, reverse=True)

        countdown = Countdown(prefix='Aggregation: ', suffix=' left.')
        while sorted_list:
            countdown.print(len(sorted_list))
            sorted_list.sort(key=lambda x: x.prefixlen, reverse=True)
            base = sorted_list.pop(0)
            aggregated = base.supernet()

            for compared in sorted_list:
                if compared.prefixlen < base.prefixlen:
                    aggr_list.append(base)
                    break
                if compared.subnet_of(aggregated):
                    sorted_list.remove(compared)
                    sorted_list.append(aggregated)
                    break
            else:
                aggr_list.append(base)

        countdown.close('Done')
        return sorted(aggr_list)


def delete_separated(rangelist_str):
    """Delete small range already containd in others.

    Args:
        rangelist_str(list): List of IP ranges, string fromat.

    Returns:
        set: Set of list of Uniq IP ranges, ipaddress format.
            (list for ipv4, list for ipv6)

    """

    return result


if __name__ == '__main__':
    import sys
    import argparse

    # Parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--extract_san',
                        action='store_true',
                        help='Download cert and extract SAN',
                        default=False)
    parser.add_argument('file',
                        help='Txt format ip range list.')
    args = parser.parse_args()

    # Run
    with open(args.file, 'r') as fd:
        lines = fd.readlines()

    aggr = IPRangeAggregation(lines)
