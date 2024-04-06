import os
import json
from IndexManager import *
from cookieLib import *
from ObjectManager import *
import subprocess
import shutil

###################################################################
#               Preconditions:
#
#   - there should be not directory named 'Test_Repo' as this test
#       will create it and apply basic commands on it
#   - DEBUG should be true in order for login to not matter
#
##################################################################

cookiePath="D:\\stuffs\\Licenta"

def test_branching1():
    #initialize
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "init", "Test_Repo"]
    )
    os.chdir("Test_Repo")
    #add a file
    with open("file.txt", 'w') as file:
        file.write("dummy content")
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "add", "file.txt"]
    )
    #create commit
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "commit", "-m", "Added file.txt"]
    )
    #create new branch and switch to it
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "create_branch", "-b", "secondary_branch"]
    )
    with open(os.path.join('.cookie', 'HEAD')) as headFile:
        head=json.load(headFile)
    assert head["name"]=='secondary_branch'
    
    #change file content
    with open("file.txt", 'w') as file:
        file.seek(0)
        file.write("something new")
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "add", "file.txt"]
    )
    #commit on secondary branch
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "commit", "-m", "Changed file.txt on secondary branch"]
    )
    #switch back to master
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "checkout", "master"]
    )
    with open(os.path.join('.cookie', 'HEAD'), 'r') as headFile:
        head=json.load(headFile)
    assert head["name"]=='master'
    with open("file.txt", 'r') as file:
        content=file.read()
    assert "dummy content" in content

def test_cleanup():
    os.chdir(cookiePath)
    shutil.rmtree("Test_Repo")
    assert not os.path.exists("Test_Repo")