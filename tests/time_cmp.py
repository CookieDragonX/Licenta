import subprocess
import time
import os
import shutil

def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.
    
    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def measure_time(fct):
    def inner(*argv, **kwargs):
        t0=time.time()
        rez=fct(*argv, **kwargs)
        t1=time.time()
        print(f'Execution time is : {t1-t0} for function {fct.__name__}')
        return rez
    return inner

def setup_git():
    resource_path = os.path.dirname(os.path.abspath(__file__))
    resource_path = os.path.join(resource_path, "time_cmp_files")
    shutil.copytree(resource_path,"Test_Repo")
    os.chdir("Test_Repo")
    subprocess.run(["git", "init"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) 


@measure_time
def git_add(initial_path):
    os.chdir(os.path.join(initial_path, "Test_Repo"))
    subprocess.run(["git", "add", "."], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) 


@measure_time
def git_status(initial_path):
    os.chdir(os.path.join(initial_path, "Test_Repo"))
    subprocess.run(["git", "status"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) 


@measure_time
def git_commit(initial_path):
    os.chdir(os.path.join(initial_path, "Test_Repo"))
    subprocess.run(["git", "commit", "-m", "test"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) 

@measure_time
def git_reset_to_master(initial_path):
    os.chdir(os.path.join(initial_path, "Test_Repo"))
    subprocess.run(["git", "checkout", "-b", "new"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) 
    for file in os.listdir():
        if file != '.git':
            if os.path.isdir(file):
                shutil.rmtree(file, onerror=onerror)
            else:
                os.remove(file)
    subprocess.run(["git", "add", "."], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) 
    subprocess.run(["git", "commit", "-m", "test2"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) 
    subprocess.run(["git", "checkout", "master"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) 


def setup_cookie():
    resource_path = os.path.dirname(os.path.abspath(__file__))
    resource_path = os.path.join(resource_path, "time_cmp_files")
    shutil.copytree(resource_path,"Test_Repo")
    os.chdir("Test_Repo")
    subprocess.run(["cookie", "init"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) 
    subprocess.run(['cookie', "login", "-u", 'test_user', "-e", 'test_email'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

@measure_time
def cookie_add(initial_path):
    os.chdir(os.path.join(initial_path, "Test_Repo"))
    subprocess.run(["cookie", "add", "."], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) 

@measure_time
def cookie_status(initial_path):
    os.chdir(os.path.join(initial_path, "Test_Repo"))
    subprocess.run(["cookie", "status"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) 

@measure_time
def cookie_commit(initial_path):
    os.chdir(os.path.join(initial_path, "Test_Repo"))
    subprocess.run(["cookie", "commit", "-m", "test"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) 

@measure_time
def cookie_reset_to_master(initial_path):
    os.chdir(os.path.join(initial_path, "Test_Repo"))
    subprocess.run(["cookie", "create_branch", "-b", "new"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) 
    for file in os.listdir():
        if file != '.cookie':
            if os.path.isdir(file):
                shutil.rmtree(file, onerror=onerror)
            else:
                os.remove(file)
    subprocess.run(["cookie", "add", "."], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) 
    subprocess.run(["cookie", "commit", "-m", "test2"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) 
    subprocess.run(["cookie", "checkout", "master"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) 

def cleanup(initial_path):
    os.chdir(initial_path)
    shutil.rmtree("Test_Repo", onerror=onerror)

    
initial_path = os.getcwd()
if os.path.exists(os.path.join(initial_path, "Test_Repo")):
    cleanup(initial_path)

setup_git()
git_status(initial_path)
git_add(initial_path)
git_commit(initial_path)
git_reset_to_master(initial_path)
cleanup(initial_path)


setup_cookie()
cookie_status(initial_path)
cookie_add(initial_path)
cookie_commit(initial_path)
cookie_reset_to_master(initial_path)
cleanup(initial_path)
