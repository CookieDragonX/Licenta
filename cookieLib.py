import argparse
import sys
import os
import json
from time import time
from IndexManager import *
from ObjectManager import Commit

from prettyPrintLib import printColor

argparser = argparse.ArgumentParser(description="Cookie: World's Best SCM!")

argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True

#init subcommand definition
argsp = argsubparsers.add_parser("init", help="Initialize a new, empty repository.")
argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=os.getcwd(),
                   help="Where to create the repository.")

#add subcommand definition
argsp = argsubparsers.add_parser("add", help="Add a file to staging area.")
argsp.add_argument("paths",
                   nargs="+",
                   help="File(s) to add to staging area")

#status subcommand definition
argsp = argsubparsers.add_parser("status", help="Report the status of the current cookie repository.")

#commit subcommand definition
argsp = argsubparsers.add_parser("commit", help="Commit your changes.")
argsp.add_argument("-m",
                   "--message",
                   metavar="message",
                   required=True,
                   help="Message for this commit.")

#login subcommand definition
argsp = argsubparsers.add_parser("login", help="Set username and email for local user.")


def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    if args.command == 'add':
        add(args)
    elif args.command == 'init':
        init(args)
    elif args.command == 'commit':
        commit(args)
    elif args.command == 'checkout':
        checkout(args)
    elif args.command == 'status':
        status(args)
    elif args.command == 'login':
        login(args)
    else:
        printColor("Unknown command: {}".format(args.command),'red')
        sys.exit(1)

def resolveCookieRepository():
    prevwd=os.getcwd()
    while '.cookie' not in os.listdir():
        os.chdir('..')
        if prevwd==os.getcwd():
            printColor('Could not resolve cookie repository at this location','red')
            sys.exit(1)
    return os.getcwd()

def init(args):
    project_dir=os.path.join(args.path, '.cookie')
    try:
        os.mkdir(project_dir)
        os.mkdir(os.path.join(project_dir, "objects"))
        os.mkdir(os.path.join(project_dir, "branches"))
        os.mkdir(os.path.join(project_dir, "logs"))
        os.mkdir(os.path.join(project_dir, "refs"))
        with open(os.path.join(project_dir, "index"), 'w') as fp:
            fp.write('{}')
        with open(os.path.join(project_dir, "staged"), 'w') as fp:
            fp.write('{"A":{},"C":{},"D":{},"M":{},"R":{},"T":{},"X":{}}')
        with open(os.path.join(project_dir, "unstaged"), 'w') as fp:
            fp.write('{"A":{},"D":{},"M":{}}')
        with open(os.path.join(project_dir, "HEAD"), 'w') as fp:
            pass
        with open(os.path.join(project_dir, "userdata"), 'w') as fp:
            fp.write('{"user":"","email":""}')
    except OSError:
        printColor("Already a cookie repository at {}".format(project_dir),'red')
        sys.exit(1)
    printColor("Successfully initialized a cookie repository at {}".format(project_dir),'green')

def add(args):
    stageFiles(args.paths, resolveCookieRepository())


def checkout(args):
    pass

def status(args, quiet=False, project_dir=None):
    if project_dir==None:
        project_dir=resolveCookieRepository()
    compareToIndex(project_dir)
    resolveStagingMatches(project_dir)
    if not quiet:
        print("")
        printStaged(project_dir)
        print("")
        printUnstaged(project_dir)

def commit(args):
    project_dir=resolveCookieRepository()
    status(args,quiet=True, project_dir=project_dir)
    if not isThereStagedStuff(project_dir):
        printColor("There is noting to commit...", "blue")
        printColor("    Use 'cookie add <filename>' in order to prepare any change for commit.","blue")
        sys.exit(1) 
    metaData=['C']
    if os.stat(os.path.join(project_dir, '.cookie', 'HEAD')).st_size == 0:
        metaData.append('None')
    else:
        with open(os.path.join(project_dir, '.cookie', 'HEAD'), 'r') as headFile:
            metaData.append(headFile.read())
    metaData.append('A')
    with open(os.path.join(project_dir, '.cookie', 'userdata'), 'r') as fp:
        userdata=json.load(fp)
        
    if userdata['user'] == "":
        printColor("Please login with a valid e-mail first!",'red')
        printColor("Use 'cookie login'",'white')
        sys.exit(0)
    else:
        metaData.append(userdata['user'])
    
    metaData.append(args.message)
    metaData.append(str(time()))
    with open(os.path.join(project_dir, '.cookie', 'index'), 'r') as indexFile:
        index=json.load(indexFile)
    targetDirs=getTargetDirs(project_dir)
    metaData.append(TreeHash(project_dir, index, os.path.join(project_dir, '.cookie', 'objects'), project_dir, targetDirs))
    newCommit=Commit(':'.join(metaData))
    store(newCommit, os.path.join(project_dir, '.cookie', 'objects'))
    with open(os.path.join(project_dir, '.cookie', 'HEAD'), 'w') as headFile:
        headFile.write(newCommit.getHash())
    resetStagingArea(project_dir)
    saveIndex(project_dir, targetDirs)

def login(args):
    printColor("Please enter a valid username (empty to keep old one): ", 'white')
    user=input()
    printColor("Please enter a valid email: (empty to keep old one)", 'white')
    email=input()
    project_dir=resolveCookieRepository()
    with open(os.path.join(project_dir, '.cookie', 'userdata'), 'r') as fp:
        data=json.load(fp)
    if user != '':
        data["user"] = user
    if email != '':
        data["email"] = email
    print(data)
    with open(os.path.join(project_dir, '.cookie', 'userdata'), 'w') as fp:
        json.dump(data, fp)