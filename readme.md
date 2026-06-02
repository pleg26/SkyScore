# SkyScore

Modular Django application for ULM competition management.

## Current Functional Scope
Implemented modules:
1. Authentication (email-only login)
2. Season management (select active, view active, view others)
3. Database management for Country and Airfield (create, edit, delete)
4. Competition domain models with automatic season linking
5. Centralized map utilities (Folium) and OSM tile proxy

## Tech Stack
1. Python 3.11+
2. Django 5.x
3. SQLite in development
4. Folium for map rendering

## Quick Start
1. Create and activate the virtual environment:
```bash
python3 -m venv src/python/venv
source src/python/venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r src/python/requirements.txt
```

3. Apply migrations:
```bash
cd src/python
venv/bin/python manage.py migrate
```

4. Run the project:
```bash
venv/bin/python manage.py runserver
```

## Main URLs
1. Login: /login/
2. Home: /home/
3. Seasons: /season/
4. Database menu: /database/
5. OSM tile proxy: /osm-tiles/<z>/<x>/<y>.png

## Documentation
See:
1. [docs/architecture.md](docs/architecture.md)
2. [docs/actors_and_roles.md](docs/actors_and_roles.md)
3. [docs/organizer_season_management.md](docs/organizer_season_management.md)