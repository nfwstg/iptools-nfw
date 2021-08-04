import ipaddress
import os
import glob
import ipaddress
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
            end='',
            file=sys.stderr)

    def close(self, message):
        sys.stdout.flush()
        print('{}{}\033[0K'.format(self.prefix, message),
            file=sys.stderr)


class AggregatedRange():
    """Aggregated IP range.

    Attributes:
        network(ipaddress.IPv4Network or IPv6Network):
            IP range.

        prefixlen(int): Prefix length of self.network.

        components(list): List of Aggregated Ranges.
            ipaddress.IPv4Network or IPv6Network.

        missings(list): List of not aggregated parts.
            ipaddress.IPv4Network or IPv6Network.

        pare(ipaddress.IPv4Network or IPv6Network):
            Pared range.

    """
    def __init__(self, network, components=None):
        self.network = network
        self.prefixlen = self.network.prefixlen
        if components:
            self.components = components
        else:
            self.components = [self.network]
        self.missings = []
        self.supernet = self.network.supernet()
        self.pare = list(self.supernet.address_exclude(self.network))[0]

    def __lt__(self, other):
        return self.network < other.network

    def __gt__(self, other):
        return self.network > other.network

    def is_pare(self, other):
        if other.network == self.pare:
            return True
        return False

    def aggregate(self, dest):
        if not self.is_pare(dest):
            raise Exception()
        superrange = AggregatedRange(
                self.supernet, self.components + dest.components)
        superrange.missings = self.missings + dest.missings
        return superrange

    def pseudo_aggregate(self):
        superrange = AggregatedRange(
                self.supernet, self.components)
        superrange.missings = self.missings + [self.pare]
        return superrange


