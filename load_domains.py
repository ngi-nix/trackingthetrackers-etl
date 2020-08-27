#!/usr/bin/env python3

import pandas as pd
import json
from typing import List, Set

import onemillion
import tldextract

import trackingthetrackers as ttt




search_space = None



def load_search_space(filename: str):
    global search_space

    search_space = json.load(open(filename))


def strip_stuff_from_domains(x) -> str:
    y = x.lstrip('|.-/*')
    return y.rstrip('|.-/*')


def clean_domain_names():
    global search_space

    return map(strip_stuff_from_domains, search_space['apks'][0]['domainNames'])


def load_onemillion(listname: str = '~/.onemillion/alexa.csv') -> Set:
    global om_domains

    # one way to do it:
    om_domains = onemillion.OneMillion()        # this impliclity fetches the lists and caches them!

    # another way, have more control. We are actually not interested in the order here
    df = pd.read_csv(listname, names=["count", "domain"])
    om_domains = set(df['domain'].tolist())
    # print(om_domains)


def reduce_to_domain_part(domainlist: List) -> List: 
    l = [] 
    extracted_domains = map(tldextract.extract, domainlist) 
    for ext in extracted_domains:
        # ext is a tuple: (ext.subdomain, ext.domain, ext.suffix)
        l.append( '.'.join(ext[-2:]))
    return l

    
if __name__ == "__main__":
    load_search_space("search_space.json")      #  "./feature_vectors.json")
    tracker_domains = list(clean_domain_names())
    print(80*"=" + " tracking domains " + 80*"=")
    print(tracker_domains)
    print("(found %d domain names)" % len(tracker_domains))
    print(80*"=" + " onemillion domains " + 80*"=")
    load_onemillion()
    print("(found %d onemillion names)" % len(om_domains))
    print("... done...")
    print(80*"=" + " normalized tracker domains " + 80*"=")
    normalized_tracker_domains = set(reduce_to_domain_part(tracker_domains))
    print("(found %d normalized domain names)" % len(normalized_tracker_domains))
    print(80*"=" + " good domains (onemillion - trackers) " + 80*"=")
    good_domains = om_domains.difference(normalized_tracker_domains)
    print("(found %d good names)" % len(good_domains))



