# Quiz App - Microservices Architecture

A quiz application built with microservices architecture using Express Gateway, Flask services, and JWT authentication. Saga Pattern (Orchestration approach using Celery and Redis)

## Architecture

- **Express Gateway** (Port 8080) - API Gateway with JWT authentication
- **User Service** (Port 5001) - Flask service for user registration and login
- **Quiz Service** (Port 5002) - Flask service for quiz functionality
- **Saga Orchestrator** (Port 5003) - Orchestrates distributed transactions using Saga Pattern
- **Celery Worker** - Processes async saga tasks
- **Redis** (Port 6379) - Message broker and result backend for Celery

## Prerequisites

- Python 3.8+
- Node.js 14+
- npm
- Redis (for Saga Pattern)
- MySQL (or SQLite for development)

## Setup Instructions

### 1. Clone and Navigate
```bash
cd quiz-app
```

### 2. Set Up User Service

```bash
cd user-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `user-service/`:
```
DATABASE_URL=sqlite:///user_service.db
JWT_SECRET=dev-jwt-secret-change-me
SECRET_KEY=your-secret-key-here
```

### 3. Set Up Quiz Service

```bash
cd ../quiz-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `quiz-service/`:
```
DATABASE_URL=sqlite:///quiz_service.db
JWT_SECRET=dev-jwt-secret-change-me
SECRET_KEY=your-secret-key-here
```

**Important:** Use the same `JWT_SECRET` in both services and gateway!

### 4. Set Up Saga Orchestrator (Optional - for Saga Pattern)

```bash
cd saga-orchestrator
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Install Redis:**
- macOS: `brew install redis && brew services start redis`
- Linux: `sudo apt-get install redis-server && sudo systemctl start redis`

### 5. Set Up Express Gateway

```bash
cd ../gateway
npm install
```

The gateway uses Express Gateway framework with configuration in `config/gateway.config.yml`.

**Important:** Update `JWT_SECRET` in `config/gateway.config.yml` to match your services (default: `dev-jwt-secret-change-me`).

## Running the Application

### Basic Setup (Without Saga)

Open **3 separate terminal windows**:

### Terminal 1 - User Service
```bash
cd user-service
source venv/bin/activate  # On Windows: venv\Scripts\activate
export JWT_SECRET=dev-jwt-secret-change-me
python run.py
```
Should show: `Running on http://127.0.0.1:5001`

### Terminal 2 - Quiz Service
```bash
cd quiz-service
source venv/bin/activate  # On Windows: venv\Scripts\activate
export JWT_SECRET=dev-jwt-secret-change-me
python run.py
```
Should show: `Running on http://0.0.0.0:5002`

### Terminal 3 - Express Gateway ⚠️ **REQUIRED**
```bash
cd gateway
npm start
```
Should show: Express Gateway running on port 8080

**Important**: The gateway is **REQUIRED** for login and registration to work. Without it, you'll get `ERR_CONNECTION_REFUSED` errors.

## Accessing the Application

1. Open your browser and go to: `http://localhost:5002`
2. You'll be redirected to the login page
3. Register a new account or login
4. Start taking quizzes!

## API Endpoints

### Public (via Gateway)
- `POST http://localhost:8080/auth/register` - Register new user
- `POST http://localhost:8080/auth/login` - Login (returns JWT token)

### Protected (via Gateway - requires JWT)
- `GET http://localhost:8080/api/quiz/home` - Get quiz categories
- `GET http://localhost:8080/api/user/profile` - Get user profile

### Direct Access (Quiz Service)
- `http://localhost:5002/login` - Login page
- `http://localhost:5002/register` - Register page
- `http://localhost:5002/home` - Home page (after login)
- `http://localhost:5002/history` - Quiz history (user-specific)

### Saga Orchestrator (Port 5003)
- `POST http://localhost:5003/saga/register` - Start user registration saga
- `GET http://localhost:5003/saga/status/<task_id>` - Check saga status
- `GET http://localhost:5003/saga/health` - Health check

### With Saga Pattern (Optional)

Open **5 separate terminal windows**:

**Terminal 1-3:** Same as above (User Service, Quiz Service, Gateway)

**Terminal 4 - Saga Orchestrator:**
```bash
cd saga-orchestrator
source venv/bin/activate
python run.py
```
Should show: `Running on http://0.0.0.0:5003`

**Terminal 5 - Celery Worker:**
```bash
cd saga-orchestrator
source venv/bin/activate
celery -A celery_worker.celery worker --loglevel=info
```
Should show: `celery@hostname ready`

**Note:** Redis must be running (`redis-cli ping` should return PONG)

## Features

- ✅ JWT-based authentication
- ✅ User registration and login
- ✅ User-specific quiz attempts
- ✅ Quiz history filtered by user
- ✅ Express Gateway for API routing
- ✅ Microservices architecture
- ✅ Saga Pattern for distributed transactions (optional)

## Development Notes

- Gateway validates JWT and forwards `X-User-Id` header to services
- Quiz attempts are filtered by `user_id` - users only see their own attempts
- JWT tokens expire after 12 hours
- Sessions are stored in Flask session (server-side) and localStorage (client-side)

## Saga Pattern

The app includes an optional Saga Pattern implementation for distributed transactions. See `SAGA_EXPLANATION.md` for detailed explanation.

**Quick Test:**
```bash
# Test saga registration
python saga-orchestrator/test_saga.py
```

**Saga Flow:**
1. User registration triggers saga
2. Creates user in User Service
3. Initializes profile in Quiz Service
4. If any step fails, automatically rolls back (compensation)

## Troubleshooting

### Gateway Connection Issues
- **ERR_CONNECTION_REFUSED on port 8080**: The gateway is not running. Start it with `cd gateway && npm start`
- Ensure all services are running on correct ports
- Check gateway logs for connection errors
- Verify service endpoints in `gateway/config/gateway.config.yml`
- **Login/Register not working**: Make sure the gateway is running on port 8080

### Authentication Issues
- Make sure you're logged in (check browser localStorage for `jwt_token`)
- Clear browser cache and localStorage if having issues
- Restart all services if authentication stops working

### Saga Pattern Issues
- Make sure Redis is running: `redis-cli ping`
- Check Celery worker is running and processing tasks
- Verify all services (User, Quiz, Orchestrator) are accessible
- Check Celery worker logs for saga execution details

