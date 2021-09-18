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
