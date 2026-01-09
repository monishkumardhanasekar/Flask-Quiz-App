# Express Gateway

This is the Express Gateway for the Quiz App microservices architecture.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the gateway:
```bash
npm start
```

For development with auto-reload:
```bash
npm run dev
```

## Configuration

- Gateway runs on port **8080**
- Admin panel runs on port **9876**
- Configuration file: `config/gateway.config.yml`

## Routes

- `/auth/*` → User Service (public, no auth required)
- `/api/quiz/*` → Quiz Service (protected, requires JWT)
- `/api/user/*` → User Service (protected, requires JWT)

## Service Ports

- User Service: **5001**
- Quiz Service: **5002**

## JWT Secret

Make sure `JWT_SECRET` in `gateway.config.yml` matches the secret used in User Service and Quiz Service.

Default: `dev-jwt-secret-change-me`

## Testing

Test the gateway:
```bash
curl http://localhost:8080/auth/health
```

Make sure both services are running before testing routes.
