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


def strip_stuff_from_broadcastR(x) -> str:
    if x == "":
        return None
    else:
        return x.strip()


def strip_stuff_from_perms(x) -> str:
    if x == "":
        return None
    else:
        return x.strip()


def strip_stuff_from_dependencies(x) -> str:
    if x == "":
        return None
    else:
        return x.strip()


def strip_stuff_from_metaDataNames(x) -> str:
    if x == "":
        return None
    else:
        return x.strip()


def cleanup_domain_names():
    global search_space

    return filter(lambda i: i, map(strip_stuff_from_domains, search_space['apks'][0]['domainNames']))


def cleanup_broadcastReceivers():
    global search_space

    return filter(lambda i: i, map(strip_stuff_from_broadcastR, search_space['apks'][0]["broadcastReceiverIntentFilterActionNames"]))


def cleanup_permissions():
    global search_space

    return filter(lambda i: i, map(strip_stuff_from_perms, search_space['apks'][0]["usesPermissions"]))


def cleanup_dependencies():
    global search_space

    return filter(lambda i: i, map(strip_stuff_from_dependencies, search_space['apks'][0]["dependencies"]))


def cleanup_metaDataNames():
    global search_space

    return filter(lambda i: i, map(strip_stuff_from_metaDataNames, search_space['apks'][0]["metaDataNames"]))


def load_onemillion(listname: str = '~/.onemillion/alexa.csv') -> Set:

    # one way to do it:
    om_domains = onemillion.OneMillion()        # this impliclity fetches the lists and caches them!

    # another way, have more control. We are actually not interested in the order here
    df = pd.read_csv(listname, names=["count", "domain"])
    om_domains = set(df['domain'].tolist())
    # print(om_domains)
    return om_domains


def reduce_to_domain_part(domainlist: List) -> List:
    l = []
    extracted_domains = map(tldextract.extract, domainlist)
    for ext in extracted_domains:
        # ext is a tuple: (ext.subdomain, ext.domain, ext.suffix)
        l.append('.'.join(ext[-2:]))
    return l


if __name__ == "__main__":

    # load all data
    load_search_space("search_space.json")      # "./feature_vectors.json")

    # get the known tracking domains
    tracker_domains = list(cleanup_domain_names())
    print(40*"=" + " tracking domains " + 40*"=")
    print(tracker_domains)
    print("(found %d domain names)" % len(tracker_domains))

    # normlizing them
    print(40*"=" + " normalized tracker domains " + 40*"=")
    normalized_tracker_domains = set(reduce_to_domain_part(tracker_domains))
    print("(found %d normalized domain names)" % len(normalized_tracker_domains))

    # load the one million list
    print(40*"=" + " onemillion domains " + 40*"=")
    om_domains = load_onemillion()
    print("(found %d onemillion names)" % len(om_domains))

    # calculate the set of domains which are in the onemillion but not in the trackers list
    print(40*"=" + " good domains (i.e. onemillion - trackers) " + 40*"=")
    good_domains = om_domains.difference(normalized_tracker_domains)
    print("(found %d good names)" % len(good_domains))


    # broadcastReceivers 
    print(40*"=" + " broadcastRecevier/Intent strings" + 40*"=")
    bc_receivers =  list(cleanup_broadcastReceivers())
    print("head (n=10) bc_receivers: %r" % bc_receivers[:10])
    print("(found %d normalized broadcastReceiver strings)" % len(bc_receivers))

    # dependencies 
    print(40*"=" + " dependencies " + 40*"=")
    dependencies = list(cleanup_dependencies())
    print("head (n=10) dependencies: %r" % dependencies[:10])
    print("(found %d normalized dependencies strings)" % len(dependencies))

    #  metaDataNames 
    print(40*"=" + " metaDataNames " + 40*"=")
    metaDataNames = list(cleanup_metaDataNames())
    print("head (n=10) metaDataNames: %r" % metaDataNames[:10])
    print("(found %d normalized metaDataNames strings)" % len(metaDataNames))

    # permissions 
    print(40*"=" + " permissions " + 40*"=")
    permissions = list(cleanup_permissions())
    print("head (n=10) permissions: %r" % permissions[:10])
    print("(found %d normalized permissions strings)" % len(permissions))
