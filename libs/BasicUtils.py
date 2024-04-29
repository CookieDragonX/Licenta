import os
from utils.prettyPrintLib import printColor
import sys
import json

def getResource(name, specificPath=None):
    #for all json objects in .cookie dir
    if specificPath:
        if not os.path.isdir(specificPath):
            printColor("[DEV ERROR][getResource] Cannot find resource '{}' at '{}'.".format(name, specificPath), "red")
            sys.exit(1)
        path=os.path.join(specificPath, name)
    elif name not in ["HEAD", "history", "index", "refs", "staged", "unstaged", "userdata", "logs"]:
        printColor("[DEV ERROR][getResource] Unknown resource '{}'.".format(name), "red")
        sys.exit(1)  
    else:
        path=os.path.join(".cookie", name)
    with open(path, "r") as fp:
        content=json.load(fp)
    return content

def dumpResource(name, newContent):
    if name not in ["HEAD", "history", "index", "refs", "staged", "unstaged", "userdata", "logs"]:
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
        
def createDirectoryStructure(args):
    project_dir=os.path.join(args.path, '.cookie')
    try:
        os.makedirs(project_dir)
        os.mkdir(os.path.join(project_dir, "objects"))
        os.makedirs(os.path.join(project_dir, "cache",  "undo_cache"))
        os.makedirs(os.path.join(project_dir, "cache",  "index_cache"))
        os.makedirs(os.path.join(project_dir, "cache",  "merge_cache"))
        safeWrite(os.path.join(project_dir, "index"), {}, jsonDump=True)
        safeWrite(os.path.join(project_dir, "staged"), {"A":{},"C":{},"D":{},"M":{},"R":{},"T":{},"X":{}}, jsonDump=True)
        safeWrite(os.path.join(project_dir, "unstaged"), {"A":{},"D":{},"M":{}}, jsonDump=True)
        safeWrite(os.path.join(project_dir, "HEAD"), {"name":"master","hash":""}, jsonDump=True)
        safeWrite(os.path.join(project_dir, "userdata"), {"user":"", "email":"", "host":"192.168.0.101", "port":"22", "remote_user":"Utilizator", "ssh_key_path":"C:\\Users\\utilizator\\.ssh\\id_rsa", "host_os":"win32", "remote_scripts_path":"D:\CookieRemote"}, jsonDump=True)
        safeWrite(os.path.join(project_dir, "refs"), {"B":{"master":""},"T":{}}, jsonDump=True)
        safeWrite(os.path.join(project_dir, "history"), {"index":0,"commands":{}}, jsonDump=True)
        safeWrite(os.path.join(project_dir, "logs"), {"adj":{}, "nodes":{}, "edges":{}, "edge_index":0}, jsonDump=True)
    except OSError as e:
        print(e.__traceback__)
        printColor("Already a cookie repository at {}".format(project_dir),'red')
        sys.exit(1)
    printColor("Successfully initialized a cookie repository at {}".format(project_dir),'green')

def statDictionary(mode):
    dictionary={}
    dictionary['mode']=mode.st_mode
    dictionary['uid']=mode.st_uid
    dictionary['gid']=mode.st_gid
    dictionary['size']=mode.st_size
    dictionary['mtime']=mode.st_mtime
    dictionary['ctime']=mode.st_ctime
    return dictionary

def printStaged():
    staged=getResource("staged")
    if staged['A']!={} or staged['D']!={} or staged['M']!={} or staged['C']!={} or staged['R']!={} or staged['T']!={} or staged['X']!={}:
        printColor("-----------------------------------------------------------------", "white")
        printColor("    <> Changes to be committed:","white")
        if staged['A']!={}:
            printColor("-->Files added:",'green')
            print(*["   {}".format(file) for file in staged['A']], sep=os.linesep)
        if staged['D']!={}:
            printColor("-->Files deleted:",'green')
            print(*["   {}".format(file) for file in staged['D']], sep=os.linesep)
        if staged['M']!={}:
            printColor("-->Files modified:",'green')
            print(*["   {}".format(file) for file in staged['M']], sep=os.linesep)
        if staged['C']!={}:
            printColor("-->Files copied:",'green')
            print(*["   {} <-- {}".format(file, staged['C'][file][0]) for file in staged['C']], sep=os.linesep)
        if staged['R']!={}:
            moved=dict()
            for item in staged['R']:
                if os.path.basename(item)==os.path.basename(staged['R'][item][0]):
                    moved[item]=staged['R'][item]
            if len(moved) > 0 :
                printColor("-->Files moved:",'green')
                print(*["   {} --> {}".format(moved[file][0], file) for file in moved], sep=os.linesep)
            if len(moved) < len(staged['R']):
                printColor("-->Files renamed:",'green')
                print(*["   {} --> {}".format(staged['R'][file][0], file) if file not in moved else "" for file in staged['R']], sep=os.linesep)
        if staged['T']!={}:
            printColor("-->Files with type changes:",'green')
            print(*["   {}".format(file) for file in staged['T']], sep=os.linesep)
        if staged['X']!={}:
            printColor("-->Files with unknown modifications:",'green')
            print(*["   {}".format(file) for file in staged['X']], sep=os.linesep)
        printColor("-----------------------------------------------------------------", "white")
        return True
    return False

def printUnstaged():
    unstaged=getResource("unstaged")
    if unstaged['A']!={} or unstaged['D']!={} or unstaged['M']!={}:
        printColor("-----------------------------------------------------------------", "white")
        printColor("    <> Unstaged changes:","white")
        if unstaged['A']!={}:
            printColor("-->Files untracked:",'red')
            print(*["   {}".format(file) for file in unstaged['A']], sep=os.linesep)
        if unstaged['D']!={}:
            printColor("-->Files deleted:",'red')
            print(*["   {}".format(file) for file in unstaged['D']], sep=os.linesep)
        if unstaged['M']!={}:
            printColor("-->Files modified:",'red')
            print(*["   {}".format(file) for file in unstaged['M']], sep=os.linesep)
        printColor("    Use 'cookie add <filename>' in order to prepare any change for commit.","blue")
        printColor("-----------------------------------------------------------------", "white")
        return True
    return False
    
def cacheFile(pathname, cacheType='index', fileContent=None):
    if not fileContent:
        with open(pathname, 'r') as fileToCache:
            fileContent=fileToCache.read()

    if cacheType not in ['undo', 'merge', 'index']:
        printColor("[DEV ERROR][cacheFile] unknown cache type received '{}'!".format(cacheType), "red")
        sys.exit(1)
    else:
        cacheTypeDir = "{}_cache".format(cacheType)
    safeWrite(os.path.join('.cookie', 'cache', cacheTypeDir, pathname), fileContent)
