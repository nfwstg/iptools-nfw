import ipaddr
import os
import glob


class IPGrep():
    """File target ip or ip range strings in files.

    Args:
        filename_or_directory (str): Filename or directory name to search.

    """
    def __init__(self):
        pass


if __name__ == '__main__':
    import sys
    import argparse

    # Parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--extract_san',
                        action='store_true',
                        help='Download cert and extract SAN',
                        default=False)
    parser.add_argument('domain',
                        help='Search target domain')
    args = parser.parse_args()

    # Run
    ## Open file and load list of ranges.
    files = []
    if os.path.isfile(arg.file_or_domain):
        files = []
    if os.path.isdir(arg.file_or_domain):
        dname = os.path.join(arg.file_or_directory, '**')
        files = glob.glob(dname, recursive=True)
