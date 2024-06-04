import os
from utils.prettyPrintLib import printColor
import sys
import json
import shutil

def getResource(name, specificPath=None):
    #for all json objects in .cookie dir
    if specificPath:
        if not os.path.isdir(specificPath):
            printColor("[DEV ERROR][getResource] Cannot find resource '{}' at '{}'.".format(name, specificPath), "red")
            sys.exit(1)
        path=os.path.join(specificPath, name)
    elif name not in ["head", "history", "index", "refs", "staged", "unstaged", "userdata", "logs", "remote_config"]:
        printColor("[DEV ERROR][getResource] Unknown resource '{}'.".format(name), "red")
        sys.exit(1)  
    else:
        path=os.path.join(".cookie", name)
    with open(path, "r") as fp:
        content=json.load(fp)
    return content

def dumpResource(name, newContent):
    if name not in ["head", "history", "index", "refs", "staged", "unstaged", "userdata", "logs", "remote_config"]:
        printColor("[DEV ERROR] Unknown resource {}".format(name), "red")
    path=os.path.join(".cookie", name)
    safeWrite(path, newContent, jsonDump=True)
    
def safeWrite(path, content, jsonDump=False, binary=False):
    if not os.path.exists(path):
        os.makedirs(os.path.abspath(os.path.join(path, os.pardir)), exist_ok=True)
    bak="{}.bak".format(path)
    if binary:
        with open(bak, "wb") as fp:
            if jsonDump:
                fp.seek(0)
                fp.write(json.dumps(content, indent=4))
            else:
                fp.seek(0)
                fp.write(content)
    else:
        with open(bak, "w") as fp:
            if jsonDump:
                fp.seek(0)
                fp.write(json.dumps(content, indent=4))
            else:
                fp.seek(0)
                fp.write(content)
    if os.path.exists(bak):
        if os.path.exists(path):
            os.remove(path)
        os.rename(bak, path)

def clearDir(dir):
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def createDirectoryStructure(args):
    project_dir=os.path.join(args.path, '.cookie')
    try:
        try:
            os.makedirs(project_dir)
        except FileExistsError:
            pass
        os.mkdir(os.path.join(project_dir, "objects"))
        os.makedirs(os.path.join(project_dir, "cache",  "undo_cache"))
        os.makedirs(os.path.join(project_dir, "cache",  "index_cache"))
        os.makedirs(os.path.join(project_dir, "cache",  "merge_cache"))
        os.makedirs(os.path.join(project_dir, "cache",  "remote_cache"))
        safeWrite(os.path.join(project_dir, "index"), {}, jsonDump=True)
        safeWrite(os.path.join(project_dir, "staged"), {"A":{},"C":{},"D":{},"M":{},"R":{},"T":{},"X":{}}, jsonDump=True)
        safeWrite(os.path.join(project_dir, "unstaged"), {"A":{},"D":{},"M":{}}, jsonDump=True)
        safeWrite(os.path.join(project_dir, "head"), {"name":"master","hash":"","tag":False}, jsonDump=True)
        safeWrite(os.path.join(project_dir, "userdata"), {"user":"", "email":""}, jsonDump=True)
        safeWrite(os.path.join(project_dir, "remote_config"), {"host":"<hostname>","port":"<port for ssh (22)>","remote_user":"<remote username>","local_ssh_private_key":"<path to local key>","host_os":"<nt/posix>","remote_path":"<path to remote repositories>"}, jsonDump=True)
        safeWrite(os.path.join(project_dir, "refs"), {"B":{"master":""},"T":{}, "D":{}}, jsonDump=True)
        safeWrite(os.path.join(project_dir, "history"), {"index":0,"commands":{}}, jsonDump=True)
        safeWrite(os.path.join(project_dir, "logs"), {"adj":{}, "nodes":{}, "edges":{}, "edge_index":0}, jsonDump=True)
    except OSError as e:
        print(e.__traceback__)
        printColor("Already a cookie repository at {}".format(project_dir),'red')
        sys.exit(1)
    printColor("Successfully initialized a cookie repository at {}".format(project_dir),'green')

def checkRepositoryInSubdirs(path):
    try:
        os.makedirs(path)
    except FileExistsError:
        pass
    for pathname in os.listdir(path):
        if pathname == '.cookie':
            printColor("Found another cookie repository at '{}'...".format(path), "red")
            printColor("Delete '.cookie' directory if files are needed.", "red")
            sys.exit(1)
        if pathname =='.git':
            pass
        if os.path.isdir(pathname):
            checkRepositoryInSubdirs(pathname)
    pass
def clearLocalData():
    safeWrite(os.path.join(".cookie", "history"), {"index":0,"commands":{}}, jsonDump=True)
    safeWrite(os.path.join(".cookie", "staged"), {"A":{},"C":{},"D":{},"M":{},"R":{},"T":{},"X":{}}, jsonDump=True)
    clearDir(os.path.join(".cookie", "cache", "undo_cache"))
    clearDir(os.path.join(".cookie", "cache", "index_cache"))
    clearDir(os.path.join(".cookie", "cache", "merge_cache"))
    clearDir(os.path.join(".cookie", "cache", "remote_cache"))

def statDictionary(mode):
    dictionary={}
    dictionary['mode']=mode.st_mode
    dictionary['uid']=mode.st_uid
    dictionary['gid']=mode.st_gid
    dictionary['size']=mode.st_size
    dictionary['mtime']=mode.st_mtime
    dictionary['ctime']=mode.st_ctime
    return dictionary

def cacheFile(pathname, cacheType='index', fileContent=None):
    if not fileContent:
        with open(pathname, 'r+b') as fileToCache:
            fileContent=fileToCache.read()

    if cacheType not in ['undo', 'merge', 'index', 'remote']:
        printColor("[DEV ERROR][cacheFile] unknown cache type received '{}'!".format(cacheType), "red")
        sys.exit(1)
    else:
        cacheTypeDir = "{}_cache".format(cacheType)
    safeWrite(os.path.join('.cookie', 'cache', cacheTypeDir, pathname), fileContent, binary=True)

def clearCommand():
    opt = None
    while opt not in ['y', 'n', 'yes', 'no']:
        print     ("==============================================")
        print     (" <> Do you wish to clear all local data?")
        printColor("    This cannot be undone!", "red")
        print     ("==============================================")
        opt = input("Please provide an option (y/n): ").lower()
        if opt not in ['y', 'n', 'yes', 'no']:
            printColor("Please provide a valid option!", "red")
    if opt in ["y", "yes"]:
        clearLocalData()
        printColor("Local data cleared...", "green")
    else:
        sys.exit(1)