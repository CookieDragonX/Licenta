from libs.objectLib.Object import Object
import os

# Tree --> map{string, Tree|Blob}
# T:path:hash:path:hash:path:hash...

class Tree(Object):
    def __init__(self, metaData) -> None:
        if metaData!=None:
            try:
                metaDataDecoded = metaData.decode(encoding='utf-8')
            except AttributeError:
                metaDataDecoded = metaData
            metaDataSplit = metaDataDecoded.split('?')[1:]
            self.map = {}
            for path, hash in zip(*[iter(metaDataSplit)]*2):
                self.map[os.sep.join(path.split('/'))] = hash
        else:
            self.map = {}
    def getMetaData(self):
        return ('T?{}'.format('?'.join(['{}?{}'.format("/".join(key.split(os.sep)),value) for key, value in self.map.items()]))).encode('utf-8')