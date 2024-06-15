import os
import json
import subprocess
import shutil
import pytest

if os.name == 'nt':
    interpreter = ["py", "-3"]
else:
    interpreter = ["python3"]

IGNORE_BRANCHING_TESTS=False

cookiePath=os.getcwd()

@pytest.mark.skipif(IGNORE_BRANCHING_TESTS,
                    reason="IGNORE_BRANCHING_TESTS is True")
def test_branching1():
    os.chdir(cookiePath)
    if os.path.exists("Test_Repo"):
        shutil.rmtree("Test_Repo")
    #initialize
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "init", "Test_Repo"]
    )
    os.chdir("Test_Repo")
    #add a file
    with open("file.txt", 'w') as file:
        file.write("dummy content")
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "add", "file.txt"]
    )
    #login
    test_user="Awesome_User"
    test_email="totally_valid_address@gmail.com"
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "login", "-u", test_user, "-e", test_email],
        capture_output = True,
        text = True 
    )
    with open(os.path.join(".cookie", "userdata"), "r") as file:
        userdata=json.load(file)
    assert userdata["user"]==test_user
    assert userdata["email"]==test_email
    #create commit
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "commit", "-m", "Added file.txt"]
    )
    #create new branch and switch to it
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "create_branch", "-b", "secondary_branch", "-c"]
    )
    with open(os.path.join('.cookie', 'head')) as headFile:
        head=json.load(headFile)
    assert head["name"]=='secondary_branch'
    
    #change file content
    with open("file.txt", 'w') as file:
        file.seek(0)
        file.write("something different")
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "add", "file.txt"]
    )

    #commit on secondary branch
    result=subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "commit", "-m", "Changed file.txt on secondary branch"],
        capture_output=True,
        text=True
    )
    assert "Successfully commited changes on branch 'secondary_branch'" in result.stdout
    #switch back to master
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "checkout", "-r", "master"]
    )
    with open(os.path.join('.cookie', 'head'), 'r') as headFile:
        head=json.load(headFile)
    assert head["name"]=='master'
    with open("file.txt", 'r') as file:
        content=file.read()
    assert "dummy content" in content

@pytest.mark.skipif(IGNORE_BRANCHING_TESTS,
                    reason="IGNORE_BRANCHING_TESTS is True")
def test_branching2():
    os.chdir(cookiePath)
    if os.path.exists("Test_Repo"):
        shutil.rmtree("Test_Repo")
    #initialize
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "init", "Test_Repo"]
    )
    os.chdir("Test_Repo")
    #add a file
    with open("file.txt", 'w') as file:
        file.write("dummy content")
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "add", "file.txt"]
    )
    #login
    test_user="Awesome_User"
    test_email="totally_valid_address@gmail.com"
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "login", "-u", test_user, "-e", test_email],
        capture_output = True,
        text = True 
    )
    with open(os.path.join(".cookie", "userdata"), "r") as file:
        userdata=json.load(file)
    assert userdata["user"]==test_user
    assert userdata["email"]==test_email
    #create commit
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "commit", "-m", "Added file.txt"]
    )
    #create new branch and switch to it
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "create_branch", "-b", "secondary_branch", "-c"]
    )
    with open(os.path.join('.cookie', 'head')) as headFile:
        head=json.load(headFile)
    assert head["name"]=='secondary_branch'
    
    #change file content
    with open("file.txt", 'w') as file:
        file.seek(0)
        file.write("something different11111111111111111111111111111111111111111111")
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "add", "file.txt"]
    )

    #commit on secondary branch
    result=subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "commit", "-m", "Changed file.txt on secondary branch"],
        capture_output=True,
        text=True
    )
    assert "Successfully commited changes on branch 'secondary_branch'" in result.stdout
    #switch back to master
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "checkout", "master"]
    )
    with open(os.path.join('.cookie', 'head'), 'r') as headFile:
        head=json.load(headFile)
    assert head["name"]=='master'
    with open("file.txt", 'r') as file:
        content=file.read()
    assert "something different" in content
    result = subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "status"],
        capture_output = True,
        text = True 
    )
    #assert 'Files modified' in result.stdout
    assert 'file.txt' in result.stdout

@pytest.mark.skipif(IGNORE_BRANCHING_TESTS,
                    reason="IGNORE_BRANCHING_TESTS is True")
def test_branching3():
    # at the end of test_branching1() we are on master with one commit
    test_branching1() 
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "checkout", "secondary_branch"]
    )
    with open("file.txt", 'r') as file:
        content=file.read()
    assert "dummy content" in content
    result = subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "checkout", "secondary_branch", "-r"],
        capture_output = True,
        text = True 
    )
    assert "Already on branch secondary_branch!" in result.stdout
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "checkout", "secondary_branch", "-rf"],
    )
    with open("file.txt", 'r') as file:
        content=file.read()
    assert "something different" in content

@pytest.mark.skipif(IGNORE_BRANCHING_TESTS,
                    reason="IGNORE_BRANCHING_TESTS is True")
def test_cleanup_branching():
    result = subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "delete"],
        capture_output = True,
        text = True 
    )
    assert "Cookie does not assume responsability!" in result.stdout
    os.chdir(cookiePath)
    shutil.rmtree("Test_Repo")
