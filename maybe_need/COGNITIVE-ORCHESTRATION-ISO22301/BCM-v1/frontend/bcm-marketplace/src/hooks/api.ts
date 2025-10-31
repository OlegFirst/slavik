import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import {
  specialistsAPI,
  requestsAPI,
  proposalsAPI,
  projectsAPI,
  reviewsAPI,
  referenceAPI,
  solutionsAPI,
  knowledgeAPI,
  casesAPI,
} from '@/lib/api';
import { SearchFilters, Specialist, ServiceRequest, ServiceProposal, Project } from '@/types';

// Query keys
export const queryKeys = {
  specialists: {
    all: ['specialists'] as const,
    list: (filters?: SearchFilters) => [...queryKeys.specialists.all, 'list', filters] as const,
    detail: (id: string) => [...queryKeys.specialists.all, 'detail', id] as const,
    reviews: (id: string) => [...queryKeys.specialists.all, 'reviews', id] as const,
  },
  requests: {
    all: ['requests'] as const,
    list: (params?: any) => [...queryKeys.requests.all, 'list', params] as const,
    detail: (id: string) => [...queryKeys.requests.all, 'detail', id] as const,
    proposals: (id: string) => [...queryKeys.requests.all, 'proposals', id] as const,
  },
  proposals: {
    all: ['proposals'] as const,
    list: (params?: any) => [...queryKeys.proposals.all, 'list', params] as const,
    detail: (id: string) => [...queryKeys.proposals.all, 'detail', id] as const,
  },
  projects: {
    all: ['projects'] as const,
    list: (params?: any) => [...queryKeys.projects.all, 'list', params] as const,
    detail: (id: string) => [...queryKeys.projects.all, 'detail', id] as const,
  },
  reference: {
    specializations: ['reference', 'specializations'] as const,
    industries: ['reference', 'industries'] as const,
    countries: ['reference', 'countries'] as const,
    languages: ['reference', 'languages'] as const,
  },
  solutions: {
    all: ['solutions'] as const,
    list: (filters?: any) => [...queryKeys.solutions.all, 'list', filters] as const,
    detail: (id: string) => [...queryKeys.solutions.all, 'detail', id] as const,
  },
  knowledge: {
    all: ['knowledge'] as const,
    list: (filters?: any) => [...queryKeys.knowledge.all, 'list', filters] as const,
    detail: (id: string) => [...queryKeys.knowledge.all, 'detail', id] as const,
  },
  cases: {
    all: ['cases'] as const,
    list: (filters?: any) => [...queryKeys.cases.all, 'list', filters] as const,
    detail: (id: string) => [...queryKeys.cases.all, 'detail', id] as const,
  },
};

// Specialists hooks
export const useSpecialists = (filters?: SearchFilters) => {
  return useQuery({
    queryKey: queryKeys.specialists.list(filters),
    queryFn: () => specialistsAPI.search(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useSpecialist = (id: string) => {
  return useQuery({
    queryKey: queryKeys.specialists.detail(id),
    queryFn: () => specialistsAPI.getById(id),
    enabled: !!id,
  });
};

export const useSpecialistReviews = (id: string) => {
  return useQuery({
    queryKey: queryKeys.specialists.reviews(id),
    queryFn: () => specialistsAPI.getReviews(id),
    enabled: !!id,
  });
};

export const useCreateSpecialist = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: specialistsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.specialists.all });
      toast.success('Профиль специалиста создан успешно!');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Ошибка при создании профиля');
    },
  });
};

export const useUpdateSpecialist = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      specialistsAPI.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.specialists.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.specialists.all });
      toast.success('Профиль обновлен успешно!');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Ошибка при обновлении профиля');
    },
  });
};

// Service Requests hooks
export const useServiceRequests = (params?: any) => {
  return useQuery({
    queryKey: queryKeys.requests.list(params),
    queryFn: () => requestsAPI.getAll(params),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

export const useServiceRequest = (id: string) => {
  return useQuery({
    queryKey: queryKeys.requests.detail(id),
    queryFn: () => requestsAPI.getById(id),
    enabled: !!id,
  });
};

export const useRequestProposals = (id: string) => {
  return useQuery({
    queryKey: queryKeys.requests.proposals(id),
    queryFn: () => requestsAPI.getProposals(id),
    enabled: !!id,
  });
};

export const useCreateServiceRequest = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: requestsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.requests.all });
      toast.success('Запрос на услуги создан успешно!');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Ошибка при создании запроса');
    },
  });
};

export const useUpdateServiceRequest = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      requestsAPI.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.requests.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.requests.all });
      toast.success('Запрос обновлен успешно!');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Ошибка при обновлении запроса');
    },
  });
};

export const useAssignSpecialist = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ requestId, proposalId }: { requestId: string; proposalId: string }) =>
      requestsAPI.assign(requestId, proposalId),
    onSuccess: (_, { requestId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.requests.detail(requestId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.requests.proposals(requestId) });
      toast.success('Специалист назначен на проект!');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Ошибка при назначении специалиста');
    },
  });
};

// Proposals hooks
export const useProposals = (params?: any) => {
  return useQuery({
    queryKey: queryKeys.proposals.list(params),
    queryFn: () => proposalsAPI.getAll(params),
    staleTime: 2 * 60 * 1000,
  });
};

export const useProposal = (id: string) => {
  return useQuery({
    queryKey: queryKeys.proposals.detail(id),
    queryFn: () => proposalsAPI.getById(id),
    enabled: !!id,
  });
};

