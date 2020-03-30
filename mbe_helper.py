#!/usr/bin/env python2

from pwn import *
import sqlite3
import os

mbeUserTemplate='lab{}{}'
mbePassTemplate='lab0{}start'
mbeLevelTemplate='lab0{}'

db=sqlite3.connect('status.db')
cursor=db.cursor()

def getNextUser(currentUser): 
    if currentUser[-1]=='A':
        return currentUser[:-1]+'end'
    elif currentUser[3]=='7':
        return 'lab7A'
    else:
        return (currentUser[:-1]+chr(ord(currentUser[-1])-1))

def solve(mbe_user):

    cursor.execute('''UPDATE STATUS SET solved = 1 WHERE user = ? ''',(mbe_user,))

    nextPass=raw_input("Enter password for "+getNextUser(mbe_user)+" ").strip()
    comment=raw_input("Any comments for this level ").strip()
    
    cursor.execute('''UPDATE STATUS SET comments     = ? WHERE user = ? ''',(mbe_user, comment))
    cursor.execute('''UPDATE STATUS SET password = ? WHERE user = ? ''',(nextPass, getNextUser(mbe_user)))

    if mbe_user[-1]=='A':
        cursor.execute('''UPDATE STATUS SET solved = 1 WHERE user = ? ''',(getNextUser(mbe_user),))
    
    db.commit()

def delfiles(mbe_user):
    cursor.execute('''SELECT files FROM FILES WHERE user = ?''',(mbe_user,))
    files=cursor.fetchone()
    deleted=False
    if files[0] != None:
        delfile=files[0].split()
        for File in delfile:
            if os.path.isfile(File):
                os.remove(File)
                deleted=True
    if deleted: return True
    else: return False


def fixIP(mbe_ip):
    
    cursor.execute('''UPDATE IP SET ip = ?''',(mbe_ip,))
    db.commit()

def fixPass(mbe_user):
    new_pass=raw_input("Enter correct Password").strip()
    
    cursor.execute('''UPDATE STATUS SET password = ? WHERE user = ?''',(new_pass,mbe_user))
    db.commit()

def dbFiles(mbe_user,fileList):
    cursor.execute('''UPDATE FILES SET files = ? WHERE user = ? ''',(mbe_user, fileList))
    db.commit()

def generateDB(mbe_ip):

    cursor.execute('''CREATE TABLE IP(ip TEXT)''')
    cursor.execute('''CREATE TABLE FILES(user TEXT, files TEXT)''')
    cursor.execute('''INSERT INTO IP(ip) VALUES(?)''',(mbe_ip,))
    cursor.execute('''CREATE TABLE STATUS(level INTEGER , sublevel INTEGER, user TEXT PRIMARY KEY, password TEXT, solved INTEGER, comments TEXT)''')

    for level in range(1,10):
        for sublevel in ['C','B','A','end']:
            if ((level==7 or level==9) and sublevel=='B'):continue
            if sublevel == 'C':cursor.execute('''INSERT INTO STATUS(level, sublevel, user, password, solved, comments) VALUES(:level, :sublevel, :user, :password, :solved, :comments)''',{'level':level, 'sublevel':sublevel, 'user':mbeUserTemplate.format(level,sublevel), 'password':mbePassTemplate.format(level), 'solved':0, 'comments':None})
            else:cursor.execute('''INSERT INTO STATUS(level, sublevel, user, password, solved, comments) VALUES(:level, :sublevel, :user, :password, :solved, :comments)''',{'level':level, 'sublevel':sublevel, 'user':mbeUserTemplate.format(level,sublevel), 'password':None, 'solved':0, 'comments':None})


    
    for level in range(1,10):
        for sublevel in ['C','B','A']:
            if ((level==7 or level==9) and sublevel=='B'):continue
            if sublevel == 'C':cursor.execute('''INSERT INTO FILES(user, files) VALUES(:user, :files)''',{'user':mbeUserTemplate.format(level,sublevel), 'files':None})
            else:cursor.execute('''INSERT INTO FILES(user, files) VALUES(:user, :files)''',{'user':mbeUserTemplate.format(level,sublevel), 'files':None})   


    db.commit()

def connect():
    while(1):
        cursor.execute('''SELECT ip FROM IP''')
        host=cursor.fetchone()[0]
        cursor.execute('''SELECT user, password FROM STATUS WHERE solved=0''')
        values=cursor.fetchone()
        user,password=values[0],values[1]
        print ("Connecting to "+ user +" with password "+ password)

        try:
            Conn=ssh(host=host,user=user,password=password)
            if Conn.connected():return Conn
            break
        except: 
            print('Wrong IP or password for the user, Please check IP or enter correct password')
            choice=int(raw_input("1.Enter IP\n2.Enter Password\n>>>").strip())
            if choice==1:
                fixIP(str(raw_input("Enter IP address of your MBE VM ")).strip())
            elif choice==2:
                fixPass(user)
    return Conn


try:
    cursor.execute('''SELECT ip FROM IP''')
except:
    generateDB(str(raw_input("Enter IP address of your MBE VM ")).strip())

while(1):
    conn=connect()

    datadir=('/levels/'+mbeLevelTemplate.format(conn.user[3])+'/')
    conn.set_working_directory(datadir)

    if(delfiles(conn.user)):
        print ("\nPrevious Files deleted\n")

    files=conn.ls().split()
    filelist=""
    for File in files:
        if conn.user in File:
            conn.download(datadir+File)
            filelist+=File+" "
    
    dbFiles(conn.user,filelist.strip())

    print("\nThe challenge files have been downloaded to the working directory\nPlease solve the challenge\n")
    print("Press any key to go interactive and solve the question on server\nOnce done check with whoami to see if you have escalated shell\n")
    raw_input("Run cat /home/"+getNextUser(conn.user)+"/.pass to get password for user "+getNextUser(conn.user)+"\n\nExit the interactive session and come save the password")

    conn.interactive()
    choice=raw_input("\n1.Enter password for next level\n2.I failed, lemme retry.\n3.Exit\n>>> ").strip()
    if choice=='1':
        solve(conn.user)
        delfiles(conn.user)
    elif choice=='3':break
    else: 
        conn.close()
        continue

db.close()
