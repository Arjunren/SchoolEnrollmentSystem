# School Enrollment System

A Django 6.1 REST API for academic programs, courses, terms, class sections, enrollment, and grading.

## Highlights

- Token authentication with admin, registrar, teacher, and student roles
- Student registration with unique generated student numbers
- Program, course, term, and section CRUD with search, ordering, and pagination
- Transactional capacity-controlled enrollment with duplicate protection
- Student-owned enrollment views and teacher-scoped class lists
- Assigned-teacher-only grading and enrollment status controls
- Dashboard reporting, structured errors, CORS allowlist, migrations, seed data, Docker, and PostgreSQL CI

## Run locally

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

macOS/Linux activation: `source .venv/bin/activate`. SQLite is used when PostgreSQL variables are absent.

Development accounts are `admin`, `teacher`, and `student`, all with password `ChangeMe123!`.

API routes live under `/api/`; authentication routes are under `/api/auth/`. Send tokens as `Authorization: Token <token>`.

## Verify

```bash
pytest
python manage.py check
python manage.py makemigrations --check --dry-run
pip check
```

Use `docker compose up --build` for the PostgreSQL-backed container stack.

## License

MIT