class IPRangeAggregation():
    """Aggregate IP ranges.

    Attributes:
        iprangelist_ipv4 (list): List of ipaddress format data for ipv4.

        iprangelist_ipv6 (list): List of ipaddress format data for ipv6.

        aggregatedlist_ipv4 (list): Aggregated list of ipaddress.

        aggregatedlist_ipv6 (list): Aggregated list of ipaddress.

        missing_ipv4 (list): Missing ranges if roghly aggregated.

        missing_ipv6 (list): Missing ranges if roghly aggregated.

    Args:
        ipranges_str (list): List of IP ranges to aggregate.
            IP range must be string like "XXX.XXX.XXX.XXX/24".

        maxranges_ipv4 (int): Maximum range number for ipv4.
            If aggregated range is larger than maxranges, aggregate roughly.

        maxranges_ipv6 (int): Maximum range number for ipv4.
            If aggregated range is larger than maxranges, aggregate roughly.

        ignore_invalid (bool): Ignore strange range format, decault: False.
            Raise Exception for strange range format when False.

    """

    def __init__(self, iprangelist_str,
            maxranges_ipv4=None, maxranges_ipv6=None, ignore_invalid=False):
        self.maxranges_ipv4 = maxranges_ipv4
        self.maxranges_ipv6 = maxranges_ipv6
        self.ignore_invalid = ignore_invalid
        (list_ipv4, list_ipv6) = self._generate_iprange(
                iprangelist_str, self.ignore_invalid)
        self.iprangelist_ipv4 = list_ipv4
        self.iprangelist_ipv6 = list_ipv6

        (aggr_ipv4, miss_ipv4) = \
            self._aggregate_iprange(list_ipv4, self.maxranges_ipv4)
        (aggr_ipv6, miss_ipv6) = \
            self._aggregate_iprange(list_ipv6, self.maxranges_ipv6)

        self.aggregateds_ipv4 = aggr_ipv4
        self.missings_ipv4 = miss_ipv4
        self.aggregateds_ipv6 = aggr_ipv6
        self.missings_ipv6 = miss_ipv6

    def _generate_iprange(self, iprangelist_str, ignore_invalid):
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

            if not ignore_invalid:
                raise Exception("Range format error, {}".format(iprange_str))

        return (list_ipv4, list_ipv6)

    def _aggregate_iprange(self, list_ip, maxranges):
        uniq_list = self._uniq_iprange(list_ip)
        aggr_list = self._do_aggregate(uniq_list)
        if maxranges and maxranges >= 1:
            (aggr_list, missing_list) = \
                    self._do_rough_aggregate(aggr_list, maxranges)
        else:
            missing_list = []

        return (aggr_list, missing_list)

    def _uniq_iprange(self, list_ip):
        uniq_list = []
        sorted_list = list(set(list_ip))
        sorted_list.sort()

        countdown = Countdown(prefix='Unification: ', suffix=' left.')
        base = sorted_list.pop(0)
        while sorted_list:
            countdown.print(len(sorted_list))
            compared = sorted_list.pop(0)
            if compared.broadcast_address > base.broadcast_address:
                uniq_list.append(base)
                base = compared
        uniq_list.append(base)

        countdown.close('Done')
        return uniq_list

    def _do_aggregate(self, uniq_list_in):
        aggr_list = []
        uniq_list = []

        for network in uniq_list_in:
            uniq_list.append(AggregatedRange(network))

        countdown = Countdown(prefix='Aggregation: ', suffix=' left.')
        while uniq_list:
            countdown.print(len(uniq_list))

            prefixlen = max([base.prefixlen for base in uniq_list])

            bases = [base for base in uniq_list
                    if base.prefixlen == prefixlen]
            bases.sort()
            uniq_list = [base for base in uniq_list
                    if base.prefixlen < prefixlen]

            while bases:
                # Case: Last One.
                if len(bases) == 1:
                    aggr_list.append(bases.pop(0))
                    break

                base = bases.pop(0)
                compared = bases.pop(0)

                # Case: Aggregated
                if base.is_pare(compared):
                    aggregated = base.aggregate(compared)
                    uniq_list.insert(0, aggregated)
                    continue

                # Case: Pare not exists, not aggregate
                aggr_list.append(base)
                bases.insert(0, compared)

        countdown.close('Done')
        return list(arange.network for arange in aggr_list)

    def _do_rough_aggregate(self, aggr_list_in, maxranges):
        def _recursive_aggregate(base, supers_in):
            supers = supers_in.copy()
            compareds = [snet for snet in supers if snet.prefixlen == base.prefixlen]
            for compared in compareds:
                if base.is_pare(compared):
                    supers.remove(compared)
                    aggregate = base.aggregate(compared)
                    return _recursive_aggregate(aggregate, supers)
            else:
                supers.append(base)
                return supers

        aggr_list = []
        for network in aggr_list_in:
            aggr_list.append(AggregatedRange(network))

        countdown = Countdown(prefix='RoughAggregation: ', suffix=' left.')
        while len(aggr_list) > maxranges:
            countdown.print(len(aggr_list) - maxranges)

            prefixlen = max([arange.prefixlen for arange in aggr_list])

            bases = [base for base in aggr_list if base.prefixlen == prefixlen]
            supers = [snet for snet in aggr_list if snet.prefixlen < prefixlen]
            for base in bases:
                aggregated = base.pseudo_aggregate()
                supers = _recursive_aggregate(aggregated, supers)
            aggr_list = supers

        countdown.close('Done')

        aggr_list = []
        missing_list = []
        for arange in aggr_list:
            if len(arange.components) == 1:
                aggr_list.append(arange.components[0])
            else:
                aggr_list.append(arange.network)
                missing_list += arange.missings

        return (aggr_list, missing_list)

    def export_aggregated_ipv4(self):
        return [str(arange) for arange in self.aggregateds_ipv4]

    def export_aggregated_ipv6(self):
        return [str(arange) for arange in self.aggregateds_ipv6]

    def export_aggregated(self):
        return self.export_aggregated_ipv4() + self.export_aggregated_ipv6()

    def export_missings_ipv4(self):
        return [str(missing) for missing in self.missings_ipv4]

    def export_missings_ipv6(self):
        return [str(missing) for missing in self.missings_ipv6]

    def export_missings(self):
        return self.export_missings_ipv4() + self.export_missings_ipv6()


if __name__ == '__main__':
    import sys
    import argparse

    # Parser
    parser = argparse.ArgumentParser()
    parser.add_argument('file',
                        nargs='?',
                        default=None,
                        help='Txt format ip range list.')
    parser.add_argument('-m', '--maxranges',
                        type=int,
                        default=0,
                        help='Maxrange for rough aggregate. 0 means disable rough aggregate. Default: 0')
    args = parser.parse_args()

    # Run
    if args.file:
        with open(args.file, 'r') as fd:
            lines = fd.readlines()
    else:
        lines = []
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            lines.append(line)

    maxrange = args.maxranges

    aggr = IPRangeAggregation(lines,
            maxranges_ipv4=maxrange, maxranges_ipv6=maxrange)
    print('Aggregateds')
    print('\n'.join(aggr.export_aggregated()))
    print('Missings')
    print('\n'.join(aggr.export_missings()))
