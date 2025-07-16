## Opis projektu

Aplikacja webowa do zarządzania automatycznym systemem podlewania trawnika.  
Główne funkcje:

- **Harmonogram irygacji** – tworzenie i edycja planów podlewania w kalendarzu,
- **Integracja z prognozą pogody** – system dostosowuje podlewanie do warunków (opady, upały),
- **Integracja z czujnikami** – analiza wilgotności gleby i temperatury, by dostosować podlewanie do rzeczywistych potrzeb,
- **Platforma Django** – CRUD wydarzeń irygacyjnych, połączenie z API pogodowym i sensorami na żywo,
- **Uruchamiane na Raspberry Pi** – sterownik sprzętowy do obsługi czujników i zaworów.

Aplikacja pozwala sterować podlewaniem trawnika w sposób efektywny, niezależny od pogody i faktycznego stanu gleby.

---

## Technologie

- **Backend:** Python 3 + Django
- **Frontend:** HTML, CSS, JavaScript (z wykorzystaniem SSE lub AJAX)
- **Baza danych:** SQLite (lub inna kompatybilna z Django)
- **Raspberry Pi:** sterowanie GPIO czujnikami wilgotności i temperatury (DHT, czujniki gleby)
- **Integracja pogodowa:** dowolne API pogodowe (np. OpenWeatherMap)
- **Urządzenia:** zawory solenoidowe, czujniki wilgotności i temperatury, przekaźniki, ewentualny panel solarny
