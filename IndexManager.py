import os,sys
from stat import *
import json
from ObjectManager import store, createBlob
from Tree import Tree
from Blob import Blob
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


def getIndex(dir, data, targetDirs, ignoreTarget):
    for file in os.listdir(dir):
        pathname = os.path.join(dir, file)
        if pathname not in targetDirs:
            if not ignoreTarget:
                continue
        mode = os.lstat(pathname)
        if S_ISDIR(mode.st_mode) or S_ISREG(mode.st_mode):
            data[pathname]=statDictionary(mode)
            if S_ISDIR(mode.st_mode) and file!='.cookie':
                getIndex(pathname, data, targetDirs, ignoreTarget)
        else:
            print('Skipping %s, unknown file type' % pathname) 
    return data

def saveIndex(dir, targetDirs):
    indexPath=os.path.join(dir, '.cookie', 'index')
    dictionary=getIndex(dir, {}, targetDirs, False)
    with open(indexPath, "w") as outfile:
        outfile.write(json.dumps(dictionary, indent=4))

def getTargetDirs(repoPath):
    stagedFiles=getStagedFiles(repoPath)
    dirs=[]
    for path in stagedFiles:
        separated_dirs=path.split(os.sep)
        for length in range(1,len(separated_dirs)+1):
            if separated_dirs[0:length]!=[]:
                dirs.append(os.path.join(*separated_dirs[0:length]))
    return dirs

def TreeHash(dir, index, objectsPath, repoPath, targetDirs):
    metaData=['T']
    for pathname in os.listdir(dir):
        if pathname == '.cookie' or pathname == '.git':
            continue
        if pathname not in targetDirs: 
            if pathname in index:
                metaData.append(index[pathname]['hash']) #case where there's an unmodified file in the repo
            else:
                #case where file is not tracked 
                pass
        elif os.is_dir(pathname):
            metaData.append(TreeHash(pathname, index, objectsPath, repoPath, targetDirs))
        else:
            if pathname in index:
                metaData.append(index['hash'])
            else:
                metaData.append(addFileToIndex(pathname, repoPath))
    tree=Tree(':'.join(metaData))
    store(tree, objectsPath)
    return tree.getHash()

def addFileToIndex(pathname, repoPath):
    indexPath=os.path.join(repoPath, '.cookie', 'index')
    with open(indexPath, 'r') as indexFile:
        index=json.load(indexFile)
    mode = os.lstat(pathname)
    blob = createBlob(pathname)
    store(blob, os.path.join(repoPath, '.cookie', 'objects'))
    index[pathname]=statDictionary(mode)
    index[pathname].update({"hash":blob.getHash()})
    return blob.getHash()

def compareToIndex(dir):
    with open(os.path.join(dir, '.cookie', 'index'), 'r') as indexFile:
        index=json.load(indexFile)
    with open(os.path.join(dir, '.cookie', 'staged'), 'r') as stagingFile:
        staged=json.load(stagingFile)
    differences={'A':{},
               'D':{},
               'M':{}
               }
    differences=populateDifferences(dir, index, staged, differences)
    with open(os.path.join(dir, '.cookie', 'unstaged'), 'w') as unstaged:
        unstaged.write(json.dumps(differences, indent=4))

def resolveStagingMatches(dir, thorough=False):
    #method should match some stuff to find renames/movement/copying/renamed
    pass

def resetStagingArea(repoPath):
    with open(os.path.join(repoPath, ".cookie", "staged"), 'w') as fp:
        fp.write('{"A":{},"C":{},"D":{},"M":{},"R":{},"T":{},"X":{}}')
        
        
#some fixes in logic to be done here, EDIT 12.3 some changes made needs testing. Big method :(
        
def populateDifferences(dir, index, staged, differences):
    for file in os.listdir(dir):
        pathname = os.path.join(dir, file)
        mode = os.lstat(pathname)
        if pathname not in index and pathname not in staged['A'] and pathname not in staged['D'] and pathname not in staged['M'] and pathname not in staged['C'] and pathname not in staged['R'] and pathname not in staged['T'] and pathname not in staged['X']:
            if S_ISDIR(mode.st_mode):
                differences.update(getIndex(pathname, {} , targetDirs=[], ignoreTarget=True))
            elif S_ISREG(mode.st_mode):
                differences['A'].update({pathname: statDictionary(mode)})
            else:
                print('Skipping %s, unknown file type' % pathname)
        elif S_ISDIR(mode.st_mode):
            differences=populateDifferences(pathname, index, staged, differences)
    for item in index:
        if not os.path.exists(item):
            differences['D'].update({item: statDictionary(mode)})
            continue
        mode = os.lstat(item)
        if index.get(item)!=statDictionary(mode) and not S_ISDIR(mode.st_mode):
            differences['M'].update({item: statDictionary(mode)})        
    return differences

