import sys
from Blob import Blob

if __name__=="__main":
    x=Blob("fun text","smth else")
    print(x.bytes[0])
    sys.exit(0)