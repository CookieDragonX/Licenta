==============================</br>
Cookie File Versioning System</br>
  Milencovici Radoliub Vlad</br>
https://github.com/CookieDragonX/Licenta</br>
==============================</br>
BUILD REQUIREMENTS:
- python 3 (minimum 3.9.4)
- pyinstaller: https://pyinstaller.org/en/stable/
- libraries: shutil, paramiko, diff-match-patch, psutil, termcolor, colorama (install with pip)

BUILD COMMAND: "pyinstaller cookie"</br>
("pyinstaller cookie -noconfirm" to auto replace old binaries)</br>
  - exe at 'C:\<LOCAL PATH>\dist\cookie\cookie.exe'
  - create env variable with 'C:\<LOCAL PATH>\dist\cookie'

RUN TESTS COMMAND: 
  WINDOWS: "pytest"
  UNIX   : "python3 -m pytest" (in case of versioning conflicts)
  - TESTS EXPECT THE COMMAND TO BE RUN IN THE BEGINNING DIR OF SOURCE CODE!!!
  - MUST HAVE pytest INSTALLED: https://docs.pytest.org/en/8.2.x/

TO DISABLE CERTAIN TEST SUITES:</br>
  - EACH TEST SUITE HAS A VARIABLE "IGNORE_\<suite name\>_TESTS" AT THE BEGINNING </br>
  - SET VARIABLE TO TRUE IF A CERTAIN SUITE NEEDS TO BE IGNORED</br>
  - REMOTE TESTS ARE DISABLED BY DEFAULT</br>
  
COMMANDS:
	init                Initialize a new, empty repository.</br>
    add                 Add a file to staging area.</br>
    remove              Remove a file to staging area.</br>
    status              Report the status of the current cookie repository.</br>
    commit              Commit your changes.</br>
    login               Set username and email for local user.</br>
    checkout            Checkout a previous snapshot.</br>
    create_branch       Create a new branch.</br>
    delete_branch       Delete an existing branch.</br>
    merge               Merge Commits or branches.</br>
    create_tag          Create a new tag.</br>
    delete_tag          Delete an existing tag.</br>
    log                 Print commit data.</br>
    clone               Clone remote repository.</br>
    rconfig             Configure remote data.</br>
    clear               Clear local data(caches, history).</br>
    pull                Pull changes from remote.</br>
    push                Push changes to remote.</br>
    fetch               Fetch remote changes without updating local repo.</br>
    undo                Undo a command.</br>
