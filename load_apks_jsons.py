#!/usr/bin/env python

import os
import sys
import json
from pathlib import Path
import argparse
from jsonschema import validate
import time
from tqdm import tqdm
import pandas as pd
from typing import Dict

from bloom_filter import BloomFilter

import searchspace



parser = argparse.ArgumentParser(description='Process sampled domain lists for clean and trackers')

parser.add_argument('stop_after', metavar='N', type=int, nargs='?', help='Stop after N files', default=-1)
parser.add_argument('path', type=str, help="root path where to search for clean and trackers/ subdirs")
args = parser.parse_args()



# instantiate BloomFilter with custom settings,
# max_elements is how many elements you expect the filter to hold.
# error_rate defines accuracy; You can use defaults with
# `BloomFilter()` without any arguments. Following example
# is same as defaults:
# bloom = BloomFilter(max_elements=100000, error_rate=0.01)

cache = dict()

def calc_domains(data: dict) -> (int, int, int):
    """ here we want to calculate the number of occurences of (good/tracker/unknown) domains """
    nr_clean = 0
    nr_trackers = 0
    nr_unknown = 0


    for el in data["apks"]:
        for d in el["domainNames"]:
            d = searchspace.normalize_to_basedomain(searchspace.strip_stuff_from_domains(d))
            print("XXX %s" %d)
            if d in searchspace.known_clean_domains:
                nr_clean += 1
            if d in searchspace.known_tracker_domains:
                nr_trackers += 1
            if d not in searchspace.known_tracker_domains and d not in searchspace.known_clean_domains:
                nr_unknown +=1 
    return (nr_clean, nr_trackers, nr_unknown)


def filter_out_appIds(j: dict) -> Dict:
    for el in j["apks"]:
        appId = el["applicationId"]
        if appId not in cache:
            cache[appId] = 1
        else:
            print("deleting duplicate appId %s" % (appId,))
            j["apks"] = []
            return j
    return j
    

def read_json(filename: Path) -> Dict:
    # validate the json file actually
    with open(filename, 'r') as f:
        data = json.load(f)
        data = filter_out_appIds(data)
        (nr_clean_domains, nr_tracker_domains, nr_unknown_domains) = calc_domains(data)
    return { "nr_tracker_domains": nr_tracker_domains, 
        "nr_clean_domains": nr_clean_domains,
        "nr_unknown_domains": nr_unknown_domains }


def evaluate_dir(basedir: Path) -> pd.DataFrame:
    """
    walks over @basedir and expects two subfolders: clean/ and trackers/.
    In each of these, it will search for .json files and iterate over them, load the JSON 
    files and create a dataframe for training.

    add the result to a pd.DataFrame which is returned.
    Format of the df is described in https://gitlab.com/trackingthetrackers/wiki/-/wikis/Pandas-internal-data-format-for-the-ML-part
    :param basedir:
    :return: pd.DataFrame
    """
    df = pd.DataFrame()
    tqdm.pandas(ncols=50)
    l = [] 

    files = sorted(Path(basedir).glob('**/*.json'))
    cleanfiles = list(filter(lambda i: "clean" in str(i), files))
    trackerfiles = list(filter(lambda i: "trackers" in str(i), files))
    print("going to process %d clean and %d tracker JSON files (but max. %d files)." %(len(cleanfiles), len(trackerfiles), args.stop_after))
    i=0
    for f in cleanfiles:
        print("processing %s" %f)
        data=read_json(f)
        print(data)
        # TODO: turn permissions, metaDataNames, ... to bitmaps
        # TODO: put all of this into a dataframe as documented in https://gitlab.com/trackingthetrackers/wiki/-/wikis/Pandas-internal-data-format-for-the-ML-part
        # TODO: verify of these two steps are correct
        # TODO maybe: plot distribution of nr_clean_domains/nr_tracker_domains etc. for trackers as well as clean. What's the overlap in the distributions?
        # TODO finally: send the dataframe to the ML part
        #df.loc[i] = { "filename": filename, "sha256": "xxx", "ground truth": "clean", "prediction": 0.1 }
        i+=1
        if i >= int(args.stop_after/2):
            break
    for f in trackerfiles:
        print("processing %s" %f)
        data=read_json(f)
        print(data)
        #l.append({ "filename": filename, "ground truth": "trackers", "prediction": 0.1})
        i+=1 
        if i >= int(args.stop_after):
            break
    return json.dumps(l)


if __name__ == "__main__":
    searchspace.load()
    # print(searchspace.known_tracker_domains)
    # print(searchspace.known_clean_domains)
    evaluate_dir(args.path)



