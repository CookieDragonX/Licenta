import sys
import os
from libs.objectLib.ObjectManager import store, load, getObjectType
from libs.objectLib.Commit import Commit
from libs.objectLib.Tree import Tree
from libs.objectLib.Blob import Blob
from libs.BranchingManager import getSnapshotFromCommit, updateHead, resetToSnapshot
from libs.BasicUtils import getResource, dumpResource
from utils.prettyPrintLib import printColor
from utils.stringMerge import merge
from time import time
from libs.LogsManager import logCommit

def mergeSourcesIntoTarget(target, sources):
    if target == None:
        target = getResource("HEAD")["name"]
    createMergeCommit(target, sources)

def mergeBlobs(target, source, base, objectsPath): #the args are hashes
    filename = None
    if target == None:
        targetBlob = Blob(None)
    else:
        targetBlob = load(target, objectsPath)
        if not filename:
            filename=targetBlob.filename
    if source == None:
        sourceBlob = Blob(None)
    else:
        sourceBlob = load(source, objectsPath)
        if not filename:
            filename=sourceBlob.filename
    if base != None:
        baseBlob = None
    else:
        baseBlob = load(base, objectsPath)
    
    metaData=["B"]
    metaData.append(filename)

    if baseBlob!=None:
        mergedContent=merge(sourceBlob.content, targetBlob.content, baseBlob.content)
    else:
        mergedContent=merge(sourceBlob.content, targetBlob.content, "")
    metaData.append(mergedContent)
    newBlob = Blob('?'.join(metaData))
    store(newBlob, objectsPath)
    return newBlob.getHash()

def mergeTrees(target, source, base, objectsPath): # the args are hashes
    if target == None:
        targetTree = Tree(None)
    else:
        targetTree=load(target, objectsPath)
    if source == None:
        sourceTree = Tree(None)
    else:
        sourceTree=load(source, objectsPath)
    if base == None:
        baseTree=Tree(None)
    else:
        baseTree=load(base, objectsPath)

    if targetTree.__class__.__name__!= "Tree" or sourceTree.__class__.__name__!= "Tree" or baseTree.__class__.__name__!= "Tree":
        printColor("[DEV ERROR][mergeTrees] Received a hash that is not a tree!", "red")
        sys.exit(1)
    for item in targetTree.map:
        objType = getObjectType(targetTree.map[item])
        targetArg=None
        sourceArg=None
        baseArg=None
        if item not in sourceTree.map:
            if item in baseTree.map:
                if targetTree.map[item]!= baseTree.map[item]:
                    # CONFLICT item modified in target & deleted in source
                    targetArg = targetTree.map[item]
                    baseArg = baseTree.map[item]
                else:
                    del targetTree.map[item] # ACTION item deleted in source ==> remove it from target
                    continue
            else:
                continue
                # OK item added since base in target but not in source, makes sense
        elif item in sourceTree.map:
            if targetTree.map[item] != sourceTree.map[item]:
                if item in baseTree.map:
                    # CONFLICT merge blobs or trees with base
                    targetArg = targetTree.map[item]
                    sourceArg = sourceTree.map[item]
                    baseArg = baseTree.map[item]
                else:
                    # CONFLICT merge blobs or trees with no base
                    targetArg = targetTree.map[item]
                    sourceArg = sourceTree.map[item]
            elif targetTree.map[item] == sourceTree.map[item]:
                continue
                # OK items are the same, alles gut
        else:
            printColor("[DEV ERROR][mergeTrees] what?", "red")
        if objType == 'T':
            targetTree.map[item]= mergeTrees(targetArg, sourceArg, baseArg, objectsPath)
        elif objType == 'B':
            targetTree.map[item] = mergeBlobs(targetArg, sourceArg, baseArg, objectsPath)
        else: 
            printColor("[DEV ERROR][mergeTrees] Found commit object in tree merging", "red")
            sys.exit(1)

    for item in sourceTree.map:
        # only for items in source that are not in target
        if item in targetTree.map:
            # case SHOULD have already been handled above
            continue
        else:
            if item in baseTree.map[item]:
                # CONFLICT item was deleted in target yet it still exists in source
                objType = getObjectType(sourceTree.map[item], objectsPath)
                targetArg = None
                sourceArg = sourceTree.map[item]
                baseArg = baseTree.map[item]
            else:
                # OK item was added in source and is to be added in target
                targetTree.map[item] = sourceTree.map[item]
                continue
        if objType == 'T':
            targetTree.map[item]= mergeTrees(targetArg, sourceArg, baseArg, objectsPath)
        elif objType == 'B':
            targetTree.map[item] = mergeBlobs(targetArg, sourceArg, baseArg, objectsPath)
        else: 
            printColor("[DEV ERROR][mergeTrees] Found commit object in tree merging", "red")
            sys.exit(1)
    
    store(targetTree, objectsPath)
    return targetTree.getHash()

