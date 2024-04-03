import sys
from Blob import Blob
import os
from cookieLib import main
import json
from IndexManager import *
from cookieLib import *
from ObjectManager import *
import subprocess
import shutil
cookiePath="D:\\stuffs\\Licenta"

def test_init():
    subprocess.run(["py", "-3", os.path.join(cookiePath, 'cookie'), "init", "Test_Repo"])
    assert os.path.isdir(os.path.join('Test_Repo', '.cookie', 'objects')) 
    
def test_status():
    os.chdir("Test_Repo")
    result = subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    assert result.stdout==''
    with open("file.txt", 'w') as file:
        file.write("dummy content")
    result = subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    assert "file.txt" in result.stdout


def test_add():
    pass

def test_delete():
    subprocess.run(["py", "-3", os.path.join(cookiePath, 'cookie'), "delete"])
    assert not os.path.isdir('.cookie') 
    os.chdir("..")
    shutil.rmtree("Test_Repo")
    pass