import os
import re
import glob
import tqdm
import ipdb

files = list(glob.glob("data/public/results/*/*html"))


def fix_static(file):
    with open(file) as f:
        fdata = f.read()

    matches = re.findall(r"\"resstyle.*?\"", fdata) + re.findall(r"\"images.*?\"", fdata)

    if "{% load static %}" not in fdata:
        fdata = "{% load static %}\n\n" + fdata

    for match in matches:
        new_text = "{% static 'results/" + match.strip('"') + "' %}"
        fdata = fdata.replace(match, new_text)
    # ipdb.set_trace()
    with open(file, "w") as f:
        f.write(fdata)


if __name__ == "__main__":
    for file in tqdm.tqdm(files):
        fix_static(file)
        # pass
