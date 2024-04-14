import os,sys
from stat import *
import json
from libs.objectLib.ObjectManager import store, load, createBlob
from libs.objectLib.Tree import Tree
from libs.objectLib.Commit import Commit
from utils.prettyPrintLib import printColor
from time import time
from libs.BranchingManager import updateBranchSnapshot
from libs.BasicUtils import statDictionary, printStaged, printUnstaged


def getIndex(dir, data, targetDirs, ignoreTarget, ignoreDirs):
    for file in os.listdir(dir):
        if file == '.cookie' or file == '.git' or file in ignoreDirs:
            continue
        if dir=='.':
            pathname=file
        else:
            pathname=os.path.join(dir,file)
        if file not in targetDirs:
            if not ignoreTarget:
                continue
        mode = os.lstat(pathname)
        if S_ISDIR(mode.st_mode) or S_ISREG(mode.st_mode):
            data[file]=statDictionary(mode)
            if S_ISDIR(mode.st_mode) and file!='.cookie':
                getIndex(pathname, data, targetDirs, ignoreTarget, ignoreDirs)
        else:
            print('Skipping %s, unknown file type' % file) 
    return data

def getTargetDirs():
    stagedFiles=getStagedFiles()
    dirs=[]
    for path in stagedFiles:
        separated_dirs=path.split(os.sep)
        for length in range(1,len(separated_dirs)+1):
            if separated_dirs[0:length]!=[]:
                dirs.append(os.path.join(*separated_dirs[0:length]))
    return dirs

def createCommit(args, DEBUG=False):
    generateStatus(args,quiet=True)
    if not isThereStagedStuff():
        printColor("There is noting to commit...", "blue")
        printColor("    Use 'cookie add <filename>' in order to prepare any change for commit.","blue")
        sys.exit(1) 
    metaData=['C']
    with open(os.path.join('.cookie', 'HEAD'), 'r') as headFile:
        head=json.load(headFile)
    if head["hash"] == "" :
        metaData.append('None')
    else :
        metaData.append(head["hash"])
    metaData.append('A')
    if DEBUG:
        metaData.append("Totally_Valid_Username")
    else:
        with open(os.path.join('.cookie', 'userdata'), 'r') as fp:
            userdata=json.load(fp)
            
        if userdata['user'] == "":
            printColor("Please login with a valid e-mail first!",'red')
            printColor("Use 'cookie login'",'white')
            sys.exit(0)
        else:
            metaData.append(userdata['user'])
    metaData.append(args.message)
    metaData.append(str(time()))
    targetDirs=getTargetDirs()
    ignoreDirs=getDeletedFiles()
    metaData.append(generateSnapshot(targetDirs, ignoreDirs))
    newCommit=Commit('?'.join(metaData))
    store(newCommit, os.path.join('.cookie', 'objects'))
    with open(os.path.join('.cookie', 'HEAD'), 'w') as headFile:
        head["hash"]=newCommit.getHash()
        headFile.seek(0)
        headFile.write(json.dumps(head, indent=4))
        currentBranch=head["name"]
    resetStagingAreaAndIndex(ignoreDirs)
    updateBranchSnapshot()
    printColor("Successfully commited changes on branch '{}'".format(currentBranch),"green")
    printColor("Current commit hash: '{}'".format(newCommit.getHash()), 'green')

def TreeHash(dir, index, objectsPath, targetDirs, ignoreDirs):
    metaData=['T']
    for file in os.listdir(dir):
        if dir=='.':
            pathname=file
        else:
            pathname=os.path.join(dir,file)
        if pathname == '.cookie' or pathname == '.git' or pathname in ignoreDirs:
            continue
        if pathname not in targetDirs: 
            if pathname in index:
                metaData.append(pathname)
                metaData.append(index[pathname]['hash']) #case where there's an unmodified file in the repo
            else:
                #case where file is not tracked 
                pass
        elif os.path.isdir(pathname):
            metaData.append(pathname)
            metaData.append(TreeHash(pathname, index, objectsPath, targetDirs, ignoreDirs))
        else:
            metaData.append(pathname)
            metaData.append(addFileToIndex(pathname))
    tree=Tree('?'.join(metaData))
    store(tree, objectsPath)
    return tree.getHash()

