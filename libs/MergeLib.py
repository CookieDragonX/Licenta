import sys
import os
from libs.objectLib.ObjectManager import store, load, getObjectType
from libs.objectLib.Commit import Commit
from libs.objectLib.Tree import Tree
from libs.objectLib.Blob import Blob
from libs.BranchingManager import getSnapshotFromCommit
from libs.BasicUtils import getResource
from utils.prettyPrintLib import printColor
from utils.stringMerge import merge
from time import time
from three_merge import merge 


def mergeBlobs(target, source, base, objectsPath): #the args are hashes
    if base != None:
        baseBlob = load(base, objectsPath)
    else:
        baseBlob = None
    targetBlob=load(target, objectsPath)
    sourceBlob=load(source, objectsPath)
    metaData=["B"]
    if targetBlob.filename != sourceBlob.filename:
        printColor("[DEV ERROR][mergeBlobs] target and source filenames are different?", "red")
    else:
        filename=targetBlob.filename
    metaData.append(filename)
    if baseBlob!=None:
        mergedContent=merge(sourceBlob.content, targetBlob.content, baseBlob.content)
    else:
        mergedContent=merge(sourceBlob.content, targetBlob.content, "")
    metaData.append(mergedContent)
    store(Blob('?'.join(metaData)), objectsPath)

def mergeTrees(target, source, base, objectsPath): # the args are hashes
    targetTree=load(target, objectsPath)
    sourceTree=load(source, objectsPath)
    if base != None:
        baseTree=load(base, objectsPath)
    else:
        baseTree=Tree(None)
    if targetTree.__class__!= "Tree" or sourceTree.__class__!= "Tree" or baseTree.__class__!= "Tree":
        printColor("[DEV ERROR][mergeTrees] Received a hash that is not a tree!", "red")
    
    for item in targetTree.map:
        try:
            if targetTree.map[item] != sourceTree.map[item]:
                if (getObjectType(targetTree.map[item])=='B'): #conflict case
                    if item in baseTree.map:
                        baseTree.map[item]=mergeBlobs(targetTree.map[item], sourceTree.map[item], baseTree.map[item], objectsPath)
                    else:
                        baseTree.map[item]=mergeBlobs(targetTree.map[item], sourceTree.map[item], None, objectsPath)
                else:
                    if item in baseTree.map:
                        baseTree.map[item]=mergeTrees(targetTree.map[item], sourceTree.map[item], baseTree.map[item],  objectsPath)
                    else:
                        baseTree.map[item]=mergeTrees(targetTree.map[item], sourceTree.map[item], None,  objectsPath)

            else:
                baseTree.map[item]=targetTree.map[item]
        except KeyError:
            # targetTree has file that source tree doesn't, thus sourceTree.map[item] cannot be accessed, continuing...
            # we wish for newTree to not contain this item since it was deleted in sourceTree so we pop it!
            # would make sense i think
            # think about this 16.4
            del baseTree.map[item]
            continue
    store(baseTree, objectsPath)
    return baseTree.getHash()

def createMergeCommit(target, source, DEBUG=False):
    objectsPath = os.path.join(".cookie", "objects")
    #generateStatus(None,quiet=True)
    metaData=['C']
    refs=getResource("refs")
    if target in refs["B"]:
        targetSha=getSnapshotFromCommit(refs["B"][target], objectsPath)
    if getObjectType(targetSha) != 'C':
        printColor("Cannot merge into {} -- not a branch name".format(target), "red")
    metaData.append(targetSha)

    if source in refs["B"]:
        sourceSha=getSnapshotFromCommit(refs["B"][source], objectsPath)
    else:
        sourceSha=source
    if getObjectType(sourceSha) != 'C':
        printColor("Cannot merge from {} -- not a commit or a branch name".format(target), "red")
    metaData.append(sourceSha)
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
    metaData.append("Merge into {} from {}".format(target, source))
    metaData.append(str(time()))
    baseSha = getSnapshotFromCommit(getMergeBase(targetSha, sourceSha))
    metaData.append(mergeTrees(targetSha, sourceSha, baseSha, objectsPath))
    store(Commit('?'.join(metaData)), objectsPath)


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