import urllib.request
import json
import ipaggr


url = 'https://www.gstatic.com/ipranges/goog.json'

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read())
    headers = response.getheaders()
    status = response.getcode()

ips = []
for pref in data['prefixes']:
    if 'ipv4Prefix' in pref.keys():
        ips.append(pref['ipv4Prefix'])
    if 'ipv6Prefix' in pref.keys():
        ips.append(pref['ipv6Prefix'])

aggr = ipaggr.IPRangeAggregation(ips)

print('IPv4, original: {}, aggregated: {}'.format(
    len(aggr.iprangelist_ipv4), len(aggr.aggregateds_ipv4)))
with open('./google_ipv4.txt', 'w') as fd:
    fd.write('\n'.join(aggr.export_aggregated_ipv4()))

print('IPv6, original: {}, aggregated: {}'.format(
    len(aggr.iprangelist_ipv6), len(aggr.aggregateds_ipv6)))
with open('./google_ipv6.txt', 'w') as fd:
    fd.write('\n'.join(aggr.export_aggregated_ipv6()))