def generateSnapshot(targetDirs, ignoreDirs):
    with open(os.path.join('.cookie', 'index'), 'r') as indexFile:
        index=json.load(indexFile)
    return TreeHash(".", index, os.path.join('.cookie', 'objects'), targetDirs, ignoreDirs)

def addFileToIndex(pathname):
    indexPath=os.path.join('.cookie', 'index')
    with open(indexPath, 'r') as indexFile:
        index=json.load(indexFile)
    mode = os.lstat(pathname)
    blob = createBlob(os.path.join('.cookie', 'cache', pathname))
    store(blob, os.path.join('.cookie', 'objects'))
    index[pathname]=statDictionary(mode)
    index[pathname].update({"hash":blob.getHash()})
    with open(indexPath, 'w') as indexFile:
        indexFile.seek(0)
        indexFile.write(json.dumps(index, indent=4))
    return blob.getHash()

def compareToIndex():
    with open(os.path.join('.cookie', 'index'), 'r') as indexFile:
        index=json.load(indexFile)
    with open(os.path.join('.cookie', 'staged'), 'r') as stagingFile:
        staged=json.load(stagingFile)
    differences={'A':{},
               'D':{},
               'M':{}
               }
    differences=populateDifferences(".", index, staged, differences)
    with open(os.path.join('.cookie', 'unstaged'), 'w') as unstaged:
        unstaged.seek(0)
        unstaged.write(json.dumps(differences, indent=4))

def resolveAddedStaging(pathname, staged, index):
    #check for renamed files WIP
    possible_match=True
    try:
        oldFilePathname=list(staged['D'].keys())[list(staged['D'].values()).index(staged['A'][pathname])]
        print(oldFilePathname)
    except ValueError:
        possible_match=False
    if possible_match:
        if len(oldFilePathname) == 0:
            # no renaming here, no sir
            pass
        if len(oldFilePathname) > 1:
            printColor("[DEV ERROR][resolveAddedStaging] Unicorn case! More than one file with the same stat dictionary in index!", "red")
            sys.exit(1)
        elif len(oldFilePathname) == 1:
            oldFilePathname=oldFilePathname[0]
            if oldFilePathname not in index:
                printColor("[DEV ERROR][resolveAddedStaging] Detected file deletion but no such file is recorded: {}".format(oldFilePathname), "red")
                sys.exit(1)
            recordedBlob=load(index[oldFilePathname]['hash'], os.path.join('.cookie', 'objects'))
            with open(pathname, 'r'):
                newContent=pathname.read()
            if recordedBlob.content==newContent:
                #file renamed, remove from A and D, and add to R
                del staged['A'][pathname]
                del staged['D'][oldFilePathname]
                staged['R'][pathname]=oldFilePathname
        
    #check for copied files WIP
    indexCopy=index
    for val in indexCopy.values():
        del val['hash']
    possible_match=True
    try:
        list(indexCopy.keys())[list(indexCopy.values()).index(staged['A'][pathname])]
    except ValueError:
        possible_match=False
    if possible_match:
        if len(oldFilePathname) == 0:
            # no renaming here, no sir
            pass
        elif len(sourceFilePathname) > 1:
            printColor("[DEV ERROR][resolveAddedStaging] Unicorn case! More than one file with the same stat dictionary in index!", "red")
            sys.exit(1)
        elif len(sourceFilePathname) == 1:
            sourceFilePathname=sourceFilePathname[0]
            recordedBlob=load(index[sourceFilePathname]['hash'], os.path.join('.cookie', 'objects'))
            with open(pathname, 'r'):
                newContent=pathname.read()
            if recordedBlob.content==newContent:
                #file copied, remove from A and D, and add to R
                del staged['A'][pathname]
                staged['C'][pathname]=sourceFilePathname

