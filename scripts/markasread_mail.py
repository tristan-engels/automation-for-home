# mark_all_read.py
import os
from dotenv import load_dotenv
from imapclient import IMAPClient

def mark_all_read(
    host: str = None,
    username: str = None,
    password: str = None,
    folder: str = 'INBOX',
    batch_size: int = 500
) -> int:
 
    load_dotenv()
    host = host or 'imap.gmail.com'
    username = username or os.getenv('GMAIL_USER')
    password = password or os.getenv('GMAIL_APP_PASSWORD')

    if not username or not password:
        raise RuntimeError(
            "Bitte GMAIL_USER und GMAIL_APP_PASSWORD in der .env definieren!"
        )

    with IMAPClient(host, ssl=True) as client:
        client.login(username, password)
        client.select_folder(folder)

        # Alle ungelesenen UIDs abfragen
        uids = client.search(['UNSEEN'])
        print(f'Gefundene ungelesene Mails: {len(uids)}')

        if not uids:
            return 0

        # In Chargen teilen
        for i in range(0, len(uids), batch_size):
            batch = uids[i:i + batch_size]
            client.add_flags(batch, '\\Seen')

        print("Alle ungelesenen Mails wurden als gelesen markiert.")
        return len(uids)


if __name__ == '__main__':
    # Direktaufruf erlaubt: gibt die Anzahl der markierten Mails zurück
    count = mark_all_read()
    if count == 0:
        print("Keine ungelesenen Mails zum Markieren.")
    else:
        print(f"{count} Mails wurden als gelesen markiert.")
