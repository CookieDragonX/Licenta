import argparse
import sys
import os

from IndexManager import compareToIndex

argparser = argparse.ArgumentParser(description="Cookie: World's Best SCM!")

argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True

def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    if args.command == 'add':
        add()
    elif args.command == 'init':
        init()
    elif args.command == 'commit':
        commit()
    elif args.command == 'checkout':
        checkout()
    elif args.command == 'status':
        status()
    else:
        print("Unknown command: "+args.command)
        sys.exit(1)

def add():
    pass

def init(path=None):
    project_dir=os.environ["PROJECT_DIR"]
    os.mkdir(project_dir)
    os.mkdir(os.path.join(project_dir, "objects"))
    os.mkdir(os.path.join(project_dir, "branches"))
    os.mkdir(os.path.join(project_dir, "logs"))
    os.mkdir(os.path.join(project_dir, "refs"))
    with open(os.path.join(project_dir, "index"), 'w') as fp:
        pass
    with open(os.path.join(project_dir, "HEAD"), 'w') as fp:
        pass

def checkout():
    pass

def status():

    pass

def commit():
    # deleted/modified are already added, new files need to be added tho
    pass