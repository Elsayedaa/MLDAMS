#Caching version
import sys
from pathlib import PurePath
filepath = PurePath(__file__)
abspath = str(filepath.parent)
appParentDir = abspath.replace(r'\Curation_Related_GUI_Branch','')
sys.path.append(appParentDir)
import os, os.path 
import re
import pandas as pd
import pickle
import csv

pd.set_option('display.width', 1000)
pd.options.display.max_rows = 999999

tcompdir = r"\\dm11\mousebrainmicro\tracing_complete"

def locCompiler():
    locdic = {"sample":[], "tag":[], "somaloc":[], "script":[]}

    incomplete = [
        "2015-07-11-G-011",
        "2015-07-11-G-022",
        "2016-04-04-R-015",
        "2016-04-04-R-016",
        "2016-10-25-G-037",
        "2016-10-31-R-020",
        "2017-02-22-G-013",
        "2017-02-22-R-003",
        "2018-08-01-G-281"
    ]
    
    for x in os.listdir(tcompdir):
        if re.search(r"\d+-\d+-\d+$",x):
            for y in os.listdir("{}\{}".format(tcompdir,x)):
                if re.search(r"[A-Z]-\d*",y) and "{}-{}".format(x,y) not in incomplete and "soma.txt" in os.listdir("{}\{}\{}".format(tcompdir,x,y)):
                    with open("{}\{}\{}\soma.txt".format(tcompdir, x, y)) as soma:
                        somaread = soma.read()
                        locdic["sample"].append(x)
                        locdic["tag"].append(y)
                        if 'Curated compartment:' in somaread:
                            ic = somaread.find(":")
                            isc = somaread.find("\n")
                            locdic["somaloc"].append(somaread[ic+1:].strip())
                            locdic["script"].append(somaread[:isc].strip())
                        else:
                            locdic["somaloc"].append(somaread.strip())
                            locdic["script"].append(somaread.strip())
                elif re.search(r"[A-Z]-\d*",y) and "{}-{}".format(x, y) not in incomplete and "soma.txt" not in os.listdir("{}\{}\{}".format(tcompdir, x, y)):
                    locdic["sample"].append(x)
                    locdic["tag"].append(y)
                    locdic["somaloc"].append("Soma location cannot be found")
    somalocdf = pd.DataFrame.from_dict(locdic)
    somalocdf.to_pickle(r'{}\cached_somaloc.pkl'.format(appParentDir))
    return somalocdf

def datereader(datetimestr):
    moddates = pd.read_pickle(r'{}\moddates.pkl'.format(appParentDir))
    if str(moddates.loc[(moddates["path"]==tcompdir)]["moddate"].values[0]) == datetimestr:
        return True

def dataloader(reload=None):
    print("Loading soma location data...")
    readdate = datereader(str(os.path.getmtime(tcompdir)))
    if readdate == True and reload == None:
        df = pd.read_pickle(r'{}\cached_somaloc.pkl'.format(appParentDir))
        print("Location data loaded from cache")
    elif reload == True or readdate == None:
        print("Tracing complete folder was recently updated, recompiling soma location data...")
        df = locCompiler()

        pd.DataFrame.from_dict({
            "path": [tcompdir], 
            "moddate": [str(os.path.getmtime(tcompdir))]
        }).to_pickle(r'{}\moddates.pkl'.format(appParentDir))

        print("Soma location data recompiled successfully.")
    return df 

def availInSamp(*s, reload=None):
    df = dataloader(reload=reload)
    sample_dict={}
    for sample in df["sample"].values:
        if sample not in sample_dict:
            sample_dict[sample] = list(df.loc[(df["sample"]==sample)]["tag"].values)
    if s == ():
        return sample_dict
    else:
        return sample_dict[s[0]]

def locator(sample, *tag, reload=None):
    df = dataloader(reload=reload)
    if tag == ():
        for somaloc in list(df.loc[(df["sample"]==sample)]["somaloc"].values):
            print(somaloc)
        if len(df.loc[(df["sample"]==sample)].index) == 0:
            print('Pandas is returning an empty dataframe.\nThis might be caused by a missing sample folder in Tracing Complete.')
        else:
            return df.loc[(df["sample"]==sample)]
    else:
        try:
            return df.loc[(df["sample"]==sample)&(df["tag"]==tag[0])]["somaloc"].values[0]
        except Exception as e:
            if 'index 0 is out of bounds for axis 0 with size 0' in e.args[0]:
                print('Pandas is returning an empty series for the sample/tag combo provided.\nThis might be caused by a missing sample or neuron folder in Tracing Complete.')
