import sys
from Blob import Blob
import os
from cookieLib import main
import json
from IndexManager import resetStagingArea
from cookieLib import *
from cookieLib import cookieCertified

@cookieCertified
def nothing(x):
    print(x)
    print(os.getcwd())

if __name__=="__main__":
    nothing(123)
    sys.exit(0)      
