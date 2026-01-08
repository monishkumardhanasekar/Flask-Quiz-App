const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const http = require('http');

const app = express();
const PORT = 8080;

const JWT_SECRET = process.env.JWT_SECRET || 'dev-jwt-secret-change-me';

// CORS middleware
app.use(cors({
  origin: '*',
  credentials: true
}));

// Body parser middleware - must be before proxy
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Service endpoints - use 127.0.0.1 to avoid IPv6 issues
const USER_SERVICE = 'http://127.0.0.1:5001';
const QUIZ_SERVICE = 'http://127.0.0.1:5002';

function authMiddleware(req, res, next) {
  const authHeader = req.headers['authorization'] || '';
  const token = authHeader.startsWith('Bearer ')
    ? authHeader.slice(7).trim()
    : null;

  if (!token) {
    return res.status(401).json({ error: 'missing token' });
  }

  try {
    const payload = jwt.verify(token, JWT_SECRET);
    // Forward user info to downstream services
    req.headers['x-user-id'] = payload.user_id;
    req.user = payload;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'invalid or expired token' });
  }
}

// Public auth routes - no authentication required
app.use('/auth', createProxyMiddleware({
  target: USER_SERVICE,
  changeOrigin: true,
  agent: new http.Agent({ 
    family: 4, // Force IPv4
    keepAlive: false, // Disable keepAlive to avoid connection issues
  }),
  pathRewrite: {
    '^/auth': '', // Remove /auth prefix when forwarding
  },
  logLevel: 'debug', // Enable debug logging
  onProxyReq: (proxyReq, req, res) => {
    console.log(`[Gateway] ${req.method} ${req.url} → ${USER_SERVICE}${req.url.replace('/auth', '')}`);
    // Ensure body is forwarded
    if (req.body && Object.keys(req.body).length > 0) {
      const bodyData = JSON.stringify(req.body);
      proxyReq.setHeader('Content-Type', 'application/json');
      proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
      proxyReq.write(bodyData);
    }
  },
  onError: (err, req, res) => {
    console.error(`[Gateway Error] ${err.message}`, err);
    if (!res.headersSent) {
      res.status(502).json({ error: 'Service unavailable', message: err.message });
    }
  },
  onProxyRes: (proxyRes, req, res) => {
    console.log(`[Gateway] Response: ${proxyRes.statusCode} for ${req.method} ${req.url}`);
  },
  onTimeout: (req, res) => {
    console.error(`[Gateway] Timeout for ${req.method} ${req.url}`);
    if (!res.headersSent) {
      res.status(504).json({ error: 'Gateway timeout' });
    }
  }
}));

// Protected quiz routes - requires JWT validation
app.use('/api/quiz',
  authMiddleware,
  createProxyMiddleware({
    target: QUIZ_SERVICE,
    changeOrigin: true,
    agent: new http.Agent({ 
      family: 4, // Force IPv4
      keepAlive: true,
      timeout: 5000
    }),
    timeout: 5000,
    pathRewrite: {
      '^/api/quiz': '', // Remove /api/quiz prefix when forwarding
    },
    onProxyReq: (proxyReq, req, res) => {
      // Forward user id header
      if (req.headers['x-user-id']) {
        proxyReq.setHeader('x-user-id', req.headers['x-user-id']);
      }
      console.log(`[Gateway] ${req.method} ${req.url} → ${QUIZ_SERVICE}`);
    },
    onError: (err, req, res) => {
      console.error(`[Gateway Error] ${err.message}`);
      if (!res.headersSent) {
        res.status(502).json({ error: 'Service unavailable', message: err.message });
      }
    }
  })
);

// Protected user routes - requires JWT validation
app.use('/api/user',
  authMiddleware,
  createProxyMiddleware({
    target: USER_SERVICE,
    changeOrigin: true,
    agent: new http.Agent({ 
      family: 4, // Force IPv4
      keepAlive: true,
      timeout: 5000
    }),
    timeout: 5000,
    pathRewrite: {
      '^/api/user': '', // Remove /api/user prefix when forwarding
    },
    onProxyReq: (proxyReq, req, res) => {
      if (req.headers['x-user-id']) {
        proxyReq.setHeader('x-user-id', req.headers['x-user-id']);
      }
      console.log(`[Gateway] ${req.method} ${req.url} → ${USER_SERVICE}`);
    },
    onError: (err, req, res) => {
      console.error(`[Gateway Error] ${err.message}`);
      if (!res.headersSent) {
        res.status(502).json({ error: 'Service unavailable', message: err.message });
      }
    }
  })
);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'gateway' });
});

app.listen(PORT, () => {
  console.log(`🚀 Gateway running on http://localhost:${PORT}`);
  console.log(`   Auth routes: /auth/* → ${USER_SERVICE}`);
  console.log(`   Quiz routes: /api/quiz/* → ${QUIZ_SERVICE}`);
  console.log(`   User routes: /api/user/* → ${USER_SERVICE}`);
});

