from libs.objectLib.Object import Object
import os

# Blob --> array of bytes
# B:filename:text

class Blob(Object):
    def __init__(self,metaData) -> None:
        if metaData != None:
            try:
                metaDataDecoded=metaData.decode(encoding='utf-8')
            except AttributeError:
                metaDataDecoded=metaData
            metaDataSplit=metaDataDecoded.split('?')
            self.filenameAbsPath=metaDataSplit[1]
            self.filename = os.sep.join(self.filenameAbsPath.split(os.sep))
            self.content='?'.join(metaDataSplit[2:])
        else :
            self.filenameAbsPath = ""
            self.filename = ""
            self.content = ""
    def getMetaData(self):
        return ('B?{}?{}'.format(self.filenameAbsPath,self.content)).encode('utf-8')

