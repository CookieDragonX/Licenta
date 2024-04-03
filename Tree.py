from Object import Object
from hashlib import sha1

# Tree --> map{string, Tree|Blob}
# T:path:hash:path:hash:path:hash...

class Tree(Object):
    def __init__(self, metaData) -> None:
        try:
            metaDataDecoded=metaData.decode(encoding='utf-8')
        except AttributeError:
            metaDataDecoded=metaData
        metaDataSplit=metaDataDecoded.split(':')[1:]
        self.map={}
        for path, hash in zip(*[iter(metaDataSplit)]*2):
            self.map[path]=hash
    def getMetaData(self):
        return ('T:{}'.format(':'.join(['{}:{}'.format(key,value) for key, value in self.map.items()]))).encode('utf-8')