from django.shortcuts import render, redirect
from . import models
from . import utils
from django.utils.dateparse import parse_datetime
from django.contrib import admin
import requests
from django.conf import settings
import datetime

def test_view(request):
    return render(request, 'test_page.html', {'message': 'To jest przykładowa strona testowa!'})

def home_view(request):
    return render(request, 'home_page.html')

def delete_events(request):
    if request.method == 'POST':
        date_to_delete = request.POST.get('date_to_delete')
        cycle = int(request.POST.get('recurrence_interval'))
        date_to_delete = datetime.datetime.strptime(date_to_delete, '%Y-%m-%d').date()

        end_of_cycle = date_to_delete.replace(year=date_to_delete.year+1, month=date_to_delete.month, day=date_to_delete.day)

        if cycle > 0:  # Create recurring events if cycle is greater than 0
            while date_to_delete < end_of_cycle:
                models.ScheduleEvent.objects.filter(start__date=date_to_delete).delete()
                date_to_delete += datetime.timedelta(days=cycle)
        else:
            models.ScheduleEvent.objects.filter(start__date=date_to_delete).delete()
    return redirect('schedule')  # Redirect to the schedule page


def schedule_view(request):
    if request.method == 'POST':
        # Pobierz dane z formularza
        date = request.POST.get('date')
        time = request.POST.get('time')
        cycle = int(request.POST.get('recurrence_interval'))
        duration = int(request.POST.get('duration'))

        # Przelicz czas rozpoczęcia i zakończenia
        start = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end = start + datetime.timedelta(minutes=duration)

        end_of_cycle = start.replace(year=start.year+1, month=start.month, day=start.day)


        # Zapisz wydarzenie w bazie danych
        if cycle > 0:  # Create recurring events if cycle is greater than 0
            while start < end_of_cycle:
                models.ScheduleEvent.objects.create(start=start, end=end)
                start += datetime.timedelta(days=cycle)
                end = start + datetime.timedelta(minutes=duration)
        else:  # Create a single event if cycle is 0
            models.ScheduleEvent.objects.create(start=start, end=end)
            
        # Przekieruj na tę samą stronę, by odświeżyć widok
        return redirect('schedule')

    events = models.ScheduleEvent.objects.all()
    events_json = [{
    'title': event.title,
    'start': event.start.isoformat(),
    'end': event.end.isoformat()
    } for event in events]

    print(f"Events_debug{events_json}")

    return render(request, 'schedule_page.html', {'events': events_json})

def settings_view(request):
    try:
        settings = utils.load_settings()
    except FileNotFoundError:
        return render(
            request,
            "error.html",
            {"message": "Plik ustawień nie został znaleziony. Skontaktuj się z administratorem."},
        )
    except ValueError:
        return render(
            request,
            "error.html",
            {"message": "Plik ustawień jest uszkodzony. Skontaktuj się z administratorem."},
        )

    if request.method == "POST":
        try:
            # Aktualizacja ustawień z formularza
            settings["pump_efficiency"] = float(request.POST.get("pump_efficiency", settings["pump_efficiency"]))
            settings["city"] = request.POST.get("city", settings["city"])
            settings["watering_duration"] = int(request.POST.get("watering_duration", settings["watering_duration"]))
            settings["min_rain"] = float(request.POST.get("min_rain", settings.get("min_rain", 0)))
            settings["disable_on_rain"] = request.POST.get("disable_on_rain", "false") == "true"
            settings["max_temp"] = float(request.POST.get("max_temp", settings.get("max_temp", 35)))
            settings["OPENWEATHER_API_KEY"] = request.POST.get("openweather_api_key", settings["OPENWEATHER_API_KEY"])

            # Zapis ustawień
            utils.save_settings(settings)
            return redirect("settings")
        except (ValueError, TypeError) as e:
            # Jeśli coś poszło nie tak, zwróć błąd na stronie
            return render(
                request,
                "error.html",
                {"message": f"Niepoprawne dane w formularzu: {e}. Sprawdź i spróbuj ponownie."},
            )

    return render(request, "settings_page.html", {"settings": settings})


def weather_view(request):
    weather_data = utils.get_weather_data()
    
    return render(request, 'weather_page.html', {'weather': weather_data})

def sensor_view(request):
    return render(request, 'sensor_page.html')