def resolveDeletedStaging(pathname, staged, index):   
    # pass WHEN FILE IS DELETED BUT IS IN STAGED['A'] OR STAGED['M'] REMOVE FROM THERE!!!
    if pathname in staged['A']:
        del staged['D'][pathname]
        del staged['A'][pathname]
    if pathname in staged['M']:
        del staged['D'][pathname]
        del staged['M'][pathname]
    if pathname in staged['C']:
        del staged['D'][pathname]
        del staged['C'][pathname]
    if pathname in staged['R']:
        staged['D'][staged['R'][pathname]]="empty"
        del staged['R'][pathname]
    if pathname in staged['T']:
        del staged['D'][pathname]
        del staged['T'][pathname]
    if pathname in staged['X']:
        del staged['D'][pathname]
        del staged['X'][pathname]
    #also check here for renamed files!
    possible_match=True
    try:
        oldFilePathname=list(staged['A'].keys())[list(staged['A'].values()).index(staged['D'][pathname])]
    except ValueError:
        possible_match=False
    if possible_match:
        if len(oldFilePathname) == 0:
            # no renaming here, no sir
            pass
        if len(oldFilePathname) > 1:
            printColor("[DEV ERROR][resolveDeletedStaging] Unicorn case! More than one file with the same stat dictionary in index!", "red")
            sys.exit(1)
        elif len(oldFilePathname) == 1:
            oldFilePathname=oldFilePathname[0]
            if oldFilePathname not in index:
                printColor("[DEV ERROR][resolveDeletedStaging] Detected file deletion but no such file is recorded: {}".format(oldFilePathname), "red")
                sys.exit(1)
            recordedBlob=load(index[oldFilePathname]['hash'], os.path.join('.cookie', 'objects'))
            with open(pathname, 'r'):
                newContent=pathname.read()
            if recordedBlob.content==newContent:
                #file renamed, remove from A and D, and add to R
                del staged['D'][pathname]
                del staged['A'][oldFilePathname]
                staged['R'][pathname]=oldFilePathname

def resolveModifiedStaging(pathname, staged, index):
    # handle different types of changes
    if pathname in index:
        oldStats=index[pathname]
        recordedBlob=load(oldStats['hash'], os.path.join('.cookie', 'objects'))
        del oldStats['hash']
        with open(pathname, 'r') as fp:
            newContent=fp.read()
        if recordedBlob.content==newContent:
            if oldStats['uid']!=staged[pathname]['uid'] or oldStats['gid']!=staged[pathname]['gid'] or oldStats['mode']!=staged[pathname]['mode']:
                staged['T'][pathname]=staged['M'][pathname]
                del staged['M'][pathname]
            else:
                staged['X'][pathname]=staged['M'][pathname]
                del staged['M'][pathname]
        else:
            #file's just modified bro
            pass
    elif pathname in staged['A']:
        cacheFile(pathname)
        staged['A'][pathname]=staged['M'][pathname]
        del staged['M'][pathname]
    elif pathname in staged['M']:
        #file's just modified bro
        pass
    elif pathname in staged['T'] or pathname in staged['X']:
        oldStats=index[pathname]
        recordedBlob=load(oldStats['hash'], os.path.join('.cookie', 'objects'))
        del oldStats['hash']
        with open(pathname, 'r') as fp:
            newContent=fp.read()
        if recordedBlob.content==newContent:
            if oldStats['uid']!=staged[pathname]['uid'] or oldStats['gid']!=staged[pathname]['gid'] or oldStats['mode']!=staged[pathname]['mode']:
                staged['T'][pathname]=staged['M'][pathname]
                del staged['M'][pathname]
            else:
                staged['X'][pathname]=staged['M'][pathname]
                del staged['M'][pathname]
    elif pathname in staged['D']:
        printColor("[DEV ERROR][resolveModifiedStaging] File should not appear as modified if staged as deleted", "red")
    else:
        printColor("[DEV ERROR][resolveModifiedStaging] File should not appear as M if not in index or deleted or smth!", "red")
    pass

