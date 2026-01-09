# User Service

Flask-based user service providing registration, login, and profile endpoints.

## Run
```bash
pip install -r requirements.txt
python run.py
```
Runs on port **5001**.

## Endpoints
- `POST /register` - body: `{ "email": "...", "password": "..." }`
- `POST /login` - body: `{ "email": "...", "password": "..." }` → returns JWT
- `GET /profile` - requires `Authorization: Bearer <token>`
- `GET /health` - service health check

## Env vars
- `SECRET_KEY` (optional) - Flask secret key
- `DATABASE_URL` (optional) - defaults to `sqlite:///user_service.db`
- `JWT_SECRET` (optional) - signing key for JWT (default: dev value, change in prod)



