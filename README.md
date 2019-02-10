A python script which helps you while you attempt RPISEC's Modern Binary Exploitation.

It keeps track of all the passwords and automatically downloads the files for the current level. You need to just focus on exploitation and leave the connection and file downloading part to the script.
 
Basically just automated as much as I could so people can just focus on exploitation
 
Known issues:
1. Works on python2 because of pwntools, but should work on python3 when pwntools comes to python3
2. Delete files function has bugs

TODO:
1. Add the functionality to revisit any level
2. Show passwords and comments for a level

When running for the first time, the script generates a sqlite3 database in which it stores all the data. Deleting data in the script can yield unintended results though if you delete the passwords from level and adjust the status to 0, it will login you to the last level which has the status set to 1
