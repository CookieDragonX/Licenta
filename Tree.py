from Object import Object
from hashlib import sha1
# Tree --> map{string, Tree|Blob}

class Tree(Object):
    def __init__(self,metaData) -> None:
        self.metaData=metaData
        self.id=sha1(object.metaData)
        metaDataDecoded=metaData.decode(encoding='utf-8')
        metaDataDecoded.split(':')[1:]
        self.map={}
        for name, hash in zip(*[iter(metaDataDecoded.split(':')[1:])]*2):
            self.map[name]=hash