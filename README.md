==============================</br>
Cookie File Versioning System</br>
- Milencovici Radoliub Vlad</br>
==============================</br>
TO DO:

---- TOP PRIO ----
 
- encrypt data in objects

- checkout strategy test more

- merging strategies

- cookie undo

- format file names when adding...

- write more tests

---- BUG ---- 
Check all usage of ':' character splitting
- for example in commit message ':' character breaks command

- either do not allow for ':' char to be used or find other split/way to store data

- PLAN FOR THIS ---> replace with '?', seems like git itself doesn't allow it, in pr names at least!!!

- if they appear remove them, no one will ever know :D


---- LOW TO NO PRIO? ----
- client server
