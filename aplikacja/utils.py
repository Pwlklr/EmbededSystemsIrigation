import requests
from django.conf import settings
import json
import os
import adafruit_dht
import board
import time
import serial

# Ścieżka do pliku ustawień
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

sensor = adafruit_dht.DHT11(board.D17)


# Funkcja do pobierania danych o pogodzie
def get_weather_data():
    # Użyj swojego klucza API, który otrzymałeś z OpenWeatherMap
    settings = load_settings()  # Załaduj ustawienia z pliku settings.json
    api_key = settings.get("OPENWEATHER_API_KEY")  # Pobierz klucz API
    city = settings.get("city")
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    
    # Tworzenie pełnego URL z nazwą miasta i kluczem API
    url = f"{base_url}q={city}&appid={api_key}&units=metric&lang=pl"

    # Wykonaj zapytanie GET do API
    response = requests.get(url)
    
    # Jeśli odpowiedź jest poprawna (status 200)
    if response.status_code == 200:
        data = response.json()
        
        # Wydobywanie interesujących danych z odpowiedzi
        weather = {
            'city': data['name'],
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'rain': data.get('rain', {}).get('1h', 0)
        }
        
        return weather
    else:
        # Jeśli wystąpił błąd (np. złe miasto)
        return None
    

    
def load_settings():
    """Ładuje ustawienia z pliku settings.json."""
    try:
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Plik ustawień {SETTINGS_FILE} nie został znaleziony.")
    
    except json.JSONDecodeError:
        raise ValueError(f"Plik ustawień {SETTINGS_FILE} jest uszkodzony lub zawiera nieprawidłowe dane.")

def save_settings(settings):
    """Zapisuje ustawienia do pliku settings.json."""
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)

def getTemperature():
    # Ustawienie typu czujnika (DHT11) i pinu GPIO (GPIO 17)

    temperature_c = sensor.temperature
    humidity = sensor.humidity

    if humidity is not None and temperature_c is not None:
        return temperature_c, humidity
    else:
        return "Error"


def get_humidity():
    # Otwórz port szeregowy, aby komunikować się z Arduino
    arduino = serial.Serial('/dev/ttyUSB0', 9600)  # Ustaw odpowiedni port i prędkość (9600)
    time.sleep(2)  # Poczekaj chwilę, aż Arduino się zainicjalizuje

    while True:
        # Sprawdź, czy dane są dostępne do odczytu
        if arduino.in_waiting > 0:
            # Odczytaj dane z portu szeregowego
            data = arduino.readline().decode('utf-8').strip()

            # Sprawdź, czy dane zawierają wilgotność
            if "Wilgotność gleby:" in data:
                # Odczytaj wilgotność
                return data

        time.sleep(1)  # Sprawdź co 1 sekundę

