from libs.objectLib.Object import Object

# Commit --> struct{
#     parents : array{Commit}
#     author : str
#     message : str
#     timestamp : int
#     snapshot : Tree
# }
# C:hash:hash:hash:A:author:msg:time:snapHash


class Commit(Object):
    def __init__(self, metaData) -> None:
        try:
            metaDataDecoded=metaData.decode(encoding='utf-8')
        except AttributeError:
            metaDataDecoded=metaData
        try:
            metaDataSplit=metaDataDecoded.split('?')[1:]
            self.parents=[]
            iter=0
            for parent in metaDataSplit:
                if parent=='A':
                    iter+=1
                    break
                self.parents.append(parent)
                iter+=1
            self.author=metaDataSplit[iter]
            self.message=metaDataSplit[iter+1]
            self.time=metaDataSplit[iter+2]
            self.snapshot=metaDataSplit[iter+3]
        except IndexError:
            print("[DEV ERROR][Commit constructor]")
            print(metaData)

    def getMetaData(self):
        return ('C?{}?A?{}?{}?{}?{}'.format('?'.join(self.parents),self.author, self.message, self.time, self.snapshot)).encode('utf-8')
    