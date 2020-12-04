import os
import glob
import tqdm
import json
import re


tracker_file = "trackers.json"

with open(tracker_file) as f:
    tjs = json.load(f)
    tcodes = tjs.values()

htmls = list(glob.glob("*html")) + list(glob.glob("*/*html")) + list(glob.glob("*/*/*html")) + list(glob.glob("*/*/*/*html"))


def add_tracker(tcode, file):
    with open(file) as f:
        curr = f.read()
    if not re.sub("\s", "", tcode) in re.sub("\s", "", curr):
        with open(file, "w") as f:
            f.write(curr.replace("</head>", f"{tcode}\n</head>"))

def remove_tracker(tcode, file):
    with open(file, "w") as f:
        f.write(curr.replace(tcode, ""))


if __name__ == "__main__":

    for file in tqdm.tqdm(htmls):
        for tcode in tcodes:
            add_tracker(tcode, file)
            # remove_tracker(tcode, file)
