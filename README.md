# Contact Manager

Aplikacja webowa w Django do zarządzania kontaktami. Umożliwia dodawanie,
edycję, usuwanie i wyszukiwanie kontaktów, ich sortowanie, zbiorczy import
z pliku CSV, podgląd aktualnej pogody w mieście zamieszkania kontaktu oraz
udostępnia REST API do zarządzania kontaktami. Dostęp do aplikacji wymaga
zalogowania — każdy użytkownik widzi i zarządza wyłącznie własnymi
kontaktami.

## Funkcjonalność

- **Logowanie** (`/`) — prosty system uwierzytelniania oparty o wbudowany
  Django `LoginView` (własny model użytkownika `CustomUser` w aplikacji
  `users`). **Nie ma rejestracji** — konta użytkowników zakłada się z
  poziomu panelu admina lub komendą `createsuperuser` (patrz sekcja
  instalacji). Wszystkie widoki listy/dodawania/edycji/usuwania/importu
  kontaktów wymagają zalogowania (`LOGIN_URL = 'users:login'`), a każdy
  kontakt jest przypisany do konkretnego użytkownika (`Contact.user`) —
  użytkownicy nie widzą nawzajem swoich kontaktów.
- **Lista kontaktów** (`/list/`) z wyszukiwaniem po imieniu, nazwisku, emailu,
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
  zapisane częściowo). Kontakty z już istniejącym (dla tego samego
  zalogowanego użytkownika) emailem lub numerem telefonu są pomijane.
  Jeśli w pliku brakuje statusu, ustawiany jest domyślnie status `nowy`.
- **Pogoda w czasie rzeczywistym** — dla każdego kontaktu na liście
  pobierana jest aktualna temperatura, wilgotność i prędkość wiatru dla
  jego miasta zamieszkania. Realizowane przez dwuetapowe zapytanie:
  geokodowanie miasta (Nominatim/OpenStreetMap) → pobranie pogody dla
  współrzędnych (Open-Meteo). Wynik jest **cache'owany po stronie serwera
  przez 30 minut** (per nazwa miasta), żeby nie odpytywać zewnętrznych API
  przy każdym odświeżeniu listy.
- **REST API** (Django REST Framework, `ContactViewSet` + `DefaultRouter`).
  Zwraca i modyfikuje wyłącznie kontakty zalogowanego użytkownika
  (`get_queryset` filtruje po `request.user`, `perform_create` automatycznie
  przypisuje nowy kontakt do zalogowanego użytkownika):

  | Metoda | Endpoint | Opis |
  |---|---|---|
  | GET | `/api/contacts/` | lista kontaktów |
  | POST | `/api/contacts/` | dodanie kontaktu |
  | GET | `/api/contacts/{id}/` | szczegóły kontaktu |
  | PUT / PATCH | `/api/contacts/{id}/` | edycja kontaktu |
  | DELETE | `/api/contacts/{id}/` | usunięcie kontaktu |

  `GET /api/contacts/` (lista) korzysta z `ContactSerializer` — pola:
  `id, first_name, last_name, city_of_residence, status, date` (zgodnie
  z wymaganiami zadania). Pozostałe akcje (`POST`, `GET` szczegóły,
  `PUT`/`PATCH`, `DELETE`) korzystają z `ContactDetailSerializer`, który
  obejmuje też `phone_number` i `email` — dzięki temu dodawanie/edycja
  kontaktu przez API faktycznie pozwala ustawić wszystkie pola. Status
  podaje się jako nazwa tekstowa (np. `"nowy"`), dzięki `SlugRelatedField`.

  > **Uwaga:** `ContactViewSet` nie ma jawnie ustawionych `permission_classes`
  > (np. `IsAuthenticated`) — dostęp do API zakłada zalogowanego użytkownika
  > tylko przez filtrowanie w `get_queryset()` po `request.user`. Dla
  > niezalogowanego żądania `request.user` to `AnonymousUser`, co przy próbie
  > filtrowania po polu `ForeignKey` do `CustomUser` kończy się błędem
  > serwera (500), zamiast czytelnego `401/403`. Warto dodać
  > `permission_classes = [IsAuthenticated]` do `ContactViewSet`.

## Stack technologiczny

