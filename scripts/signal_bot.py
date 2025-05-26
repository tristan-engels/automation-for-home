#!/usr/bin/env python3
import os
import json
import subprocess
import time
import logging
from dotenv import load_dotenv
from scripts.weather import get_weather_report
from scripts.weather_forecast import get_forecast_report
from scripts.news_aggregator import get_news_report
from scripts.fetch_mail import fetch_unread_senders_last_days
from scripts.markasread_mail import mark_all_read

# Konfiguration laden
load_dotenv()
SIGNAL_NUMBER = os.getenv("SIGNAL_NUMBER")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))

# Logging konfigurieren
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

def extract_message(msg_obj) -> str:
    """
    Sucht rekursiv nach dem ersten nicht-leeren 'message'-Feld in einem JSON-Objekt.
    """
    if isinstance(msg_obj, dict):
        for k, v in msg_obj.items():
            if k == "message" and isinstance(v, str) and v.strip():
                return v.strip()
            result = extract_message(v)
            if result:
                return result
    elif isinstance(msg_obj, list):
        for item in msg_obj:
            result = extract_message(item)
            if result:
                return result
    return ""

def send_message(recipient: str, text: str):
    """
    Sendet eine Nachricht per signal-cli.
    """
    logger.debug(f"Sendet Nachricht an {recipient!r}: {text!r}")
    cmd = [
        "signal-cli",
        "-u", SIGNAL_NUMBER,
        "send",
        "-m", text,
        recipient
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        logger.error(f"Fehler beim Senden an {recipient}: {res.stderr.strip()}")

# --- Einzelne Befehle ---

def handle_wetter(recipient: str):
    report = get_weather_report()
    send_message(recipient, report)

def handle_wetter_vorhersage(recipient: str):
    report = get_forecast_report()
    send_message(recipient, report)

def handle_news(recipient: str, body_lower: str):
    parts = body_lower.split(maxsplit=1)
    if len(parts) < 2:
        send_message(
            recipient,
            "⚠️ Bitte Kategorie angeben: `!news weltweit|deutschland|it|it-security`"
        )
    else:
        category = parts[1].strip()
        logger.debug("!news %s erkannt von %s", category, recipient)
        report = get_news_report(category)
        send_message(recipient, report)

def handle_email_neu(recipient: str):
    if recipient != SIGNAL_NUMBER:
        send_message(recipient, "❌ Du bist dafür nicht autorisiert.")
        return

    entries = fetch_unread_senders_last_days(days=3)
    if not entries:
        report = "Keine ungelesenen Mails in den letzten 3 Tagen."
    else:
        lines = [
            f"{i + 1}. {name + ' – ' if name else ''}{subj}"
            for i, (name, subj) in enumerate(entries)
        ]
        report = "Ungelesene Mails der letzten 3 Tage:\n" + "\n".join(lines)
    send_message(recipient, report)

def handle_email_read(recipient: str):
    if recipient != SIGNAL_NUMBER:
        send_message(recipient, "❌ Du bist dafür nicht autorisiert.")
        return

    try:
        count = mark_all_read()
        if count == 0:
            send_message(recipient, "📭 Keine ungelesenen Mails gefunden.")
        else:
            send_message(recipient, f"✅ {count} ungelesene Mail(s) als gelesen markiert.")
    except Exception as e:
        # Optional: logge den Fehler auf deinem Server
        send_message(recipient, f"⚠️ Fehler beim Markieren der Mails: {e}")

# --- Haupt-Loop ---

def main():
    last_ts = 0
    logger.info("Starte Signal-Bot (Polling alle %d s)", POLL_INTERVAL)

    while True:
        res = subprocess.run(
            ["signal-cli", "-u", SIGNAL_NUMBER, "--output=json", "receive"],
            capture_output=True, text=True
        )

        for line in res.stdout.splitlines():
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

            env = msg.get("envelope", {})
            ts = env.get("timestamp", 0)
            source = env.get("source")
            body = extract_message(msg)
            body_lower = body.lower()

            # nur neue Nachrichten verarbeiten
            if ts <= last_ts:
                continue
            last_ts = ts

            logger.info("Eingang von %s: %r", source, body)

            # Befehlserkennung
            if body_lower.startswith("!wetter-vorhersage"):
                logger.debug("!wetter-vorhersage erkannt von %s", source)
                handle_wetter_vorhersage(source)
            elif body_lower.startswith("!wetter"):
                logger.debug("!wetter erkannt von %s", source)
                handle_wetter(source)
            elif body_lower.startswith("!news"):
                handle_news(source, body_lower)
            elif body_lower.startswith("!email-neu"):
                logger.debug("!email-neu erkannt von %s", source)
                handle_email_neu(source)
            elif body_lower.startswith("!email-lesen"):
                logger.debug("!email-lesen erkannt von %s", source)
                handle_email_read(source)    

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
