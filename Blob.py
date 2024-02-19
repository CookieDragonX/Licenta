from Object import Object
from hashlib import sha1
# Blob --> array of bytes

def loadBlob(metaData):
    splitBlobData=metaData.split(':')
    return Blob(splitBlobData[1],splitBlobData[1:].join(':'))

class Blob(Object):
    def __init__(self,filename,text) -> None:
        super().__init__()
        metaDataDecoded="B:{filename}:{text}".format(filename=filename, text=text)
        self.metaData = bytearray(metaDataDecoded.encode('utf-8'))
    
