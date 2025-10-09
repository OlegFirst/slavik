import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import type {
  LoginRequest,
  LoginResponse,
  Organization,
  OrganizationInsights,
  QueueTheoryRequest,
  QueueTheoryResponse,
  ScenarioTemplate,
  AdvancedAIRequest,
} from './types';

// Auth
export const useLogin = () => {
  return useMutation({
    mutationFn: async (credentials: LoginRequest) => {
      const { data } = await apiClient.post<LoginResponse>('/api/v1/auth/login', credentials);
      return data;
    },
    onSuccess: (data) => {
      if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', data.access_token);
      }
    },
  });
};

export const useLogout = () => {
  return useMutation({
    mutationFn: async () => {
      await apiClient.post('/api/v1/auth/logout');
    },
    onSuccess: () => {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
      }
    },
  });
};

// Organizations
export const useOrganizations = () => {
  return useQuery({
    queryKey: ['organizations'],
    queryFn: async () => {
      const { data } = await apiClient.get<Organization[]>('/api/v1/organizations/');
      return data;
    },
  });
};

export const useOrganization = (id: string) => {
  return useQuery({
    queryKey: ['organizations', id],
    queryFn: async () => {
      const { data } = await apiClient.get<Organization>(`/api/v1/organizations/${id}`);
      return data;
    },
    enabled: !!id,
  });
};

export const useOrganizationInsights = (orgId: string) => {
  return useQuery({
    queryKey: ['organizations', orgId, 'insights'],
    queryFn: async () => {
      const { data } = await apiClient.get<OrganizationInsights>(`/api/v1/organizations/${orgId}/insights`);
      return data;
    },
    enabled: !!orgId,
    refetchInterval: 60000, // Refetch every minute
  });
};

export const useCreateOrganization = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (org: Partial<Organization>) => {
      const { data } = await apiClient.post<Organization>('/api/v1/organizations/', org);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
    },
  });
};

// Queue Theory BIA
export const useQueueTheoryBIA = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (request: QueueTheoryRequest) => {
      const { data } = await apiClient.post<QueueTheoryResponse>('/api/v1/bia/queue-theory', request);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bia'] });
    },
  });
};

// Scenarios
export const useScenarios = () => {
  return useQuery({
    queryKey: ['scenarios'],
    queryFn: async () => {
      const { data } = await apiClient.get<{ items: ScenarioTemplate[] }>('/api/v1/scenarios/');
      return data.items;
    },
  });
};

export const useAIScenarioGeneration = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (request: AdvancedAIRequest) => {
      const { data } = await apiClient.post<ScenarioTemplate>('/api/v1/scenarios/ai-generate-advanced', request);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenarios'] });
    },
  });
};
