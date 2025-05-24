# mark_all_read.py
import os
from dotenv import load_dotenv
from imapclient import IMAPClient

# .env einlesen
load_dotenv()
HOST = 'imap.gmail.com'
USERNAME = os.getenv('GMAIL_USER')
APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')

if not USERNAME or not APP_PASSWORD:
    raise RuntimeError("Bitte GMAIL_USER und GMAIL_APP_PASSWORD in der .env definieren!")

with IMAPClient(HOST, ssl=True) as client:
    client.login(USERNAME, APP_PASSWORD)
    client.select_folder('INBOX')

    # Alle ungelesenen UIDs abfragen
    uids = client.search(['UNSEEN'])
    print(f'Gefundene ungelesene Mails: {len(uids)}')

    if not uids:
        print("Keine ungelesenen Mails zum Markieren.")
        exit(0)

    # In Chargen teilen, z.B. 500 UIDs pro STORE-Kommando
    BATCH_SIZE = 500
    for i in range(0, len(uids), BATCH_SIZE):
        batch = uids[i:i + BATCH_SIZE]
        # richtigen Flag-String übergeben
        client.add_flags(batch, '\\Seen')

    print("Alle ungelesenen Mails wurden als gelesen markiert.")
