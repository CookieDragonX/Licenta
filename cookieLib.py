import argparse
import sys
import os

from IndexManager import compareToIndex, printStaged, printUnstaged, stageFiles, resolveStagingMatches

from prettyPrintLib import printColor

argparser = argparse.ArgumentParser(description="Cookie: World's Best SCM!")

argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True

argsp = argsubparsers.add_parser("init", help="Initialize a new, empty repository.")
argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=os.getcwd(),
                   help="Where to create the repository.")


argsp = argsubparsers.add_parser("add", help="Add a file to staging area.")
argsp.add_argument("paths",
                   nargs="+",
                   help="File(s) to add to staging area")

argsp = argsubparsers.add_parser("status", help="Report the status of the current cookie repository.")

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
            pass
        with open(os.path.join(project_dir, "staging"), 'w') as fp:
            fp.write('{"A":{},"C":{},"D":{},"M":{},"R":{},"T":{},"X":{}}')
            pass
        with open(os.path.join(project_dir, "unstaged"), 'w') as fp:
            fp.write('{"A":{},"D":{},"M":{}}')
            pass
        with open(os.path.join(project_dir, "HEAD"), 'w') as fp:
            pass
    except OSError:
        printColor("Already a cookie repository at {}".format(project_dir),'red')
        sys.exit(1)
    printColor("Successfully initialized a cookie repository at {}".format(project_dir),'green')

def add(args):
    stageFiles(args.paths, resolveCookieRepository())


def checkout(args):
    pass

def status(args, quiet=False):
    project_dir=resolveCookieRepository()
    compareToIndex(project_dir)
    resolveStagingMatches(project_dir)
    if not quiet:
        printStaged(project_dir)
        printUnstaged(project_dir)

def commit(args):
    status(quiet=True)
    # deleted/modified are already added, new files need to be added tho
    pass