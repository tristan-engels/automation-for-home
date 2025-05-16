# fetch_subjects_last3days.py
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

    # Betreffzeilen holen
    subjects = []
    response = client.fetch(uids, ['ENVELOPE'])
    for uid, data in response.items():
        envelope = data[b'ENVELOPE']
        raw_subj = envelope.subject or b''
        # raw_subj ist bytes, evtl. encodiert – daher dekodieren
        decoded = decode_header(raw_subj.decode('utf-8', errors='ignore'))[0][0]
        if isinstance(decoded, bytes):
            try:
                decoded = decoded.decode('utf-8')
            except:
                decoded = decoded.decode('latin-1', errors='replace')
        subjects.append(decoded)

    # Liste ausgeben
    print("Betreff:")
    for i, subj in enumerate(subjects, 1):
        print(f"{i}. {subj}")
