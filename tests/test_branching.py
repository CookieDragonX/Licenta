import os
import json
import subprocess
import shutil

cookiePath="D:\\stuffs\\Licenta"

def test_branching1():
    if os.path.exists("Test_Repo"):
        shutil.rmtree("Test_Repo")
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
    #login
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
    #create commit
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "commit", "-m", "Added file.txt"]
    )
    #create new branch and switch to it
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "create_branch", "-b", "secondary_branch"]
    )
    with open(os.path.join('.cookie', 'head')) as headFile:
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
    result=subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "commit", "-m", "Changed file.txt on secondary branch"],
        capture_output=True,
        text=True
    )
    assert "Successfully commited changes on branch 'secondary_branch'" in result.stdout
    #switch back to master
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "checkout", "master"]
    )
    with open(os.path.join('.cookie', 'head'), 'r') as headFile:
        head=json.load(headFile)
    assert head["name"]=='master'
    with open("file.txt", 'r') as file:
        content=file.read()
    assert "dummy content" in content

def test_branching2():
    if os.path.exists("Test_Repo"):
        shutil.rmtree("Test_Repo")
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
    #login
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
    #create commit
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "commit", "-m", "Added file.txt"]
    )
    #create new branch and switch to it
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "create_branch", "-b", "secondary_branch"]
    )
    with open(os.path.join('.cookie', 'head')) as headFile:
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
    result=subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "commit", "-m", "Changed file.txt on secondary branch"],
        capture_output=True,
        text=True
    )
    assert "Successfully commited changes on branch 'secondary_branch'" in result.stdout
    #switch back to master
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "checkout", "master"]
    )
    with open(os.path.join('.cookie', 'head'), 'r') as headFile:
        head=json.load(headFile)
    assert head["name"]=='master'
    with open("file.txt", 'r') as file:
        content=file.read()
    assert "dummy content" in content


def test_cleanup():
    result = subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "delete"],
        capture_output = True,
        text = True 
    )
    assert "Cookie does not assume responsability!" in result.stdout
    os.chdir("..")
    shutil.rmtree("Test_Repo")