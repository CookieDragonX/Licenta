import sys
from Blob import Blob
import os
from cookieLib import main
import json
from IndexManager import resetStagingArea
from cookieLib import *

if __name__=="__main__":
    dir="D:\stuffs\Licenta"
    print(getIndex(dir, {}, getTargetDirs(dir), False))
    sys.exit(0)      
