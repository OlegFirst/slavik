import axios from 'axios';

// API Gateway URL (use environment variable or default to localhost)
const API_GATEWAY_URL = import.meta.env.VITE_API_GATEWAY_URL || 'http://localhost:8888';

// BCM API Client - connects to our API Gateway
const bcmAPI = axios.create({
  baseURL: API_GATEWAY_URL,
  timeout: 30000, // Increased for gateway processing
  headers: {
    'Content-Type': 'application/json',
  }
});

// Prometheus API Client
const prometheusAPI = axios.create({
  baseURL: '/prometheus/api/v1',
  timeout: 5000,
});

// Docker API Client (через backend proxy)
const dockerAPI = axios.create({
  baseURL: '/api/docker',
  timeout: 15000,
});

// Request interceptors for authentication
bcmAPI.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptors for error handling
[bcmAPI, prometheusAPI, dockerAPI].forEach(api => {
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      console.error('API Error:', error.response?.data || error.message);
      return Promise.reject(error);
    }
  );
});

export { bcmAPI, prometheusAPI, dockerAPI };
