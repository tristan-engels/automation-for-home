# fetch_senders_last3days.py
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from imapclient import IMAPClient
from email.header import decode_header

# .env einlesen
load_dotenv()

HOST = 'imap.gmail.com'
USERNAME = os.getenv('GMAIL_USER')
APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')

if not USERNAME or not APP_PASSWORD:
    raise RuntimeError("Bitte GMAIL_USER und GMAIL_APP_PASSWORD in der .env definieren!")

# Datum für „letzte 3 Tage“
since_date = (datetime.now() - timedelta(days=3)).date()
since_str = since_date.strftime('%d-%b-%Y')

with IMAPClient(HOST, ssl=True) as client:
    client.login(USERNAME, APP_PASSWORD)
    client.select_folder('INBOX')

    # Suche: ungelesen & seit vor 3 Tagen
    uids = client.search(['UNSEEN', 'SINCE', since_str])
    print(f'Anzahl ungelesener Mails seit {since_str}: {len(uids)}')

    if not uids:
        exit(0)

    # Sendername & Betreff holen
    entries = []
    response = client.fetch(uids, ['ENVELOPE'])
    for uid, data in response.items():
        env = data[b'ENVELOPE']

        # Betreff dekodieren
        raw_subj = env.subject or b''
        subj, enc = decode_header(raw_subj.decode('utf-8', errors='ignore'))[0]
        if isinstance(subj, bytes):
            subj = subj.decode(enc or 'utf-8', errors='replace')

        # Absendername ermitteln (erstes from_-Element)
        name = None
        if env.from_:
            addr = env.from_[0]
            if addr.name:
                name = addr.name.decode() if isinstance(addr.name, bytes) else addr.name

        entries.append((name, subj))

    # Ausgabe
    print("\nUngelesene Mails der letzten 3 Tage:")
    for i, (name, subj) in enumerate(entries, 1):
        if name:
            print(f"{i}. {name} – {subj}")
        else:
            print(f"{i}. {subj}")
