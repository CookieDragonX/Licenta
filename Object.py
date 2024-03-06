from hashlib import sha1
import os
from errors import NoSuchObjectException

class Object:
    def __init__(self,metaData) -> None:
        self.metaData=metaData
        self.id=sha1(metaData)
    
        