import sys
from Blob import Blob
import os

if __name__=="__main__":
    os.environ["PROJECT_DIR"]="/home/cookie/Cookie_Repo/.cookie"
    os.environ["OBJECTS_PATH"]=os.path.join(os.environ["PROJECT_DIR"],"objects")
    x=Blob("file.txt","fun text")
    x.store()
    sys.exit(0)