import os,sys
from stat import *
import json

def statDictionary(mode):
    dictionary={}
    dictionary['mode']=mode.st_mode
    dictionary['uid']=mode.st_uid
    dictionary['gid']=mode.st_gid
    dictionary['size']=mode.st_size
    dictionary['atime']=mode.st_atime
    dictionary['mtime']=mode.st_mtime
    dictionary['ctime']=mode.st_ctime
    return dictionary

def getIndex(dir, data):
    for file in os.listdir(dir):
        pathname = os.path.join(dir, file)
        mode = os.lstat(pathname)
        if S_ISDIR(mode.st_mode) or S_ISREG(mode.st_mode):
            data[pathname]=statDictionary(mode)
            if S_ISDIR(mode.st_mode):
                getIndex(pathname, data)
        else:
            print('Skipping %s, unknown file type' % pathname) 
    return data

def saveIndex(dir, indexPath):
    dictionary=getIndex(dir,{})
    index = json.dumps(dictionary, indent=4)
    with open(indexPath, "w") as outfile:
        outfile.write(index)

def compareToIndex(dir, infoPath):
    index=json.load(os.path.join(infoPath, 'index'))
    staged=json.load(os.path.join(infoPath, 'staging'))
    untracked={'A':None,
               'C':None,
               'D':None,
               'M':None,
               'R':None,
               'T':None,
               'U':None,
               'X':None}
    differences=populateDifferences(index,staged,untracked)
    # differences to untracked file

def populateDifferences(index, staged, untracked):
    for file in os.listdir(dir):
        pathname = os.path.join(dir, file)
        mode = os.lstat(pathname)
        if pathname not in index and pathname not in staged:
            if S_ISDIR(mode.st_mode):
                untracked.update(getIndex(pathname,{}))
            elif S_ISREG(mode.st_mode):
                untracked.update(statDictionary(mode))
            else:
                print('Skipping %s, unknown file type' % pathname)
        #elif differences in files:
        # function should be reccursive probably
    #return (untrackedFiles, differences)


# stage particular file because stage all is equivalent to saveIndex 
def stageFile(pathname, infoPath):
    #index=json.load(os.path.join(infoPath, 'index'))
    stagedPath=os.path.join(infoPath, 'staging')
    staged=json.load(stagedPath)
    staged.update(statDictionary(os.lstat(pathname)))
    with open(stagedPath, "w") as outfile:
        outfile.write(json.dumps(staged, indent=4))
    
