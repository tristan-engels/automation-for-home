#!/usr/bin/env python3
import os
import requests
import subprocess
from datetime import datetime, date
from dotenv import load_dotenv

def get_forecast(api_key: str, city: str) -> dict:
    """Ruft die 5-Tage/3-Stunden-Vorhersage ab."""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "de"
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

def filter_today(forecast: dict) -> list[dict]:
    """Filtert nur die Forecast-Einträge für das heutige Datum."""
    today_str = date.today().isoformat()
    return [
        entry for entry in forecast["list"]
        if entry["dt_txt"].startswith(today_str)
    ]

def format_today(entries: list[dict], city: str) -> str:
    """Formatiert die heutigen Forecast-Einträge als lesbaren Text."""
    heute = date.today().strftime("%d.%m.%Y")
    if not entries:
        return f"Guten Morgen! Für {city} am {heute} liegen keine Vorhersagedaten vor."
    lines = [f"Guten Morgen! Die Wettervorhersage für {city} am {heute}:"]
    for e in entries:
        dt   = datetime.fromisoformat(e["dt_txt"])
        desc = e["weather"][0]["description"].capitalize()
        temp = e["main"]["temp"]
        lines.append(f"  • {dt.hour:02d}:00 – {temp:.1f} °C, {desc}")
    return "\n".join(lines)

def send_via_signal(message: str, signal_number: str):
    """Schickt die Nachricht als Note-to-Self via signal-cli."""
    cmd = [
        "signal-cli",
        "-u", signal_number,
        "send",
        "--note-to-self",
        "-m", message
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Fehler beim Senden:", res.stderr)
    else:
        print("✅ Nachricht per Signal verschickt.")

def main():
    load_dotenv()
    api_key       = os.getenv("OWM_API_KEY")
    city          = os.getenv("CITY", "Osterode am Harz,DE")
    signal_number = os.getenv("SIGNAL_NUMBER")

    if not api_key:
        print("Bitte setze OWM_API_KEY in der .env.")
        return
    if not signal_number:
        print("Bitte setze SIGNAL_NUMBER in der .env.")
        return

    try:
        forecast   = get_forecast(api_key, city)
        today_data = filter_today(forecast)
        message    = format_today(today_data, city)
        print(message)  # zur Kontrolle in der Konsole
        send_via_signal(message, signal_number)
    except requests.HTTPError as e:
        print("Fehler beim Abruf der Vorhersage:", e)

if __name__ == "__main__":
    main()
