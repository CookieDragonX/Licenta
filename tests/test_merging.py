import os
import json
import subprocess
import shutil
from tests.test_branching import test_branching1, test_cleanup
from libs.MergeLib import mergeSourceIntoTarget
from libs.BasicUtils import getResource
###################################################################
#               Preconditions:
#
#   - there should be not directory named 'Test_Repo' as this test
#       will create it and apply basic commands on it
#
##################################################################

cookiePath="D:\\stuffs\\Licenta"

def test_merging1(monkeypatch):
    # at the end of test_branching1() we are on master with one commit
    test_branching1() 
    with open("newFile.txt", 'w') as file:
        file.seek(0)
        file.write("content content")
    subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "add", "newFile.txt"]
    )

    # commit on secondary branch
    result=subprocess.run(
        ["py", "-3", os.path.join(cookiePath, 'cookie'), "commit", "-m", "added new file"],
        capture_output=True,
        text=True
    )
    assert "Successfully commited changes on branch 'master'" in result.stdout
    
    # merge branches but quit at the end
    inputs = iter(['T', 'n'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    head = getResource("HEAD")
    oldHead=head["hash"]
    mergeSourceIntoTarget("master", "secondary_branch")
    head = getResource("HEAD")
    newHead = head["hash"]
    assert oldHead == newHead

    # merge branches fully 
    inputs = iter(['s', 'Y'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    mergeSourceIntoTarget("master", "secondary_branch")
    with open("file.txt", "r") as fp:
        content = fp.read()
    assert content == "something new"

# def test_clean_merge():
#     test_cleanup()