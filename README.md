# IP Range tools
Some tools about IP management.
- ipaggr.py: Aggregate separated IP ranges.
- ipgrep.py: Search target IP range in target document.

Usage(ipaggr.py)
-----
```
$ python3 ./ipaggr.py -h
usage: ipaggr.py [-h] [-m MAXRANGES] [file]

positional arguments:
  file                  Txt format ip range list.

optional arguments:
  -h, --help            show this help message and exit
  -m MAXRANGES, --maxranges MAXRANGES
                        Maxrange for rough aggregate.0 means disable rough aggregate.Default: 0
  -v, --verbose         Show progress and details
```

Need to limit IP range number, try -m option.

```
% cat ./tests/sample01.txt
192.168.0.0
192.168.0.1
192.168.0.255
10.0.0.1

% python3 ./ipaggr.py -v ./tests/sample01.txt
Unification: Done
Aggregation: Done
Aggregateds
10.0.0.1/32
192.168.0.255/32
192.168.0.0/31
Missings

% python3 ./ipaggr.py -v -m 2 ./tests/sample01.txt
Unification: Done
Aggregation: Done
RoughAggregation: Done
Aggregateds
10.0.0.0/25
192.168.0.0/24
Missings
10.0.0.0/32
10.0.0.2/31
10.0.0.4/30
10.0.0.8/29
10.0.0.16/28
10.0.0.32/27
10.0.0.64/26
192.168.0.254/32
192.168.0.252/31
192.168.0.248/30
192.168.0.240/29
192.168.0.224/28
192.168.0.192/27
192.168.0.128/26
192.168.0.2/31
192.168.0.4/30
192.168.0.8/29
192.168.0.16/28
192.168.0.32/27
192.168.0.64/26
```

Exsample(ipaggr.py)
-----
Check ./examples/aws.py

Usage(ipgrep.py)
-----
```
usage: ipgrep.py [-h] [-m M] [-v] network [filenames [filenames ...]]

positional arguments:
  network     Network to searh, ex.) 192.168.1.1/32
  filenames   Target files and directories to search.

optional arguments:
  -h, --help  show this help message and exit
  -m M        Match type, <match, included, include>
  -v          Show result details

```

Note(ipgrep.py)
-----
Greped files are cached in~/.ipgrep directory.


Exsample(ipgrep.py)
-----
```
python3 ./ipgrep.py 0.0.0.0/0 <Target file or directory>
```
