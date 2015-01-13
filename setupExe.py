from distutils.core import setup
import py2exe
import os
from sc2reader import utils


importDir = 'c:/Users/Xanthus/Documents/GitHub/sc2reader/sc2reader/data'
baseDir = 'c:/Users/Xanthus/Documents/GitHub/sc2reader'
Mydata_files = []
for filepath in utils.get_files(importDir, depth=-1):
    relPath = os.path.relpath(filepath, baseDir)
    path, file = os.path.split(relPath)
    ext = os.path.splitext(relPath)[1]
    if ext == '.csv' or ext == '.json':
        Mydata_files.append((os.path.normpath(path), [os.path.normpath(filepath)]))
setup(
    data_files=Mydata_files,
    zipfile=None,
    options={'py2exe':{
        'optimize':2,
        'bundle_files':0,
        'compressed':True
    }},
    console=['sc2reader/scripts/PACAnalysis.py']
    )