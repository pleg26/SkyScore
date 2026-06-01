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
sky_score/
├── src/
│   ├── python/          # Django project and apps
│   │   ├── sky_score/   # Main Django project
│   │   ├── scoring/     # Scoring logic app
│   │   ├── users/       # User management app
│   │   └── ...
│   │
│   └── latex/           # LaTeX documentation
│       ├── main.tex
│       ├── preamble.tex
│       ├── titlepage.tex
│       └── chapters/    # One folder per chapter
│
├── readme.md
├── .gitignore
└── licence

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