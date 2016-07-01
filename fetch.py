#!/usr/bin/env python3

import getpass, poplib, configparser, sqlite3, email, re, os, sys, time
from email.header import decode_header

email_extractor = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")

# read config
config = configparser.ConfigParser()
config.read('config.ini')
dir_dict = {}
for i in [x.strip() for x in config['config']['tasks'].split(",")]:
    os.makedirs(os.path.join(config['config']['base_folder'], config[i]['folder']), exist_ok=True)
    dir_dict.update({config[i]['receiver']: config[i]['folder']})
interval = int(config['config']['check_interval'])

# initialize db
conn = sqlite3.connect(config['config']['db_path'])
print("Initializating database...", file=sys.stderr)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS mailbox
             (ID INTEGER PRIMARY KEY, octets INTEGER, received INTEGER NOT NULL DEFAULT 0, sender TEXT, receiver TEXT, time TEXT, subject TEXT)''')
conn.commit()


def refresh_mail():
    # fetch mailbox
    print("Connecting to POP3 server...", file=sys.stderr, end="")
    M = poplib.POP3_SSL(config['mailbox']['server'], port=config['mailbox']['port'])
    M.user(config['mailbox']['username'])
    M.pass_(config['mailbox']['password'])
    print(M.getwelcome().decode(), file=sys.stderr)
    maillist = [tuple(x.decode('utf-8').split(" ")) for x in M.list()[1]]
    c.executemany('INSERT OR IGNORE INTO mailbox (ID, octets) VALUES (?,?)', maillist)
    conn.commit()

    # fetch mails
    print("Fetching mails...", file=sys.stderr)
    for id in [x[0] for x in c.execute('SELECT * FROM mailbox WHERE received = 0')]:
        try:
            print("  Fetching mail #%d" % id, file=sys.stderr)
            msg = b"\n".join(M.retr(id)[1])
            e = email.message_from_bytes(msg)

            def parse(data):
                """Decode encoded mail content"""
                data = decode_header(data)
                if isinstance(data, list):
                    data = "".join(x[0] if isinstance(x[0], str) else x[0].decode() if x[1] == None else x[0].decode(x[1]) for x in data)
                return data

            sender = email_extractor.findall(parse(e.get("From")))
            sender = sender[0] if sender else ""
            receiver = email_extractor.findall(parse(e.get("To")))
            receiver = receiver[0] if receiver else ""
            date = parse(e.get("Date"))
            subject = parse(e.get("Subject"))
            if receiver in dir_dict:
                # Download all attachments
                for part in e.walk():
                    c_type = part.get_content_type()
                    c_disp = part.get('Content-Disposition')
                    if c_type != 'text/plain' and c_disp != None and part.get_filename():
                        filename = parse(part.get_filename())
                        file = part.get_payload(decode=True)
                        print("    Saving attachment %s" % filename, file=sys.stderr)
                        open(os.path.join(config['config']['base_folder'], dir_dict[receiver], filename), 'wb').write(file)
            c.execute('UPDATE mailbox SET received=1, sender=?, receiver=?, time=?, subject=? WHERE ID = ?', (sender, receiver, date, subject, id))
            conn.commit()
        except KeyError:
            print("Unable to decode message.", file=sys.stderr)

    # clean up
    conn.commit()
    M.quit()

if __name__ == "__main__":
    if not interval:
        refresh_mail()
    else:
        while True:
            try:
                refresh_mail()
                print("Sleeping %d seconds." % interval, file=sys.stderr)
                time.sleep(interval)
            except KeyboardInterrupt:
                print("Quitting...", file=sys.stderr)
                break

    conn.close()
