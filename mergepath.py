#*
import os
import os.path
import sys
import numpy as np
import pandas as pd
from itertools import compress

class subPathMerger:
    def __init__(self):
        self.addpath = []
        self.autopath = os.path.dirname(os.path.realpath(__file__))

    def rsubdir(self, x):
        allsub = os.listdir(x)
        abspaths = []
        _ = np.vectorize(lambda p: abspaths.append(r"{}\{}".format(x,p)), otypes=[str])
        np.where(_(allsub))
        isdir = np.vectorize(os.path.isdir)
        arr = np.array(abspaths)
        i = np.where(isdir(arr) == True)
        return arr[i]

    def merge(self, path):
        if len(self.rsubdir(path)) == 0:
            pass
        _ = np.vectorize(lambda x: self.addpath.append(x), otypes=[str])
        np.where(_(self.rsubdir(path)))
        vectormerge = np.vectorize(self.merge, otypes=[str])
        np.where(vectormerge(self.rsubdir(path)))
    
    def getAddpath(self, path):
        self.merge(path)
        return self.addpath
    
    def mergeAddpath(self, path):
        self.merge(path)
        pathappend = np.vectorize(sys.path.append, otypes = [str])
        np.where(pathappend(self.addpath))

    def findext(self, path, ext):
        dircontents = []
        fillcontents = lambda x: [dircontents.append(f) for f in os.listdir(x)]
        dirseiries = pd.Series(self.getAddpath(path))
        dirseiries.apply(fillcontents)
        pyfind = np.vectorize(lambda x: os.path.splitext(x)[1])
        r = np.where(pyfind(np.array(dircontents))==ext)
        return np.array(dircontents)[r]


merger = subPathMerger()
print(merger.findext(os.getcwd(), '.py'))