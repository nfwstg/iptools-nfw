import ipaddress
from tools import str2network
from tools import Countdown


class AggregatedRange():
    """Aggregated IP range.

    Args:
        network(ipaddress.IPv4Network or IPv6Network):
            IP range.

        components(list): List of aggregated partial ranges, default: None.

        dedups(list): List of dedupped ranges, default: None.

        missings(list): List of not exsisting ranges in network, default: None.
            For rough aggregate mode only.

    Attributes:
        network(ipaddress.IPv4Network or IPv6Network):
            IP range.

        prefixlen(int): Prefix length of self.network.

        components(list): List of Aggregated Ranges.
            ipaddress.IPv4Network or IPv6Network.

        dedups(list): List of deduplicated ranges.
            Smaller ranges are deleted from list and contained in here.
            ipaddress.IPv4Network or IPv6Network.

        missings(list): List of not aggregated parts.
            ipaddress.IPv4Network or IPv6Network.

        pare(ipaddress.IPv4Network or IPv6Network):
            Pared range.

    """
    def __init__(self, network, components=None, dedups=None, missings=None):
        self.network = network
        self.prefixlen = self.network.prefixlen
        if components:
            self.components = components
        else:
            self.components = [self.network]
        if dedups:
            self.dedups = dedups
        else:
            self.dedups = [self.network]
        if missings:
            self.missings = missings
        else:
            self.missings = []

        if self.prefixlen != 0:
            self.supernet = self.network.supernet()
            self.pare = list(self.supernet.address_exclude(self.network))[0]
        else:
            self.supernet = None
            self.pare = None

    def __lt__(self, other):
        return self.network < other.network

    def __gt__(self, other):
        return self.network > other.network

    def __repr__(self):
        return str(self.network)

    def is_pare(self, other):
        """Check other range is pare of this range or not.
        'pare' means other subnet of same super range.

        """
        if other.network == self.pare:
            return True
        return False

    def is_supernetof(self, other):
        """Check other range is supernet of this range or not.
        IPv4Network's native method is heavy, so coded simply.

        """
        if self.network.network_address <= other.network.network_address and \
             other.network.broadcast_address <= self.network.broadcast_address:
            return True
        return False

    def dedup(self, other):
        """Add deduped ranges.

        """
        self.dedups += other.dedups

    def aggregate(self, other):
        """Aggregate pared ranges

        """
        if not self.is_pare(other):
            raise Exception()
        superrange = AggregatedRange(
                self.supernet,
                self.components + other.components,
                self.dedups + other.dedups,
                self.missings + other.missings)
        return superrange

    def pseudo_aggregate(self):
        """Aggregate even if pared range is missing.

        """
        superrange = AggregatedRange(
                self.supernet,
                self.components,
                self.dedups,
                self.missings + [self.pare])
        return superrange


