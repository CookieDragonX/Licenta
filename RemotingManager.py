from prettyPrintLib import printColor
import os
import json

def  editLoginFile(args):
    if args.user == None:
            printColor("Please enter a valid username (empty to keep old one): ", 'white')
            user=input()
    else:
        user=args.user
    if args.email == None:
        printColor("Please enter a valid email: (empty to keep old one)", 'white')
        email=input()
    else:
        email=args.email
    with open(os.path.join('.cookie', 'userdata'), 'r') as fp:
        data=json.load(fp)
    if user != '':
        data["user"] = user
    if email != '':
        data["email"] = email
    with open(os.path.join('.cookie', 'userdata'), 'w') as fp:
        json.dump(data, fp)