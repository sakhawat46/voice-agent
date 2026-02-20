# Voice Agent (Django + DRF)

A Django REST API project for user authentication, agent management, and public embeddable voice/chat experiences powered by OpenAI.

## Features

- Custom user model with email-based authentication
- JWT auth (access/refresh) with token refresh and logout flow
- OTP-based password reset via email
- Owner-scoped CRUD for voice agents
- Public embed APIs for voice session start and text chat
- Embeddable JavaScript loader (`/embed/v2.js`) for floating mic + chat panel

## Tech Stack

- Python
- Django
- Django REST Framework
- SimpleJWT (`djangorestframework_simplejwt`)
- `requests` (OpenAI API calls)
- `django-cors-headers`
- SQLite (default)

## Project Structure

```text
apps/
  users/      # auth, profile, password reset, account delete
  voice/      # agent CRUD, embed endpoints, embed JS
projects/     # settings, root urls, ASGI/WSGI
templates/    # sample frontend test page
```

## Requirements

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in project root:

```env
OPENAI_API_KEY=your_openai_api_key
```

## Local Setup

```bash
python -m venv venv
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Server runs at: `http://127.0.0.1:8000`

## Authentication Endpoints

Base path: `/api/`

- `POST /api/auth/signup/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/` (auth required)
- `GET /api/auth/profile/` (auth required)
- `PUT /api/auth/profile/` (auth required)
- `POST /api/auth/token/refresh/`
- `PUT /api/auth/change-password/` (auth required)
- `POST /api/auth/password-reset/request/`
- `POST /api/auth/password-reset/verify-otp/`
- `POST /api/auth/password-reset/change-password/` (auth required)
- `DELETE /api/delete-account/` (auth required)

## Agent & Embed Endpoints

- `GET /api/agents/` (auth required)
- `POST /api/agents/` (auth required)
- `GET /api/agents/<pk>/` (auth required)
- `PUT /api/agents/<pk>/` (auth required)
- `PATCH /api/agents/<pk>/` (auth required)
- `DELETE /api/agents/<pk>/` (auth required)
- `GET /api/agents/<pk>/embed/` (auth required, only when agent is enabled)

Public endpoints:

- `POST /api/embed/agents/<public_id>/voice/start/`
- `POST /api/embed/agents/<public_id>/chat/`
- `GET /embed/v2.js`

## Embed Script Example

```html
<script defer
  src="http://127.0.0.1:8000/embed/v2.js"
  data-agent="YOUR_AGENT_PUBLIC_ID"
  data-base-url="http://127.0.0.1:8000">
</script>
```

## OpenAI Integration

This project calls:

- `https://api.openai.com/v1/realtime/sessions`
- `https://api.openai.com/v1/realtime?model=gpt-realtime`
- `https://api.openai.com/v1/chat/completions`

## Notes

- Default DB is SQLite (`db.sqlite3`).
- CORS is currently configured to allow all origins in settings.
- Media files are served from `/media/` in debug mode.
- Email backend is configured for Gmail SMTP in settings.

## Development Commands

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
