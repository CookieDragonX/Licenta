import sys
from Blob import Blob
import os
from IndexManager import getIndex
from IndexManager import saveIndex


if __name__=="__main__":
    os.environ["PROJECT_DIR"]="/home/cookie/Cookie_Repo/.cookie"
    os.environ["OBJECTS_PATH"]=os.path.join(os.environ["PROJECT_DIR"],"objects")
    # x=Blob("file.txt","fun text")
    # x.store()
    # x=load(x.id)
    # print(x.text)
    saveIndex('/home/cookie/TPAC-Project')
    
    sys.exit(0)      
