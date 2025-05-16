#!/usr/bin/env python3
import os
import json
import subprocess
import time
import logging
from dotenv import load_dotenv

# --- Konfiguration laden ---
load_dotenv()
SIGNAL_NUMBER = os.getenv("SIGNAL_NUMBER")            # z.B. "+49XXXX…"
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))  # Sekunden

# --- Logging konfigurieren ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

def extract_message(msg_obj) -> str:
    """
    Geht rekursiv durch dicts und lists und liefert die erste
    non-empty Zeichenkette unter einem Schlüssel 'message'.
    """
    if isinstance(msg_obj, dict):
        for k, v in msg_obj.items():
            if k == "message" and isinstance(v, str) and v.strip():
                return v.strip()
            # sonst tiefer suchen
            result = extract_message(v)
            if result:
                return result
    elif isinstance(msg_obj, list):
        for item in msg_obj:
            result = extract_message(item)
            if result:
                return result
    return ""

# --- Nachricht senden ---
def send_message(recipient: str, text: str):
    logger.debug(f"send_message → Empfänger: {recipient}")
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
    else:
        logger.info(f"Nachricht erfolgreich an {recipient}")

# --- Wetter abrufen ---
def get_weather_report() -> str:
    logger.debug("get_weather_report → führe weather-now.py aus")
    proc = subprocess.run(
        ["./weather-now.py"],
        capture_output=True,
        text=True
    )
    if proc.returncode == 0:
        logger.debug("weather-now.py lief erfolgreich")
        return proc.stdout.strip()
    else:
        logger.error(f"weather-now.py-Fehler: {proc.stderr.strip()}")
        return "Fehler beim Ausführen von weather-now.py."

# --- Main Loop ---
def main():
    last_ts = 0
    logger.info("Starte Signal-Bot (Polling alle %d s)", POLL_INTERVAL)

    while True:
        logger.debug("Polling: signal-cli receive --output=json")
        res = subprocess.run(
            ["signal-cli", "-u", SIGNAL_NUMBER, "--output=json", "receive"],
            capture_output=True, text=True
        )

        lines = res.stdout.splitlines()
        logger.debug("Raw receive: %d Zeilen", len(lines))

        for line in lines:
            logger.debug("Raw line: %s", line)
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                logger.warning("Konnte JSON nicht parsen")
                continue

            env    = msg.get("envelope", {})
            ts     = env.get("timestamp", 0)
            source = env.get("source")  # Absender

            # rekursiv nach 'message' suchen
            body = extract_message(msg)
            logger.debug("Empfangen: ts=%s, source=%s, body=%r", ts, source, body)

            # nur neue Nachrichten
            if ts <= last_ts:
                logger.debug("Ignoriere alte Nachricht")
                continue
            last_ts = ts

            # auf !wetter prüfen
            if body.lower().startswith("!wetter"):
                logger.info("!wetter erkannt von %s", source)
                report = get_weather_report()
                send_message(source, report)
            else:
                logger.debug("Nicht !wetter, überspringe")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
