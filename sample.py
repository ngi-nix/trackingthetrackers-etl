#!/usr/bin/env python3

import sys
import os
import json
import pandas as pd
import ipaddress


import argparse


parser = argparse.ArgumentParser(description='Process sampled domain lists for clean and trackers')

parser.add_argument('stop_after', metavar='N', type=int, nargs='?', help='Stop after N files', default=-1)
parser.add_argument('path', type=str, help="root path where to search for clean and trackers/ subdirs")
args = parser.parse_args()

global psl


def load_psl(filename: str):
    with open(filename) as f:
        lines = [line.rstrip() for line in f]
        lines = [l for l in lines if l and '//' not in l]
        return lines


def filter_name_too_short(x):
    # cut out domain names which
    global psl
    return len(x.split(".")[0]) > 2 and x in psl


def convert_ip(x):
    try:
        ip = ipaddress.ip_address(x)
    except Exception as ex:
        # print("could not convert ip address '%s', setting to 127.0.0.222." % x, file=sys.stderr)
        ip = ipaddress.ip_address("127.0.0.222")
    return ip


def convert_domain(x):
    x = x.lstrip('*')
    x = x.lstrip('*.')
    x = x.lstrip('.')
    x = x.rstrip('.')
    suffix = x.split('.')[-1]
    if suffix and suffix not in psl:
        #print("could not find suffix %s. Ignoring, setting domain name to empty string." % suffix)
        x = ''
    return x


converter_dict = {'ip': convert_ip, 'domain': convert_domain}


def get_domain_names(filename: str):
    df = pd.read_table(filename, header=None, names=['ip', 'domain', '_asn'], converters=converter_dict)
    newdf = df[df['domain'].str.len() > 5]
    return set(newdf['domain'])


if __name__ == "__main__":
    global psl
    psl = load_psl("publicsuffix.dat")
    domains = { "trackers": [], "clean": [] }
    i=0
    # r=root, d=directories, f = files
    for r, d, f in os.walk(args.path):
        for filename in f:
            i += 1
            print("looking at file %s/%s" % (r, filename), file=sys.stderr)
            if "clean" in r:
                domains["clean"].extend(get_domain_names(r + "/" + filename))
            else:
                domains["trackers"].extend(get_domain_names(r + "/" + filename))
            if i >= int(args.stop_after):
                break
    domains["clean"] = list(set(domains["clean"]))
    domains["trackers"] = list(set(domains["trackers"]))
    print(json.dumps(domains))
    print("processed %d files. %d clean domain names, %d tracker domain names" % (i, len(domains["clean"]), len(domains["trackers"])), file=sys.stderr)
