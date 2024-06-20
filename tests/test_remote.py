import os
import subprocess
import shutil
import pytest

if os.name == 'nt':
    interpreter = ["py", "-3"]
else:
    interpreter = ["python3"]

IGNORE_REMOTE_TESTS=False

cookiePath=os.getcwd()

@pytest.mark.skipif(IGNORE_REMOTE_TESTS,
                    reason="IGNORE_REMOTE_TESTS is True")
def test_clone():
    if os.path.exists("Test_Repo"):
        shutil.rmtree("Test_Repo")
    #initialize
    result = subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "clone", "Test_Repo", "-c", os.path.join(cookiePath, "tests", "remote_config.json")],
        capture_output = True,
        text = True 
    )
    os.chdir("Test_Repo")
    assert os.path.exists("paramiko.log")
    assert os.path.exists(".cookie")
    assert os.path.exists(os.path.join("123", "hehe")) 
    assert "Checking out branch master..." in result.stdout
    os.chdir(cookiePath)
    if os.path.exists("Test_Repo"):
        shutil.rmtree("Test_Repo")
    #initialize
    result = subprocess.run(
        interpreter + [os.path.join(cookiePath, 'cookie'), "clone", "Test_Repo", "-c", os.path.join(cookiePath, "tests", "remote_config.json"), "-b", "secondary_branch"],
        capture_output = True,
        text = True 
    )
    assert "Checking out branch secondary_branch..." in result.stdout


@pytest.mark.skipif(IGNORE_REMOTE_TESTS,
                    reason="IGNORE_REMOTE_TESTS is True")
def test_clean_remote():
    os.chdir(cookiePath)
    shutil.rmtree("Test_Repo")