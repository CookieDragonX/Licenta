from Object import Object
from hashlib import sha1

# Commit --> struct{
#     parents : array{Commit}
#     author : str
#     message : str
#     timestamp : int
#     snapshot : Tree
# }
# C:hash:hash:hash:A:author:msg:time:snapHash


class Commit(Object):
    def __init__(self,metaData) -> None:
        super().__init__(metaData)
        metaDataDecoded=metaData.decode(encoding='utf-8')
        metaDataSplit=metaDataDecoded.split(':')[1:]
        self.parents=[]
        iterator=1
        for parent in metaDataSplit:
            if parent=='A':
                iter+=1
                break
            self.parents.append(parent)
            iter+=1
        self.author=metaDataSplit[iter]
        self.message=metaDataSplit[iter+1]
        self.time=metaDataSplit[iter+2]
        self.snapshow=metaDataSplit[iter+3]