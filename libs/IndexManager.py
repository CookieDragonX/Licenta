import os,sys
from stat import *
from libs.objectLib.ObjectManager import store, load, createBlob
from libs.objectLib.Tree import Tree
from libs.objectLib.Commit import Commit
from utils.prettyPrintLib import printColor
from time import time
from libs.BranchingManager import updateBranchSnapshot
from libs.BasicUtils import statDictionary, printStaged, printUnstaged, dumpResource, getResource, cacheFile
from libs.LogsManager import logCommit
from libs.RemotingManager import getRemoteResource
from copy import deepcopy
import paramiko
import traceback    

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
    head=getResource("head")
    if head["hash"] == "" :
        metaData.append('None')
    else :
        metaData.append(head["hash"])
    metaData.append('A')
    if DEBUG:
        metaData.append("Totally_Valid_Username")
    else:
        userdata=getResource("userdata")    
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
    logCommit(newCommit)
    head["hash"]=newCommit.getHash()
    currentBranch=head["name"]
    dumpResource("head", head)
    
    resetStagingAreaAndIndex(ignoreDirs)
    updateBranchSnapshot()
    printColor("Successfully commited changes on branch '{}'".format(currentBranch),"green")
    printColor("Current commit hash: '{}'".format(newCommit.getHash()), 'green')

def generateSnapshot(targetDirs, ignoreDirs):
    index=getResource("index")
    return TreeHash(".", index, os.path.join('.cookie', 'objects'), targetDirs, ignoreDirs)

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
            elif os.path.isdir(pathname): 
                metaData.append(pathname)
                metaData.append(TreeHash(pathname, index, objectsPath, targetDirs, ignoreDirs))
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

def addFileToIndex(pathname):
    index=getResource("index")
    mode = os.lstat(pathname)
    blob = createBlob(os.path.join('.cookie', 'cache', "index_cache", pathname), forcePath=pathname)
    store(blob, os.path.join('.cookie', 'objects'))
    index[pathname]=statDictionary(mode)
    index[pathname].update({"hash":blob.getHash()})
    dumpResource("index", index)
    return blob.getHash()

def compareToIndex():
    index=getResource("index")
    staged=getResource("staged")
    differences={'A':{},
               'D':{},
               'M':{}
               }
    differences=populateDifferences(".", index, staged, differences)
    dumpResource("unstaged", differences)

def resolveAddedStaging(pathname, staged, index):
    #check for renamed files 
    stagedAddedPathCopy=deepcopy(staged['A'][pathname])
    del stagedAddedPathCopy['mtime']
    for item in list(staged['D']):
        stagedDeletedCopy = {key: value for key, value in staged['D'][item].items() if 'mtime' not in key}
        if stagedAddedPathCopy == stagedDeletedCopy:
            if item not in index:
                del staged['D'][item]
            else:
                oldObject=load(index[item]['hash'], os.path.join('.cookie', 'objects'))
                with open(pathname, "r+b") as newFile:
                    newFileContent=newFile.read()
                if newFileContent==oldObject.content:
                    # File renamed, delete stuff from where it was and add to 'R'
                    del staged['A'][pathname]
                    del staged['D'][item]
                    staged['R'][pathname]=[]
                    staged['R'][pathname].append(item)
                    staged['R'][pathname].append(statDictionary(os.lstat(pathname)))
                    return
    #check for copied files
    stagedAddedPathCopy=deepcopy(staged['A'][pathname])
    del stagedAddedPathCopy['mtime']
    del stagedAddedPathCopy['ctime']
    indexCopy=deepcopy(index)
    for item in list(indexCopy):
        del indexCopy[item]['mtime']
        del indexCopy[item]['ctime']
        del indexCopy[item]['hash']
        if indexCopy[item] == stagedAddedPathCopy:
            oldObject=load(index[item]['hash'], os.path.join('.cookie', 'objects'))
            with open(pathname, "r+b") as newFile:
                newFileContent=newFile.read()
            if newFileContent==oldObject.content:
                # File renamed, delete stuff from where it was and add to 'C'
                del staged['A'][pathname]
                staged['C'][pathname]=[]
                staged['C'][pathname].append(item)
                staged['C'][pathname].append(statDictionary(os.lstat(pathname)))
                return


