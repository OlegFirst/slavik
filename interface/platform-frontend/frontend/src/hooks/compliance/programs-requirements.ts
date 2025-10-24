/**
 * Compliance Module - Programs & Requirements Hooks
 * React Query hooks for Compliance Programs and Requirements management
 *
 * Created: 2025-10-24
 * Agent: 18 (Compliance Module Data Layer)
 *
 * Total Hooks: 25
 * - Programs: 12 hooks (4 query + 8 mutation)
 * - Requirements: 13 hooks (5 query + 8 mutation)
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type {
  ComplianceProgram,
  ComplianceProgramCreate,
  ComplianceProgramUpdate,
  ComplianceRequirement,
  ComplianceRequirementCreate,
  ComplianceRequirementUpdate,
  ComplianceStandard,
  RequirementCategory,
} from '@/types/compliance';

// ============================================================================
// QUERY KEY FACTORIES
// ============================================================================

/**
 * Query key factory for compliance programs
 * Provides centralized, type-safe query key management
 */
export const programQueryKeys = {
  all: ['compliance', 'programs'] as const,
  lists: () => [...programQueryKeys.all, 'list'] as const,
  list: (params: UseProgramsParams) => [...programQueryKeys.lists(), params] as const,
  details: () => [...programQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...programQueryKeys.details(), id] as const,
  byStandard: (standard: ComplianceStandard) =>
    [...programQueryKeys.all, 'byStandard', standard] as const,
};

/**
 * Query key factory for compliance requirements
 * Provides centralized, type-safe query key management
 */
export const requirementQueryKeys = {
  all: ['compliance', 'requirements'] as const,
  lists: () => [...requirementQueryKeys.all, 'list'] as const,
  list: (params: UseRequirementsParams) => [...requirementQueryKeys.lists(), params] as const,
  details: () => [...requirementQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...requirementQueryKeys.details(), id] as const,
  byStandard: (standard: ComplianceStandard) =>
    [...requirementQueryKeys.all, 'byStandard', standard] as const,
  byCategory: (category: RequirementCategory) =>
    [...requirementQueryKeys.all, 'byCategory', category] as const,
};

// ============================================================================
// TYPE DEFINITIONS - PROGRAMS
// ============================================================================

/**
 * Parameters for listing compliance programs with filters
 */
export interface UseProgramsParams {
  organization_id: string;
  standard?: ComplianceStandard;
  status?: string;
  search?: string;
  page?: number;
  limit?: number;
  enabled?: boolean;
}

/**
 * Parameters for fetching a single program
 */
export interface UseProgramParams {
  programId: string;
  enabled?: boolean;
}

/**
 * Options for program mutations
 */
export interface UseProgramMutationOptions {
  onSuccess?: (program: ComplianceProgram) => void;
  onError?: (error: Error) => void;
}

/**
 * Parameters for updating a program
 */
export interface UpdateProgramParams {
  programId: string;
  data: ComplianceProgramUpdate;
}

/**
 * List response for programs
 */
export interface ListProgramsResponse {
  programs: ComplianceProgram[];
  total: number;
  page: number;
  limit: number;
}

// ============================================================================
// TYPE DEFINITIONS - REQUIREMENTS
// ============================================================================

/**
 * Parameters for listing compliance requirements with filters
 */
export interface UseRequirementsParams {
  organization_id: string;
  standard?: ComplianceStandard;
  category?: RequirementCategory;
  is_active?: boolean;
  search?: string;
  page?: number;
  limit?: number;
  enabled?: boolean;
}

/**
 * Parameters for fetching a single requirement
 */
export interface UseRequirementParams {
  requirementId: string;
  enabled?: boolean;
}

/**
 * Options for requirement mutations
 */
export interface UseRequirementMutationOptions {
  onSuccess?: (requirement: ComplianceRequirement) => void;
  onError?: (error: Error) => void;
}

/**
 * Parameters for updating a requirement
 */
export interface UpdateRequirementParams {
  requirementId: string;
  data: ComplianceRequirementUpdate;
}

/**
 * Parameters for importing requirements
 */
