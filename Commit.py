from Object import Object
import os 
from errors import NoSuchObjectException

# Commit --> struct{
#     parents : array{Commit}
#     author : str
#     message : str
#     timestamp : int
#     snapshot : Tree
# }

class Commit(Object):
    def __init__(self) -> None:
        super().__init__()
    