def resolveDeletedStaging(pathname, staged, index):   
    # pass WHEN FILE IS DELETED BUT IS IN STAGED['A'] OR STAGED['M'] REMOVE FROM THERE!!!
    if pathname in staged['A']:
        del staged['D'][pathname]
        del staged['A'][pathname]
        return
    if pathname in staged['M']:
        del staged['D'][pathname]
        del staged['M'][pathname]
        return
    if pathname in staged['C']:
        del staged['D'][pathname]
        del staged['C'][pathname]
        return
    if pathname in staged['R']:
        staged['D'][staged['R'][pathname]]="empty"
        del staged['R'][pathname]
        return
    if pathname in staged['T']:
        del staged['D'][pathname]
        del staged['T'][pathname]
        return
    if pathname in staged['X']:
        del staged['D'][pathname]
        del staged['X'][pathname]
        return
    #also check here for renamed files!
    stagedDeletedPathCopy=deepcopy(staged['D'][pathname])
    del stagedDeletedPathCopy['mtime']
    for item in list(staged['A']):
        stagedAddedCopy = {key: value for key, value in staged['A'][item].items() if 'mtime' not in key}
        if stagedDeletedPathCopy == stagedAddedCopy:
            oldObject=load(index[pathname]['hash'], os.path.join('.cookie', 'objects'))
            with open(item, "r+b") as newFile:
                newFileContent=newFile.read()
            if newFileContent==oldObject.content:
                # File renamed, delete stuff from where it was and add to 'R'
                del staged['A'][item]
                del staged['D'][pathname]
                staged['R'][item]=[]
                staged['R'][item].append(pathname)
                staged['R'][item].append(statDictionary(os.lstat(item)))

def resolveModifiedStaging(pathname, staged, index):
   
    # handle different types of changes
    if pathname in index:
        oldStats=deepcopy(index[pathname])
        recordedBlob=load(oldStats['hash'], os.path.join('.cookie', 'objects'))
        del oldStats['hash']
        with open(pathname, 'r+b') as fp:
            newContent=fp.read()
        if recordedBlob.content==newContent:
            if oldStats['uid']!=staged[pathname]['uid'] or oldStats['gid']!=staged[pathname]['gid'] or oldStats['mode']!=staged[pathname]['mode']:
                staged['T'][pathname]=staged['M'][pathname]
                del staged['M'][pathname]
            else:
                staged['X'][pathname]=staged['M'][pathname]
                del staged['M'][pathname]
        else:
            #file's just modified
            pass
    # handle changes since file was staged
    elif pathname in staged['A']:
         #yet again, check here for renamed files!
        stagedAddedPathCopy=deepcopy(staged['M'][pathname])
        del stagedAddedPathCopy['mtime']
        for item in list(staged['D']):
            stagedDeletedCopy = {key: value for key, value in staged['D'][item].items() if 'mtime' not in key}
            if stagedAddedPathCopy == stagedDeletedCopy:
                if item not in index:
                    del staged['D'][item]
                else:
                    oldObject=load(index[item]['hash'], os.path.join('.cookie', 'objects'))
                    with open(pathname, "r+b") as newFile:
                        newFileContent=newFile.read()
                    if newFileContent==oldObject.content:
                        # File renamed, delete stuff from where it was and add to 'R'
                        del staged['M'][pathname]
                        del staged['D'][item]
                        del staged['A'][pathname]
                        staged['R'][pathname]=[]
                        staged['R'][pathname].append(item)
                        staged['R'][pathname].append(statDictionary(os.lstat(pathname)))
                        return
        cacheFile(pathname)
        staged['A'][pathname]=staged['M'][pathname]
        del staged['M'][pathname]
    elif pathname in staged['R']:
        staged['A'][pathname]=staged['M'][pathname]
        del staged['M'][pathname]
        indexCopy=deepcopy(index[staged['R'][pathname][0]])
        del indexCopy['hash']
        staged['D'][staged['R'][pathname][0]]=indexCopy
        del staged['R'][pathname]
    elif pathname in staged['C']:
        staged['A'][pathname]=staged['M'][pathname]
        del staged['M'][pathname]
        del staged['C'][pathname]
    elif pathname in staged['T'] or pathname in staged['X']:
        oldStats=deepcopy(index[pathname])
        recordedBlob=load(oldStats['hash'], os.path.join('.cookie', 'objects'))
        del oldStats['hash']
        with open(pathname, 'r+b') as fp:
            newContent=fp.read()
        if recordedBlob.content==newContent:
            if oldStats['uid']!=staged[pathname]['uid'] or oldStats['gid']!=staged[pathname]['gid'] or oldStats['mode']!=staged[pathname]['mode']:
                staged['T'][pathname]=staged['M'][pathname]
                del staged['M'][pathname]
            else:
                staged['X'][pathname]=staged['M'][pathname]
                del staged['M'][pathname]
    elif pathname in staged['M']:
        #file's just modified
        pass
    elif pathname in staged['D']:
        printColor("[DEV ERROR][resolveModifiedStaging] File should not appear as modified if staged as deleted", "red")
    else:
        printColor("[DEV ERROR][resolveModifiedStaging] File should not appear as M if not in index or deleted or smth!", "red")

