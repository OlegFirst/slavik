import axios from 'axios';
import { ApiResponse, ApiError } from '@/types';

// Create axios instance
export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8069',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Generic API helper functions
export const apiRequest = async <T>(
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH',
  url: string,
  data?: any,
  params?: any
): Promise<T> => {
  try {
    const response = await api.request({
      method,
      url,
      data,
      params,
    });

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw error.response.data;
    }
    throw error;
  }
};

// Specific API endpoints
export const authAPI = {
  login: (credentials: { email: string; password: string }) =>
    apiRequest<ApiResponse<{ token: string; user: any }>>('POST', '/api/v1/auth/login', credentials),

  register: (userData: any) =>
    apiRequest<ApiResponse<{ token: string; user: any }>>('POST', '/api/v1/auth/register', userData),

  me: () =>
    apiRequest<ApiResponse<any>>('POST', '/api/v1/auth/me', {}),

  logout: () =>
    apiRequest<ApiResponse<null>>('POST', '/api/v1/auth/logout', {}),
};

export const specialistsAPI = {
  getAll: (params?: any) =>
    apiRequest<ApiResponse<any>>('GET', '/api/v1/specialists', null, params),

  getById: (id: string) =>
    apiRequest<ApiResponse<any>>('POST', `/api/v1/specialists/${id}`, {}),

  create: (data: any) =>
    apiRequest<ApiResponse<any>>('POST', '/api/v1/specialists', data),

  update: (id: string, data: any) =>
    apiRequest<ApiResponse<any>>('PUT', `/api/v1/specialists/${id}`, data),

  getReviews: (id: string) =>
    apiRequest<ApiResponse<any>>('POST', `/api/v1/specialists/${id}/reviews`, {}),

  search: (filters: any) =>
    apiRequest<ApiResponse<any>>('POST', '/api/v1/specialists/search', filters),
};

export const requestsAPI = {
  getAll: (params?: any) =>
    apiRequest<ApiResponse<any>>('POST', '/api/v1/requests', params || {}),

  getById: (id: string) =>
    apiRequest<ApiResponse<any>>('POST', `/api/v1/requests/${id}`, {}),

  create: (data: any) =>
    apiRequest<ApiResponse<any>>('POST', '/api/v1/requests/create', data),

  update: (id: string, data: any) =>
    apiRequest<ApiResponse<any>>('POST', `/api/v1/requests/${id}/update`, data),

  getProposals: (id: string) =>
    apiRequest<ApiResponse<any>>('POST', `/api/v1/requests/${id}/proposals`, {}),

  invite: (id: string, specialistIds: string[]) =>
    apiRequest<ApiResponse<any>>('POST', `/api/v1/requests/${id}/invite`, { specialistIds }),

  assign: (id: string, proposalId: string) =>
    apiRequest<ApiResponse<any>>('POST', `/api/v1/requests/${id}/assign`, { proposalId }),
};

export const proposalsAPI = {
  getAll: (params?: any) =>
    apiRequest<ApiResponse<any>>('GET', '/proposals', null, params),

  getById: (id: string) =>
    apiRequest<ApiResponse<any>>('GET', `/proposals/${id}`),

  create: (data: any) =>
    apiRequest<ApiResponse<any>>('POST', '/proposals', data),

  update: (id: string, data: any) =>
    apiRequest<ApiResponse<any>>('PUT', `/proposals/${id}`, data),

  submit: (id: string) =>
    apiRequest<ApiResponse<any>>('POST', `/proposals/${id}/submit`),

  accept: (id: string) =>
    apiRequest<ApiResponse<any>>('POST', `/proposals/${id}/accept`),

  reject: (id: string, reason?: string) =>
    apiRequest<ApiResponse<any>>('POST', `/proposals/${id}/reject`, { reason }),
};

