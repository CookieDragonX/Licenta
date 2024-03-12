import os,sys
from stat import *
import json
from ObjectManager import store, getHash
import Tree
import Blob
from prettyPrintLib import printColor

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
            if S_ISDIR(mode.st_mode) and file!='.cookie':
                getIndex(pathname, data)
        else:
            print('Skipping %s, unknown file type' % pathname) 
    return data

def saveIndex(dir, indexPath):
    dictionary=getIndex(dir,{})
    with open(indexPath, "w") as outfile:
        outfile.write(json.dumps(dictionary, indent=4))

def compareToIndex(dir):
    with open(os.path.join(dir, '.cookie', 'index'), 'r') as indexFile:
        index=json.load(indexFile)
    with open(os.path.join(dir, '.cookie', 'staging'), 'r') as stagingFile:
        staging=json.load(stagingFile)
    
    differences={'A':{},
               'D':{},
               'M':{}
               }
    
    differences=populateDifferences(dir, index, staging, differences)
    with open(os.path.join(dir, '.cookie', 'unstaged'), 'w') as unstaged:
        unstaged.write(json.dumps(differences, indent=4))
#some fixes in logic to be done here!!!
        
def populateDifferences(dir, index, staging, differences):
    for file in os.listdir(dir):
        pathname = os.path.join(dir, file)
        mode = os.lstat(pathname)
        if pathname not in index and pathname not in staging:
            if S_ISDIR(mode.st_mode):
                differences.update(getIndex(pathname,{}))
            elif S_ISREG(mode.st_mode):
                differences['A'].update({pathname: statDictionary(mode)})
            else:
                print('Skipping %s, unknown file type' % pathname)
    for item in index:
        if not os.path.exists(item):
            differences['D'].update({item: statDictionary(mode)})
            continue
        mode = os.lstat(item)
        if index.get(item)!=statDictionary(mode) and not S_ISDIR(mode.st_mode):
            differences['M'].update({item: statDictionary(mode)})
        
    return differences

def printDifferences(dir):
    with open(os.path.join(dir, '.cookie', 'unstaged'), 'r') as unstagedFile:
        unstaged=json.load(unstagedFile)
    if unstaged['A']!={}:
        printColor("-->Files added:",'green')
        print(*[file for file in unstaged['A']], sep=os.linesep)
    if unstaged['D']!={}:
        printColor("-->Files deleted:",'red')
        print(*[file for file in unstaged['D']], sep=os.linesep)
    if unstaged['M']!={}:
        printColor("-->Files modified:",'blue')
        print(*[file for file in unstaged['M']], sep=os.linesep)
    

def stageFiles(paths, repoPath):
    stagingPath=os.path.join(repoPath, '.cookie', 'staging')
    with open(stagingPath, 'r') as stagingFile:
        staging=json.load(stagingFile)
    for pathname in paths:
        staging[pathname]=statDictionary(os.lstat(pathname))
    with open(stagingPath, "w") as outfile:
        outfile.write(json.dumps(staging, indent=4))

def storeStagedFiles(stagedFiles):
    for file in stagedFiles:
        with open(file, 'r') as fp:
            fileContent=fp.read()
        blobContent=':'.join(['B', file, fileContent])
        store(Blob(blobContent.encode(encoding='utf-8')))

def hashTree(dir, stagedFiles):
    children=['T']
    for pathname in os.listdir(dir):
        if os.path.isdir(pathname):
            treeHash=hashTree(dir)
            children.extend([pathname,treeHash])
        elif os.path.isfile(pathname):
            children.extend([pathname,getHash(pathname)])
    tree=Tree(':'.join(children))
    store(tree)
    return tree.id.hexdigest()