def resetStagingAreaAndIndex(ignoreDirs):
    with open(os.path.join(".cookie", "staged"), 'w') as fp:
        fp.write('{"A":{},"C":{},"D":{},"M":{},"R":{},"T":{},"X":{}}')
    indexPath = os.path.join(".cookie", "index") 
    with open(indexPath, "r") as indexFile:
        index=json.load(indexFile)
    for file in ignoreDirs:
        if file in index: 
            del index[file]
    with open(indexPath, "w") as indexFile:
        indexFile.seek(0)
        indexFile.write(json.dumps(index, indent=4))
        
#some fixes in logic to be done here, EDIT 12.3 some changes made needs testing. Big method :(
     #13.4 literally one month later, i think i got it?   
def populateDifferences(dir, index, staged, differences):
    #check files different to index
    for item in index:  #this makes sense, check for items in index if they are changed!
        if not os.path.exists(item): 
            if item not in staged['D']:
                statDict=index[item]
                del statDict["hash"]
                differences['D'].update({item: statDict})
            continue
        mode = os.lstat(item)
        itemData=index[item]
        del itemData['hash']
        if itemData!=statDictionary(mode) and not S_ISDIR(mode.st_mode):
            differences['M'].update({item: statDictionary(mode)})
    #check files different to staging area
    for item in staged['A']:
        if not os.path.exists(item):
            differences['D'].update({item: staged['A'][item]})
            continue
        mode = os.lstat(item)   
        if statDictionary(mode) != staged['A'][item]:
            differences['M'].update({item: statDictionary(mode)})
    for item in staged['M']:
        if not os.path.exists(item):
            differences['D'].update({item: staged['M'][item]})
            continue
        mode = os.lstat(item)
        if statDictionary(mode) != staged['M'][item]:
            differences['M'].update({item: statDictionary(mode)})
    for item in staged['D']:
        if os.path.exists(item):
            mode = os.lstat(item)
            differences['A'].update({item: statDictionary(mode)})
    for item in staged['C']:
        if not os.path.exists(item):
            differences['D'].update({item: staged['C'][item]})
            continue
    for item in staged['R']:
        if not os.path.exists(item):
            differences['D'].update({item: staged['R'][item]})
            continue
    for item in staged['T']:
        if not os.path.exists(item):
            differences['D'].update({item: staged['T'][item]})
    for item in staged['X']:
        if not os.path.exists(item):
            differences['D'].update({item: staged['X'][item]})
    #check mostly for new files
    findNewFiles(dir, index, staged, differences)
    return differences

def findNewFiles(dir, index, staged, differences):
    for file in os.listdir(dir):
        if file=='.cookie' or file=='.git' :
            continue
        if dir=='.':
            pathname=file
        else:
            pathname = os.path.join(dir, file)
        mode = os.lstat(pathname)
        if S_ISREG(mode.st_mode) and pathname not in index and pathname not in staged['A'] and pathname not in staged['D'] and pathname not in staged['C'] and pathname not in staged['R'] and pathname not in staged['X']:
            if S_ISREG(mode.st_mode):
                differences['A'].update({pathname: statDictionary(mode)})
            elif not S_ISDIR(mode.st_mode):
                print('Skipping %s, unknown file type' % pathname)
        elif S_ISDIR(mode.st_mode):
            differences.update(findNewFiles(pathname, index, staged, differences))
    return differences


def generateStatus(args, quiet=True):
    compareToIndex()
    if not quiet:
        outputStaged=False
        outputStaged=printStaged()
        outputUnstaged=False
        outputUnstaged=printUnstaged()
        if not outputStaged and not outputUnstaged:
            printColor("Nothing new here! No changes found.", "blue")

