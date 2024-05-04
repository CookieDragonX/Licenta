from libs.objectLib.Object import Object
import os

# Blob --> array of bytes
# B:filename:text

class Blob(Object):
    def __init__(self,metaData) -> None:
        if metaData != None:
            metaDataSplit=metaData.split(b'?')
            filenameAbsPath=metaDataSplit[1]           # split with '/'
            self.filename = os.sep.join(filenameAbsPath.decode('utf-8').split("/"))
            self.content=b'?'.join(metaDataSplit[2:])
        else :
            self.filename = ""
            self.content = bytearray()
    def getMetaData(self):
        bytes = bytearray()
        bytes.extend(b'B?')
        bytes.extend(("/".join(self.filename.split(os.sep))).encode('utf-8'))
        bytes.extend(b'?')
        bytes.extend(self.content)
        return bytes

