import time
from datetime import datetime, timedelta
from django.utils.timezone import now
from . import utils
import board
import threading
import json
import os
from digitalio import DigitalInOut, Direction

# Konfiguracja GPIO dla diody LED (symulacja pompy wody)
water_pin = DigitalInOut(board.D27)  # Ustaw pin GPIO 27 jako wyjście
water_pin.direction = Direction.OUTPUT
water_pin.value = False  # Ustaw LED jako wyłączony na starcie

_thread_lock = threading.Lock()
_thread_started = False

JSON_FILE_PATH = os.path.join(os.path.dirname(__file__), "sensors.json")



def measure_parameters():
    """
    Funkcja uruchamiana w osobnym wątku, która monitoruje wilgotność i steruje podlewaniem.
    """

    time.sleep(5)

    global _thread_started

    with _thread_lock:
        if _thread_started:
            return
        _thread_started = True
        print("The thread has started!")
    while True:
        try:
            # Odczyt wilgotności gleby i powietrza
            humidity = utils.get_humidity()
            temp, air_humidity = utils.getTemperature()

            

            humidity = float(humidity.split(":")[-1].strip().replace(" %", ""))

                # Przygotowanie danych do zapisania
            sensor_data = {
                'temperature': temp,
                'air_moisture': air_humidity,
                'ground_moisture': humidity
            }

            # Zapisanie danych do pliku JSON
            with open(JSON_FILE_PATH, 'w') as json_file:
                json.dump(sensor_data, json_file)


            # Aktualizacja harmonogramu podlewania
            update_watering_schedule(humidity)

            # Logowanie odczytów
            print(f"[{datetime.now()}] Wilgotność gleby: {humidity}%")
            print(f"Temperatura: {temp:.1f}°C, Wilgotność powietrza: {air_humidity:.1f}%")

            # Wykonaj podlewanie, jeśli jest zaplanowane
            watering()

            # Opóźnienie między cyklami (60 sekund)
            time.sleep(60)

        except Exception as e:
            print(f"Błąd w measure_parameters: {e}")
            time.sleep(10)  # Odczekaj chwilę przed kolejną próbą


def update_watering_schedule(humidity):
    """
    Aktualizuje harmonogram podlewania na podstawie wilgotności gleby.
    """

    from .models import ScheduleEvent
    from .utils import load_settings, get_weather_data


    weather = get_weather_data()
    settings = load_settings()
    rain = int(weather["rain"])
    temp = float(weather["temperature"])

    try:
        humidity = float(humidity)  # Rzutowanie na float, jeśli to string
    except ValueError:
        print(f"Niepoprawna wartość wilgotności: {humidity}")
        return


    if humidity < int(settings["pump_efficiency"]) and not rain:
        print("Wilgotność gleby niska. Dodawanie wydarzenia podlewania.")
        ScheduleEvent.objects.create(
            title="Podlewanie",
            start=now(),
            end=now() + timedelta(seconds=30),
            status="extra"
        )
    elif humidity > 80 or (settings["disable_on_rain"] and rain >= settings["min_rain"]) or temp > settings["max_temp"]:
        print("Anulowanie wydarzeń podlewania.")
        ongoing_event = ScheduleEvent.objects.filter(
            start__lte=now(),
            end__gte=now(),
            status="planned"
        ).first()
        if ongoing_event:
            ongoing_event.status = "canceled"
            ongoing_event.save()
            print(f"Anulowano wydarzenie: {ongoing_event.title}")
        else:
            print("Brak wydarzeń do anulowania.")


def watering():
    """
    Uruchamia podlewanie, jeśli jest zaplanowane w harmonogramie.
    Czas podlewania jest określany jako różnica między 'end' a 'start'.
    """

    from .models import ScheduleEvent

    ongoing_events = ScheduleEvent.objects.filter(
        start__lte=now(),
        end__gte=now(),
        status__in=["extra", "planned"]
    )

    if ongoing_events.exists():
        for event in ongoing_events:
            duration = (event.end - event.start).total_seconds()  # Czas trwania w sekundach
            
            print(f"Podlewanie rozpoczęte dla wydarzenia: {event.title} (czas trwania: {duration} sekund).")
            start_watering()
            time.sleep(duration)  # Podlewanie przez czas trwania wydarzenia
            stop_watering()
            print(f"Podlewanie zakończone dla wydarzenia: {event.title}.")
    else:
        print("Brak zaplanowanego podlewania.")


def start_watering():
    """
    Symulacja włączenia pompy wody (dioda LED).
    """
    water_pin.value = True  # Włącz LED
    print("Pompa wody WŁĄCZONA.")


def stop_watering():
    """
    Symulacja wyłączenia pompy wody (dioda LED).
    """
    water_pin.value = False  # Wyłącz LED
    print("Pompa wody WYŁĄCZONA.")