class IPRangeAggregation():
    """Aggregate IP ranges.

    Args:
        ipranges_str (list): List of IP ranges to aggregate.
            IP range must be string like "XXX.XXX.XXX.XXX/24".

        maxranges_ipv4 (int): Maximum range number for ipv4.
            If aggregated range is larger than maxranges, aggregate roughly.

        maxranges_ipv6 (int): Maximum range number for ipv4.
            If aggregated range is larger than maxranges, aggregate roughly.

        ignore_invalid (bool): Ignore strange range format, default: False.
            Raise Exception for strange range format when False.

        verbose(bool): Show progress and details or not.

    Attributes:
        iprangelist_ipv4 (list): List of ipaddress format data for ipv4.

        iprangelist_ipv6 (list): List of ipaddress format data for ipv6.

        aggregatedlist_ipv4 (list): Aggregated list of ipaddress.

        aggregatedlist_ipv6 (list): Aggregated list of ipaddress.

    """

    def __init__(self, iprangelist_str,
                 maxranges_ipv4=None, maxranges_ipv6=None,
                 ignore_invalid=False, verbose=False):
        self.verbose = verbose
        self.maxranges_ipv4 = maxranges_ipv4
        self.maxranges_ipv6 = maxranges_ipv6
        self.ignore_invalid = ignore_invalid
        (list_ipv4, list_ipv6) = self._generate_iprange(
                iprangelist_str, self.ignore_invalid)
        self.iprangelist_ipv4 = list_ipv4
        self.iprangelist_ipv6 = list_ipv6

        aggr_ipv4 = self._aggregate_iprange(list_ipv4, self.maxranges_ipv4)
        aggr_ipv6 = self._aggregate_iprange(list_ipv6, self.maxranges_ipv6)

        self.aggregateds_ipv4 = aggr_ipv4
        self.aggregateds_ipv6 = aggr_ipv6

    def _generate_iprange(self, iprangelist_str, ignore_invalid):
        list_ipv4 = []
        list_ipv6 = []

        for iprange_str in iprangelist_str:
            try:
                network = str2network(iprange_str)
            except Exception as exception:
                if not ignore_invalid:
                    raise exception

            if isinstance(network, ipaddress.IPv4Network):
                list_ipv4.append(AggregatedRange(network))
            elif isinstance(network, ipaddress.IPv6Network):
                list_ipv6.append(AggregatedRange(network))

        return (list_ipv4, list_ipv6)

    def _aggregate_iprange(self, list_ip, maxranges):
        if not list_ip:
            return []

        uniq_list = self._uniq_iprange(list_ip)
        aggr_list = self._do_aggregate(uniq_list)
        if maxranges and maxranges >= 1:
            aggr_list = self._do_rough_aggregate(aggr_list, maxranges)

        return aggr_list

    def _uniq_iprange(self, list_ip):
        uniq_list = []
        sorted_list = list_ip.copy()
        sorted_list.sort()

        if self.verbose:
            countdown = Countdown(prefix='Unification: ', suffix=' left.')
        else:
            countdown = Countdown(reportmode=None)

        base = sorted_list.pop(0)
        while sorted_list:
            countdown.print(len(sorted_list))
            compared = sorted_list.pop(0)
            if base.is_supernetof(compared):
                base.dedup(compared)
                del compared
            else:
                uniq_list.append(base)
                base = compared
        uniq_list.append(base)

        countdown.close('Done')
        return uniq_list

    def _do_aggregate(self, uniq_list_in):
        aggr_list = []
        uniq_list = uniq_list_in.copy()

        if self.verbose:
            countdown = Countdown(prefix='Aggregation: ', suffix=' left.')
        else:
            countdown = Countdown(reportmode=None)

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
        return aggr_list

    def _do_rough_aggregate(self, aggr_list_in, maxranges):
        """Aggregate ranges even if some part does not exist.

        Args:
            aggr_list_in(list): Candidates to be aggregated.
            maxranges(int): Max aggregated range number.

        Returns:
            list: List of aggregated ranges.

        """
        def _recursive_aggregate(base, supers):
            """Aggregate roughly aggregated range with other ranges.

            Args:
                base(AggregatedRange)
            """
            compareds = [snet for snet in supers
                         if snet.prefixlen == base.prefixlen]
            for compared in compareds:
                if base.is_pare(compared):
                    supers.remove(compared)
                    aggregate = base.aggregate(compared)
                    return _recursive_aggregate(aggregate, supers)

            supers.append(base)
            return supers

        aggr_list = aggr_list_in.copy()

        if self.verbose:
            countdown = Countdown(prefix='RoughAggregation: ', suffix=' left.')
        else:
            countdown = Countdown(reportmode=None)

        while len(aggr_list) > maxranges:
            countdown.print(len(aggr_list) - maxranges)

            prefixlen = max([arange.prefixlen for arange in aggr_list])

            bases = [base for base in aggr_list if base.prefixlen == prefixlen]
            aggr_list = [snet for snet in aggr_list
                         if snet.prefixlen < prefixlen]
            for base in bases:
                aggregated = base.pseudo_aggregate()
                _recursive_aggregate(aggregated, aggr_list)

        countdown.close('Done')

        return aggr_list

    def export_aggregated_ipv4(self):
        """Export aggregated result.
        IPv6 only.

        """
        return [str(arange.network) for arange in self.aggregateds_ipv4]

    def export_aggregated_ipv6(self):
        """Export aggregated result.
        IPv6 only.

        """
        return [str(arange.network) for arange in self.aggregateds_ipv6]

    def export_aggregated(self):
        """Export aggregated result.

        """
        return self.export_aggregated_ipv4() + self.export_aggregated_ipv6()

    def export_missings_ipv4(self):
        """Export not existing iprange when aggregated.
        Export ipv4 only.

        """
        return [str(missing) for arange in self.aggregateds_ipv4
                for missing in arange.missings]

    def export_missings_ipv6(self):
        """Export not existing iprange when aggregated.
        Export ipv6 only.

        """
        return [str(missing) for arange in self.aggregateds_ipv6
                for missing in arange.missings]

    def export_missings(self):
        """Export not existing iprange when aggregated.

        """
        return self.export_missings_ipv4()\
               + self.export_missings_ipv6()


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
                        help='Maxrange for rough aggregate.' +
                             '0 means disable rough aggregate.' +
                             'Default: 0')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Show progress and details')
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

    aggr = IPRangeAggregation(lines,
                              maxranges_ipv4=args.maxranges,
                              maxranges_ipv6=args.maxranges,
                              verbose=args.verbose)
    if args.verbose:
        print('Aggregateds')
        print('\n'.join(aggr.export_aggregated()))
        if args.maxranges > 0:
            print('Missings')
            print('\n'.join(aggr.export_missings()))
    else:
        print('\n'.join(aggr.export_aggregated()))
