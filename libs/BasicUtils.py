import os
from utils.prettyPrintLib import printColor
import sys
import json

def createDirectoryStructure(args):
    project_dir=os.path.join(args.path, '.cookie')
    try:
        os.makedirs(project_dir)
        os.mkdir(os.path.join(project_dir, "objects"))
        os.mkdir(os.path.join(project_dir, "logs"))
        os.makedirs(os.path.join(project_dir, "cache"))
        with open(os.path.join(project_dir, "index"), 'w') as fp:
            fp.write('{}')
        with open(os.path.join(project_dir, "staged"), 'w') as fp:
            fp.write('{"A":{},"C":{},"D":{},"M":{},"R":{},"T":{},"X":{}}')
        with open(os.path.join(project_dir, "unstaged"), 'w') as fp:
            fp.write('{"A":{},"D":{},"M":{}}')
        with open(os.path.join(project_dir, "HEAD"), 'w') as fp:
            fp.write('{"name":"master","hash":""}')
        with open(os.path.join(project_dir, "userdata"), 'w') as fp:
            fp.write('{"user":"","email":""}')
        with open(os.path.join(project_dir, "refs"), 'w') as fp:
            fp.write('{"B":{"master":""},"T":{}}')
        with open(os.path.join(project_dir, "history"), "w") as fp:
            fp.write('{"index":0,"commands":{}}')
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
    with open(os.path.join('.cookie', 'staged'), 'r') as stagedFile:
        staged=json.load(stagedFile)
    if staged['A']!={} or staged['D']!={} or staged['M']!={} or staged['C']!={} or staged['R']!={} or staged['T']!={} or staged['X']!={}:
        printColor("    Changes to be committed:","white")
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
            print(*["   {}".format(file) for file in staged['M']], sep=os.linesep)
        if staged['R']!={}:
            printColor("-->Files renamed:",'green')
            print(*["   {}".format(file) for file in staged['M']], sep=os.linesep)
        if staged['T']!={}:
            printColor("-->Files with type changes:",'green')
            print(*["   {}".format(file) for file in staged['M']], sep=os.linesep)
        if staged['X']!={}:
            printColor("-->Files with unknown modifications:",'green')
            print(*["   {}".format(file) for file in staged['M']], sep=os.linesep)
        return True
    return False

def printUnstaged():
    with open(os.path.join('.cookie', 'unstaged'), 'r') as unstagedFile:
        unstaged=json.load(unstagedFile)
    if unstaged['A']!={} or unstaged['D']!={} or unstaged['M']!={}:
        printColor("    Unstaged changes:","white")
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
        return True
    return False