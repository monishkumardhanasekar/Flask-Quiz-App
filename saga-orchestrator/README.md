# Saga Orchestrator Service

This service implements the **Orchestration approach of the Saga Design Pattern** using Celery and Redis.

## What is the Saga Pattern?

The Saga Pattern manages distributed transactions across microservices. Instead of a single ACID transaction (which doesn't work across services), it uses:
- **Forward steps**: Execute operations in sequence
- **Compensation**: Rollback in reverse order if any step fails

## Architecture

```
┌──────────────────┐
│ Saga Orchestrator│ ← Flask Service (Port 5003)
│   (Coordinator)  │
└────────┬─────────┘
         │
    ┌────┴────┐
    │  Redis  │ ← Message Broker + Result Backend
    └────┬────┘
         │
    ┌────┴────┐
    │ Celery  │ ← Task Queue Worker
    └────┬────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│  User  │ │  Quiz  │
│Service │ │Service │
└────────┘ └────────┘
```

## User Registration Saga Flow

### Success Path:
1. **Step 1**: Create user in User Service → Returns `user_id`
2. **Step 2**: Initialize profile in Quiz Service → Returns `stats_id`
3. **Success**: Both steps complete, user is fully registered

### Failure Path (with Compensation):
1. **Step 1**: Create user in User Service → ✅ Success, `user_id = 5`
2. **Step 2**: Initialize profile in Quiz Service → ❌ Fails
3. **Compensation**: 
   - Delete profile (if created) → Skip (didn't create)
   - Delete user → ✅ Rollback user_id = 5
4. **Result**: System returns to original state

## Setup

### 1. Install Dependencies

```bash
cd saga-orchestrator
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install and Start Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### 3. Start Services

**Terminal 1 - Saga Orchestrator:**
```bash
cd saga-orchestrator
source venv/bin/activate
python run.py
```
Should show: `Running on http://0.0.0.0:5003`

**Terminal 2 - Celery Worker:**
```bash
cd saga-orchestrator
source venv/bin/activate
celery -A celery_worker.celery worker --loglevel=info
```
Should show: `celery@hostname ready`

**Terminal 3 - User Service** (if not already running):
```bash
cd user-service
source venv/bin/activate
python run.py
```

**Terminal 4 - Quiz Service** (if not already running):
```bash
cd quiz-service
source venv/bin/activate
python run.py
```

## API Endpoints

### Start User Registration Saga
```bash
POST http://localhost:5003/saga/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (202 Accepted):**
```json
{
  "message": "User registration saga started",
  "task_id": "abc-123-def-456",
  "status": "processing"
}
```

### Check Saga Status
```bash
GET http://localhost:5003/saga/status/{task_id}
```

**Response (Success):**
```json
{
  "state": "SUCCESS",
  "status": "Saga completed successfully",
  "result": {
    "status": "success",
    "saga_id": "uuid-here",
    "user_id": 5,
    "email": "user@example.com"
  }
}
```

**Response (Failure with Compensation):**
```json
{
  "state": "FAILURE",
  "status": "Saga failed",
  "error": "Error message",
  "result": {
    "status": "failed",
    "saga_id": "uuid-here",
    "compensation_log": [...]
  }
}
```

## How It Works

### 1. Saga Orchestrator (`user_registration_saga`)
- Coordinates the saga execution
- Tracks compensation log
- Executes compensation on failure

### 2. Individual Tasks (`saga_tasks.py`)
- `create_user_task`: Calls User Service API
- `init_quiz_profile_task`: Calls Quiz Service API
- `compensate_delete_user_task`: Rollback user creation
- `compensate_delete_profile_task`: Rollback profile creation

### 3. Celery + Redis
- **Celery**: Executes tasks asynchronously
- **Redis**: Stores task queue and results
- **Worker**: Processes tasks from queue

### 4. Compensation Logic
- If Step 2 fails, Step 1 is automatically rolled back
- Compensation executes in reverse order
- Each compensation is idempotent (safe to retry)

