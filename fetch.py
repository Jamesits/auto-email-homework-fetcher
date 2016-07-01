#!/usr/bin/env python3

import getpass, poplib, configparser

# read config
config = configparser.ConfigParser()
config.read('config.ini')

M = poplib.POP3_SSL(config['mailbox']['server'], port=config['mailbox']['port'])
M.user(config['mailbox']['username'])
M.pass_(config['mailbox']['password'])
numMessages = len(M.list()[1])
for i in range(numMessages):
    for j in M.retr(i+1)[1]:
        print(j)
M.quit()
