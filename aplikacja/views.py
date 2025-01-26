from django.shortcuts import render, redirect
from . import models
from . import utils
from django.utils.dateparse import parse_datetime
from django.contrib import admin
from django.db.models import Sum, Count, F
import requests
from django.conf import settings
import datetime
import calendar
import threading
import os
import json
# from wateringControl import measure_parameters

JSON_FILE_PATH = os.path.join(os.path.dirname(__file__), "sensors.json")


# def start_background_thread():
#     thread = threading.Thread(target=measure_parameters, daemon=True)
#     thread.start()

def test_view(request):
    return render(request, 'test_page.html', {'message': 'To jest przykładowa strona testowa!'})



def home_view(request):
    return render(request, 'home_page.html')

def statistics_view(request):
    today = datetime.date.today()
    current_month = today.month
    current_year = today.year

    # Wydarzenia dla bieżącego miesiąca
    monthly_events = models.ScheduleEvent.objects.filter(start__month=current_month, start__year=current_year)

    # Wydarzenia dla bieżącego roku
    yearly_events = models.ScheduleEvent.objects.filter(start__year=current_year)

    # Zliczamy liczbę planowych, odwołanych i dodatkowych wydarzeń w bieżącym miesiącu i roku
    monthly_status_count = monthly_events.values('status').annotate(count=Count('status'))
    yearly_status_count = yearly_events.values('status').annotate(count=Count('status'))

    # Przygotowanie danych dziennych (bieżący miesiąc)
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    daily_stats = []
    for day in range(1, days_in_month + 1):
        day_start = datetime.datetime(current_year, current_month, day)
        day_end = day_start + datetime.timedelta(days=1)
        daily_events = monthly_events.filter(start__gte=day_start, start__lt=day_end)
        duration = daily_events.aggregate(total_time=Sum(F('end') - F('start')))['total_time']
        daily_stats.append({
            'day': day,
            'duration': duration.total_seconds() / 3600 if duration else 0  # czas w godzinach
        })

    # Przygotowanie danych miesięcznych (bieżący rok)
    monthly_stats = []
    for month in range(1, 13):
        month_events = yearly_events.filter(start__month=month)
        duration = month_events.aggregate(total_time=Sum(F('end') - F('start')))['total_time']
        monthly_stats.append({
            'month': month,
            'duration': duration.total_seconds() / 3600 if duration else 0  # czas w godzinach
        })

    # Przekształcenie wyników liczenia statusów na słownik
    monthly_status_dict = {status['status']: status['count'] for status in monthly_status_count}
    yearly_status_dict = {status['status']: status['count'] for status in yearly_status_count}

    # Dodanie brakujących statusów w przypadku, gdy nie ma takich wydarzeń
    for status in ['planned', 'canceled', 'extra']:
        if status not in monthly_status_dict:
            monthly_status_dict[status] = 0
        if status not in yearly_status_dict:
            yearly_status_dict[status] = 0

    context = {
        'daily_stats': daily_stats,
        'monthly_stats': monthly_stats,
        'monthly_status': monthly_status_dict,  # Ilosc odwolanych odbytych i dodatkowych podlewan w miesiacu
        'yearly_status': yearly_status_dict,    # Ilosc odwolanych odbytych i dodatkowych podlewan w roku
        'current_month': current_month,
        'current_year': current_year,
    }
    return render(request, 'statistics_page.html', context)


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

    # print(f"Events_debug{events_json}")

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
    # Odczytanie danych z pliku JSON
    try:
        with open(JSON_FILE_PATH, 'r') as json_file:
            sensor_data = json.load(json_file)

        temperature = sensor_data.get('temperature')
        air_moisture = sensor_data.get('air_moisture')
        ground_moisture = sensor_data.get('ground_moisture')

    except FileNotFoundError:
        # Jeśli plik nie istnieje, można ustawić domyślne wartości
        temperature = 'Brak danych'
        air_moisture = 'Brak danych'
        ground_moisture = 'Brak danych'

    return render(request, 'sensor_page.html', {'temperature': temperature, 'air_moisture': air_moisture, 'ground_moisture': ground_moisture})