- Python 3 / Django 6.0
- Django REST Framework — REST API
- django-crispy-forms + crispy-bootstrap5 — stylowanie formularzy
- requests — komunikacja z Nominatim / Open-Meteo
- dj-database-url + psycopg — obsługa PostgreSQL przez zmienną środowiskową
  (domyślnie: SQLite, bez dodatkowej konfiguracji)
- python-dotenv — wczytywanie zmiennych z pliku `.env`
- Docker + Docker Compose — konteneryzacja (app + PostgreSQL + Adminer), patrz sekcja niżej
- Django auth (`django.contrib.auth`) — logowanie oparte o własny model
  użytkownika `CustomUser` (aplikacja `users`), bez rejestracji

## Struktura projektu (skrót)

```
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yaml
├── config/                 # ustawienia projektu
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── contact/                 # aplikacja z całą logiką
│   ├── models.py             # Contact, ContactStatusChoices
│   ├── forms.py               # ContactForm
│   ├── views.py                # widoki CRUD, import CSV, ContactViewSet
│   ├── urls.py                  # routing widoków + /api/contacts/
│   ├── serializers.py            # ContactSerializer, ContactDetailSerializer
│   └── services.py                # get_weather_for_city (Nominatim + Open-Meteo, cache)
├── users/                    # logowanie (bez rejestracji)
│   ├── models.py              # CustomUser (AbstractUser)
│   ├── forms.py                 # UserLoginForm
│   ├── views.py                  # LoginUserView, logout_view
│   └── urls.py                    # '/', '/logout/'
├── templates/               # add.html, list.html, edit.html, delete.html, import.html, login_form.html
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
- `DB_CONNECTION_STRING` — **opcjonalny**. Jeśli go nie ustawisz,
  aplikacja użyje lokalnej bazy SQLite (`db.sqlite3`) i nie musisz nic więcej
  konfigurować. Jeśli chcesz użyć PostgreSQL, podaj connection string w
  formacie:
  ```env
  DB_CONNECTION_STRING=postgres://user:password@localhost:5432/dbname
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

### 8. Utworzenie konta użytkownika (logowanie)

Aplikacja **nie ma formularza rejestracji** — to jedyny sposób na
utworzenie konta, którym można się zalogować i korzystać z aplikacji:

```bash
python manage.py createsuperuser
```

Powstałym kontem logujesz się na stronie głównej (`/`) i dopiero wtedy
masz dostęp do listy/dodawania/edycji kontaktów oraz importu CSV — wszystkie
te widoki wymagają zalogowania.

### 9. Uruchomienie serwera developerskiego

```bash
python manage.py runserver
```

Aplikacja będzie dostępna pod adresem: **http://127.0.0.1:8000/**

- Logowanie: `http://127.0.0.1:8000/` (bez zalogowania pozostałe widoki przekierują tutaj)
- Wylogowanie: `http://127.0.0.1:8000/logout/`
- Lista/zarządzanie kontaktami: `http://127.0.0.1:8000/list/`
- Dodawanie kontaktu: `http://127.0.0.1:8000/add/`
- Import CSV: `http://127.0.0.1:8000/import/`
- Panel admina: `http://127.0.0.1:8000/admin/`
- REST API: `http://127.0.0.1:8000/api/contacts/`

## Uruchomienie z Dockerem (docker-compose)

Projekt zawiera `Dockerfile` oraz `docker-compose.yaml`, więc zamiast
kroków 1–9 z sekcji powyżej można postawić całość jedną komendą — łącznie
z bazą PostgreSQL i panelem Adminer do jej podglądu.

Skład środowiska (`docker-compose.yaml`):

| Usługa | Opis | Port |
|---|---|---|
| `web` | aplikacja Django (budowana z `Dockerfile`, migracje odpalają się automatycznie przy starcie) | `8000` |
| `db` | baza PostgreSQL 17 z danymi trzymanymi w wolumenie `postgres_data` | — (wewnętrzny) |
| `adminer` | graficzny panel do podglądu bazy danych | `8080` |

### 1. Wymagania wstępne

- Docker + Docker Compose

### 2. Plik `.env`

