from errors import NoSuchObjectException
import os
from hashlib import sha1 
from libs.objectLib.Blob import Blob
from libs.objectLib.Tree import Tree
from libs.objectLib.Commit import Commit

def load(hash, objectsPath):
    if not os.path.isfile(os.path.join(objectsPath, hash[:2], hash[2:])):
        raise NoSuchObjectException
    else:
        with open(os.path.join(objectsPath, hash[:2], hash[2:]), 'rb') as object:
            metaData=object.read()
        metaData=metaData.decode(encoding='utf-8')
        objectType=metaData.split('?')[0]
        if objectType=='B':
            return Blob(metaData)
        elif objectType=='C':
            return Commit(metaData)
        elif objectType=='T':
            return Tree(metaData)
    return None

def store(object, objectsPath):
    id=object.getHash()
    if not os.path.isdir(os.path.join(objectsPath, id[:2])):
        os.mkdir(os.path.join(objectsPath, id[:2]))
    with open(os.path.join(objectsPath, id[:2], id[2:]),'wb') as fp:
        fp.write(object.getMetaData())

def getHash(path): #only Blob but not really an useful method
    with open(path, 'r') as fp:
        fileContent=fp.read()
    blobContent='?'.join(['B', path, fileContent])
    return sha1(blobContent.encode(encoding='utf-8'))

def createBlob(path):
    with open(path, 'r') as fp:
        fileContent=fp.read()
    metaData='?'.join(['B', path, fileContent])
    return Blob(metaData)

def getObjectType(hash, objectsPath):
    if not os.path.isfile(os.path.join(objectsPath, hash[:2], hash[2:])):
        raise NoSuchObjectException
    with open(os.path.join(objectsPath, hash[:2], hash[2:]), 'rb') as object:
        metaData=object.read()
    metaData=metaData.decode(encoding='utf-8')
    return metaData.split('?')[0]

def getMetaData(hash,objectsPath):
    with open(os.path.join(objectsPath, hash[:2], hash[2:]), 'r') as object:
        return object.read().decode(encoding='utf-8')
    
def hashTree(dir, objectsPath):
    metaData=['T']
    for pathname in os.listdir(dir):
        if os.path.isdir(pathname):
            treeHash=hashTree(dir)
            metaData.extend([pathname, treeHash])
        elif os.path.isfile(pathname):
            metaData.extend([pathname, getHash(pathname)])
    tree=Tree('?'.join(metaData))
    store(tree, objectsPath)
    return tree.getHash()

def mergeBlobs(target, source, objectsPath): #the args are hashes
    newBlobData=["B"]
    # this is way easier, difflib the 2 contents, parse result create new blob, ask to solve conflict if there is conflict
    # if that sounds good at that point too, here's sample, ly
            # import difflib

            # with open('file1.txt','r') as f1, open('file2.txt','r') as f2:
            #     for line in difflib.unified_diff(f1.read(), f2.read(), fromfile='file1', tofile='file2', lineterm=''):
            #         print(line)
    store(Blob('?'.join(newBlobData)), objectsPath)
    pass

def mergeTrees(target, source, objectsPath): # the args are hashes
    targetTree=load(target)
    sourceTree=load(source)
    newTree=load(target)
    for item in targetTree.map:
        try:
            if targetTree.map[item] != sourceTree.map[item]:
                if (getObjectType(targetTree.map[item])=='B'): #conflict case
                    newTree.map[item]=mergeBlobs(targetTree.map[item], sourceTree.map[item])
                else:
                    newTree.map[item]=mergeTrees(targetTree.map[item], sourceTree.map[item])
        except KeyError:
            # targetTree has file that source tree doesn't, thus sourceTree.map[item] cannot be accessed, continuing...
            continue
    store(newTree, objectsPath)
    return newTree.computeHash()

def mergeCommits(target, source, objectsPath):
    mergeCommitData=['C']
    mergeCommitData.append('whatever matters in commit idk')
    #new commit has snapshot mergeTrees(target.getSnapshot(), source.getSnapshot())
    store(Commit('?'.join(mergeCommitData)), objectsPath)

def getSnapshotFromCommit(hash):
    commit=load(hash, os.path.join('.cookie', 'objects'))
    return commit.snapshot
