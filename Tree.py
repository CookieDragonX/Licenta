from Object import Object
from hashlib import sha1

# Tree --> map{string, Tree|Blob}
# T:str:obj:str:obj:str:obj...

class Tree(Object):
    def __init__(self,metaData) -> None:
        super().__init__(metaData)
        metaDataDecoded=metaData.decode(encoding='utf-8')
        metaDataSplit=metaDataDecoded.split(':')[1:]
        self.map={}
        for name, hash in zip(*[iter(metaDataSplit)]*2):
            self.map[name]=hash