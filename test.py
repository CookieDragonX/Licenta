import sys
from Blob import Blob
import os
from cookieLib import main
import json
from cookieLib import *
if __name__=="__main__":
    os.environ["PROJECT_DIR"]="/home/cookie/Cookie_Repo/.cookie"
    os.environ["OBJECTS_PATH"]=os.path.join(os.environ["PROJECT_DIR"],"objects")

    #saveIndex('/home/cookie/TPAC-Project','/home/cookie/TPAC-Project/.cookie/index')
    # stagedPath=os.path.join('.cookie', 'unstaged')
    # with open(stagedPath, 'r') as stagingFile:
    #     staged=json.load(stagingFile)
    # del staged['A']["D:\stuffs\Licenta\Blob.py"]
    # print(staged)
    # with open(stagedPath, "w") as outfile:
    #     outfile.write(json.dumps(staged, indent=4))
    print(resolveCookieRepository())
    
    sys.exit(0)      