def printStaged(dir):
    with open(os.path.join(dir, '.cookie', 'staged'), 'r') as stagedFile:
        staged=json.load(stagedFile)
    if staged['A']!={} or staged['D']!={} or staged['M']!={} or staged['C']!={} or staged['R']!={} or staged['T']!={} or staged['X']!={}:
        printColor("    Changes to be committed:","white")
        if staged['A']!={}:
            printColor("-->Files added:",'green')
            print(*["   {}".format(file) for file in staged['A']], sep=os.linesep)
        if staged['D']!={}:
            printColor("-->Files deleted:",'green')
            print(*["   {}".format(file) for file in staged['D']], sep=os.linesep)
        if staged['M']!={}:
            printColor("-->Files modified:",'green')
            print(*["   {}".format(file) for file in staged['M']], sep=os.linesep)
        if staged['C']!={}:
            printColor("-->Files copied:",'green')
            print(*["   {}".format(file) for file in staged['M']], sep=os.linesep)
        if staged['R']!={}:
            printColor("-->Files renamed:",'green')
            print(*["   {}".format(file) for file in staged['M']], sep=os.linesep)
        if staged['T']!={}:
            printColor("-->Files with type changes:",'green')
            print(*["   {}".format(file) for file in staged['M']], sep=os.linesep)
        if staged['X']!={}:
            printColor("-->Files with unknown modifications:",'green')
            print(*["   {}".format(file) for file in staged['M']], sep=os.linesep)
    
def printUnstaged(dir):
    with open(os.path.join(dir, '.cookie', 'unstaged'), 'r') as unstagedFile:
        unstaged=json.load(unstagedFile)
    if unstaged['A']!={} or unstaged['D']!={} or unstaged['M']!={}:
        printColor("    Unstaged changes:","white")
        if unstaged['A']!={}:
            printColor("-->Files untracked:",'red')
            print(*["   {}".format(file) for file in unstaged['A']], sep=os.linesep)
        if unstaged['D']!={}:
            printColor("-->Files deleted:",'red')
            print(*["   {}".format(file) for file in unstaged['D']], sep=os.linesep)
        if unstaged['M']!={}:
            printColor("-->Files modified:",'red')
            print(*["   {}".format(file) for file in unstaged['M']], sep=os.linesep)
        printColor("    Use 'cookie add <filename>' in order to prepare any change for commit.","blue")
    

def stageFiles(paths, repoPath):
    stagedPath=os.path.join(repoPath, '.cookie', 'staged')
    with open(stagedPath, 'r') as stagingFile:
        staged=json.load(stagingFile)
    unstagedPath=os.path.join(repoPath, '.cookie', 'unstaged')
    with open(unstagedPath, 'r') as unstagedFile:
        unstaged=json.load(unstagedFile)
    for pathname in paths:
        if pathname in unstaged['A']:
            staged['A'][pathname]=statDictionary(os.lstat(pathname))
            del unstaged['A'][pathname]
        elif pathname in unstaged['D']:
            staged['D'][pathname]=statDictionary(os.lstat(pathname))
            del unstaged['D'][pathname]
        elif pathname in unstaged['M']:
            staged['M'][pathname]=statDictionary(os.lstat(pathname))
            del unstaged['M'][pathname]
    with open(stagedPath, "w") as outfile:
        outfile.write(json.dumps(staged, indent=4))
    with open(unstagedPath, "w") as outfile:
        outfile.write(json.dumps(unstaged, indent=4))

def getStagedFiles(repoPath):
    stagedPath=os.path.join(repoPath, '.cookie', 'staged')
    with open(stagedPath, 'r') as stagingFile:
        staged=json.load(stagingFile)
    stagedFiles=dict()
    stagedFiles.update(staged['A'])
    stagedFiles.update(staged['D'])
    stagedFiles.update(staged['M'])
    stagedFiles.update(staged['C'])
    stagedFiles.update(staged['T'])
    stagedFiles.update(staged['R'])
    stagedFiles.update(staged['X'])
    return list(stagedFiles.keys())

def storeStagedFiles(repoPath):
    stagedFiles=getStagedFiles(repoPath)
    for file in stagedFiles:
        with open(file, 'r') as fp:
            fileContent=fp.read()
        blobContent=':'.join(['B', file, fileContent])
        store(Blob(blobContent.encode(encoding='utf-8')), os.path.join(repoPath, '.cookie', 'objects'))

def isThereStagedStuff(repoPath):
    stagedPath=os.path.join(repoPath, '.cookie', 'staged')
    with open(stagedPath, 'r') as stagingFile:
        staged=json.load(stagingFile)
    if staged['A']!={} or staged['D']!={} or staged['M']!={} or staged['C']!={} or staged['R']!={} or staged['T']!={} or staged['X']!={}:
        return True