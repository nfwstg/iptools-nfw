import urllib.request
import json
import sys
import ipaggr


print('Check latest URL and input:')
print('https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519')
url = input("input:")


with urllib.request.urlopen(url) as response:
    data = json.loads(response.read())
    headers = response.getheaders()
    status = response.getcode()

ips = []
for pref in data['values']:
    ips += pref['properties']['addressPrefixes']

aggr = ipaggr.IPRangeAggregation(ips)

print('IPv4, original: {}, aggregated: {}'.format(
    len(aggr.iprangelist_ipv4), len(aggr.aggregateds_ipv4)))
with open('./azure_ipv4.txt', 'w') as fd:
    fd.write('\n'.join(aggr.export_aggregated_ipv4()))

print('IPv6, original: {}, aggregated: {}'.format(
    len(aggr.iprangelist_ipv6), len(aggr.aggregateds_ipv6)))
with open('./azure_ipv6.txt', 'w') as fd:
    fd.write('\n'.join(aggr.export_aggregated_ipv6()))
