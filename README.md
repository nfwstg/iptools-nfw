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
TODO


Exsample(ipgrep.py)
-----
TODO

