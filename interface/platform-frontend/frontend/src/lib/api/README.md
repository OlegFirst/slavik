# API Layer Documentation

Production-ready API client with interceptors, error handling, and retry logic.

## Overview

This API layer provides a robust, type-safe HTTP client for the platform frontend with:

- **Automatic authentication** - JWT token injection and refresh
- **Error handling** - Standardized error classes with detailed information
- **Retry logic** - Exponential backoff with jitter for failed requests
- **Request deduplication** - Prevents duplicate identical requests
- **Progress tracking** - Upload/download progress callbacks
- **Type safety** - Full TypeScript support with generics

## Quick Start

```typescript
import { get, post, put, del } from '@/lib/api';

// Simple GET request
const users = await get<User[]>('/users');

// POST with data
const newUser = await post<User>('/users', {
  name: 'John Doe',
  email: 'john@example.com',
});

// PUT to update
const updated = await put<User>(`/users/${userId}`, {
  name: 'Jane Doe',
});

// DELETE
await del(`/users/${userId}`);
```

## Core Components

### 1. API Client (`client.ts`)

Base Axios client with interceptors for authentication and error handling.

**Features:**
- JWT token injection
- Token refresh on 401
- Tenant ID headers
- Request ID tracking
- Request deduplication

**Configuration:**

```typescript
import { apiClient, APIClient } from '@/lib/api';

// Use default client
apiClient.getAxiosInstance();

// Create custom client
const customClient = new APIClient({
  baseURL: 'https://api.example.com',
  timeout: 60000,
  headers: {
    'X-Custom-Header': 'value',
  },
});

// Set custom token refresh callback
apiClient.setTokenRefreshCallback(async () => {
  const response = await fetch('/api/auth/refresh');
  const { token } = await response.json();
  return token;
});
```

### 2. Error Handling (`errors.ts`)

Standardized error classes for different HTTP status codes.

**Error Types:**

- `APIError` - Base error class
- `AuthenticationError` - 401 Unauthorized
- `AuthorizationError` - 403 Forbidden
- `ValidationError` - 400/422 with field errors
- `NotFoundError` - 404 Not Found
- `ConflictError` - 409 Conflict
- `RateLimitError` - 429 Rate Limit
- `ServerError` - 500+ Server errors
- `NetworkError` - No response from server
- `TimeoutError` - Request timeout

**Usage:**

```typescript
import {
  get,
  isValidationError,
  isAuthenticationError,
  ValidationError
} from '@/lib/api';

try {
  await get('/users');
} catch (error) {
  if (isValidationError(error)) {
    console.log('Validation errors:', error.errors);
  } else if (isAuthenticationError(error)) {
    // Redirect to login
    router.push('/login');
  } else {
    console.error('Error:', error.message);
  }
}
```

### 3. Retry Logic (`retry.ts`)

Automatic retry with exponential backoff and jitter.

**Features:**
- Configurable max retries (default: 3)
- Exponential backoff (1s, 2s, 4s, 8s)
- Jitter to prevent thundering herd
- Smart retry conditions (only 5xx and network errors)

**Configuration:**

```typescript
import { get } from '@/lib/api';

// Automatic retry enabled by default
const data = await get('/users');

// Disable retry
const data = await get('/users', { retry: false });

// Custom retry settings
const data = await get('/users', {
  retry: true,
  maxRetries: 5,
});

// Manual retry with custom logic
import { retryRequest } from '@/lib/api';

const data = await retryRequest(
  () => fetch('/api/data'),
  {
    maxRetries: 5,
    baseDelay: 2000,
    maxDelay: 60000,
    shouldRetry: (error) => error.status >= 500,
  }
);
```

### 4. Request Methods (`request.ts`)

High-level request wrapper with convenience methods.

**Basic Requests:**

```typescript
import { get, post, put, patch, del } from '@/lib/api';

// GET
const users = await get<User[]>('/users');
const user = await get<User>(`/users/${id}`);

// POST
const newUser = await post<User>('/users', userData);

// PUT (full update)
const updated = await put<User>(`/users/${id}`, userData);

// PATCH (partial update)
const patched = await patch<User>(`/users/${id}`, { name: 'New Name' });

// DELETE
await del(`/users/${id}`);
```

**Advanced Options:**

```typescript
import { request, createCancelToken } from '@/lib/api';

// Request with all options
const cancelToken = createCancelToken();

const data = await request<MyType>('/endpoint', {
  method: 'POST',
  data: { key: 'value' },
  params: { filter: 'active' },
  headers: { 'X-Custom': 'header' },
  retry: true,
  maxRetries: 3,
  deduplicate: true,
  timeout: 10000,
  cancelToken,
  onUploadProgress: (event) => {
    console.log(`Uploaded: ${event.loaded}/${event.total}`);
  },
});

// Cancel request
cancelToken.cancel('Request cancelled by user');
```

**File Upload:**

