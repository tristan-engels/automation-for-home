# File: scripts/forecast.py
from datetime import datetime, date
import os
import requests
from dateutil import parser as dateparser

# 1. Grob: API abrufen, Einträge filtern und formatieren

def get_forecast(api_key: str, city: str) -> dict:
    """Ruft die 5-Tage/3-Stunden-Vorhersage ab."""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": api_key, "units": "metric", "lang": "de"}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


def filter_today(forecast: dict) -> list[dict]:
    """Filtert nur die Forecast-Einträge für das heutige Datum."""
    today_str = date.today().isoformat()
    return [e for e in forecast.get("list", []) if e.get("dt_txt", "").startswith(today_str)]


def format_today(entries: list[dict], city: str, max_items: int = 5) -> str:
    """Formatiert die heutigen Forecast-Einträge als lesbaren Report."""
    heute = date.today().strftime("%d.%m.%Y")
    header = f"*Wettervorhersage für {city} am {heute}:*"
    if not entries:
        return header + "\nKeine Vorhersagedaten für heute."

    selected = entries[:max_items]
    lines = [header, ""]
    for e in selected:
        dt = datetime.fromisoformat(e["dt_txt"])
        desc = e["weather"][0]["description"].capitalize()
        temp = e["main"]["temp"]
        lines.append(f"{dt.hour:02d}:00 – {temp:.1f} °C, {desc}")
        lines.append("")  # Leerzeile nach jedem Eintrag
    return "\n".join(lines).rstrip()


def get_forecast_report(category: str = None, max_items: int = 5) -> str:
    """Wrapper, um config zu laden und Report zurückzugeben."""
    # .env laden
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OWM_API_KEY")
    city    = os.getenv("CITY", "Osterode am Harz,DE")
    if not api_key:
        raise RuntimeError("OWM_API_KEY fehlt in der Umgebung")

    forecast = get_forecast(api_key, city)
    entries  = filter_today(forecast)
    return format_today(entries, city, max_items)
