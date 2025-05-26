# mail_utils.py

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from imapclient import IMAPClient
from email.header import decode_header

# .env einmal beim Import laden
load_dotenv()

HOST = 'imap.gmail.com'
USERNAME = os.getenv('GMAIL_USER')
APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')

def fetch_unread_senders_last_days(days: int = 3) -> list[tuple[str|None, str]]:
    """
    Ruft alle ungelesenen Mails der letzten `days` Tage ab
    und gibt eine Liste von (Absendername, Betreff) zurück.
    Absendername ist None, falls nicht gesetzt.
    """
    if not USERNAME or not APP_PASSWORD:
        raise RuntimeError("Bitte GMAIL_USER und GMAIL_APP_PASSWORD in der .env definieren!")

    since_date = (datetime.now() - timedelta(days=days)).date()
    since_str  = since_date.strftime('%d-%b-%Y')

    with IMAPClient(HOST, ssl=True) as client:
        client.login(USERNAME, APP_PASSWORD)
        client.select_folder('INBOX')

        # Suche nur ungelesene, neue Mails
        uids = client.search(['UNSEEN', 'SINCE', since_str])
        entries: list[tuple[str|None, str]] = []
        if not uids:
            return entries

        data = client.fetch(uids, ['ENVELOPE'])
        for uid, msg in data.items():
            env = msg[b'ENVELOPE']

            # Betreff dekodieren
            raw_subj = env.subject or b''
            subj_part, encoding = decode_header(raw_subj.decode('utf-8', errors='ignore'))[0]
            if isinstance(subj_part, bytes):
                subj = subj_part.decode(encoding or 'utf-8', errors='replace')
            else:
                subj = subj_part

            # Absendername (falls vorhanden)
            name = None
            if env.from_:
                addr = env.from_[0]
                raw_name = addr.name
                if raw_name:
                    name = raw_name.decode() if isinstance(raw_name, bytes) else raw_name

            entries.append((name, subj))

        return entries
