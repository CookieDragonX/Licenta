import argparse
import sys
import os
argparser = argparse.ArgumentParser(description="The stupidest content tracker")

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

def init():
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
    pass