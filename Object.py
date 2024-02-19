from hashlib import sha1
import os
from errors import NoSuchObjectException
from Blob import loadBlob
from Tree import loadTree
from Commit import loadCommit

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
            return loadBlob(metaData)
        elif objectType=='C':
            return loadCommit(metaData)
        elif objectType=='T':
            return loadTree(metaData)
    return None
        

class Object:
    def __init__(self) -> None:
        pass
    def store(self):
        self.id=sha1(self.metaData)
        if not os.path.isdir(os.path.join(os.environ['OBJECTS_PATH'],self.id.hexdigest()[:2])):
            os.mkdir(os.path.join(os.environ['OBJECTS_PATH'],self.id.hexdigest()[:2]))
        with open(os.path.join(os.environ['OBJECTS_PATH'], self.id.hexdigest()[:2], self.id.hexdigest()[2:]),'wb') as object:
            object.write(self.metaData)
        #print(self.id.hexdigest())
    
        