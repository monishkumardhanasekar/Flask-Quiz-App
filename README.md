# Quiz App - Microservices Architecture

A quiz application built with microservices architecture using Express Gateway, Flask services, and JWT authentication.

## Architecture

- **Express Gateway** (Port 8080) - API Gateway with JWT authentication
- **User Service** (Port 5001) - Flask service for user registration and login
- **Quiz Service** (Port 5002) - Flask service for quiz functionality

## Prerequisites

- Python 3.8+
- Node.js 14+
- npm
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

### 4. Set Up Express Gateway

```bash
cd ../gateway
npm install
```

The gateway uses Express Gateway framework with configuration in `config/gateway.config.yml`.

**Important:** Update `JWT_SECRET` in `config/gateway.config.yml` to match your services (default: `dev-jwt-secret-change-me`).

## Running the Application

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

### Terminal 3 - Express Gateway
```bash
cd gateway
npm start
```
Should show: Express Gateway running on port 8080

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