```typescript
import { uploadFile } from '@/lib/api';

const file = document.querySelector('input[type="file"]').files[0];

const response = await uploadFile(
  '/upload',
  file,
  'document', // field name
  { category: 'report', year: 2024 }, // additional data
  (percent) => {
    console.log(`Upload progress: ${percent}%`);
  }
);
```

**File Download:**

```typescript
import { downloadFile } from '@/lib/api';

// Download and save file
await downloadFile('/files/report.pdf', 'report.pdf', (percent) => {
  console.log(`Download progress: ${percent}%`);
});

// Get blob without triggering download
const blob = await downloadFile('/files/report.pdf');
```

**Pagination:**

```typescript
import { getPaginated, PaginatedResponse } from '@/lib/api';

const response = await getPaginated<User>('/users', {
  page: 1,
  pageSize: 20,
  params: { status: 'active' },
});

console.log(response.data); // User[]
console.log(response.meta); // { page, pageSize, total, totalPages }
```

**Batch Requests:**

```typescript
import { batch, sequence } from '@/lib/api';

// Parallel requests
const [users, roles, settings] = await batch([
  { url: '/users' },
  { url: '/roles' },
  { url: '/settings' },
]);

// Sequential requests (one after another)
const [create, update, notify] = await sequence([
  { url: '/users', options: { method: 'POST', data: userData } },
  { url: `/users/${id}`, options: { method: 'PUT', data: updateData } },
  { url: '/notify', options: { method: 'POST', data: notifyData } },
]);
```

## Environment Variables

```env
# API base URL (required)
NEXT_PUBLIC_API_URL=http://localhost:8024

# Optional: API timeout in milliseconds
NEXT_PUBLIC_API_TIMEOUT=30000
```

## Error Handling Best Practices

```typescript
import {
  get,
  APIError,
  isValidationError,
  isAuthenticationError,
  isNetworkError,
} from '@/lib/api';

async function fetchUser(id: string) {
  try {
    return await get<User>(`/users/${id}`);
  } catch (error) {
    // Check specific error types
    if (isValidationError(error)) {
      toast.error('Invalid user data', {
        description: Object.entries(error.errors || {})
          .map(([field, errors]) => `${field}: ${errors.join(', ')}`)
          .join('\n'),
      });
    } else if (isAuthenticationError(error)) {
      // Redirect to login
      router.push('/login');
    } else if (isNetworkError(error)) {
      toast.error('Network error', {
        description: 'Please check your internet connection',
      });
    } else {
      // Generic error handling
      toast.error('Error', {
        description: error.message,
      });
    }

    throw error; // Re-throw if needed
  }
}
```

## React Integration Examples

### With React Query

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';
import { get, post } from '@/lib/api';

// Query
function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => get<User[]>('/users'),
  });
}

// Mutation
function useCreateUser() {
  return useMutation({
    mutationFn: (data: CreateUserData) => post<User>('/users', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}
```

### With useState

```typescript
import { useEffect, useState } from 'react';
import { get } from '@/lib/api';

function UserList() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    get<User[]>('/users')
      .then(setUsers)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  return <div>{/* render users */}</div>;
}
```

## Testing

```typescript
import { apiClient } from '@/lib/api';
import MockAdapter from 'axios-mock-adapter';

describe('API Client', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient.getAxiosInstance());
  });

  afterEach(() => {
    mock.restore();
  });

  it('should fetch users', async () => {
    const users = [{ id: 1, name: 'John' }];
    mock.onGet('/users').reply(200, users);

    const result = await get<User[]>('/users');
    expect(result).toEqual(users);
  });

  it('should handle errors', async () => {
    mock.onGet('/users').reply(500, { message: 'Server error' });

    await expect(get('/users')).rejects.toThrow('Server error');
  });
});
```

## Architecture

```
src/lib/api/
├── client.ts          # Axios client with interceptors (362 lines)
├── errors.ts          # Error classes and parsing (329 lines)
├── retry.ts           # Retry logic with backoff (247 lines)
├── request.ts         # High-level request wrapper (336 lines)
├── index.ts           # Main exports (71 lines)
└── README.md          # This file
```

## Performance Considerations

1. **Request Deduplication**: Identical concurrent requests are automatically deduplicated
2. **Retry Logic**: Smart retry only on retryable errors (5xx, network issues)
3. **Exponential Backoff**: Prevents overwhelming the server during issues
4. **Jitter**: Randomized delays prevent thundering herd problem
5. **Cancel Tokens**: Support for request cancellation to prevent memory leaks

## Security Features

1. **Automatic Token Injection**: JWT tokens added to all requests
2. **Token Refresh**: Automatic token refresh on 401 errors
3. **Tenant Isolation**: Tenant ID headers for multi-tenant applications
4. **Request Tracing**: Unique request IDs for debugging and monitoring
5. **HTTPS Enforcement**: Configurable via environment variables

## License

Proprietary - Part of AI Platform ISO