export interface ImportRequirementsParams {
  organization_id: string;
  standard: ComplianceStandard;
  overwrite_existing?: boolean;
}

/**
 * Import requirements response
 */
export interface ImportRequirementsResponse {
  imported_count: number;
  skipped_count: number;
  updated_count: number;
  requirements: ComplianceRequirement[];
}

/**
 * List response for requirements
 */
export interface ListRequirementsResponse {
  requirements: ComplianceRequirement[];
  total: number;
  page: number;
  limit: number;
}

// ============================================================================
// API CLIENT FUNCTIONS - PROGRAMS
// ============================================================================

const PROGRAMS_BASE = '/api/v1/compliance/programs';

/**
 * List compliance programs
 */
async function listPrograms(params: UseProgramsParams): Promise<ListProgramsResponse> {
  const query = new URLSearchParams();
  query.set('organization_id', params.organization_id);
  if (params.standard) query.set('standard', params.standard);
  if (params.status) query.set('status', params.status);
  if (params.search) query.set('search', params.search);
  if (params.page !== undefined) query.set('page', String(params.page));
  if (params.limit !== undefined) query.set('limit', String(params.limit));

  return apiClient.request<ListProgramsResponse>({
    method: 'GET',
    url: `${PROGRAMS_BASE}?${query.toString()}`,
  });
}

/**
 * Get single program by ID
 */
async function getProgram(programId: string): Promise<ComplianceProgram> {
  return apiClient.request<ComplianceProgram>({
    method: 'GET',
    url: `${PROGRAMS_BASE}/${programId}`,
  });
}

/**
 * Create new program
 */
async function createProgram(data: ComplianceProgramCreate): Promise<ComplianceProgram> {
  return apiClient.request<ComplianceProgram>({
    method: 'POST',
    url: PROGRAMS_BASE,
    data,
  });
}

/**
 * Update program
 */
async function updateProgram(
  programId: string,
  data: ComplianceProgramUpdate
): Promise<ComplianceProgram> {
  return apiClient.request<ComplianceProgram>({
    method: 'PUT',
    url: `${PROGRAMS_BASE}/${programId}`,
    data,
  });
}

/**
 * Delete program
 */
async function deleteProgram(programId: string): Promise<void> {
  return apiClient.request<void>({
    method: 'DELETE',
    url: `${PROGRAMS_BASE}/${programId}`,
  });
}

/**
 * Activate program
 */
async function activateProgram(programId: string): Promise<ComplianceProgram> {
  return apiClient.request<ComplianceProgram>({
    method: 'POST',
    url: `${PROGRAMS_BASE}/${programId}/activate`,
  });
}

/**
 * Archive program
 */
async function archiveProgram(programId: string): Promise<ComplianceProgram> {
  return apiClient.request<ComplianceProgram>({
    method: 'POST',
    url: `${PROGRAMS_BASE}/${programId}/archive`,
  });
}

/**
 * Get programs by standard
 */
async function getProgramsByStandard(
  organizationId: string,
  standard: ComplianceStandard
): Promise<ComplianceProgram[]> {
  const query = new URLSearchParams();
  query.set('organization_id', organizationId);

  return apiClient.request<ComplianceProgram[]>({
    method: 'GET',
    url: `${PROGRAMS_BASE}/standard/${standard}?${query.toString()}`,
  });
}

// ============================================================================
// API CLIENT FUNCTIONS - REQUIREMENTS
// ============================================================================

const REQUIREMENTS_BASE = '/api/v1/compliance/requirements';

/**
 * List compliance requirements
 */
async function listRequirements(
  params: UseRequirementsParams
): Promise<ListRequirementsResponse> {
  const query = new URLSearchParams();
  query.set('organization_id', params.organization_id);
  if (params.standard) query.set('standard', params.standard);
  if (params.category) query.set('category', params.category);
  if (params.is_active !== undefined) query.set('is_active', String(params.is_active));
  if (params.search) query.set('search', params.search);
  if (params.page !== undefined) query.set('page', String(params.page));
  if (params.limit !== undefined) query.set('limit', String(params.limit));

  return apiClient.request<ListRequirementsResponse>({
    method: 'GET',
    url: `${REQUIREMENTS_BASE}?${query.toString()}`,
  });
}

