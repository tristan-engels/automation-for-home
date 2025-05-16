#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

def get_current_weather(api_key: str, city: str = "Osterode am Harz,DE") -> dict:
    url    = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "de"
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

def format_weather(data: dict) -> str:
    w     = data["weather"][0]
    m     = data["main"]
    wind  = data.get("wind", {})
    return (
        f"Wetter in {data['name']}:\n"
        f"• {w['description'].capitalize()}\n"
        f"• Temperatur: {m['temp']:.1f} °C (Min {m['temp_min']:.1f}, Max {m['temp_max']:.1f})\n"
        f"• Luftfeuchte: {m['humidity']} %\n"
        f"• Wind: {wind.get('speed', 0):.1f} m/s"
    )

def main():
    load_dotenv()  # lädt .env im Skript-Ordner
    key = os.getenv("OWM_API_KEY")
    if not key:
        print("Lege eine .env mit OWM_API_KEY=… an.")
        return

    try:
        weather = get_current_weather(key)
        print(format_weather(weather))
    except requests.HTTPError as e:
        print("Fehler beim Abruf:", e)

if __name__ == "__main__":
    main()
