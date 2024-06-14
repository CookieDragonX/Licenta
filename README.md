==============================</br>
Cookie File Versioning System</br>
  Milencovici Radoliub Vlad</br>
==============================</br>
BUILD REQUIREMENTS:
- python 3 (minimum 3.9.4)
- pyinstaller: https://pyinstaller.org/en/stable/
- libraries: shutil, paramiko, diff-match-patch, psutil, termcolor, colorama (install with pip)

BUILD COMMAND: "pyinstaller cookie"
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
