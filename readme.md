# SkyScore

A modular scoring system for ULM (Ultralight Aviation) competitions.
Built with **Django (Python)** for the backend and **LaTeX** for documentation, following a clean, maintainable, and text-only file architecture.

---

## 📌 Features
- Modular Django backend for scoring, user management, and competition data.
- LaTeX documentation and PDF report generation.
- PostgreSQL database support.
- Designed for fairness, reproducibility, and ease of use in ULM race scoring.

---

## 🛠️ Project Structure
SkyScore/
├── src/
│   ├── python/
│   │   ├── sky_score/       # Dossier du projet Django
│   │   │   ├── __init__.py
│   │   │   ├── settings.py
│   │   │   ├── urls.py
│   │   │   ├── asgi.py
│   │   │   └── wsgi.py
│   │   ├── manage.py        # Fichier de gestion Django
│   │   └── venv/            # Environnement virtuel
│   └── latex/
├── readme.md
└── .gitignore

---

## 🚀 Getting Started
### Prerequisites
- Python 3.11+
- PostgreSQL
- LaTeX (for documentation)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/tu_utilisateur/SkyScore.git
   cd SkyScore