/**
 * Get single requirement by ID
 */
async function getRequirement(requirementId: string): Promise<ComplianceRequirement> {
  return apiClient.request<ComplianceRequirement>({
    method: 'GET',
    url: `${REQUIREMENTS_BASE}/${requirementId}`,
  });
}

/**
 * Create new requirement
 */
async function createRequirement(
  data: ComplianceRequirementCreate
): Promise<ComplianceRequirement> {
  return apiClient.request<ComplianceRequirement>({
    method: 'POST',
    url: REQUIREMENTS_BASE,
    data,
  });
}

/**
 * Update requirement
 */
async function updateRequirement(
  requirementId: string,
  data: ComplianceRequirementUpdate
): Promise<ComplianceRequirement> {
  return apiClient.request<ComplianceRequirement>({
    method: 'PUT',
    url: `${REQUIREMENTS_BASE}/${requirementId}`,
    data,
  });
}

/**
 * Delete requirement
 */
async function deleteRequirement(requirementId: string): Promise<void> {
  return apiClient.request<void>({
    method: 'DELETE',
    url: `${REQUIREMENTS_BASE}/${requirementId}`,
  });
}

/**
 * Import requirements from standard
 */
async function importRequirements(
  params: ImportRequirementsParams
): Promise<ImportRequirementsResponse> {
  return apiClient.request<ImportRequirementsResponse>({
    method: 'POST',
    url: `${REQUIREMENTS_BASE}/import`,
    data: params,
  });
}

/**
 * Get requirements by standard
 */
async function getRequirementsByStandard(
  organizationId: string,
  standard: ComplianceStandard
): Promise<ComplianceRequirement[]> {
  const query = new URLSearchParams();
  query.set('organization_id', organizationId);

  return apiClient.request<ComplianceRequirement[]>({
    method: 'GET',
    url: `${REQUIREMENTS_BASE}/standard/${standard}?${query.toString()}`,
  });
}

/**
 * Get requirements by category
 */
async function getRequirementsByCategory(
  organizationId: string,
  category: RequirementCategory
): Promise<ComplianceRequirement[]> {
  const query = new URLSearchParams();
  query.set('organization_id', organizationId);

  return apiClient.request<ComplianceRequirement[]>({
    method: 'GET',
    url: `${REQUIREMENTS_BASE}/category/${category}?${query.toString()}`,
  });
}

// ============================================================================
// QUERY HOOKS - PROGRAMS
// ============================================================================

/**
 * Hook: useCompliancePrograms
 * Fetch list of compliance programs with filtering and pagination
 *
 * @param params - Filter parameters including organization_id, standard, status, etc.
 * @returns Query result with compliance programs list
 *
 * @example
 * ```tsx
 * const { data, isLoading, error } = useCompliancePrograms({
 *   organization_id: 'org-123',
 *   standard: ComplianceStandard.ISO_22301,
 *   page: 1,
 *   limit: 20,
 * });
 * ```
 */
export function useCompliancePrograms(params: UseProgramsParams) {
  const { enabled = true, ...queryParams } = params;

  return useQuery({
    queryKey: programQueryKeys.list(queryParams),
    queryFn: () => listPrograms(queryParams),
    enabled: enabled && !!queryParams.organization_id,
    staleTime: 30000, // 30 seconds
  });
}

/**
 * Hook: useComplianceProgram
 * Fetch a single compliance program by ID
 *
 * @param params - Program ID and enabled flag
 * @returns Query result with single compliance program
 *
 * @example
 * ```tsx
 * const { data: program, isLoading } = useComplianceProgram({
 *   programId: 'prog-123',
 *   enabled: true,
 * });
 * ```
 */
export function useComplianceProgram({ programId, enabled = true }: UseProgramParams) {
  return useQuery({
    queryKey: programQueryKeys.detail(programId),
    queryFn: () => getProgram(programId),
    enabled: enabled && !!programId,
    staleTime: 60000, // 1 minute
  });
}

