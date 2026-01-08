# Express Gateway

This is the API Gateway for the Quiz App microservices architecture.

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
- Routes:
  - `/auth/*` → User Service (public, no auth required)
  - `/api/quiz/*` → Quiz Service (protected, requires JWT - will add in step 4)
  - `/api/user/*` → User Service (protected, requires JWT - will add in step 4)

## Service Ports

- User Service: **5001**
- Quiz Service: **5000**

## Testing

Test the gateway:
```bash
curl http://localhost:8080/health
```

Make sure both services are running before testing routes.

