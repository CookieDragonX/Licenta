Cookie File Versioning System
- Milencovici Radoliub Vlad
                 _    _      
  ___ ___   ___ | | _(_) ___ 
 / __/ _ \ / _ \| |/ / |/ _ \
| (_| (_) | (_) |   <| |  __/
 \___\___/ \___/|_|\_\_|\___|

TO DO:
---- TOP PRIO ----
- data doesn't get hashed right and tree doesn't keep track of children (impacts checkout command development)
- checkout strategy

- <BUG> Check all usage of ':' character splitting
        - for example in commit message ':' character breaks command
        - either do not allow for ':' char to be used or find other split/way to store data
- merging strategies

---- LOW TO NO PRIO? ----
- client server
