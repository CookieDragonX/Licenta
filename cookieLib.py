import argparse
import sys
import os

from IndexManager import compareToIndex, printDifferences

argparser = argparse.ArgumentParser(description="Cookie: World's Best SCM!")

argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True

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
        print("Unknown command: "+args.command)
        sys.exit(1)

def add(args):
    if args[1]=='.':
        #add all to staging
        pass
    else:   
        for arg in args:
            print(arg)

def init(args):
    project_dir=os.environ["PROJECT_DIR"]
    try:
        os.mkdir(project_dir)
        os.mkdir(os.path.join(project_dir, "objects"))
        os.mkdir(os.path.join(project_dir, "branches"))
        os.mkdir(os.path.join(project_dir, "logs"))
        os.mkdir(os.path.join(project_dir, "refs"))
        with open(os.path.join(project_dir, "index"), 'w') as fp:
            fp.write('{}')
            pass
        with open(os.path.join(project_dir, "staged"), 'w') as fp:
            fp.write('{}')
            pass
        with open(os.path.join(project_dir, "unstaged"), 'w') as fp:
            fp.write('{}')
            pass
        with open(os.path.join(project_dir, "HEAD"), 'w') as fp:
            fp.write('{}')
            pass
    except OSError:
        print("Already a cookie repository at "+project_dir)
        sys.exit(1)

def checkout(args):
    pass

def status(args):
    project_dir=os.environ["PROJECT_DIR"]
    compareToIndex(project_dir)
    printDifferences(project_dir)

def commit(args):
    # deleted/modified are already added, new files need to be added tho
    pass