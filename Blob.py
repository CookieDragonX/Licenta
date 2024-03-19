from Object import Object
from hashlib import sha1

# Blob --> array of bytes
# B:filename:text

class Blob(Object):
    def __init__(self,metaData) -> None:
        super().__init__(metaData)
        metaDataDecoded=metaData.decode(encoding='utf-8')
        metaDataSplit=metaDataDecoded.split(':')[1:]
        filename=metaDataSplit[1]
        self.content=metaDataSplit[2:].join(':')
    def getMetaData(self):
        return 'B:{}:{}'.format(self.filename,self.content)

