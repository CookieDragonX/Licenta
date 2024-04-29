import os
import json
import subprocess
import shutil
from libs.BasicUtils import getResource
###################################################################
#               Preconditions:
#
#   - there should be not directory named 'Test_Repo' as this test
#       will create it and apply basic commands on it
#   
##################################################################

cookiePath="D:\\stuffs\\Licenta"

def test_init():
    if os.path.exists("Test_Repo"):
        shutil.rmtree("Test_Repo")
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

def test_add2():
    os.makedirs(os.path.join("dir1", "dir2"))
    with open(os.path.join("dir1", "dir2", "nestedFile"), "w") as fp:
        fp.write("some stuff")
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "add", os.path.join("dir1", "dir2", "nestedFile")],
    )
    os.remove("file.txt")
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "add", os.path.join("file.txt")],
    )
    result = subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    assert os.path.join("dir1", "dir2", "nestedFile") in result.stdout
    assert "Files deleted" in result.stdout
    assert "file.txt" in result.stdout

def test_commit2():
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "commit", "-m", "Removed file.txt& added nested file"],
    )
    with open(os.path.join(".cookie", "index"), "r") as indexFile:
        index=json.load(indexFile)
    assert "file.txt" not in index
    assert os.path.join("dir1", "dir2", "nestedFile") in index

def test_modified():
    with open(os.path.join("blah.txt"), "w") as testFile:
        testFile.write("content")
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "add", os.path.join("blah.txt")],
    )
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "commit", "-m", "add blah.txt."],
    )
    with open(os.path.join("blah.txt"), "w") as testFile:
        testFile.write("should appear as modified.")
    result = subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    assert "-->Files modified:" in result.stdout

def test_renamed():
    with open(os.path.join("blah.txt"), "w") as testFile:
        testFile.write("content")
    os.rename('blah.txt', 'new.txt')
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "add", os.path.join("blah.txt")],
    )
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "add", os.path.join("new.txt")],
    )
    result = subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    assert "-->Files renamed:" in result.stdout
    assert "{} --> {}".format("blah.txt", "new.txt") in result.stdout
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "commit", "-m", "rename blah.txt to new.txt"],
    )
    index = getResource("index")
    assert "blah.txt" not in index
    assert "new.txt" in index

def test_copied():
    os.makedirs("somedir", exist_ok=True)
    with open(os.path.join("somedir", "new_copy.txt"), "w") as testFile:
        testFile.write("content")

    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "add", os.path.join("somedir", "new_copy.txt")],
    )
    result = subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    assert "-->Files copied:" in result.stdout
    assert "{} <-- {}".format(os.path.join("somedir", "new_copy.txt"), "new.txt") in result.stdout
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "commit", "-m", "copy new.txt to somedir"],
    )

def test_delete_and_cleanup():
    result = subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "delete"],
        capture_output = True,
        text = True 
    )
    assert "Cookie does not assume responsability!" in result.stdout
    os.chdir("..")
    #shutil.rmtree("Test_Repo")
