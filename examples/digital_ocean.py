import requests
import ipaggr


url = 'https://digitalocean.com/geo/google.csv'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0'}

with requests.get(url, headers=headers) as response:
    data = response.text
    headers = response.headers
    status = response.status_code

ips = []
for pref in data.split('\n'):
    ips.append(pref.split(',')[0])

aggr = ipaggr.IPRangeAggregation(ips, ignore_invalid=True)

print('IPv4, original: {}, aggregated: {}'.format(
    len(aggr.iprangelist_ipv4), len(aggr.aggregateds_ipv4)))
with open('./digital_ocean_ipv4.txt', 'w') as fd:
    fd.write('\n'.join(aggr.export_aggregated_ipv4()))

print('IPv6, original: {}, aggregated: {}'.format(
    len(aggr.iprangelist_ipv6), len(aggr.aggregateds_ipv6)))
with open('./digital_ocean_ipv6.txt', 'w') as fd:
    fd.write('\n'.join(aggr.export_aggregated_ipv6()))
