from Object import Object
import os 

# Commit --> struct{
#     parents : array{Commit}
#     author : str
#     message : str
#     timestamp : int
#     snapshot : Tree
# }

class Commit(Object):
    def __init__(self,metaData) -> None:
        super().__init__()
        pass