export const projectsAPI = {
  getAll: (params?: any) =>
    apiRequest<ApiResponse<any>>('GET', '/projects', null, params),

  getById: (id: string) =>
    apiRequest<ApiResponse<any>>('GET', `/projects/${id}`),

  update: (id: string, data: any) =>
    apiRequest<ApiResponse<any>>('PUT', `/projects/${id}`, data),

  start: (id: string) =>
    apiRequest<ApiResponse<any>>('POST', `/projects/${id}/start`),

  complete: (id: string) =>
    apiRequest<ApiResponse<any>>('POST', `/projects/${id}/complete`),

  // Milestones
  createMilestone: (projectId: string, data: any) =>
    apiRequest<ApiResponse<any>>('POST', `/projects/${projectId}/milestones`, data),

  updateMilestone: (projectId: string, milestoneId: string, data: any) =>
    apiRequest<ApiResponse<any>>('PUT', `/projects/${projectId}/milestones/${milestoneId}`, data),

  submitMilestone: (projectId: string, milestoneId: string) =>
    apiRequest<ApiResponse<any>>('POST', `/projects/${projectId}/milestones/${milestoneId}/submit`),

  approveMilestone: (projectId: string, milestoneId: string) =>
    apiRequest<ApiResponse<any>>('POST', `/projects/${projectId}/milestones/${milestoneId}/approve`),

  // Timesheets
  createTimesheet: (projectId: string, data: any) =>
    apiRequest<ApiResponse<any>>('POST', `/projects/${projectId}/timesheets`, data),

  updateTimesheet: (projectId: string, timesheetId: string, data: any) =>
    apiRequest<ApiResponse<any>>('PUT', `/projects/${projectId}/timesheets/${timesheetId}`, data),

  submitTimesheet: (projectId: string, timesheetId: string) =>
    apiRequest<ApiResponse<any>>('POST', `/projects/${projectId}/timesheets/${timesheetId}/submit`),

  approveTimesheet: (projectId: string, timesheetId: string) =>
    apiRequest<ApiResponse<any>>('POST', `/projects/${projectId}/timesheets/${timesheetId}/approve`),
};

export const reviewsAPI = {
  create: (data: any) =>
    apiRequest<ApiResponse<any>>('POST', '/reviews', data),

  update: (id: string, data: any) =>
    apiRequest<ApiResponse<any>>('PUT', `/reviews/${id}`, data),

  respond: (id: string, response: string) =>
    apiRequest<ApiResponse<any>>('POST', `/reviews/${id}/respond`, { response }),

  markHelpful: (id: string, helpful: boolean) =>
    apiRequest<ApiResponse<any>>('POST', `/reviews/${id}/helpful`, { helpful }),
};

// Solutions API
export const solutionsAPI = {
  search: (filters: any) =>
    apiRequest<ApiResponse<any>>('POST', '/api/v1/solutions/search', filters),

  getById: (id: string) =>
    apiRequest<ApiResponse<any>>('POST', `/api/v1/solutions/${id}`, {}),

  purchase: (id: string, data: any) =>
    apiRequest<ApiResponse<any>>('POST', `/api/v1/solutions/${id}/purchase`, data),

  download: (id: string) =>
    apiRequest<ApiResponse<any>>('POST', `/api/v1/solutions/${id}/download`, {}),
};

// Knowledge Base API
export const knowledgeAPI = {
  search: (filters: any) =>
    apiRequest<ApiResponse<any>>('POST', '/api/v1/knowledge/search', filters),

  getById: (id: string) =>
    apiRequest<ApiResponse<any>>('POST', `/api/v1/knowledge/${id}`, {}),

  bookmark: (id: string) =>
    apiRequest<ApiResponse<any>>('POST', `/api/v1/knowledge/${id}/bookmark`, {}),

  rate: (id: string, rating: number) =>
    apiRequest<ApiResponse<any>>('POST', `/api/v1/knowledge/${id}/rate`, { rating }),
};

// Case Studies API
export const casesAPI = {
  search: (filters: any) =>
    apiRequest<ApiResponse<any>>('POST', '/api/v1/cases/search', filters),

  getById: (id: string) =>
    apiRequest<ApiResponse<any>>('POST', `/api/v1/cases/${id}`, {}),

  like: (id: string) =>
    apiRequest<ApiResponse<any>>('POST', `/api/v1/cases/${id}/like`, {}),

  download: (id: string) =>
    apiRequest<ApiResponse<any>>('POST', `/api/v1/cases/${id}/download`, {}),
};

// Reference data APIs
export const referenceAPI = {
  getSpecializations: () =>
    apiRequest<ApiResponse<any>>('POST', '/api/v1/reference/specializations', {}),

  getIndustries: () =>
    apiRequest<ApiResponse<any>>('POST', '/api/v1/reference/industries', {}),

  getCountries: () =>
    apiRequest<ApiResponse<any>>('POST', '/api/v1/reference/countries', {}),

  getLanguages: () =>
    apiRequest<ApiResponse<any>>('POST', '/api/v1/reference/languages', {}),
};