export const useCreateProposal = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: proposalsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.all });
      toast.success('Предложение отправлено успешно!');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Ошибка при отправке предложения');
    },
  });
};

export const useSubmitProposal = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => proposalsAPI.submit(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.all });
      toast.success('Предложение подано на рассмотрение!');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Ошибка при подаче предложения');
    },
  });
};

export const useAcceptProposal = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => proposalsAPI.accept(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all });
      toast.success('Предложение принято! Проект создан.');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Ошибка при принятии предложения');
    },
  });
};

export const useRejectProposal = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      proposalsAPI.reject(id, reason),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.all });
      toast.success('Предложение отклонено');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Ошибка при отклонении предложения');
    },
  });
};

// Projects hooks
export const useProjects = (params?: any) => {
  return useQuery({
    queryKey: queryKeys.projects.list(params),
    queryFn: () => projectsAPI.getAll(params),
    staleTime: 2 * 60 * 1000,
  });
};

export const useProject = (id: string) => {
  return useQuery({
    queryKey: queryKeys.projects.detail(id),
    queryFn: () => projectsAPI.getById(id),
    enabled: !!id,
  });
};

export const useStartProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => projectsAPI.start(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all });
      toast.success('Проект запущен!');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Ошибка при запуске проекта');
    },
  });
};

export const useCompleteProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => projectsAPI.complete(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all });
      toast.success('Проект завершен!');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Ошибка при завершении проекта');
    },
  });
};

// Milestone hooks
export const useCreateMilestone = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ projectId, data }: { projectId: string; data: any }) =>
      projectsAPI.createMilestone(projectId, data),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.detail(projectId) });
      toast.success('Веха создана успешно!');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Ошибка при создании вехи');
    },
  });
};

export const useSubmitMilestone = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ projectId, milestoneId }: { projectId: string; milestoneId: string }) =>
      projectsAPI.submitMilestone(projectId, milestoneId),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.detail(projectId) });
      toast.success('Веха отправлена на проверку!');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Ошибка при отправке вехи');
    },
  });
};

export const useApproveMilestone = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ projectId, milestoneId }: { projectId: string; milestoneId: string }) =>
      projectsAPI.approveMilestone(projectId, milestoneId),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.detail(projectId) });
      toast.success('Веха утверждена!');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Ошибка при утверждении вехи');
    },
  });
};

// Timesheet hooks
export const useCreateTimesheet = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ projectId, data }: { projectId: string; data: any }) =>
      projectsAPI.createTimesheet(projectId, data),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.detail(projectId) });
      toast.success('Время добавлено успешно!');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Ошибка при добавлении времени');
    },
  });
};

// Reference data hooks
export const useSpecializations = () => {
  return useQuery({
    queryKey: queryKeys.reference.specializations,
    queryFn: referenceAPI.getSpecializations,
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
};

export const useIndustries = () => {
  return useQuery({
    queryKey: queryKeys.reference.industries,
    queryFn: referenceAPI.getIndustries,
    staleTime: 30 * 60 * 1000,
  });
};

export const useCountries = () => {
  return useQuery({
    queryKey: queryKeys.reference.countries,
    queryFn: referenceAPI.getCountries,
    staleTime: 60 * 60 * 1000, // 1 hour
  });
};

export const useLanguages = () => {
  return useQuery({
    queryKey: queryKeys.reference.languages,
    queryFn: referenceAPI.getLanguages,
    staleTime: 60 * 60 * 1000,
  });
};

// Solutions hooks
export const useSolutions = (filters?: any) => {
  return useQuery({
    queryKey: queryKeys.solutions.list(filters),
    queryFn: () => solutionsAPI.search(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useSolution = (id: string) => {
  return useQuery({
    queryKey: queryKeys.solutions.detail(id),
    queryFn: () => solutionsAPI.getById(id),
    enabled: !!id,
  });
};

export const usePurchaseSolution = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      solutionsAPI.purchase(id, data),
    onSuccess: () => {
      toast.success('Solution purchased successfully!');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Error purchasing solution');
    },
  });
};

// Knowledge Base hooks
export const useKnowledgeArticles = (filters?: any) => {
  return useQuery({
    queryKey: queryKeys.knowledge.list(filters),
    queryFn: () => knowledgeAPI.search(filters),
    staleTime: 5 * 60 * 1000,
  });
};

export const useKnowledgeArticle = (id: string) => {
  return useQuery({
    queryKey: queryKeys.knowledge.detail(id),
    queryFn: () => knowledgeAPI.getById(id),
    enabled: !!id,
  });
};

export const useBookmarkArticle = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => knowledgeAPI.bookmark(id),
    onSuccess: () => {
      toast.success('Article bookmarked!');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Error bookmarking article');
    },
  });
};

// Case Studies hooks
export const useCaseStudies = (filters?: any) => {
  return useQuery({
    queryKey: queryKeys.cases.list(filters),
    queryFn: () => casesAPI.search(filters),
    staleTime: 5 * 60 * 1000,
  });
};

export const useCaseStudy = (id: string) => {
  return useQuery({
    queryKey: queryKeys.cases.detail(id),
    queryFn: () => casesAPI.getById(id),
    enabled: !!id,
  });
};

export const useLikeCaseStudy = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => casesAPI.like(id),
    onSuccess: () => {
      toast.success('Case study liked!');
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Error liking case study');
    },
  });
};