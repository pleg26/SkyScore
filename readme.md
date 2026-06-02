# SkyScore

*A modular scoring system for ULM (Ultralight Aviation) competitions.*
*Built with Django (Python) and LaTeX for documentation.*

---

## **📌 Project Overview**
SkyScore manages competitions, seasons, and rankings for **Paramotor** and **Microlight** events (Classic, Slalom, STOL).
It provides:
- **Season management** (with active season per administrator).
- **Competition and event organization**.
- **Real-time scoring and rankings**.
- **LaTeX documentation** for specifications and reports.

---

## **🏗️ Architecture**
SkyScore follows a **modular Django architecture**:
- Each feature is a **separate Django app** (e.g., `season/`, `competition/`, `scoring/`).
- Shared logic (authentication, base models) is in the `common/` app.
- Menus are **dynamically generated** based on active apps and user permissions.

See [docs/architecture.md](docs/architecture.md) for details.

---

## **🛠️ Setup Instructions**
### Prerequisites
- Python 3.11+
- PostgreSQL (for production) or SQLite (for development)
- LaTeX (for documentation)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/tu_utilisateur/SkyScore.git
   cd SkyScore
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv src/python/venv
   source src/python/venv/bin/activate  # On macOS/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r src/python/requirements.txt
   ```
4. Run Django migrations:
   ```bash
   cd src/python/
   python3 manage.py migrate
   ```
5. Start the development server:
   ```bash
   python3 manage.py runserver
   ```

6. Access the app at http://127.0.0.1:8000.

## **📂 Project Structure**
See docs/architecture.md for the full structure.

## **🤝 Contributing**
Pull requests are welcome. For major changes, please open an issue first.

## **📄 License**
This project is licensed under the MIT License.