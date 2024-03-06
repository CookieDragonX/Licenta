from Object import Object
from errors import NoSuchObjectException
import os
from hashlib import sha1 
from Blob import Blob
from Tree import Tree
from Commit import Commit


class ObjectHandler():
    def __init__(self) -> None:
        pass
    def load(hash):
        if not os.path.isdir(os.path.join(os.environ['OBJECTS_PATH'],hash[:2])):
            raise NoSuchObjectException
        elif not os.path.isfile(os.path.join(os.environ['OBJECTS_PATH'],hash[2:])):
            raise NoSuchObjectException
        else:
            with open(os.path.join(os.environ['OBJECTS_PATH'], hash[:2], hash[2:]),'rb') as object:
                metaData=object.read()
            metaData=metaData.decode(encoding='utf-8')
            objectType=metaData.split(':')[0]
            if objectType=='B':
                return Blob(metaData)
            elif objectType=='C':
                return Commit(metaData)
            elif objectType=='T':
                return Tree(metaData)
        return None
    
    def store(object):
        if not os.path.isdir(os.path.join(os.environ['OBJECTS_PATH'],object.id.hexdigest()[:2])):
            os.mkdir(os.path.join(os.environ['OBJECTS_PATH'],object.id.hexdigest()[:2]))
        with open(os.path.join(os.environ['OBJECTS_PATH'], object.id.hexdigest()[:2], object.id.hexdigest()[2:]),'wb') as object:
            object.write(object.metaData)
    