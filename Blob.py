from Object import Object
from hashlib import sha1
# Blob --> array of bytes

class Blob(Object):
    def __init__(self,metaData) -> None:
        super().__init__()
        #metaDataDecoded="B:{filename}:{text}".format(filename=filename, text=text)
        #self.metaData = bytearray(metaDataDecoded.encode('utf-8'))
        self.metaData=metaData
        self.id=sha1(object.metaData)
        metaDataDecoded=metaData.decode(encoding='utf-8')
        self.filename=metaDataDecoded.split(':')[1]
        self.content=metaDataDecoded.split(':')[2:].join(':')

