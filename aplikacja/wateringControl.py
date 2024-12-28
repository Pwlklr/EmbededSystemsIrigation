import time
from datetime import datetime
from django.utils.timezone import now
from datetime import timedelta
#Nie dziala na kali linuxie do przetestowania z raspberry 
#import RPi.GPIO as GPIO  # Import GPIO for Raspberry Pi (replace if using other hardware)
#ALTERNATYWNE DO TESTOWANIA
from gpiozero import LED

# Konfiguracja GPIO -> przy powroce do RPi.GPIO USUNAC LED() -> 17
WATER_PIN = LED(17)  # GPIO pin controlling the water pump or valve


# GPIO.setmode(GPIO.BCM)
# GPIO.setup(WATER_PIN, GPIO.OUT)
# GPIO.output(WATER_PIN, GPIO.LOW)  # Upewnij się, że pompa jest wyłączona na początku

def measure_parameters():
    while True:
        # Symulacja odczytu danych z sensorów
        humidity = get_humidity()
        
        # Aktualizacja danych w bazie danych (przykładowo kalendarza)
        update_watering_schedule(humidity)
        
        # Logowanie
        print(f"[{datetime.now()}] Wilgotność: {humidity}% - Sprawdzono")
        watering()
        # Odczekaj 60 sekund przed kolejnym odczytem
        time.sleep(60)

def get_humidity():
    # Przykład odczytu z sensora (zastąp odpowiednim kodem)
    return 40  # Zwróć procentową wilgotność

def update_watering_schedule(humidity):
    from aplikacja.models import ScheduleEvent  # Załaduj model Django
    if humidity < 30:
        print("Wilgotność niska, dodaj wydarzenie podlewania.")
        # Dodaj logikę modyfikującą kalendarz
        ScheduleEvent.objects.create(
            title="Podlewanie",
            start=now(),
            end=now() + timedelta(seconds=30),
            status="extra"
        )
    elif humidity > 70:
        print("Wilgotność wysoka, anulowanie podlewania.")
        # Zmień istniejące wydarzenia
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
            print("Brak zaplanowanego wydarzenia do anulowania.")

def watering():
    #watering if scheduled or too dry
    from aplikacja.models import ScheduleEvent
    # Pobierz wydarzenia podlewania zaplanowane na teraz
    ongoing_events = ScheduleEvent.objects.filter(
        start__lte=now(),
        end__gte=now(),
        status__in=["extra", "planned"]
    )

    if ongoing_events.exists():
        print("Podlewanie rozpoczęte.")
        start_watering()
        time.sleep(30)  # Czas trwania podlewania w sekundach
        stop_watering()
        print("Podlewanie zakończone.")
    else:
        print("Brak zaplanowanego podlewania.")

def start_watering():
    """Symulacja włączenia pompy wody."""
    WATER_PIN.on()
    print("Pompa wody WŁĄCZONA.")

def stop_watering():
    """Symulacja wyłączenia pompy wody."""
    WATER_PIN.off()
    print("Pompa wody WYŁĄCZONA.")