def stageFiles(paths):
    stagedPath=os.path.join('.cookie', 'staged')
    with open(stagedPath, 'r') as stagingFile:
        staged=json.load(stagingFile)
    unstagedPath=os.path.join('.cookie', 'unstaged')
    with open(unstagedPath, 'r') as unstagedFile:
        unstaged=json.load(unstagedFile)
    with open(os.path.join('.cookie', 'index'), 'r') as indexFile:
        index=json.load(indexFile)
    for pathname in paths:
        pathname=os.path.relpath(pathname, "")
        if pathname in unstaged['A']:
            staged['A'][pathname]=statDictionary(os.lstat(pathname))
            cacheFile(pathname)
            resolveAddedStaging(pathname, staged, index)
            del unstaged['A'][pathname]
        elif pathname in unstaged['D']:
            if pathname in index:
                statDict=index[pathname]
                del statDict["hash"]
                staged['D'][pathname]=statDict
            else:
                staged['D'][pathname]="empty"          #should be deleted so we allow empty value
            resolveDeletedStaging(pathname, staged, index) 
            del unstaged['D'][pathname]
        elif pathname in unstaged['M']:
            staged['M'][pathname]=statDictionary(os.lstat(pathname))
            cacheFile(pathname)
            resolveModifiedStaging(pathname, staged, index)
            del unstaged['M'][pathname]
        else:
            printColor("Cannot stage file '{}'".format(pathname), "red")
            printColor("Make sure it exists or contains differences!", "red")
    with open(stagedPath, "w") as outfile:
        outfile.seek(0)
        outfile.write(json.dumps(staged, indent=4))
    with open(unstagedPath, "w") as outfile:
        outfile.seek(0)
        outfile.write(json.dumps(unstaged, indent=4))

def unstageFiles(paths):
    stagedPath=os.path.join('.cookie', 'staged')
    with open(stagedPath, 'r') as stagingFile:
        staged=json.load(stagingFile)
    for path in paths:
        pathname=os.path.relpath(pathname, "")
        if path in staged['A']:
            del staged['A'][path]
        if path in staged['D']:
            del staged['D'][path]
        if path in staged['M']:
            del staged['M'][path]
    with open(stagedPath, "w") as outfile:
        outfile.seek(0)
        outfile.write(json.dumps(staged, indent=4))

def getStagedFiles():
    stagedPath=os.path.join('.cookie', 'staged')
    with open(stagedPath, 'r') as stagingFile:
        staged=json.load(stagingFile)
    stagedFiles=dict()
    stagedFiles.update(staged['A'])
    #stagedFiles.update(staged['D'])
    stagedFiles.update(staged['M'])
    stagedFiles.update(staged['C'])
    stagedFiles.update(staged['T'])
    stagedFiles.update(staged['R'])
    stagedFiles.update(staged['X'])
    return list(stagedFiles.keys())

def getDeletedFiles():
    stagedPath=os.path.join('.cookie', 'staged')
    with open(stagedPath, 'r') as stagingFile:
        staged=json.load(stagingFile)
    deletedFiles=dict()
    deletedFiles.update(staged['D'])
    return list(deletedFiles.keys())

def isThereStagedStuff():
    stagedPath=os.path.join('.cookie', 'staged')
    with open(stagedPath, 'r') as stagingFile:
        staged=json.load(stagingFile)
    if staged['A']!={} or staged['D']!={} or staged['M']!={} or staged['C']!={} or staged['R']!={} or staged['T']!={} or staged['X']!={}:
        return True

def cacheFile(pathname):
    with open(pathname, 'r') as fileToCache:
        fileContent=fileToCache.read()
    os.makedirs(os.path.abspath(os.path.join('.cookie', 'cache', pathname, os.pardir)), exist_ok=True)
    with open(os.path.join('.cookie', 'cache', pathname), 'w') as cacheFile:
        cacheFile.write(fileContent)