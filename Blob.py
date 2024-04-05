from Object import Object
from hashlib import sha1

# Blob --> array of bytes
# B:filename:text

class Blob(Object):
    def __init__(self,metaData) -> None:
        try:
            metaDataDecoded=metaData.decode(encoding='utf-8')
        except AttributeError:
            metaDataDecoded=metaData
        metaDataSplit=metaDataDecoded.split(':')
        self.filename=metaDataSplit[1]
        self.content=':'.join(metaDataSplit[2:])
    def getMetaData(self):
        return ('B:{}:{}'.format(self.filename,self.content)).encode('utf-8')

