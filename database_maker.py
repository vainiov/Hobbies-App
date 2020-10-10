#-*- coding: utf-8 -*-
import sqlite3
from datetime import datetime

conn=sqlite3.connect("HobbiesDatabase3.db")
cursor=conn.cursor()
    
'''
cursor.execute("""CREATE TABLE IF NOT EXISTS Players(
    age INTEGER NOT NULL,
    sex TEXT NOT NULL,
    name TEXT NOT NULL,
    bio TEXT NOT NULL, 
    password NULL,
    number INTEGER PRIMARY KEY,
    photo TEXT);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS Events(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    header TEXT NOT NULL,
    sport TEXT NOT NULL, 
    place TEXT NOT NULL,
    city TEXT NOT NULL,
    time TEXT NOT NULL,
    description TEXT NOT NULL,
    limits INTEGER,
    num INTEGER,
    creatorid INTEGER);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS PartIn(
    playerid INTEGER NOT NULL,
    eventid INTEGER NOT NULL);""")


cursor.execute("""INSERT into Events values(NULL,'Höntsä jalkapalloa tänään Brakulla klo 19','Jalkapallo', 
    'Brahenkenttä', 'Helsinki', '19:00', 'Höntsäfutista tänään Brakulla. Tehdään sekajengit eikä tarvitse olla pro.
     Ei tarvitse nappiksia mutta voi toki myös ottaa.',10, 1 ,555)""")
    
    
cursor.execute("""INSERT into Players values(22, 'Male', 'Vertti', 'Harrastanut jalkapalloa lapsena 7 vuotta', 
'vertti', 555, 'default.png')""")


cursor.execute("""INSERT into Events values(
    NULL,
    'Pesispeli Meilahdessa klo 20',
    'Pesäpallo', 
    'Meilahden pesiskenttö',
    'Helsinki', 
    '20:00', 
    'Höntsä pesispeli tänään Meilahden kentällä, ei tarvitse olla pro mutta joskus edes pelannut',
     10,
     1,
     555)""")

cursor.execute("""INSERT into PartIn values(555,1)""")
cursor.execute("""INSERT into PartIn values(555,2)""")
    
cursor.execute("""INSERT into Players values(21, 'Female', 'Sofia', 'Tanssija sekä yleisesti urheilullinen', 
'sofia', 111, 'default.png')""")


for i in range(5):
    cursor.execute("""INSERT into Events values(NULL,'Höntsä jalkapalloa tänään Brakulla klo 19','Jalkapallo', 
        'Brahenkenttä', 'Helsinki', '19:00', 'Höntsäfutista tänään Brakulla. Tehdään sekajengit eikä tarvitse olla pro.
         Ei tarvitse nappiksia mutta voi toki myös ottaa.',10, 1 ,111)""")
    cursor.execute("""INSERT into PartIn values(111,?)""",(3+i,))



cursor.execute("""DELETE * from partin where playerid=999""")



conn.commit()

conn.close()
'''

def sql_query(q, args=None, commit=False, get_id=False):
    if args is None:
        args = []
    for attempt in range(10):
        try:
            con = sqlite3.connect("HobbiesDatabase3.db")
            cur = con.cursor()
            cur.execute(q, args)
            ans = cur.fetchall()
            if commit:
                con.commit()
            if get_id:
                ans=cur.lastrowid
            cur.close()
            con.close()
            del cur
            del con
            return ans
        except sqlite3.IntegrityError:
            return 2
        except sqlite3.OperationalError:
            time.sleep(3)
        
    return None


events=sql_query("SELECT * FROM Events;")
for i in events:
    print(i)






