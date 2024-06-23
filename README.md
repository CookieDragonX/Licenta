```
                      __   .__                              
   ____  ____   ____ |  | _|__| ____   ___  __ ____   ______
 _/ ___\/  _ \ /  _ \|  |/ /  |/ __ \  \  \/ // ___\ /  ___/
 \  \__(  <_> |  <_> )    <|  \  ___/   \   /\  \___ \___ \ 
  \___  >____/ \____/|__|_ \__|\___  >   \_/  \___  >____  >
      \/                  \/       \/             \/     \/ 
```

# ==============================</br>
# Cookie Version Control System</br>
###  Milencovici Radoliub Vlad</br>
### https://github.com/CookieDragonX/Licenta</br>
# ==============================</br>

# BUILD REQUIREMENTS:
- python 3 (minimum 3.9.4)
- pyinstaller: https://pyinstaller.org/en/stable/
- external libraries: ```shutil, paramiko, diff-match-patch, psutil, termcolor, colorama``` (install with pip)

# BUILD COMMAND:
```"pyinstaller cookie"```
  - exe at 'C:\<LOCAL PATH>\dist\cookie\cookie.exe'
  - create env variable with 'C:\<LOCAL PATH>\dist\cookie'
  - MUST HAVE pyinstaller INSTALLED: https://pyinstaller.org/en/stable/installation.html </br>
```"pyinstaller cookie -noconfirm" to auto replace old binaries```</br>


# RUN TESTS COMMAND:
```
  WINDOWS: "pytest"
  UNIX   : "python3 -m pytest" (in case of versioning conflicts)
```
  - TESTS EXPECT THE COMMAND TO BE RUN IN THE BEGINNING DIR OF SOURCE CODE!!!
  - MUST HAVE pytest INSTALLED: https://docs.pytest.org/en/8.2.x/

# TO DISABLE CERTAIN TEST SUITES:</br>
  - EACH TEST SUITE HAS A VARIABLE "IGNORE_\<suite name\>_TESTS" AT THE BEGINNING </br>
  - SET VARIABLE TO TRUE IF A CERTAIN SUITE NEEDS TO BE IGNORED</br>
  - REMOTE TESTS ARE DISABLED BY DEFAULT</br>
  
# COMMANDS:
 - see command arguments:```cookie <command name> -h/--help```

```
    init                Initialize a new, empty repository.
    add                 Add a file to staging area.
    remove              Remove a file to staging area.
    status              Report the status of the current cookie repository.
    commit              Commit your changes.
    login               Set username and email for local user.
    checkout            Checkout a previous snapshot.
    create_branch       Create a new branch.
    delete_branch       Delete an existing branch.
    merge               Merge Commits or branches.
    create_tag          Create a new tag.
    delete_tag          Delete an existing tag.
    log                 Print commit data.
    clone               Clone remote repository.
    rconfig             Configure remote data.
    clear               Clear local data(caches, history).
    pull                Pull changes from remote.
    push                Push changes to remote.
    fetch               Fetch remote changes without updating local repo.
    undo                Undo a command.
```