/**
 * Hook: useProgramsByStandard
 * Fetch compliance programs filtered by standard
 *
 * @param organizationId - Organization ID
 * @param standard - Compliance standard to filter by
 * @param enabled - Whether query is enabled
 * @returns Query result with programs for the standard
 *
 * @example
 * ```tsx
 * const { data: programs } = useProgramsByStandard(
 *   'org-123',
 *   ComplianceStandard.ISO_22301
 * );
 * ```
 */
export function useProgramsByStandard(
  organizationId: string,
  standard: ComplianceStandard,
  enabled = true
) {
  return useQuery({
    queryKey: programQueryKeys.byStandard(standard),
    queryFn: () => getProgramsByStandard(organizationId, standard),
    enabled: enabled && !!organizationId,
    staleTime: 30000,
  });
}

/**
 * Hook: useActivePrograms
 * Fetch only active compliance programs
 *
 * @param organizationId - Organization ID
 * @returns Query result with active programs
 *
 * @example
 * ```tsx
 * const { data } = useActivePrograms('org-123');
 * const activePrograms = data?.programs || [];
 * ```
 */
export function useActivePrograms(organizationId: string) {
  return useCompliancePrograms({
    organization_id: organizationId,
    status: 'active',
  });
}

// ============================================================================
// MUTATION HOOKS - PROGRAMS
// ============================================================================

/**
 * Hook: useCreateComplianceProgram
 * Create a new compliance program
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for creating compliance programs
 *
 * @example
 * ```tsx
 * const createProgram = useCreateComplianceProgram({
 *   onSuccess: (program) => {
 *     toast.success(`Program "${program.program_name}" created`);
 *     router.push(`/compliance/programs/${program.id}`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to create program: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * createProgram.mutate({
 *   organization_id: 'org-123',
 *   program_name: 'ISO 22301 Compliance Program',
 *   standard: ComplianceStandard.ISO_22301,
 *   description: 'Business continuity management system',
 *   scope_description: 'All critical business processes',
 *   applicable_departments: ['IT', 'Operations', 'Finance'],
 *   applicable_processes: ['proc-1', 'proc-2'],
 *   overall_score: 0,
 *   compliance_status: ComplianceStatus.NOT_ASSESSED,
 *   program_owner: 'user-123',
 *   created_by: 'user-123',
 * });
 * ```
 */
