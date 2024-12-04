from django.shortcuts import render, redirect
from . import models
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

    return render(request, 'schedule_page.html', {'events': events_json})

# Funkcja do pobierania danych o pogodzie
def get_weather_data(city):
    # Użyj swojego klucza API, który otrzymałeś z OpenWeatherMap
    api_key = settings.OPENWEATHER_API_KEY
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


def weather_view(request):
    city = 'Poznan'
    weather_data = get_weather_data(city)
    
    return render(request, 'weather_page.html', {'weather': weather_data})

def sensor_view(request):
    return render(request, 'sensor_page.html')