def resetStagingAreaAndIndex(ignoreDirs):
    dumpResource("staged", {"A":{},"C":{},"D":{},"M":{},"R":{},"T":{},"X":{}})
    index=getResource("index")
    for file in ignoreDirs:
        if file in index: 
            del index[file]
    dumpResource("index", index)
        
#some fixes in logic to be done here, EDIT 12.3 some changes made needs testing. Big method :(
     #13.4 literally one month later, i think i got it?   
     #14.4 looks good
def populateDifferences(dir, index, staged, differences):
    #check files different to index
    for item in index:
        if not os.path.exists(item): 
            if item not in staged['D']:
                addToDelete=True
                for renamedFile in staged['R']:
                    if item in staged['R'][renamedFile]:
                        addToDelete=False
                for copiedFile in staged['C']:
                    if item in staged['C'][copiedFile]:
                        addToDelete=False
                if addToDelete :
                    statDict=index[item]
                    del statDict["hash"]
                    differences['D'].update({item: statDict})
            continue
        mode = os.lstat(item)
        itemData=deepcopy(index[item])
        del itemData['hash']
        del itemData['ctime']
        stats = statDictionary(mode)
        del stats['ctime']
        if itemData!=stats and not S_ISDIR(mode.st_mode):
            if item not in staged["M"]:
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
            differences['D'].update({item: staged['C'][item][1]})
            continue
        mode = os.lstat(item)
        if statDictionary(mode) != staged['C'][item][1]:
            differences['M'].update({item: statDictionary(mode)})
    for item in staged['R']:
        if not os.path.exists(item):
            differences['D'].update({item: staged['R'][item][1]})
            continue    
        mode = os.lstat(item)
        if statDictionary(mode) != staged['R'][item][1]:
            differences['M'].update({item: statDictionary(mode)})
    for item in staged['T']:
        if not os.path.exists(item):
            differences['D'].update({item: staged['T'][item]}) 
        mode = os.lstat(item)
        if statDictionary(mode) != staged['T'][item]:
            differences['M'].update({item: statDictionary(mode)})
    for item in staged['X']:
        if not os.path.exists(item):
            differences['D'].update({item: staged['X'][item]})
        mode = os.lstat(item)
        if statDictionary(mode) != staged['X'][item][1]:
            differences['M'].update({item: statDictionary(mode)})
    #check for new files
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
        head = getResource("head")
        refs = getResource("refs")
        config = getResource("remote_config")
        try:
            try:
                private_key = paramiko.RSAKey.from_private_key_file(config["local_ssh_private_key"])
            except OSError:
                printColor("Please configure remote data first!", "red")
                sys.exit(1)
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                ssh_client.connect(config["host"] , config["port"], config["remote_user"], pkey=private_key)
            except TimeoutError:
                printColor("Connection attempt timed out!", "red")
                traceback.print_exc()
                printColor("Check remote host configuration", "red")
                sys.exit(1) 
                
            if config["remote_os"] == 'nt':
                sep = '\\'
            else :
                sep = '/'
            sftp = ssh_client.open_sftp()
            remotePath = sep.join([config["remote_path"], "CookieRepositories", config["repo_name"]])
            
            refs = getResource("refs")
            head = getResource("head")
            remoteRefs = getRemoteResource(sftp, remotePath, "refs", sep)
            if refs["B"][head["name"]] ==  remoteRefs["B"][head["name"]]:
                printColor("Local branch is on par with remote branch.", "green")
            else:
                printColor("Local branch is behind remote branch.", "red")
                printColor("Please use 'cookie pull' before comitting.", "green")
        except:
            printColor("Could not resolve remote, please check configuration.", "red")
            printColor("Unless this is before first push, in which case all is good!", "red")
        if head['hash']=='':
            printColor("    <> On branch '{}', no commits yet...".format(head["name"]), "white")
        else:
            printColor("    <> On branch '{}', commit '{}'.".format(head["name"], head["hash"]), "white")
        outputStaged=False
        outputStaged=printStaged()
        outputUnstaged=False
        outputUnstaged=printUnstaged()
        if not outputStaged and not outputUnstaged:
            printColor("Nothing new here! No changes found.", "blue")

