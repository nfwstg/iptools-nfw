import requests
import ipaggr
import sys


print('Check latest URL and input:')
print('https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519')
url = input("input:")


with requests.get(url) as response:
    data = response.json()
    headers = response.headers
    status = response.status_code

ips = []
for pref in data['values']:
    ips += pref['properties']['addressPrefixes']

aggr = ipaggr.IPRangeAggregation(ips)

print('IPv4, original: {}, aggregated: {}'.format(
    len(aggr.iprangelist_ipv4), len(aggr.aggregateds_ipv4)))
with open('./microsoft_ipv4.txt', 'w') as fd:
    fd.write('\n'.join(aggr.export_aggregated_ipv4()))

print('IPv6, original: {}, aggregated: {}'.format(
    len(aggr.iprangelist_ipv6), len(aggr.aggregateds_ipv6)))
with open('./microsoft_ipv6.txt', 'w') as fd:
    fd.write('\n'.join(aggr.export_aggregated_ipv6()))