def createMergeCommit(target, sources):
    objectsPath = os.path.join(".cookie", "objects")
    #generateStatus(None,quiet=True)
    metaData=['C']
    refs=getResource("refs")
    head=getResource("HEAD")
    targetIsHead=False
    targetIsBranchName=False
    if target in refs["B"]:
        targetSha = refs["B"][target]
        targetIsBranchName=True
        if target == head["name"]:
            targetIsHead=True
    else:
        targetSha=target
        if target == head["hash"]:
            targetIsHead = True
    targetTreeSha=getSnapshotFromCommit(targetSha, objectsPath)

    if getObjectType(targetSha, objectsPath) != 'C':
        printColor("Cannot merge into {} -- not a branch name or commit.".format(target), "red")
    metaData.append(targetSha)
    for source in sources:
        if source in refs["B"]:
            sourceSha=refs["B"][source]
        else:
            sourceSha=source
        sourceTreeSha=getSnapshotFromCommit(refs["B"][source], objectsPath)
        if getObjectType(sourceSha, objectsPath) != 'C':
            printColor("Cannot merge from {} -- not a commit or a branch name".format(target), "red")
        metaData.append(sourceSha)
        baseTreeSha = getSnapshotFromCommit(getMergeBase(targetSha, sourceSha), objectsPath)
        targetTreeSha = mergeTrees(targetTreeSha, sourceTreeSha, baseTreeSha, objectsPath)
        
    metaData.append('A')
    userdata=getResource("userdata")    
    if userdata['user'] == "":
        printColor("Please login with a valid e-mail first!",'red')
        printColor("Use 'cookie login'",'white')
        sys.exit(0)
    else:
        metaData.append(userdata['user'])
        
    metaData.append("Merge into {} from {}".format(target, "; ".join(sources)))
    metaData.append(str(time()))
    metaData.append(targetTreeSha)
    newCommit = Commit('?'.join(metaData))
    store(newCommit, objectsPath)
    logCommit(newCommit)
    if targetIsBranchName:
        refs[target] = newCommit.getHash()
        if targetIsHead:
            updateHead(target, currentRef=False, ref=newCommit.getHash())
            resetToSnapshot(newCommit.snapshot)
    dumpResource("refs", refs)


def getMergeBase(target, source):
    logs = getResource("logs")
    return findLCA([target],[source], logs)

def findLCA(a, b, graph):
    while a[-1] != b[-1]:
        if graph['nodes'][a[-1]] >= graph['nodes'][b[-1]]:
            if len(graph['adj'][a[-1]])==1:
                a.append(graph['edges'][str(graph['adj'][a[-1]][0])]['to'])
            else:
                a.append(findLCA(graph['edges'][str(graph['adj'][a[-1]][0])]['to'], graph['edges'][str(graph['adj'][a[-1]][1])]['to']))
        else:
            if len(graph['adj'][b[-1]])==1:
                b.append(graph['edges'][str(graph['adj'][b[-1]][0])]['to'])
            else:
                b.append(findLCA(graph['edges'][str(graph['adj'][b[-1]][0])]['to'], graph['edges'][str(graph['adj'][b[-1]][1])]['to']))
    return a[-1]