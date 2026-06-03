# SkyScore

Modular Django application for ULM competition management.

## Current Functional Scope
Implemented modules:
1. Authentication (email-only login)
2. Season management (select active, view active, view others)
3. Database management for Country, Airfield, User, and Competitor (create, edit, delete)
4. Competition domain models with automatic season linking
5. Competitor profile domain with:
	1. Aircraft type and class
	2. Pilot/Navigator crew logic
	3. Conditional equipment model based on aircraft type and class
	4. Eligibility flags (insurance and medical certificate)
6. User profile settings with synchronization to linked competitor profile
7. Centralized map utilities (Folium) and OSM tile proxy

## Tech Stack
1. Python 3.11+
2. Django 6.x
3. SQLite in development
4. Folium for map rendering

## Quick Start
1. Create and activate the virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r src/python/requirements.txt
```

3. Apply migrations:
```bash
.venv/bin/python src/python/manage.py migrate
```

4. Run the project:
```bash
.venv/bin/python src/python/manage.py runserver 127.0.0.1:8001
```

## Main URLs
1. Login: /login/
2. Home: /home/
3. Seasons: /season/
4. Database menu: /database/
5. Profile settings: /profile/settings/
6. OSM tile proxy: /osm-tiles/<z>/<x>/<y>.png

## Documentation
See:
1. [docs/architecture.md](docs/architecture.md)
2. [docs/actors_and_roles.md](docs/actors_and_roles.md)
3. [docs/organizer_season_management.md](docs/organizer_season_management.md)
4. [docs/Competitor_Model_Philosophy.md](docs/Competitor_Model_Philosophy.md)