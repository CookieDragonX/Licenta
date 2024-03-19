from abc import abstractmethod
from hashlib import sha1
import os
from errors import NoSuchObjectException

class Object:
    def __init__(self) -> None:
        #self.metaData=metaData
        #self.id=sha1(metaData)
        pass

    @abstractmethod
    def getMetaData(self):
        pass

    def getHash(self):
        return sha1(self.getMetaData()).hexdigest()
        