# scripts/weather.py
import os
import sys
import subprocess
import logging

logger = logging.getLogger(__name__)

def get_weather_report() -> str:
    """
    Ruft das weather-now.py im selben Verzeichnis auf.
    """
    # Verzeichnis dieses Moduls
    script_dir = os.path.dirname(os.path.abspath(__file__))
    weather_script = os.path.join(script_dir, "weather-now.py")

    # Stelle sicher, dass wir mit deinem Python-Interpreter starten
    cmd = [sys.executable, weather_script]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode == 0:
        return proc.stdout.strip()
    else:
        logger.error(f"weather-now.py-Fehler: {proc.stderr.strip()}")
        return "⚠️ Fehler beim Abrufen des Wetters."
