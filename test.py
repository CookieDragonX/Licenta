import sys
from Blob import Blob
import os
from cookieLib import main
import json
from IndexManager import *
from cookieLib import *
from cookieLib import cookieCertified

@cookieCertified
def nothing(x):
    print(x)
    print(os.getcwd())

if __name__=="__main__":
    print(getTargetDirs())
    sys.exit(0)      
