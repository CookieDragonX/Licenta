import os
import subprocess
from tests.test_branching import test_branching1, test_cleanup
from libs.MergeLib import mergeSourceIntoTarget
from libs.BasicUtils import getResource

cookiePath="D:\\stuffs\\Licenta"

def test_undo_add():
    # at the end of test_branching1() we are on master with one commit
    test_branching1() 
    with open("something.txt", 'w') as file:
        file.write("stuff stuff stuff")
    
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "add", "."]
    )
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "undo"]
    )
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "status"]
    )
    unstaged = getResource("unstaged")
    staged = getResource("staged")
    
    assert "something.txt" not in staged["A"]
    assert "something.txt" in unstaged["A"]
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "add", "."]
    )
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "remove", "."]
    )
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "undo"]
    )
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "status"]
    )
    unstaged = getResource("unstaged")
    staged = getResource("staged")
    assert "something.txt" in staged["A"]
    assert "something.txt" not in unstaged["A"]

def test_undo_commit():
    head = getResource("head")
    oldCommit = head["hash"]
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "commit", "-m", "committed file"]
    )
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "undo"]
    )
    head = getResource("head")
    staged = getResource("staged")
    assert "something.txt" in staged["A"]
    assert head["hash"] == oldCommit

# def test_clean_undo():
#     test_cleanup()