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
#   
##################################################################

cookiePath="D:\\stuffs\\Licenta"

def test_init():
    subprocess.run(["py", "-3", os.path.join(cookiePath, 'cookie'), "init", "Test_Repo"])
    assert os.path.isdir(os.path.join('Test_Repo', '.cookie', 'objects')) 
    assert os.path.isfile(os.path.join('Test_Repo', '.cookie', 'HEAD')) 
    assert os.path.isfile(os.path.join('Test_Repo', '.cookie', 'index'))
    assert os.path.isfile(os.path.join('Test_Repo', '.cookie', 'refs'))
    assert os.path.isfile(os.path.join('Test_Repo', '.cookie', 'staged'))
    assert os.path.isfile(os.path.join('Test_Repo', '.cookie', 'unstaged'))
    assert os.path.isfile(os.path.join('Test_Repo', '.cookie', 'userdata'))


def test_status():
    os.chdir("Test_Repo")
    result = subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    assert "Nothing new here! No changes found." in result.stdout
    with open("file.txt", 'w') as file:
        file.write("dummy content")
    result = subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    assert "file.txt" in result.stdout
    assert "Files untracked" in result.stdout
    assert "Unstaged changes:" in result.stdout

def test_add():
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "add", "file.txt"],
        capture_output = True,
        text = True 
    )
    result = subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    assert "Changes to be committed:" in result.stdout
    assert "Files added" in result.stdout
    assert "Unstaged changes:" not in result.stdout

def test_login():
    test_user="Awesome_User"
    test_email="totally_valid_address@gmail.com"
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "login", "-u", test_user, "-e", test_email],
        capture_output = True,
        text = True 
    )
    with open(os.path.join(".cookie", "userdata"), "r") as file:
        userdata=json.load(file)
    assert userdata["user"]==test_user
    assert userdata["email"]==test_email


def test_commit():
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "commit", "-m", "Added file.txt"],
        capture_output = True,
        text = True 
    )
    with open(os.path.join(".cookie", "HEAD"), "r") as file:
        HEAD=json.load(file)
    assert HEAD["name"]=="master"
    assert HEAD["hash"]!=""
    
def test_delete_and_cleanup():
    subprocess.run(["py", "-3", os.path.join(cookiePath, 'cookie'), "delete"])
    assert not os.path.isdir('.cookie') 
    os.chdir("..")
    shutil.rmtree("Test_Repo")
