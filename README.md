# SkillSpring

SkillSpring is a Flask and SQLite learning platform for students. It combines
structured roadmaps, lessons, practical projects, challenges, quizzes, trusted
resources, and progress tracking.

## Setup on Windows PowerShell

Run these commands from:

```powershell
cd C:\Users\Prasanthi\OneDrive\Desktop\SkillSpringg
```

Create or activate the virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set a strong `SECRET_KEY` for anything beyond
local development.

The application creates missing SQLite tables without deleting existing data.
Seed starter content (the command is repeatable):

```powershell
.\.venv\Scripts\python.exe scripts\seed_data.py
```

Run the test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Start the application:

```powershell
.\.venv\Scripts\python.exe run.py
```

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## Main features

- CSRF-protected registration, login, and POST-only logout
- Personalized dashboard with real enrollments, lesson progress, and activity
- Searchable skills and roadmaps
- Roadmap enrollment and lesson completion
- Guided projects with milestone tracking
- Server-scored quizzes with persisted attempts and responses
- Verified-completion learning challenges
- Searchable trusted resources with bookmarks
- Profile updates, progress history, achievements-ready activity records
- Contact submission storage without claiming email delivery
- About, privacy, and terms pages

The application does not execute user-submitted code and does not provide
unconfigured password reset, email delivery, OAuth, or AI services.
