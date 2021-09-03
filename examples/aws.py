import requests
import ipaggr


url = 'https://ip-ranges.amazonaws.com/ip-ranges.json'

with requests.get(url) as response:
    data = response.json()
    headers = response.headers
    status = response.status_code

ips = []
for pref in data['prefixes']:
    ips.append(pref['ip_prefix'])
for pref in data['ipv6_prefixes']:
    ips.append(pref['ipv6_prefix'])

aggr = ipaggr.IPRangeAggregation(ips)

print('IPv4, original: {}, aggregated: {}'.format(
    len(aggr.iprangelist_ipv4), len(aggr.aggregateds_ipv4)))
with open('./aws_ipv4.txt', 'w') as fd:
    fd.write('\n'.join(aggr.export_aggregated_ipv4()))

print('IPv6, original: {}, aggregated: {}'.format(
    len(aggr.iprangelist_ipv6), len(aggr.aggregateds_ipv6)))
with open('./aws_ipv6.txt', 'w') as fd:
    fd.write('\n'.join(aggr.export_aggregated_ipv6()))