def stageFiles(paths):
    staged=getResource("staged")
    unstaged=getResource("unstaged")
    index=getResource("index")
    if '.' in paths :
        targetPaths = []
        targetPaths.extend(unstaged['A'].keys())
        targetPaths.extend(unstaged['M'].keys())
        targetPaths.extend(unstaged['D'].keys())
        for path in paths:
            if path in targetPaths:
                targetPaths.remove(path)
    else:
        targetPaths = paths
    for pathname in targetPaths:
        pathname=os.path.relpath(pathname, "")
        if pathname in unstaged['A']:
            staged['A'][pathname]=statDictionary(os.lstat(pathname))
            cacheFile(pathname)
            resolveAddedStaging(pathname, staged, index)
            del unstaged['A'][pathname]
        elif pathname in unstaged['D']:
            if pathname in index:
                statDict=deepcopy(index[pathname])
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
    dumpResource("staged", staged)
    dumpResource("unstaged", unstaged)

def unstageFiles(paths):
    staged=getResource("staged")
    if '.' in paths :
        targetPaths = []
        targetPaths.extend(staged['A'].keys())
        targetPaths.extend(staged['M'].keys())
        targetPaths.extend(staged['D'].keys())
        targetPaths.extend(staged['C'].keys())
        targetPaths.extend(staged['R'].keys())
        targetPaths.extend(staged['T'].keys())
        targetPaths.extend(staged['X'].keys())
        for path in paths:
            if path in targetPaths:
                targetPaths.remove(path)
    else:
        targetPaths = paths
    for pathname in targetPaths:
        pathname=os.path.relpath(pathname, "")
        if pathname in staged['A']:
            del staged['A'][pathname]
        elif pathname in staged['D']:
            del staged['D'][pathname]
        elif pathname in staged['M']:
            del staged['M'][pathname]
        elif pathname in staged['C']:
            del staged['C'][pathname]
        elif pathname in staged['R']:
            del staged['R'][pathname]
        elif pathname in staged['T']:
            del staged['T'][pathname]
        elif pathname in staged['X']:
            del staged['X'][pathname]
        else:
            printColor("Cannot remove file '{}' from staging area".format(pathname), "red")
            printColor("Make sure the file is staged!", "red")

    dumpResource("staged", staged)

def getStagedFiles():
    staged=getResource("staged")
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
    staged=getResource("staged")
    deletedFiles=list(staged['D'].keys())
    for file in staged['R']:
        deletedFiles.append(staged['R'][file][0])
    return deletedFiles

def isThereStagedStuff():
    staged=getResource("staged")
    if staged['A']!={} or staged['D']!={} or staged['M']!={} or staged['C']!={} or staged['R']!={} or staged['T']!={} or staged['X']!={}:
        return True