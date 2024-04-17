import sys
import os
from libs.objectLib.ObjectManager import store, load, getObjectType
from libs.objectLib.Commit import Commit
from libs.objectLib.Blob import Blob
from libs.IndexManager import generateStatus
from libs.BranchingManager import getSnapshotFromCommit
from libs.BasicUtils import getResource
from utils.prettyPrintLib import printColor
from time import time

def mergeBlobs(common, target, source, objectsPath): #the args are hashes
    commonBlob=load(target, objectsPath)
    targetBlob=load(target, objectsPath)
    sourceBlob=load(source, objectsPath)
    metaData=["B"]
    #get diffs common-target and source-target
    # perform 3 way merge soOmehow https://www.geeksforgeeks.org/3-way-merge-sort/
    # this is way easier, difflib the 2 contents, parse result create new blob, ask to solve conflict if there is conflict
    # if that sounds good at that point too, here's sample, ly
            # import difflib

            # with open('file1.txt','r') as f1, open('file2.txt','r') as f2:
            #     for line in difflib.unified_diff(f1.read(), f2.read(), fromfile='file1', tofile='file2', lineterm=''):
            #         print(line)
    store(Blob('?'.join(metaData)), objectsPath)
    pass

def findCommonAncestor(sha1, sha2, objectsPath):
    sha1Tree=load(sha1, objectsPath)
    sha2Tree=load(sha2, objectsPath)
    if sha1Tree.__class__!= "Tree" or sha2Tree.__class__!= "Tree":
        printColor("[DEV ERROR][findCommonAncestor] Received a hash that is not a tree!", "red")
    commonAncestorNotFound=True
    
    #get data from log YOYOOYOY FOR BOTH LISTS AT ONCE, MEMBER ANCESTORS AND CHECK ONLY NEW STUFF!!!!

def mergeTrees(target, source, objectsPath): # the args are hashes
    targetTree=load(target, objectsPath)
    sourceTree=load(source, objectsPath)
    if targetTree.__class__!= "Tree" or sourceTree.__class__!= "Tree":
        printColor("[DEV ERROR][mergeTrees] Received a hash that is not a tree!", "red")
    newTree=load(target, objectsPath)
    for item in targetTree.map:
        try:
            if targetTree.map[item] != sourceTree.map[item]:
                if (getObjectType(targetTree.map[item])=='B'): #conflict case
                    newTree.map[item]=mergeBlobs(targetTree.map[item], sourceTree.map[item])
                else:
                    newTree.map[item]=mergeTrees(targetTree.map[item], sourceTree.map[item], objectsPath)
            else:
                newTree.map[item]=targetTree.map[item]
        except KeyError:
            # targetTree has file that source tree doesn't, thus sourceTree.map[item] cannot be accessed, continuing...
            # we wish for newTree to not contain this item since it was deleted in sourceTree so we pop it!
            # would make sense i think
            # think about this 16.4
            del newTree.map[item]
            continue
    store(newTree, objectsPath)
    return newTree.getHash()

def createMergeCommit(target, source, objectsPath, DEBUG=False):
    generateStatus(None,quiet=True)
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
    metaData.append(mergeTrees(targetSha, sourceSha))
    store(Commit('?'.join(metaData)), objectsPath)
