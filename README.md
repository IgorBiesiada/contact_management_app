# Contact Manager

Aplikacja webowa w Django do zarządzania kontaktami. Umożliwia dodawanie,
edycję, usuwanie i wyszukiwanie kontaktów, ich sortowanie, zbiorczy import
z pliku CSV, podgląd aktualnej pogody w mieście zamieszkania kontaktu oraz
udostępnia REST API do zarządzania kontaktami.

## Funkcjonalność

- **Lista kontaktów** (`/`) z wyszukiwaniem po imieniu, nazwisku, emailu,
  numerze telefonu i mieście (`?q=`) oraz sortowaniem po nazwisku lub dacie
  dodania, rosnąco/malejąco (`?sort=last_name|date|-date`).
- **Dodawanie** (`/add/`), **edycja** (`/edit/<id>/`) i **usuwanie**
  (`/delete/<id>/`) kontaktu przez formularz WWW (Django Forms +
  django-crispy-forms z motywem Bootstrap 5).
- **Status kontaktu** jako osobny model `ContactStatusChoices` powiązany
  relacją `ForeignKey` — nowe statusy można dodawać z poziomu panelu admina,
  bez zmian w kodzie.
- **Import z CSV** (`/import/`) — masowe dodawanie kontaktów z pliku,
  operacja atomowa (jeśli import się nie powiedzie, żadne dane nie zostają
  zapisane częściowo). Kontakty z już istniejącym emailem lub numerem
  telefonu są pomijane. Jeśli w pliku brakuje statusu, ustawiany jest
  domyślnie status `nowy`.
- **Pogoda w czasie rzeczywistym** — dla każdego kontaktu na liście
  pobierana jest aktualna temperatura, wilgotność i prędkość wiatru dla
  jego miasta zamieszkania. Realizowane przez dwuetapowe zapytanie:
  geokodowanie miasta (Nominatim/OpenStreetMap) → pobranie pogody dla
  współrzędnych (Open-Meteo). Wynik jest **cache'owany po stronie serwera
  przez 30 minut** (per nazwa miasta), żeby nie odpytywać zewnętrznych API
  przy każdym odświeżeniu listy.
- **REST API** (Django REST Framework, `ContactViewSet` + `DefaultRouter`):

  | Metoda | Endpoint | Opis |
  |---|---|---|
  | GET | `/api/contacts/` | lista kontaktów |
  | POST | `/api/contacts/` | dodanie kontaktu |
  | GET | `/api/contacts/{id}/` | szczegóły kontaktu |
  | PUT / PATCH | `/api/contacts/{id}/` | edycja kontaktu |
  | DELETE | `/api/contacts/{id}/` | usunięcie kontaktu |

  Serializer zwraca/przyjmuje pola: `id, first_name, last_name,
  city_of_residence, status, date` (status jako nazwa tekstowa, np.
  `"nowy"`, dzięki `SlugRelatedField`).

  > **Uwaga:** serializer nie obejmuje pól `phone_number` i `email` —
  > REST API w obecnej postaci nie pozwala ich ustawić/zaktualizować.
  > Jeśli endpointy mają też zarządzać tymi danymi, trzeba dodać je do
  > `fields` w `ContactSerializer`.

## Stack technologiczny

- Python 3 / Django 6.0
- Django REST Framework — REST API
- django-crispy-forms + crispy-bootstrap5 — stylowanie formularzy
- requests — komunikacja z Nominatim / Open-Meteo
- dj-database-url + psycopg — obsługa PostgreSQL przez zmienną środowiskową
  (domyślnie: SQLite, bez dodatkowej konfiguracji)
- python-dotenv — wczytywanie zmiennych z pliku `.env`

## Struktura projektu (skrót)

```
├── manage.py
├── requirements.txt
├── config/                 # ustawienia projektu
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── contact/                 # aplikacja z całą logiką
│   ├── models.py             # Contact, ContactStatusChoices
│   ├── forms.py               # ContactForm
│   ├── views.py                # widoki CRUD, import CSV, ContactViewSet
│   ├── urls.py                  # routing widoków + /api/contacts/
│   ├── serializers.py            # ContactSerializer
│   └── services.py                # get_weather_for_city (Nominatim + Open-Meteo, cache)
├── templates/               # add.html, list.html, edit.html, delete.html, import.html
└── static/
```

## Instalacja i uruchomienie

### 1. Wymagania wstępne

- Python 3.11+ (Django 6.0 wymaga min. Python 3.12 — sprawdź swoją wersję
  poleceniem `python3 --version`)
- `pip`

### 2. Pobranie projektu

