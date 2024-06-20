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

IGNORE_UNDO_TESTS=False

cookiePath=os.getcwd()

@pytest.mark.skipif(IGNORE_UNDO_TESTS,
                    reason="IGNORE_UNDO_TESTS is True")
def test_undo_add_remove():
    # at the end of test_branching1() we are on master with one commit
    test_branching1() 
    with open("something.txt", 'w') as file:
        file.write("stuff stuff stuff")
    
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "add", "."]
    )
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "undo"]
    )
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "status"]
    )
    unstaged = getResource("unstaged")
    staged = getResource("staged")
    
    assert "something.txt" not in staged["A"]
    assert "something.txt" in unstaged["A"]
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "add", "."]
    )
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "remove", "."]
    )
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "undo"]
    )
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "status"]
    )
    unstaged = getResource("unstaged")
    staged = getResource("staged")
    assert "something.txt" in staged["A"]
    assert "something.txt" not in unstaged["A"]

@pytest.mark.skipif(IGNORE_UNDO_TESTS,
                    reason="IGNORE_UNDO_TESTS is True")
def test_undo_commit():
    head = getResource("head")
    oldCommit = head["hash"]
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "commit", "-m", "committed file"]
    )
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "undo"]
    )
    head = getResource("head")
    staged = getResource("staged")
    assert "something.txt" in staged["A"]
    assert head["hash"] == oldCommit

@pytest.mark.skipif(IGNORE_UNDO_TESTS,
                    reason="IGNORE_UNDO_TESTS is True")
def test_undo_checkout():
    test_branching1()
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "checkout", "secondary_branch"]
    )
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "undo"]
    )
    head = getResource("head")
    assert head["name"] == "master"

@pytest.mark.skipif(IGNORE_UNDO_TESTS,
                    reason="IGNORE_UNDO_TESTS is True")
def test_undo_create_delete_branch():
    test_branching1()
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "create_branch", "-b", "stuff"]
    )
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "undo"]
    )
    refs = getResource("refs")
    assert "stuff" not in refs["B"]
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "delete_branch", "-b", "secondary_branch"]
    )
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "undo"]
    )
    refs = getResource("refs")
    assert "secondary_branch" in refs["B"]


@pytest.mark.skipif(IGNORE_UNDO_TESTS,
                    reason="IGNORE_UNDO_TESTS is True")
def test_undo_create_delete_tag():
    test_branching1()
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "create_tag", "-t", "stuff"]
    )
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "undo"]
    )
    refs = getResource("refs")
    assert "stuff" not in refs["T"]
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "create_tag", "-t", "stuff"]
    )
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "delete_tag", "-t", "stuff"]
    )
    subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "undo"]
    )
    refs = getResource("refs")
    assert "stuff" in refs["T"]


@pytest.mark.skipif(IGNORE_UNDO_TESTS,
                    reason="IGNORE_UNDO_TESTS is True")
def test_clean_undo():
    os.chdir(cookiePath)
    shutil.rmtree("Test_Repo")