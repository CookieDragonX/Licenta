import os
import json
import subprocess
import shutil
from libs.BasicUtils import getResource
import pytest

if os.name == 'nt':
    interpreter = ["py", "-3"]
else:
    interpreter = ["python3"]

IGNORE_BASIC_TESTS=False

cookiePath=os.getcwd()

@pytest.mark.skipif(IGNORE_BASIC_TESTS,
                    reason="IGNORE_BASIC_TESTS is True")
def test_init():
    if os.path.exists("Test_Repo"):
        shutil.rmtree("Test_Repo")
    subprocess.run(interpreter + [os.path.join(cookiePath, 'cookie'), "init", "Test_Repo"])
    assert os.path.isdir(os.path.join('Test_Repo', '.cookie', 'objects')) 
    assert os.path.isfile(os.path.join('Test_Repo', '.cookie', 'head')) 
    assert os.path.isfile(os.path.join('Test_Repo', '.cookie', 'index'))
    assert os.path.isfile(os.path.join('Test_Repo', '.cookie', 'refs'))
    assert os.path.isfile(os.path.join('Test_Repo', '.cookie', 'staged'))
    assert os.path.isfile(os.path.join('Test_Repo', '.cookie', 'unstaged'))
    assert os.path.isfile(os.path.join('Test_Repo', '.cookie', 'userdata'))

@pytest.mark.skipif(IGNORE_BASIC_TESTS,
                    reason="IGNORE_BASIC_TESTS is True")
def test_status():
    os.chdir("Test_Repo")
    result = subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    assert "Nothing new here! No changes found." in result.stdout
    with open("file.txt", 'w') as file:
        file.write("dummy content")
    result = subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    assert "file.txt" in result.stdout
    assert "Files untracked" in result.stdout
    assert "Unstaged changes:" in result.stdout

@pytest.mark.skipif(IGNORE_BASIC_TESTS,
                    reason="IGNORE_BASIC_TESTS is True")
def test_add():
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "add", "file.txt"],
        capture_output = True,
        text = True 
    )
    result = subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    assert "Changes to be committed:" in result.stdout
    assert "Files added" in result.stdout
    assert "Unstaged changes:" not in result.stdout

@pytest.mark.skipif(IGNORE_BASIC_TESTS,
                    reason="IGNORE_BASIC_TESTS is True")
def test_login():
    test_user="Awesome_User"
    test_email="totally_valid_address@gmail.com"
    subprocess.run(
        interpreter + [ os.path.join(cookiePath, 'cookie'), "login", "-u", test_user, "-e", test_email],
        capture_output = True,
        text = True 
    )
    with open(os.path.join(".cookie", "userdata"), "r") as file:
        userdata=json.load(file)
    assert userdata["user"]==test_user
    assert userdata["email"]==test_email

@pytest.mark.skipif(IGNORE_BASIC_TESTS,
                    reason="IGNORE_BASIC_TESTS is True")
def test_commit():
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "commit", "-m", "Added file.txt"],
        capture_output = True,
        text = True 
    )
    with open(os.path.join(".cookie", "head"), "r") as file:
        head=json.load(file)
    assert head["name"]=="master"
    assert head["hash"]!=""

@pytest.mark.skipif(IGNORE_BASIC_TESTS,
                    reason="IGNORE_BASIC_TESTS is True")
def test_add2():
    os.makedirs(os.path.join("dir1", "dir2"))
    with open(os.path.join("dir1", "dir2", "nestedFile"), "w") as fp:
        fp.write("some stuff")
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "add", os.path.join("dir1", "dir2", "nestedFile")],
    )
    os.remove("file.txt")
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "add", os.path.join("file.txt")],
    )
    result = subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    assert os.path.join("dir1", "dir2", "nestedFile") in result.stdout
    assert "Files deleted" in result.stdout
    assert "file.txt" in result.stdout

@pytest.mark.skipif(IGNORE_BASIC_TESTS,
                    reason="IGNORE_BASIC_TESTS is True")
def test_commit2():
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "commit", "-m", "Removed file.txt& added nested file"],
    )
    with open(os.path.join(".cookie", "index"), "r") as indexFile:
        index=json.load(indexFile)
    assert "file.txt" not in index
    assert os.path.join("dir1", "dir2", "nestedFile") in index

@pytest.mark.skipif(IGNORE_BASIC_TESTS,
                    reason="IGNORE_BASIC_TESTS is True")
def test_modified():
    with open(os.path.join("blah.txt"), "w") as testFile:
        testFile.write("content")
    subprocess.run(
        interpreter + [ os.path.join(cookiePath, 'cookie'), "add", os.path.join("blah.txt")],
    )
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "commit", "-m", "add blah.txt."],
    )
    with open(os.path.join("blah.txt"), "w") as testFile:
        testFile.write("should appear as modified.")
    result = subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    assert "-->Files modified:" in result.stdout

@pytest.mark.skipif(IGNORE_BASIC_TESTS,
                    reason="IGNORE_BASIC_TESTS is True")
def test_renamed():
    with open(os.path.join("blah.txt"), "w") as testFile:
        testFile.write("content")
    os.rename('blah.txt', 'new.txt')
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "add", os.path.join("blah.txt")],
    )
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "add", os.path.join("new.txt")],
    )
    result = subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    assert "-->Files renamed:" in result.stdout
    assert "{} --> {}".format("blah.txt", "new.txt") in result.stdout
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "commit", "-m", "rename blah.txt to new.txt"],
    )
    index = getResource("index")
    assert "blah.txt" not in index
    assert "new.txt" in index

@pytest.mark.skipif(IGNORE_BASIC_TESTS,
                    reason="IGNORE_BASIC_TESTS is True")
def test_copied():
    os.makedirs("somedir", exist_ok=True)
    with open(os.path.join("somedir", "new_copy.txt"), "w") as testFile:
        testFile.write("content")

    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "add", os.path.join("somedir", "new_copy.txt")],
    )
    result = subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    assert "-->Files copied:" in result.stdout
    assert "{} <-- {}".format(os.path.join("somedir", "new_copy.txt"), "new.txt") in result.stdout
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "commit", "-m", "copy new.txt to somedir"],
    )

@pytest.mark.skipif(IGNORE_BASIC_TESTS,
                    reason="IGNORE_BASIC_TESTS is True")
def test_cleanup_basic():
    result = subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "delete"],
        capture_output = True,
        text = True 
    )
    assert "Cookie does not assume responsability!" in result.stdout
    os.chdir(cookiePath)
    shutil.rmtree("Test_Repo")
