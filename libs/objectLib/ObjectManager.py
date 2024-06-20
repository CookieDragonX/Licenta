from errors.NoSuchObjectException import NoSuchObjectException
import os
from hashlib import sha1 
from libs.objectLib.Blob import Blob
from libs.objectLib.Tree import Tree
from libs.objectLib.Commit import Commit
from libs.BasicUtils import safeWrite

def load(hash, objectsPath):
    if not os.path.isfile(os.path.join(objectsPath, hash[:2], hash[2:])):
        raise NoSuchObjectException("No such object!")
    else:
        with open(os.path.join(objectsPath, hash[:2], hash[2:]), 'rb') as object:
            objectType=object.read(1).decode()
            object.seek(0)
            metaData=object.read()
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
    safeWrite(os.path.join(objectsPath, id[:2], id[2:]), object.getMetaData(), binary=True)

def createBlob(path, forceContent):
    if forceContent:
        with open(forceContent, 'r+b') as fp:
            fileContent=fp.read()
    else:
        with open(path, 'r+b') as fp:
            fileContent=fp.read()
    metaData=b'?'.join([b'B', bytes(path, "utf-8"), fileContent])
    return Blob(metaData)

def getObjectType(hash, objectsPath = os.path.join(".cookie", "objects")):
    if not os.path.isfile(os.path.join(objectsPath, hash[:2], hash[2:])):
        raise NoSuchObjectException("No such object!")
    with open(os.path.join(objectsPath, hash[:2], hash[2:]), 'r') as object:
        objType=object.read(1)
    return objType


def getSnapshotFromCommit(hash, objectsPath):
    commit=load(hash, objectsPath)
    return commit.snapshot
