#!/usr/bin/env python3

import getpass, poplib, configparser, sqlite3

conn = sqlite3.connect('data.db')

# initialize db

c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS mailbox
             (ID INTEGER PRIMARY KEY, octets INTEGER, received INTEGER NOT NULL DEFAULT 0, title TEXT, content BLOB)''')
conn.commit()

# read config
config = configparser.ConfigParser()
config.read('config.ini')

# fetch mail
M = poplib.POP3_SSL(config['mailbox']['server'], port=config['mailbox']['port'])
M.user(config['mailbox']['username'])
M.pass_(config['mailbox']['password'])
M.getwelcome()
maillist = [tuple(x.decode('utf-8').split(" ")) for x in M.list()[1]]
print(maillist)
c.executemany('INSERT OR IGNORE INTO mailbox (ID, octets) VALUES (?,?)', maillist)
conn.commit()

# clean up
conn.close()
M.quit()
