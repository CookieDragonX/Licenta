import sys
from Blob import Blob
import os
from IndexManager import compareToIndex
from IndexManager import saveIndex


if __name__=="__main__":
    os.environ["PROJECT_DIR"]="/home/cookie/Cookie_Repo/.cookie"
    os.environ["OBJECTS_PATH"]=os.path.join(os.environ["PROJECT_DIR"],"objects")

    #saveIndex('/home/cookie/TPAC-Project','/home/cookie/TPAC-Project/.cookie/index')
    compareToIndex('/home/cookie/TPAC-Project')
    sys.exit(0)      
