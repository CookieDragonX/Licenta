import os
import subprocess
from tests.test_branching import test_branching1
from libs.MergeManager import mergeSourceIntoTarget
from libs.BasicUtils import getResource
import shutil 
import pytest

if os.name == 'nt':
    interpreter = ["py", "-3"]
else:
    interpreter = ["python3"]

IGNORE_MERGING_TESTS=False

cookiePath=os.getcwd()

@pytest.mark.skipif(IGNORE_MERGING_TESTS,
                    reason="IGNORE_MERGING_TESTS is True")
def test_merging1(monkeypatch):
    # at the end of test_branching1() we are on master with one commit
    test_branching1() 
    with open("newFile.txt", 'w') as file:
        file.seek(0)
        file.write("content content")
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "add", "newFile.txt"]
    )

    # commit on secondary branch
    result=subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "commit", "-m", "added new file"],
        capture_output=True,
        text=True
    )
    assert "Successfully commited changes on branch 'master'" in result.stdout
    
    # merge branches but quit at the end
    inputs = iter(['T', 'n'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    head = getResource("head")
    oldHead=head["hash"]
    mergeSourceIntoTarget("master", "secondary_branch")
    head = getResource("head")
    newHead = head["hash"]
    assert oldHead == newHead

    # merge branches fully 
    inputs = iter(['s', 'Y'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    mergeSourceIntoTarget("master", "secondary_branch")
    with open("file.txt", "r") as fp:
        content = fp.read()
    assert content == "something different"
    
@pytest.mark.skipif(IGNORE_MERGING_TESTS,
                    reason="IGNORE_MERGING_TESTS is True")
def test_clean_merge():
    os.chdir(cookiePath)
    shutil.rmtree("Test_Repo")