`docker-compose.yaml` wczytuje zmienne z pliku `.env` w katalogu głównym
projektu (przekazywane do kontenera `web` przez `env_file`, a do samego
`docker-compose.yaml` — np. na potrzeby healthchecka bazy — jako zmienne
środowiskowe hosta). Utwórz `.env`:

```env
SECRET_KEY=wpisz-tu-dlugi-losowy-ciag-znakow
DEBUG=True
DOCKER_DB_STRING=postgres://postgres:1234@db:5432/rekrutacja
DB_USER=postgres
DB_NAME=rekrutacja
```

> **Uwaga:** `DB_USER`/`DB_NAME` muszą się zgadzać z danymi bazy zaszytymi
> na sztywno w `docker-compose.yaml` (`POSTGRES_USER=postgres`,
> `POSTGRES_DB=rekrutacja`) — inaczej healthcheck usługi `db` będzie
> sprawdzał złą nazwę bazy/użytkownika i `web` może nie wystartować,
> czekając na `service_healthy`.

### 3. Budowa i uruchomienie kontenerów

```bash
docker compose up --build
```

`Dockerfile` przy starcie kontenera `web` sam odpala migracje
(`python manage.py migrate`) i serwer developerski Django
(`0.0.0.0:8000`), więc nie trzeba nic robić ręcznie.

### 4. Dostęp do aplikacji

- Aplikacja: **http://localhost:8000/**
- Panel Adminer (podgląd bazy PostgreSQL): **http://localhost:8080/**
  — System: `PostgreSQL`, Serwer: `db`, Użytkownik: `postgres`,
  Hasło: `1234`, Baza danych: `rekrutacja`

### 5. Konto administratora w kontenerze

`createsuperuser` trzeba uruchomić wewnątrz działającego kontenera `web`:

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Zatrzymanie i sprzątanie

```bash
docker compose down          # zatrzymuje kontenery
docker compose down -v       # dodatkowo usuwa wolumen z danymi bazy
```

## Znane problemy do sprawdzenia (logowanie)

- **Kolejność mixinów w widokach opartych o klasy.** `AddContactView`,
  `ContactListView`, `ContactUpdateView`, `ContactDeleteView` są
  zdefiniowane jako `class XView(SomeGenericView, LoginRequiredMixin):`.
  Django zaleca odwrotną kolejność —
  `class XView(LoginRequiredMixin, SomeGenericView):` — bo mixiny
  odpowiadające za kontrolę dostępu muszą być **pierwsze** w liście klas
  bazowych, żeby ich `dispatch()` faktycznie przechwycił żądanie przed
  resztą logiki widoku. Przy obecnej kolejności `LoginRequiredMixin` może
  nie działać tak, jak powinien — warto to zweryfikować (spróbować wejść
  na `/list/` w przeglądarce incognito, bez logowania) i w razie potrzeby
  zamienić kolejność klas bazowych.
- **Unikalność numeru telefonu.** W `Contact.Meta.constraints` telefon nie
  ma już samodzielnego ograniczenia unikalności — jest tylko część
  złożonego `UniqueConstraint(fields=['email', 'phone_number'], ...)`.
  W praktyce oznacza to, że **ten sam numer telefonu może dziś wystąpić
  wielokrotnie** (nawet u tego samego użytkownika), o ile towarzyszy mu
  inny adres email — co nie do końca spełnia wymóg zadania "numery
  telefonów... nie mogą się powtarzać". Warto rozważyć dodanie osobnego
  `UniqueConstraint(fields=['user', 'phone_number'])`.

## Import kontaktów z CSV

Plik CSV powinien mieć nagłówek z następującymi kolumnami:

```
first_name,last_name,email,phone,city_of_residence,status
```

- `status` jest opcjonalny — jeśli pominięty, kontakt otrzyma status `nowy`.
- Wiersze z emailem lub numerem telefonu, który już istnieje w bazie **dla
  tego samego zalogowanego użytkownika**, są pomijane (inni użytkownicy
  mogą mieć kontakt z tym samym adresem/numerem).

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

> Endpointy filtrują dane po zalogowanym użytkowniku, więc `curl` bez
> przekazania ciasteczka sesji (po zalogowaniu przez `/`) może zwrócić
> błąd zamiast oczekiwanego wyniku — patrz uwaga w sekcji REST API wyżej.

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