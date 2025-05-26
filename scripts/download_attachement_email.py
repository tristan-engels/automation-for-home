#!/usr/bin/env python3
# download_pdfs_since.py

import os
import email
from datetime import datetime, timedelta
from dotenv import load_dotenv
from imapclient import IMAPClient

# ————— Konfiguration —————
load_dotenv()  # lädt GMAIL_USER, GMAIL_APP_PASSWORD, ATTACHMENTS_DIR, PROCESSED_FILE, DAYS_BACK aus .env

HOST         = 'imap.gmail.com'
USERNAME     = os.getenv('GMAIL_USER')
APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
ATTACH_DIR   = os.getenv('ATTACHMENTS_DIR', 'anhaenge')
PROCESSED    = os.getenv('PROCESSED_FILE', 'processed_uids.txt')
DAYS_BACK    = int(os.getenv('DAYS_BACK', '3'))

if not USERNAME or not APP_PASSWORD:
    raise RuntimeError("Bitte GMAIL_USER und GMAIL_APP_PASSWORD in der .env definieren!")

# Zielordner anlegen
os.makedirs(ATTACH_DIR, exist_ok=True)

# Bereits verarbeitete UIDs laden
processed = set()
if os.path.exists(PROCESSED):
    with open(PROCESSED, 'r') as f:
        processed = {line.strip() for line in f if line.strip()}

# Datum X Tage zurück
since = (datetime.now() - timedelta(days=DAYS_BACK)).date().strftime('%d-%b-%Y')

with IMAPClient(HOST, ssl=True) as client:
    client.login(USERNAME, APP_PASSWORD)
    client.select_folder('INBOX')

    # Suche ALLE Mails seit dem Datum
    uids = client.search(['ALL', 'SINCE', since])
    print(f"Gefundene Mails seit {since}: {len(uids)}")

    new_processed = set()
    for uid in uids:
        uid_str = str(uid)
        if uid_str in processed:
            continue

        # kompletten Rohinhalt holen
        data = client.fetch([uid], ['RFC822'])[uid]
        msg = email.message_from_bytes(data[b'RFC822'])

        saved_any = False
        # über alle Teile iterieren – egal welchen Content-Type
        for part in msg.walk():
            filename = part.get_filename()
            if not filename:
                continue

            # Header-dekodierung der Filename (falls nötig)
            decoded_name, enc = email.header.decode_header(filename)[0]
            if isinstance(decoded_name, bytes):
                filename = decoded_name.decode(enc or 'utf-8', errors='ignore')
            else:
                filename = decoded_name

            # nur PDF-Endung akzeptieren
            if not filename.lower().endswith('.pdf'):
                continue

            # Pfad und Duplikat-Schutz
            target = os.path.join(ATTACH_DIR, filename)
            if os.path.exists(target):
                print(f"→ {uid} Überspringe vorhandene Datei {filename}")
            else:
                with open(target, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                print(f"→ {uid} Gespeichert: {filename}")
            saved_any = True

        # erst nach tatsächlichem Speichern markieren
        if saved_any:
            new_processed.add(uid_str)

    # neue UIDs in processed-file schreiben
    if new_processed:
        with open(PROCESSED, 'a') as f:
            for u in new_processed:
                f.write(u + "\n")
        print(f"{len(new_processed)} Mail(s) als verarbeitet dokumentiert in {PROCESSED}")

print("Fertig.")