```bash
git clone <adres-repozytorium>
cd <folder-projektu>
```

### 3. Utworzenie i aktywacja wirtualnego środowiska

```bash
python3 -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### 4. Instalacja zależności

```bash
pip install -r requirements.txt
```

### 5. Konfiguracja zmiennych środowiskowych

Projekt wczytuje ustawienia z pliku `.env` (przez `python-dotenv`). Utwórz
plik `.env` w katalogu głównym projektu:

```env
SECRET_KEY=wpisz-tu-dlugi-losowy-ciag-znakow
DEBUG=True
```

- `SECRET_KEY` — wymagany, Django nie wystartuje bez niego (`os.getenv('SECRET_KEY')`
  nie ma wartości domyślnej).
- `DEBUG` — ustaw `True` w trakcie developmentu, `False` na produkcji.
- `DATABASE_CONNECTION_STRING` — **opcjonalny**. Jeśli go nie ustawisz,
  aplikacja użyje lokalnej bazy SQLite (`db.sqlite3`) i nie musisz nic więcej
  konfigurować. Jeśli chcesz użyć PostgreSQL, podaj connection string w
  formacie:
  ```env
  DATABASE_CONNECTION_STRING=postgres://user:password@localhost:5432/dbname
  ```

### 6. Migracja bazy danych

```bash
python manage.py migrate
```

### 7. Utworzenie co najmniej jednego statusu kontaktu

Pole `status` w modelu `Contact` jest **wymagane** (`ForeignKey` bez
`null=True`), więc przed dodaniem pierwszego kontaktu przez formularz WWW
potrzebny jest przynajmniej jeden rekord `ContactStatusChoices`. Najprościej
zrobić to z poziomu panelu admina (patrz krok 8) lub powłoki Django:

```bash
python manage.py shell -c "from contact.models import ContactStatusChoices; ContactStatusChoices.objects.get_or_create(name='nowy')"
```

*(Import przez CSV tworzy statusy automatycznie, więc przy imporcie ten krok nie jest konieczny.)*

### 8. Utworzenie konta administratora

```bash
python manage.py createsuperuser
```

### 9. Uruchomienie serwera developerskiego

```bash
python manage.py runserver
```

Aplikacja będzie dostępna pod adresem: **http://127.0.0.1:8000/**

- Lista/zarządzanie kontaktami: `http://127.0.0.1:8000/`
- Dodawanie kontaktu: `http://127.0.0.1:8000/add/`
- Import CSV: `http://127.0.0.1:8000/import/`
- Panel admina: `http://127.0.0.1:8000/admin/`
- REST API: `http://127.0.0.1:8000/api/contacts/`

## Import kontaktów z CSV

Plik CSV powinien mieć nagłówek z następującymi kolumnami:

```
first_name,last_name,email,phone,city_of_residence,status
```

- `status` jest opcjonalny — jeśli pominięty, kontakt otrzyma status `nowy`.
- Wiersze z emailem lub numerem telefonu, który już istnieje w bazie, są
  pomijane.

Przykład:

```csv
first_name,last_name,email,phone,city_of_residence,status
Jan,Kowalski,jan.kowalski@example.com,+48123456789,Warszawa,nowy
Anna,Nowak,anna.nowak@example.com,+48987654321,Kraków,w trakcie
```

## Uwagi dot. integracji pogodowej

`services.get_weather_for_city()` korzysta z dwóch darmowych, publicznych
API (Nominatim i Open-Meteo) i wymaga dostępu do internetu. Wyniki są
cache'owane serwerowo na 30 minut per miasto (`django.core.cache`,
backend `LocMemCache`), więc kolejne odświeżenia listy w tym czasie nie
generują nowych zapytań zewnętrznych. Jeśli środowisko nie ma dostępu do
sieci albo Nominatim/Open-Meteo są niedostępne, pogoda dla danego kontaktu
nie zostanie wyświetlona.

## Testowanie REST API (przykład z `curl`)

```bash
# Lista kontaktów
curl http://127.0.0.1:8000/api/contacts/

# Dodanie kontaktu (status podajemy jako istniejącą nazwę, np. "nowy")
curl -X POST http://127.0.0.1:8000/api/contacts/ \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Jan","last_name":"Kowalski","city_of_residence":"Warszawa","status":"nowy"}'

# Edycja kontaktu o id=1
curl -X PATCH http://127.0.0.1:8000/api/contacts/1/ \
  -H "Content-Type: application/json" \
  -d '{"city_of_residence":"Kraków"}'

# Usunięcie kontaktu o id=1
curl -X DELETE http://127.0.0.1:8000/api/contacts/1/
```