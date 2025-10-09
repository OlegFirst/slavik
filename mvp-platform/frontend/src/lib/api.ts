/**
 * API Client
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // ============================================
  // AUTH
  // ============================================

  async register(email: string, password: string, fullName?: string, organizationName?: string) {
    const response = await this.client.post('/api/auth/register', {
      email,
      password,
      full_name: fullName,
      organization_name: organizationName,
    });
    return response.data;
  }

  async login(email: string, password: string) {
    const response = await this.client.post('/api/auth/login', {
      email,
      password,
    });
    return response.data;
  }

  async getMe() {
    const response = await this.client.get('/api/auth/me');
    return response.data;
  }

  async logout() {
    const response = await this.client.post('/api/auth/logout');
    return response.data;
  }

  // ============================================
  // ORGANIZATIONS
  // ============================================

  async createOrganization(data: any) {
    const response = await this.client.post('/api/organizations', data);
    return response.data;
  }

  async getMyOrganization() {
    const response = await this.client.get('/api/organizations/my');
    return response.data;
  }

  async getOrganization(orgId: string) {
    const response = await this.client.get(`/api/organizations/${orgId}`);
    return response.data;
  }

  async updateOrganization(orgId: string, data: any) {
    const response = await this.client.patch(`/api/organizations/${orgId}`, data);
    return response.data;
  }

  async listProcesses(orgId: string) {
    const response = await this.client.get(`/api/organizations/${orgId}/processes`);
    return response.data;
  }

  async createProcess(orgId: string, data: any) {
    const response = await this.client.post(`/api/organizations/${orgId}/processes`, data);
    return response.data;
  }

  async generateProcessesAI(orgId: string, industry: string, size: number, country: string) {
    const response = await this.client.post(`/api/organizations/${orgId}/processes/generate-ai`, {
      industry,
      size,
      country,
    });
    return response.data;
  }

  // ============================================
  // BIA
  // ============================================

  async createBIA(orgId: string, data: any) {
    const response = await this.client.post(`/api/bia?org_id=${orgId}`, data);
    return response.data;
  }

  async listBIAs(orgId: string, status?: string) {
    const params = status ? `?status=${status}` : '';
    const response = await this.client.get(`/api/bia?org_id=${orgId}${params}`);
    return response.data;
  }

  async getBIA(analysisId: string) {
    const response = await this.client.get(`/api/bia/${analysisId}`);
    return response.data;
  }

  async updateBIA(analysisId: string, data: any) {
    const response = await this.client.patch(`/api/bia/${analysisId}`, data);
    return response.data;
  }

  async listBIAProcesses(analysisId: string, criticality?: string) {
    const params = criticality ? `?criticality=${criticality}` : '';
    const response = await this.client.get(`/api/bia/${analysisId}/processes${params}`);
    return response.data;
  }

  async createBIAProcess(analysisId: string, data: any) {
    const response = await this.client.post(`/api/bia/${analysisId}/processes`, data);
    return response.data;
  }

  async updateBIAProcess(analysisId: string, processId: string, data: any) {
    const response = await this.client.patch(`/api/bia/${analysisId}/processes/${processId}`, data);
    return response.data;
  }

  async generateQuestionnaire(analysisId: string, data: any) {
    const response = await this.client.post(`/api/bia/${analysisId}/questionnaire/generate`, data);
    return response.data;
  }

  async getQuestions(analysisId: string) {
    const response = await this.client.get(`/api/bia/${analysisId}/questionnaire/questions`);
    return response.data;
  }

  async submitAnswers(analysisId: string, answers: any[]) {
    const response = await this.client.post(`/api/bia/${analysisId}/questionnaire/answers`, answers);
    return response.data;
  }

  async listBIAFindings(analysisId: string, findingType?: string, severity?: string) {
    let params = '';
    if (findingType) params += `?finding_type=${findingType}`;
    if (severity) params += params ? `&severity=${severity}` : `?severity=${severity}`;
    const response = await this.client.get(`/api/bia/${analysisId}/findings${params}`);
    return response.data;
  }

  async calculateRTOAI(analysisId: string, data: any) {
    const response = await this.client.post(`/api/bia/${analysisId}/ai/calculate-rto`, data);
    return response.data;
  }
}

export const api = new APIClient();
