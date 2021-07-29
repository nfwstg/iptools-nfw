import urllib.request
import json
import ipaggr

url = 'https://ip-ranges.amazonaws.com/ip-ranges.json'

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read())
    headers = response.getheaders()
    status = response.getcode()

ips = []
for pref in data['prefixes']:
    ips.append(pref['ip_prefix'])
for pref in data['ipv6_prefixes']:
    ips.append(pref['ipv6_prefix'])

aggr = ipaggr.IPRangeAggregation(ips)