export function useCreateComplianceProgram(options?: UseProgramMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ComplianceProgramCreate) => createProgram(data),
    onSuccess: (data) => {
      // Invalidate all program lists
      queryClient.invalidateQueries({ queryKey: programQueryKeys.lists() });

      // Set the new program in cache
      queryClient.setQueryData(programQueryKeys.detail(data.id), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useUpdateComplianceProgram
 * Update an existing compliance program
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for updating compliance programs
 *
 * @example
 * ```tsx
 * const updateProgram = useUpdateComplianceProgram({
 *   onSuccess: (program) => {
 *     toast.success('Program updated successfully');
 *   },
 *   onError: (error) => {
 *     toast.error(`Update failed: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * updateProgram.mutate({
 *   programId: 'prog-123',
 *   data: {
 *     program_name: 'Updated Program Name',
 *     overall_score: 85,
 *     compliance_status: ComplianceStatus.PARTIAL,
 *   },
 * });
 * ```
 */
export function useUpdateComplianceProgram(options?: UseProgramMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ programId, data }: UpdateProgramParams) =>
      updateProgram(programId, data),
    onSuccess: (data) => {
      // Invalidate all program lists
      queryClient.invalidateQueries({ queryKey: programQueryKeys.lists() });

      // Invalidate specific program detail
      queryClient.invalidateQueries({ queryKey: programQueryKeys.detail(data.id) });

      // Update the cache with new data
      queryClient.setQueryData(programQueryKeys.detail(data.id), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useDeleteComplianceProgram
 * Delete a compliance program
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for deleting compliance programs
 *
 * @example
 * ```tsx
 * const deleteProgram = useDeleteComplianceProgram({
 *   onSuccess: () => {
 *     toast.success('Program deleted successfully');
 *     router.push('/compliance/programs');
 *   },
 *   onError: (error) => {
 *     toast.error(`Delete failed: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * deleteProgram.mutate('prog-123');
 * ```
 */
export function useDeleteComplianceProgram(
  options?: Omit<UseProgramMutationOptions, 'onSuccess'> & {
    onSuccess?: () => void;
  }
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (programId: string) => deleteProgram(programId),
    onSuccess: (_, programId) => {
      // Invalidate all program lists
      queryClient.invalidateQueries({ queryKey: programQueryKeys.lists() });

      // Remove the deleted program from cache
      queryClient.removeQueries({ queryKey: programQueryKeys.detail(programId) });

      options?.onSuccess?.();
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useActivateComplianceProgram
 * Activate a compliance program
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for activating compliance programs
 *
 * @example
 * ```tsx
 * const activateProgram = useActivateComplianceProgram({
 *   onSuccess: (program) => {
 *     toast.success('Program activated successfully');
 *   },
 *   onError: (error) => {
 *     toast.error(`Activation failed: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * activateProgram.mutate('prog-123');
 * ```
 */
export function useActivateComplianceProgram(options?: UseProgramMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (programId: string) => activateProgram(programId),
    onSuccess: (data) => {
      // Invalidate all program lists
      queryClient.invalidateQueries({ queryKey: programQueryKeys.lists() });

      // Invalidate specific program detail
      queryClient.invalidateQueries({ queryKey: programQueryKeys.detail(data.id) });

      // Update the cache with new data
      queryClient.setQueryData(programQueryKeys.detail(data.id), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useArchiveComplianceProgram
 * Archive a compliance program
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for archiving compliance programs
 *
 * @example
 * ```tsx
 * const archiveProgram = useArchiveComplianceProgram({
 *   onSuccess: (program) => {
 *     toast.success('Program archived successfully');
 *   },
 *   onError: (error) => {
 *     toast.error(`Archive failed: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * archiveProgram.mutate('prog-123');
 * ```
 */
export function useArchiveComplianceProgram(options?: UseProgramMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (programId: string) => archiveProgram(programId),
    onSuccess: (data) => {
      // Invalidate all program lists
      queryClient.invalidateQueries({ queryKey: programQueryKeys.lists() });

      // Invalidate specific program detail
      queryClient.invalidateQueries({ queryKey: programQueryKeys.detail(data.id) });

      // Update the cache with new data
      queryClient.setQueryData(programQueryKeys.detail(data.id), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

// ============================================================================
// UTILITY HOOKS - PROGRAMS
// ============================================================================

/**
 * Hook: usePrefetchProgram
 * Prefetch a program for improved performance (hover states, navigation)
 *
 * @example
 * ```tsx
 * const prefetchProgram = usePrefetchProgram();
 *
 * <div onMouseEnter={() => prefetchProgram('prog-123')}>
 *   View Program
 * </div>
 * ```
 */
export function usePrefetchProgram() {
  const queryClient = useQueryClient();

  return (programId: string) => {
    queryClient.prefetchQuery({
      queryKey: programQueryKeys.detail(programId),
      queryFn: () => getProgram(programId),
      staleTime: 60000,
    });
  };
}

/**
 * Hook: useIsProgramCached
 * Check if a program is already in cache
 *
 * @param programId - Program ID to check
 * @returns Boolean indicating if program is cached
 *
 * @example
 * ```tsx
 * const isCached = useIsProgramCached('prog-123');
 * if (!isCached) {
 *   // Show loading indicator
 * }
 * ```
 */
export function useIsProgramCached(programId: string): boolean {
  const queryClient = useQueryClient();
  const data = queryClient.getQueryData(programQueryKeys.detail(programId));
  return !!data;
}

/**
 * Hook: useCachedProgram
 * Get cached program data without triggering a fetch
 *
 * @param programId - Program ID to retrieve from cache
 * @returns Cached program data or undefined
 *
 * @example
 * ```tsx
 * const cachedProgram = useCachedProgram('prog-123');
 * if (cachedProgram) {
 *   // Use cached data for optimistic UI
 * }
 * ```
 */
export function useCachedProgram(programId: string): ComplianceProgram | undefined {
  const queryClient = useQueryClient();
  return queryClient.getQueryData<ComplianceProgram>(
    programQueryKeys.detail(programId)
  );
}

/**
 * Hook: useInvalidatePrograms
 * Utility to manually invalidate all program queries
 *
 * @returns Function to invalidate program queries
 *
 * @example
 * ```tsx
 * const invalidatePrograms = useInvalidatePrograms();
 *
 * // After external update
 * invalidatePrograms();
 * ```
 */
export function useInvalidatePrograms() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: programQueryKeys.all });
}

// ============================================================================
// QUERY HOOKS - REQUIREMENTS
// ============================================================================

/**
 * Hook: useComplianceRequirements
 * Fetch list of compliance requirements with filtering and pagination
 *
 * @param params - Filter parameters including organization_id, standard, category, etc.
 * @returns Query result with compliance requirements list
 *
 * @example
 * ```tsx
 * const { data, isLoading, error } = useComplianceRequirements({
 *   organization_id: 'org-123',
 *   standard: ComplianceStandard.ISO_22301,
 *   category: RequirementCategory.BUSINESS_CONTINUITY,
 *   is_active: true,
 *   page: 1,
 *   limit: 20,
 * });
 * ```
 */
export function useComplianceRequirements(params: UseRequirementsParams) {
  const { enabled = true, ...queryParams } = params;

  return useQuery({
    queryKey: requirementQueryKeys.list(queryParams),
    queryFn: () => listRequirements(queryParams),
    enabled: enabled && !!queryParams.organization_id,
    staleTime: 30000, // 30 seconds
  });
}

/**
 * Hook: useComplianceRequirement
 * Fetch a single compliance requirement by ID
 *
 * @param params - Requirement ID and enabled flag
 * @returns Query result with single compliance requirement
 *
 * @example
 * ```tsx
 * const { data: requirement, isLoading } = useComplianceRequirement({
 *   requirementId: 'req-123',
 *   enabled: true,
 * });
 * ```
 */
export function useComplianceRequirement({
  requirementId,
  enabled = true,
}: UseRequirementParams) {
  return useQuery({
    queryKey: requirementQueryKeys.detail(requirementId),
    queryFn: () => getRequirement(requirementId),
    enabled: enabled && !!requirementId,
    staleTime: 60000, // 1 minute
  });
}

/**
 * Hook: useRequirementsByStandard
 * Fetch compliance requirements filtered by standard
 *
 * @param organizationId - Organization ID
 * @param standard - Compliance standard to filter by
 * @param enabled - Whether query is enabled
 * @returns Query result with requirements for the standard
 *
 * @example
 * ```tsx
 * const { data: requirements } = useRequirementsByStandard(
 *   'org-123',
 *   ComplianceStandard.ISO_22301
 * );
 * ```
 */
export function useRequirementsByStandard(
  organizationId: string,
  standard: ComplianceStandard,
  enabled = true
) {
  return useQuery({
    queryKey: requirementQueryKeys.byStandard(standard),
    queryFn: () => getRequirementsByStandard(organizationId, standard),
    enabled: enabled && !!organizationId,
    staleTime: 30000,
  });
}

/**
 * Hook: useRequirementsByCategory
 * Fetch compliance requirements filtered by category
 *
 * @param organizationId - Organization ID
 * @param category - Requirement category to filter by
 * @param enabled - Whether query is enabled
 * @returns Query result with requirements for the category
 *
 * @example
 * ```tsx
 * const { data: requirements } = useRequirementsByCategory(
 *   'org-123',
 *   RequirementCategory.GOVERNANCE
 * );
 * ```
 */
export function useRequirementsByCategory(
  organizationId: string,
  category: RequirementCategory,
  enabled = true
) {
  return useQuery({
    queryKey: requirementQueryKeys.byCategory(category),
    queryFn: () => getRequirementsByCategory(organizationId, category),
    enabled: enabled && !!organizationId,
    staleTime: 30000,
  });
}

/**
 * Hook: useActiveRequirements
 * Fetch only active compliance requirements
 *
 * @param organizationId - Organization ID
 * @returns Query result with active requirements
 *
 * @example
 * ```tsx
 * const { data } = useActiveRequirements('org-123');
 * const activeRequirements = data?.requirements || [];
 * ```
 */
export function useActiveRequirements(organizationId: string) {
  return useComplianceRequirements({
    organization_id: organizationId,
    is_active: true,
  });
}

// ============================================================================
// MUTATION HOOKS - REQUIREMENTS
// ============================================================================

/**
 * Hook: useCreateComplianceRequirement
 * Create a new compliance requirement
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for creating compliance requirements
 *
 * @example
 * ```tsx
 * const createRequirement = useCreateComplianceRequirement({
 *   onSuccess: (requirement) => {
 *     toast.success(`Requirement "${requirement.title}" created`);
 *     router.push(`/compliance/requirements/${requirement.id}`);
 *   },
 *   onError: (error) => {
 *     toast.error(`Failed to create requirement: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * createRequirement.mutate({
 *   organization_id: 'org-123',
 *   standard: ComplianceStandard.ISO_22301,
 *   clause: '4.1',
 *   title: 'Understanding the organization and its context',
 *   description: 'The organization shall determine external and internal issues...',
 *   category: RequirementCategory.GOVERNANCE,
 *   requirement_type: RequirementType.MANDATORY,
 *   is_mandatory: true,
 *   weight: 100,
 *   evidence_types: ['policy', 'procedure'],
 *   min_evidence_count: 2,
 *   is_active: true,
 *   created_by: 'user-123',
 * });
 * ```
 */
export function useCreateComplianceRequirement(options?: UseRequirementMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ComplianceRequirementCreate) => createRequirement(data),
    onSuccess: (data) => {
      // Invalidate all requirement lists
      queryClient.invalidateQueries({ queryKey: requirementQueryKeys.lists() });

      // Set the new requirement in cache
      queryClient.setQueryData(requirementQueryKeys.detail(data.id), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useUpdateComplianceRequirement
 * Update an existing compliance requirement
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for updating compliance requirements
 *
 * @example
 * ```tsx
 * const updateRequirement = useUpdateComplianceRequirement({
 *   onSuccess: (requirement) => {
 *     toast.success('Requirement updated successfully');
 *   },
 *   onError: (error) => {
 *     toast.error(`Update failed: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * updateRequirement.mutate({
 *   requirementId: 'req-123',
 *   data: {
 *     title: 'Updated Requirement Title',
 *     weight: 120,
 *     is_active: false,
 *   },
 * });
 * ```
 */
export function useUpdateComplianceRequirement(options?: UseRequirementMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ requirementId, data }: UpdateRequirementParams) =>
      updateRequirement(requirementId, data),
    onSuccess: (data) => {
      // Invalidate all requirement lists
      queryClient.invalidateQueries({ queryKey: requirementQueryKeys.lists() });

      // Invalidate specific requirement detail
      queryClient.invalidateQueries({ queryKey: requirementQueryKeys.detail(data.id) });

      // Update the cache with new data
      queryClient.setQueryData(requirementQueryKeys.detail(data.id), data);

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useDeleteComplianceRequirement
 * Delete a compliance requirement
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for deleting compliance requirements
 *
 * @example
 * ```tsx
 * const deleteRequirement = useDeleteComplianceRequirement({
 *   onSuccess: () => {
 *     toast.success('Requirement deleted successfully');
 *     router.push('/compliance/requirements');
 *   },
 *   onError: (error) => {
 *     toast.error(`Delete failed: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * deleteRequirement.mutate('req-123');
 * ```
 */
export function useDeleteComplianceRequirement(
  options?: Omit<UseRequirementMutationOptions, 'onSuccess'> & {
    onSuccess?: () => void;
  }
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (requirementId: string) => deleteRequirement(requirementId),
    onSuccess: (_, requirementId) => {
      // Invalidate all requirement lists
      queryClient.invalidateQueries({ queryKey: requirementQueryKeys.lists() });

      // Remove the deleted requirement from cache
      queryClient.removeQueries({ queryKey: requirementQueryKeys.detail(requirementId) });

      options?.onSuccess?.();
    },
    onError: options?.onError,
  });
}

/**
 * Hook: useImportRequirements
 * Import requirements from a compliance standard
 *
 * @param options - Success/error callbacks
 * @returns Mutation object for importing requirements
 *
 * @example
 * ```tsx
 * const importRequirements = useImportRequirements({
 *   onSuccess: (result) => {
 *     toast.success(
 *       `Imported ${result.imported_count} requirements, ` +
 *       `updated ${result.updated_count}, skipped ${result.skipped_count}`
 *     );
 *   },
 *   onError: (error) => {
 *     toast.error(`Import failed: ${error.message}`);
 *   },
 * });
 *
 * // Usage
 * importRequirements.mutate({
 *   organization_id: 'org-123',
 *   standard: ComplianceStandard.ISO_22301,
 *   overwrite_existing: false,
 * });
 * ```
 */
export function useImportRequirements(
  options?: Omit<UseRequirementMutationOptions, 'onSuccess'> & {
    onSuccess?: (result: ImportRequirementsResponse) => void;
  }
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: ImportRequirementsParams) => importRequirements(params),
    onSuccess: (data) => {
      // Invalidate all requirement lists to show imported data
      queryClient.invalidateQueries({ queryKey: requirementQueryKeys.lists() });

      // Invalidate by-standard queries
      queryClient.invalidateQueries({
        queryKey: requirementQueryKeys.byStandard(data.requirements[0]?.standard),
      });

      options?.onSuccess?.(data);
    },
    onError: options?.onError,
  });
}

// ============================================================================
// UTILITY HOOKS - REQUIREMENTS
// ============================================================================

/**
 * Hook: usePrefetchRequirement
 * Prefetch a requirement for improved performance (hover states, navigation)
 *
 * @example
 * ```tsx
 * const prefetchRequirement = usePrefetchRequirement();
 *
 * <div onMouseEnter={() => prefetchRequirement('req-123')}>
 *   View Requirement
 * </div>
 * ```
 */
export function usePrefetchRequirement() {
  const queryClient = useQueryClient();

  return (requirementId: string) => {
    queryClient.prefetchQuery({
      queryKey: requirementQueryKeys.detail(requirementId),
      queryFn: () => getRequirement(requirementId),
      staleTime: 60000,
    });
  };
}

/**
 * Hook: useIsRequirementCached
 * Check if a requirement is already in cache
 *
 * @param requirementId - Requirement ID to check
 * @returns Boolean indicating if requirement is cached
 *
 * @example
 * ```tsx
 * const isCached = useIsRequirementCached('req-123');
 * if (!isCached) {
 *   // Show loading indicator
 * }
 * ```
 */
export function useIsRequirementCached(requirementId: string): boolean {
  const queryClient = useQueryClient();
  const data = queryClient.getQueryData(requirementQueryKeys.detail(requirementId));
  return !!data;
}

/**
 * Hook: useCachedRequirement
 * Get cached requirement data without triggering a fetch
 *
 * @param requirementId - Requirement ID to retrieve from cache
 * @returns Cached requirement data or undefined
 *
 * @example
 * ```tsx
 * const cachedRequirement = useCachedRequirement('req-123');
 * if (cachedRequirement) {
 *   // Use cached data for optimistic UI
 * }
 * ```
 */
export function useCachedRequirement(
  requirementId: string
): ComplianceRequirement | undefined {
  const queryClient = useQueryClient();
  return queryClient.getQueryData<ComplianceRequirement>(
    requirementQueryKeys.detail(requirementId)
  );
}

/**
 * Hook: useInvalidateRequirements
 * Utility to manually invalidate all requirement queries
 *
 * @returns Function to invalidate requirement queries
 *
 * @example
 * ```tsx
 * const invalidateRequirements = useInvalidateRequirements();
 *
 * // After external update
 * invalidateRequirements();
 * ```
 */
export function useInvalidateRequirements() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: requirementQueryKeys.all });
}

// ============================================================================
// EXPORTS
// ============================================================================

// Types are already exported as interfaces above - no need to re-export
