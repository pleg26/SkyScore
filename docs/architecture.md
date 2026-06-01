# 🏗️ SkyScore Architecture

*Last updated: 2026-06-01*
*Validated by: Pierre LEGRENEUR*

---

## **📁 Project Structure**
SkyScore follows a **modular architecture** based on Django apps, with each feature isolated in its own sub-project.
This structure reflects the **menu hierarchy** of the interface and ensures **scalability** and **maintainability**.

SkyScore/
├── src/
│   ├── python/
│   │   ├── sky_score/          # Main Django project (settings, global URLs)
│   │   │   ├── settings.py
│   │   │   ├── urls.py         # Includes all app URLs
│   │   │   └── wsgi.py
│   │   │
│   │   ├── common/             # Shared app (authentication, base models, login)
│   │   │   ├── models.py       # Shared models (e.g., User, Administrator)
│   │   │   ├── forms.py
│   │   │   ├── views.py        # Login/logout views
│   │   │   ├── urls.py         # Authentication URLs
│   │   │   └── templates/      # Base templates (e.g., base.html, navigation.html)
│   │   │
│   │   ├── season/             # Season management app
│   │   │   ├── models.py       # Season model
│   │   │   ├── forms.py
│   │   │   ├── views.py        # CRUD views for seasons
│   │   │   ├── urls.py         # Season-specific URLs
│   │   │   └── templates/
│   │   │       └── season/     # Season templates
│   │   │
│   │   ├── competition/        # Competition management app
│   │   │   ├── models.py
│   │   │   ├── forms.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── templates/
│   │   │       └── competition/
│   │   │
│   │   ├── scoring/             # Scoring logic app
│   │   │   ├── models.py
│   │   │   ├── forms.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── templates/
│   │   │       └── scoring/
│   │   │
│   │   └── manage.py            # Django management script
│   │
│   └── latex/                   # LaTeX documentation
│
├── docs/                       # Project documentation
│   ├── architecture.md         # This file
│   ├── organizer_season_management.md
│   └── actors_and_roles.md
│
├── README.md                   # Project overview
└── .gitignore

---

## **🔧 Key Design Principles**
1. **Modularity**:
   - Each feature (e.g., `season`, `competition`) is a **self-contained Django app**.
   - Apps can be **enabled/disabled** independently in `settings.py`.

2. **Dynamic Menu Generation**:
   - The main menu (`navigation.html`) is **dynamically generated** based on:
     - Active apps in `settings.py`.
     - User permissions (e.g., organizers see "Season Management", pilots see "My Results").

3. **Shared Resources**:
   - `common/` app contains:
     - **Base models** (e.g., `User`, `Administrator`).
     - **Authentication logic** (login, logout, permissions).
     - **Base templates** (e.g., `base.html` with header/footer).

4. **Scalability**:
   - New features (e.g., `live_tracking/`) can be added as new apps **without breaking existing code**.

---

## **📌 App Naming Conventions**
| App          | Purpose                          | Example URLs               |
|--------------|----------------------------------|-----------------------------|
| `common`     | Shared logic (auth, base models)| `/login/`, `/logout/`       |
| `season`     | Season management               | `/season/create/`, `/season/list/` |
| `competition`| Competition management          | `/competition/create/`     |
| `scoring`    | Scoring logic                   | `/scoring/calculate/`      |

---

## **🚀 Next Steps**
1. **Implement the `common/` app** (base models, authentication).
2. **Implement the `season/` app** (as per `organizer_season_management.md`).
3. **Set up dynamic menu generation** in `base.html`.