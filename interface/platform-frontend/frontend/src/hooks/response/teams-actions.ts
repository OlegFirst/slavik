/**
 * Response Module - Teams & Actions Hooks
 * React Query hooks for Response Teams and Response Actions
 * ISO 22301:2019 Clause 8.4 - Incident Response & Recovery
 *
 * Created: 2025-10-24
 * Agent: 26 (Response Module Round 2)
 *
 * Total Hooks: 25
 * - Response Team Hooks: 10 hooks (4 query + 6 mutation)
 * - Response Action Hooks: 12 hooks (5 query + 7 mutation)
 * - Utility Hooks: 3 hooks
 */

'use client';

import { useQuery, useMutation, useQueryClient, type QueryClient } from '@tanstack/react-query';
import {
  responseClient,
  ActionStatus,
  type ResponseTeam,
  type ResponseTeamCreate,
  type ResponseTeamUpdate,
  type ResponseAction,
  type ResponseActionCreate,
  type ResponseActionUpdate,
} from '@/lib/api/response-client';

// ============================================================================
// QUERY KEY FACTORIES
// ============================================================================

/**
 * Query key factory for response teams
 * Provides consistent cache key generation for all team-related queries
 */
export const teamQueryKeys = {
  all: ['response', 'teams'] as const,
  lists: () => [...teamQueryKeys.all, 'list'] as const,
  list: (isActive?: boolean) => [...teamQueryKeys.lists(), { isActive }] as const,
  details: () => [...teamQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...teamQueryKeys.details(), id] as const,
  incidentTeam: (incidentId: string) => ['response', 'incidents', incidentId, 'team'] as const,
  available: () => [...teamQueryKeys.all, 'available'] as const,
};

/**
 * Query key factory for response actions
 * Provides consistent cache key generation for all action-related queries
 */
export const actionQueryKeys = {
  all: ['response', 'actions'] as const,
  lists: () => [...actionQueryKeys.all, 'list'] as const,
  list: (incidentId: string) => [...actionQueryKeys.lists(), { incidentId }] as const,
  details: () => [...actionQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...actionQueryKeys.details(), id] as const,
  byType: (incidentId: string, type: string) =>
    [...actionQueryKeys.all, 'by-type', incidentId, type] as const,
  overdue: (incidentId?: string) =>
    incidentId
      ? [...actionQueryKeys.all, 'overdue', incidentId] as const
      : [...actionQueryKeys.all, 'overdue'] as const,
};

// ============================================================================
// RESPONSE TEAMS - QUERY HOOKS (4 hooks)
// ============================================================================

/**
 * Hook Parameters - List Teams
 */
export interface UseResponseTeamsParams {
  isActive?: boolean;
  enabled?: boolean;
}

/**
 * Hook to fetch response teams
 * Returns all teams or filtered by active status
 *
 * @param params - Query parameters with optional filters
 * @returns Query result with teams array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: teams, isLoading } = useResponseTeams({
 *   isActive: true,
 *   enabled: true
 * });
 *
 * if (teams) {
 *   console.log(`Found ${teams.length} active response teams`);
 *   teams.forEach(team => {
 *     console.log(`- ${team.name}: ${team.members.length} members`);
 *   });
 * }
 * ```
 */
export function useResponseTeams({ isActive, enabled = true }: UseResponseTeamsParams = {}) {
  return useQuery({
    queryKey: teamQueryKeys.list(isActive),
    queryFn: () => responseClient.listResponseTeams(isActive),
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Single Team
 */
export interface UseResponseTeamParams {
  teamId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch a single response team by ID
 * Returns team details including all members
 *
 * @param params - Query parameters with teamId
 * @returns Query result with team data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: team, isLoading, error } = useResponseTeam({
 *   teamId: 'team-123',
 *   enabled: true
 * });
 *
 * if (team) {
 *   console.log(`Team: ${team.name}`);
 *   console.log(`Active: ${team.is_active}`);
 *   console.log(`Members: ${team.members.length}`);
 *
 *   const commander = team.members.find(m => m.role === TeamRole.INCIDENT_COMMANDER);
 *   if (commander) {
 *     console.log(`Incident Commander: ${commander.name}`);
 *   }
 * }
 * ```
 */
export function useResponseTeam({ teamId, enabled = true }: UseResponseTeamParams) {
  return useQuery({
    queryKey: teamQueryKeys.detail(teamId),
    queryFn: async () => {
      // Note: Using list endpoint and filtering since there's no single team endpoint
      const teams = await responseClient.listResponseTeams();
      const team = teams.find(t => t.id === teamId);
      if (!team) throw new Error('Team not found');
      return team;
    },
    enabled: enabled && !!teamId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Incident Team
 */
export interface UseIncidentTeamParams {
  incidentId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch the team assigned to an incident
 * Returns the response team currently assigned to the incident
 *
 * @param params - Query parameters with incidentId
 * @returns Query result with team data or null, loading state, error
 *
 * @example
 * ```tsx
 * const { data: incidentTeam } = useIncidentTeam({
 *   incidentId: 'incident-123'
 * });
 *
 * if (incidentTeam) {
 *   console.log(`Assigned Team: ${incidentTeam.name}`);
 *   console.log(`Team Size: ${incidentTeam.members.length}`);
 * } else {
 *   console.log('No team assigned yet');
 * }
 * ```
 */
export function useIncidentTeam({ incidentId, enabled = true }: UseIncidentTeamParams) {
  return useQuery({
    queryKey: teamQueryKeys.incidentTeam(incidentId),
    queryFn: () => responseClient.getIncidentTeam(incidentId),
    enabled: enabled && !!incidentId,
    staleTime: 3 * 60 * 1000, // 3 minutes (shorter for incident tracking)
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: true,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Available Teams
 */
export interface UseAvailableTeamsParams {
  enabled?: boolean;
}

/**
 * Hook to fetch available response teams
 * Returns only active teams that can be assigned to incidents
 *
 * @param params - Query parameters
 * @returns Query result with available teams array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: availableTeams } = useAvailableTeams({
 *   enabled: true
 * });
 *
 * if (availableTeams) {
 *   console.log(`${availableTeams.length} teams available for assignment`);
 * }
 * ```
 */
export function useAvailableTeams({ enabled = true }: UseAvailableTeamsParams = {}) {
  return useQuery({
    queryKey: teamQueryKeys.available(),
    queryFn: () => responseClient.listResponseTeams(true), // Only active teams
    enabled,
    staleTime: 3 * 60 * 1000, // 3 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: true,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ============================================================================
// RESPONSE TEAMS - MUTATION HOOKS (6 hooks)
// ============================================================================

/**
 * Hook Options - Create Team
 */
export interface UseCreateResponseTeamOptions {
  onSuccess?: (team: ResponseTeam) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to create a new response team
 * Automatically invalidates team list cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const createTeam = useCreateResponseTeam({
 *   onSuccess: (team) => {
 *     console.log(`Team "${team.name}" created`);
 *     router.push(`/response/teams/${team.id}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Failed to create team: ${error.message}`);
 *   }
 * });
 *
 * createTeam.mutate({
 *   name: 'Cyber Security Response Team',
 *   description: 'Primary team for cyber security incidents',
 *   is_active: true,
 *   members: [
 *     {
 *       user_id: 'user-123',
 *       role: TeamRole.INCIDENT_COMMANDER,
 *       name: 'John Smith',
 *       email: 'john.smith@company.com',
 *       phone: '+1-555-0100',
 *       is_primary: true,
 *       availability_status: 'available'
 *     },
 *     {
 *       user_id: 'user-456',
 *       role: TeamRole.TECHNICAL_LEAD,
 *       name: 'Jane Doe',
 *       email: 'jane.doe@company.com',
 *       phone: '+1-555-0101',
 *       is_primary: false,
 *       availability_status: 'available'
 *     }
 *   ],
 *   activation_criteria: {
 *     incident_types: ['cyber_attack', 'security_breach', 'data_breach'],
 *     severity_levels: ['critical', 'high']
 *   }
 * });
 * ```
 */
export function useCreateResponseTeam(options: UseCreateResponseTeamOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ResponseTeam, Error, ResponseTeamCreate>({
    mutationFn: (data: ResponseTeamCreate) => responseClient.createResponseTeam(data),

    onSuccess: (data) => {
      // Invalidate team lists to refetch with new team
      queryClient.invalidateQueries({
        queryKey: teamQueryKeys.lists(),
      });

      // Invalidate available teams
      queryClient.invalidateQueries({
        queryKey: teamQueryKeys.available(),
      });

      // Optimistically set the single team cache
      if (data.id) {
        queryClient.setQueryData(teamQueryKeys.detail(data.id), data);
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Update Team
 */
export interface UseUpdateResponseTeamOptions {
  onSuccess?: (team: ResponseTeam) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Update Team Parameters
 */
export interface UpdateResponseTeamParams {
  teamId: string;
  data: ResponseTeamUpdate;
}

/**
 * Hook to update an existing response team
 * Automatically invalidates relevant cache entries on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const updateTeam = useUpdateResponseTeam({
 *   onSuccess: (team) => {
 *     console.log(`Team "${team.name}" updated`);
 *   },
 *   onError: (error) => {
 *     console.error(`Update failed: ${error.message}`);
 *   }
 * });
 *
 * updateTeam.mutate({
 *   teamId: 'team-123',
 *   data: {
 *     description: 'Updated team description',
 *     is_active: true,
 *     activation_criteria: {
 *       incident_types: ['cyber_attack', 'data_breach'],
 *       severity_levels: ['critical']
 *     }
 *   }
 * });
 * ```
 */
export function useUpdateResponseTeam(options: UseUpdateResponseTeamOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ResponseTeam, Error, UpdateResponseTeamParams>({
    mutationFn: async ({ teamId, data }: UpdateResponseTeamParams) => {
      // Note: API client doesn't have updateTeam method, so we need to implement workaround
      // For now, we'll throw an error or implement a custom solution
      throw new Error('Update team endpoint not yet implemented in API client');
    },

    onSuccess: (data) => {
      // Invalidate team lists
      queryClient.invalidateQueries({
        queryKey: teamQueryKeys.lists(),
      });

      // Invalidate the specific team detail
      if (data.id) {
        queryClient.invalidateQueries({
          queryKey: teamQueryKeys.detail(data.id),
        });
      }

      // Invalidate available teams
      queryClient.invalidateQueries({
        queryKey: teamQueryKeys.available(),
      });

      // Update the cached team data
      if (data.id) {
        queryClient.setQueryData(teamQueryKeys.detail(data.id), data);
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Delete Team
 */
export interface UseDeleteResponseTeamOptions {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Hook to delete a response team
 * Automatically invalidates team cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const deleteTeam = useDeleteResponseTeam({
 *   onSuccess: () => {
 *     console.log('Team deleted successfully');
 *     router.push('/response/teams');
 *   },
 *   onError: (error) => {
 *     console.error(`Delete failed: ${error.message}`);
 *   }
 * });
 *
 * deleteTeam.mutate('team-123');
 * ```
 */
export function useDeleteResponseTeam(options: UseDeleteResponseTeamOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<void, Error, string>({
    mutationFn: async (teamId: string) => {
      // Note: API client doesn't have deleteTeam method
      throw new Error('Delete team endpoint not yet implemented in API client');
    },

    onSuccess: (_, teamId) => {
      // Invalidate all team lists
      queryClient.invalidateQueries({
        queryKey: teamQueryKeys.lists(),
      });

      // Invalidate the deleted team detail
      queryClient.invalidateQueries({
        queryKey: teamQueryKeys.detail(teamId),
      });

      // Invalidate available teams
      queryClient.invalidateQueries({
        queryKey: teamQueryKeys.available(),
      });

      // Remove from cache
      queryClient.removeQueries({
        queryKey: teamQueryKeys.detail(teamId),
      });

      callbackOptions.onSuccess?.();
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Assign Team
 */
export interface UseAssignResponseTeamOptions {
  onSuccess?: (updatedIncident: any) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Assign Team Parameters
 */
export interface AssignResponseTeamParams {
  incidentId: string;
  teamId: string;
}

/**
 * Hook to assign a response team to an incident
 * Links the team to the incident for coordinated response
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const assignTeam = useAssignResponseTeam({
 *   onSuccess: (incident) => {
 *     console.log(`Team assigned to incident ${incident.incident_number}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Assignment failed: ${error.message}`);
 *   }
 * });
 *
 * assignTeam.mutate({
 *   incidentId: 'incident-123',
 *   teamId: 'team-456'
 * });
 * ```
 */
export function useAssignResponseTeam(options: UseAssignResponseTeamOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<any, Error, AssignResponseTeamParams>({
    mutationFn: ({ incidentId, teamId }: AssignResponseTeamParams) =>
      responseClient.assignResponseTeam(incidentId, teamId),

    onSuccess: (data, variables) => {
      // Invalidate incident team query
      queryClient.invalidateQueries({
        queryKey: teamQueryKeys.incidentTeam(variables.incidentId),
      });

      // Invalidate incident detail
      queryClient.invalidateQueries({
        queryKey: ['response', 'incidents', variables.incidentId],
      });

      // Invalidate incidents list
      queryClient.invalidateQueries({
        queryKey: ['response', 'incidents', 'list'],
      });

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Add Team Member
 */
export interface UseAddTeamMemberOptions {
  onSuccess?: (team: ResponseTeam) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Add Team Member Parameters
 */
export interface AddTeamMemberParams {
  teamId: string;
  memberData: {
    user_id: string;
    role: string;
    name: string;
    email: string;
    phone?: string;
    is_primary?: boolean;
  };
}

/**
 * Hook to add a member to a response team
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const addMember = useAddTeamMember({
 *   onSuccess: (team) => {
 *     console.log(`Member added to ${team.name}`);
 *   }
 * });
 *
 * addMember.mutate({
 *   teamId: 'team-123',
 *   memberData: {
 *     user_id: 'user-789',
 *     role: TeamRole.SECURITY_LEAD,
 *     name: 'Bob Johnson',
 *     email: 'bob.johnson@company.com',
 *     phone: '+1-555-0102',
 *     is_primary: false
 *   }
 * });
 * ```
 */
export function useAddTeamMember(options: UseAddTeamMemberOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ResponseTeam, Error, AddTeamMemberParams>({
    mutationFn: async ({ teamId, memberData }: AddTeamMemberParams) => {
      // Note: API doesn't have add member endpoint, would need to use update
      throw new Error('Add team member endpoint not yet implemented');
    },

    onSuccess: (data) => {
      // Invalidate team lists
      queryClient.invalidateQueries({
        queryKey: teamQueryKeys.lists(),
      });

      // Invalidate the specific team detail
      if (data.id) {
        queryClient.invalidateQueries({
          queryKey: teamQueryKeys.detail(data.id),
        });
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Remove Team Member
 */
export interface UseRemoveTeamMemberOptions {
  onSuccess?: (team: ResponseTeam) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Remove Team Member Parameters
 */
export interface RemoveTeamMemberParams {
  teamId: string;
  userId: string;
}

/**
 * Hook to remove a member from a response team
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const removeMember = useRemoveTeamMember({
 *   onSuccess: (team) => {
 *     console.log(`Member removed from ${team.name}`);
 *   }
 * });
 *
 * removeMember.mutate({
 *   teamId: 'team-123',
 *   userId: 'user-789'
 * });
 * ```
 */
export function useRemoveTeamMember(options: UseRemoveTeamMemberOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ResponseTeam, Error, RemoveTeamMemberParams>({
    mutationFn: async ({ teamId, userId }: RemoveTeamMemberParams) => {
      // Note: API doesn't have remove member endpoint, would need to use update
      throw new Error('Remove team member endpoint not yet implemented');
    },

    onSuccess: (data) => {
      // Invalidate team lists
      queryClient.invalidateQueries({
        queryKey: teamQueryKeys.lists(),
      });

      // Invalidate the specific team detail
      if (data.id) {
        queryClient.invalidateQueries({
          queryKey: teamQueryKeys.detail(data.id),
        });
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

// ============================================================================
// RESPONSE ACTIONS - QUERY HOOKS (5 hooks)
// ============================================================================

/**
 * Hook Parameters - List Actions
 */
export interface UseResponseActionsParams {
  incidentId?: string;
  enabled?: boolean;
}

/**
 * Hook to fetch response actions
 * Returns all actions or filtered by incident
 *
 * @param params - Query parameters with optional incidentId
 * @returns Query result with actions array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: actions, isLoading } = useResponseActions({
 *   incidentId: 'incident-123',
 *   enabled: true
 * });
 *
 * if (actions) {
 *   console.log(`Found ${actions.length} response actions`);
 *   const pending = actions.filter(a => a.status === ActionStatus.PENDING);
 *   const inProgress = actions.filter(a => a.status === ActionStatus.IN_PROGRESS);
 *   const completed = actions.filter(a => a.status === ActionStatus.COMPLETED);
 *   console.log(`Pending: ${pending.length}, In Progress: ${inProgress.length}, Completed: ${completed.length}`);
 * }
 * ```
 */
export function useResponseActions({ incidentId, enabled = true }: UseResponseActionsParams = {}) {
  return useQuery({
    queryKey: incidentId ? actionQueryKeys.list(incidentId) : actionQueryKeys.lists(),
    queryFn: async () => {
      if (!incidentId) {
        throw new Error('incidentId is required');
      }
      return responseClient.listIncidentActions(incidentId);
    },
    enabled: enabled && !!incidentId,
    staleTime: 3 * 60 * 1000, // 3 minutes (shorter for action tracking)
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: true,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Incident Actions
 */
export interface UseIncidentActionsParams {
  incidentId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch actions for a specific incident
 * Alias for useResponseActions with required incidentId
 *
 * @param params - Query parameters with incidentId
 * @returns Query result with actions array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: incidentActions } = useIncidentActions({
 *   incidentId: 'incident-123'
 * });
 *
 * if (incidentActions) {
 *   console.log(`${incidentActions.length} actions for this incident`);
 * }
 * ```
 */
export function useIncidentActions({ incidentId, enabled = true }: UseIncidentActionsParams) {
  return useResponseActions({ incidentId, enabled });
}

/**
 * Hook Parameters - Single Action
 */
export interface UseResponseActionParams {
  actionId: string;
  enabled?: boolean;
}

/**
 * Hook to fetch a single response action by ID
 *
 * @param params - Query parameters with actionId
 * @returns Query result with action data, loading state, error
 *
 * @example
 * ```tsx
 * const { data: action, isLoading, error } = useResponseAction({
 *   actionId: 'action-123',
 *   enabled: true
 * });
 *
 * if (action) {
 *   console.log(`Action: ${action.title}`);
 *   console.log(`Type: ${action.action_type}`);
 *   console.log(`Priority: ${action.priority}`);
 *   console.log(`Status: ${action.status}`);
 *   console.log(`Progress: ${action.progress_percentage}%`);
 *   console.log(`Assigned to: ${action.assigned_to_name || 'Unassigned'}`);
 * }
 * ```
 */
export function useResponseAction({ actionId, enabled = true }: UseResponseActionParams) {
  return useQuery({
    queryKey: actionQueryKeys.detail(actionId),
    queryFn: async () => {
      // Note: API doesn't have single action endpoint, need to implement workaround
      throw new Error('Get single action endpoint not yet implemented');
    },
    enabled: enabled && !!actionId,
    staleTime: 3 * 60 * 1000, // 3 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Actions by Type
 */
export interface UseActionsByTypeParams {
  incidentId: string;
  actionType: string;
  enabled?: boolean;
}

/**
 * Hook to fetch actions filtered by type
 * Returns actions of a specific type (immediate, short_term, recovery, etc.)
 *
 * @param params - Query parameters with incidentId and actionType
 * @returns Query result with actions array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: immediateActions } = useActionsByType({
 *   incidentId: 'incident-123',
 *   actionType: 'immediate'
 * });
 *
 * if (immediateActions) {
 *   console.log(`${immediateActions.length} immediate actions`);
 *   immediateActions.forEach(action => {
 *     console.log(`- ${action.title} (${action.status})`);
 *   });
 * }
 * ```
 */
export function useActionsByType({ incidentId, actionType, enabled = true }: UseActionsByTypeParams) {
  return useQuery({
    queryKey: actionQueryKeys.byType(incidentId, actionType),
    queryFn: async () => {
      const allActions = await responseClient.listIncidentActions(incidentId);
      return allActions.filter(action => action.action_type === actionType);
    },
    enabled: enabled && !!incidentId && !!actionType,
    staleTime: 3 * 60 * 1000, // 3 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: true,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

/**
 * Hook Parameters - Overdue Actions
 */
export interface UseOverdueActionsParams {
  incidentId?: string;
  enabled?: boolean;
}

/**
 * Hook to fetch overdue response actions
 * Returns actions past their due date that are not completed
 *
 * @param params - Query parameters with optional incidentId
 * @returns Query result with overdue actions array, loading state, error
 *
 * @example
 * ```tsx
 * const { data: overdueActions } = useOverdueActions({
 *   incidentId: 'incident-123',
 *   enabled: true
 * });
 *
 * if (overdueActions && overdueActions.length > 0) {
 *   console.warn(`⚠️ ${overdueActions.length} overdue actions!`);
 *   overdueActions.forEach(action => {
 *     if (action.due_date) {
 *       const daysPast = Math.floor(
 *         (Date.now() - new Date(action.due_date).getTime()) / (1000 * 60 * 60 * 24)
 *       );
 *       console.log(`- ${action.title}: ${daysPast} days overdue`);
 *     }
 *   });
 * }
 * ```
 */
export function useOverdueActions({ incidentId, enabled = true }: UseOverdueActionsParams = {}) {
  return useQuery({
    queryKey: actionQueryKeys.overdue(incidentId),
    queryFn: async () => {
      if (!incidentId) {
        throw new Error('incidentId is required for overdue actions');
      }
      const allActions = await responseClient.listIncidentActions(incidentId);
      const now = Date.now();
      return allActions.filter(action => {
        if (!action.due_date || action.status === 'completed' || action.status === 'cancelled') {
          return false;
        }
        return new Date(action.due_date).getTime() < now;
      });
    },
    enabled: enabled && !!incidentId,
    staleTime: 1 * 60 * 1000, // 1 minute (very short for overdue tracking)
    gcTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: true,
    refetchInterval: 5 * 60 * 1000, // Auto-refetch every 5 minutes
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// ============================================================================
// RESPONSE ACTIONS - MUTATION HOOKS (7 hooks)
// ============================================================================

/**
 * Hook Options - Add Action
 */
export interface UseAddResponseActionOptions {
  onSuccess?: (action: ResponseAction) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Add Action Parameters
 */
export interface AddResponseActionParams {
  incidentId: string;
  data: ResponseActionCreate;
}

/**
 * Hook to add a new response action to an incident
 * Automatically invalidates action list cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const addAction = useAddResponseAction({
 *   onSuccess: (action) => {
 *     console.log(`Action "${action.title}" added`);
 *   },
 *   onError: (error) => {
 *     console.error(`Failed to add action: ${error.message}`);
 *   }
 * });
 *
 * addAction.mutate({
 *   incidentId: 'incident-123',
 *   data: {
 *     title: 'Isolate Affected Systems',
 *     description: 'Immediately disconnect affected systems from the network to prevent spread',
 *     action_type: 'immediate',
 *     priority: ActionPriority.URGENT,
 *     assigned_to: 'user-456',
 *     assigned_to_name: 'John Smith',
 *     due_date: new Date(Date.now() + 3600000).toISOString(), // 1 hour from now
 *     estimated_hours: 2,
 *     checklist: [
 *       { id: '1', description: 'Identify all affected systems', completed: false },
 *       { id: '2', description: 'Disconnect network cables', completed: false },
 *       { id: '3', description: 'Document isolation procedures', completed: false }
 *     ]
 *   }
 * });
 * ```
 */
export function useAddResponseAction(options: UseAddResponseActionOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ResponseAction, Error, AddResponseActionParams>({
    mutationFn: ({ incidentId, data }: AddResponseActionParams) =>
      responseClient.addResponseAction(incidentId, data),

    onSuccess: (data, variables) => {
      // Invalidate action lists to refetch with new action
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.lists(),
      });

      // Invalidate incident actions
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.list(variables.incidentId),
      });

      // Invalidate incident detail
      queryClient.invalidateQueries({
        queryKey: ['response', 'incidents', variables.incidentId],
      });

      // Invalidate by type if action has type
      if (data.action_type) {
        queryClient.invalidateQueries({
          queryKey: actionQueryKeys.byType(variables.incidentId, data.action_type),
        });
      }

      // Optimistically set the single action cache
      if (data.id) {
        queryClient.setQueryData(actionQueryKeys.detail(data.id), data);
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Update Action
 */
export interface UseUpdateResponseActionOptions {
  onSuccess?: (action: ResponseAction) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Update Action Parameters
 */
export interface UpdateResponseActionParams {
  actionId: string;
  data: ResponseActionUpdate;
}

/**
 * Hook to update an existing response action
 * Automatically invalidates relevant cache entries on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const updateAction = useUpdateResponseAction({
 *   onSuccess: (action) => {
 *     console.log(`Action "${action.title}" updated`);
 *   },
 *   onError: (error) => {
 *     console.error(`Update failed: ${error.message}`);
 *   }
 * });
 *
 * updateAction.mutate({
 *   actionId: 'action-123',
 *   data: {
 *     status: ActionStatus.IN_PROGRESS,
 *     completion_notes: 'Systems isolated. Beginning forensic analysis.'
 *   }
 * });
 * ```
 */
export function useUpdateResponseAction(options: UseUpdateResponseActionOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ResponseAction, Error, UpdateResponseActionParams>({
    mutationFn: ({ actionId, data }: UpdateResponseActionParams) =>
      responseClient.updateResponseAction(actionId, data),

    onSuccess: (data) => {
      // Invalidate action lists
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.lists(),
      });

      // Invalidate the specific action detail
      if (data.id) {
        queryClient.invalidateQueries({
          queryKey: actionQueryKeys.detail(data.id),
        });
      }

      // Invalidate incident actions
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.list(data.incident_id),
      });

      // Invalidate incident detail
      queryClient.invalidateQueries({
        queryKey: ['response', 'incidents', data.incident_id],
      });

      // Invalidate overdue actions in case status changed
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.overdue(data.incident_id),
      });

      // Update the cached action data
      if (data.id) {
        queryClient.setQueryData(actionQueryKeys.detail(data.id), data);
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Delete Action
 */
export interface UseDeleteResponseActionOptions {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Delete Action Parameters
 */
export interface DeleteResponseActionParams {
  actionId: string;
  incidentId: string;
}

/**
 * Hook to delete a response action
 * Automatically invalidates action cache on success
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const deleteAction = useDeleteResponseAction({
 *   onSuccess: () => {
 *     console.log('Action deleted successfully');
 *   },
 *   onError: (error) => {
 *     console.error(`Delete failed: ${error.message}`);
 *   }
 * });
 *
 * deleteAction.mutate({
 *   actionId: 'action-123',
 *   incidentId: 'incident-456'
 * });
 * ```
 */
export function useDeleteResponseAction(options: UseDeleteResponseActionOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<void, Error, DeleteResponseActionParams>({
    mutationFn: async ({ actionId }: DeleteResponseActionParams) => {
      // Note: API doesn't have deleteAction endpoint
      throw new Error('Delete action endpoint not yet implemented');
    },

    onSuccess: (_, variables) => {
      // Invalidate all action lists
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.lists(),
      });

      // Invalidate the deleted action detail
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.detail(variables.actionId),
      });

      // Invalidate incident actions
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.list(variables.incidentId),
      });

      // Invalidate incident detail
      queryClient.invalidateQueries({
        queryKey: ['response', 'incidents', variables.incidentId],
      });

      // Remove from cache
      queryClient.removeQueries({
        queryKey: actionQueryKeys.detail(variables.actionId),
      });

      callbackOptions.onSuccess?.();
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Complete Action
 */
export interface UseCompleteResponseActionOptions {
  onSuccess?: (action: ResponseAction) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Complete Action Parameters
 */
export interface CompleteResponseActionParams {
  actionId: string;
  completionNotes?: string;
}

/**
 * Hook to mark a response action as complete
 * Sets status to completed and records completion details
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const completeAction = useCompleteResponseAction({
 *   onSuccess: (action) => {
 *     console.log(`Action "${action.title}" completed!`);
 *     console.log(`Completed at: ${action.completed_at}`);
 *   },
 *   onError: (error) => {
 *     console.error(`Failed to complete action: ${error.message}`);
 *   }
 * });
 *
 * completeAction.mutate({
 *   actionId: 'action-123',
 *   completionNotes: 'All affected systems isolated. Forensic images captured. Network segmentation verified.'
 * });
 * ```
 */
export function useCompleteResponseAction(options: UseCompleteResponseActionOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ResponseAction, Error, CompleteResponseActionParams>({
    mutationFn: ({ actionId, completionNotes }: CompleteResponseActionParams) =>
      responseClient.completeResponseAction(actionId, completionNotes),

    onSuccess: (data) => {
      // Invalidate action lists
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.lists(),
      });

      // Invalidate the specific action detail
      if (data.id) {
        queryClient.invalidateQueries({
          queryKey: actionQueryKeys.detail(data.id),
        });
      }

      // Invalidate incident actions
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.list(data.incident_id),
      });

      // Invalidate incident detail
      queryClient.invalidateQueries({
        queryKey: ['response', 'incidents', data.incident_id],
      });

      // Invalidate overdue actions - completion removes from overdue
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.overdue(data.incident_id),
      });

      // Update the cached action data
      if (data.id) {
        queryClient.setQueryData(actionQueryKeys.detail(data.id), data);
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Assign Action
 */
export interface UseAssignActionOptions {
  onSuccess?: (action: ResponseAction) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Assign Action Parameters
 */
export interface AssignActionParams {
  actionId: string;
  assignedTo: string;
  assignedToName?: string;
}

/**
 * Hook to assign a response action to a team member
 * Updates the assigned_to field
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const assignAction = useAssignAction({
 *   onSuccess: (action) => {
 *     console.log(`Action assigned to ${action.assigned_to_name}`);
 *   }
 * });
 *
 * assignAction.mutate({
 *   actionId: 'action-123',
 *   assignedTo: 'user-456',
 *   assignedToName: 'Jane Doe'
 * });
 * ```
 */
export function useAssignAction(options: UseAssignActionOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ResponseAction, Error, AssignActionParams>({
    mutationFn: ({ actionId, assignedTo, assignedToName }: AssignActionParams) =>
      responseClient.updateResponseAction(actionId, {
        assigned_to: assignedTo,
        assigned_to_name: assignedToName,
      }),

    onSuccess: (data) => {
      // Invalidate action lists
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.lists(),
      });

      // Invalidate the specific action detail
      if (data.id) {
        queryClient.invalidateQueries({
          queryKey: actionQueryKeys.detail(data.id),
        });
      }

      // Invalidate incident actions
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.list(data.incident_id),
      });

      // Update the cached action data
      if (data.id) {
        queryClient.setQueryData(actionQueryKeys.detail(data.id), data);
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Reassign Action
 */
export interface UseReassignActionOptions {
  onSuccess?: (action: ResponseAction) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Reassign Action Parameters
 */
export interface ReassignActionParams {
  actionId: string;
  newAssignedTo: string;
  newAssignedToName?: string;
  reason?: string;
}

/**
 * Hook to reassign a response action to a different team member
 * Similar to assign but implies changing from existing assignment
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const reassignAction = useReassignAction({
 *   onSuccess: (action) => {
 *     console.log(`Action reassigned to ${action.assigned_to_name}`);
 *   }
 * });
 *
 * reassignAction.mutate({
 *   actionId: 'action-123',
 *   newAssignedTo: 'user-789',
 *   newAssignedToName: 'Bob Johnson',
 *   reason: 'Original assignee unavailable due to emergency leave'
 * });
 * ```
 */
export function useReassignAction(options: UseReassignActionOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ResponseAction, Error, ReassignActionParams>({
    mutationFn: ({ actionId, newAssignedTo, newAssignedToName }: ReassignActionParams) =>
      responseClient.updateResponseAction(actionId, {
        assigned_to: newAssignedTo,
        assigned_to_name: newAssignedToName,
      }),

    onSuccess: (data) => {
      // Invalidate action lists
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.lists(),
      });

      // Invalidate the specific action detail
      if (data.id) {
        queryClient.invalidateQueries({
          queryKey: actionQueryKeys.detail(data.id),
        });
      }

      // Invalidate incident actions
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.list(data.incident_id),
      });

      // Update the cached action data
      if (data.id) {
        queryClient.setQueryData(actionQueryKeys.detail(data.id), data);
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

/**
 * Hook Options - Update Action Progress
 */
export interface UseUpdateActionProgressOptions {
  onSuccess?: (action: ResponseAction) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  showToast?: boolean;
}

/**
 * Update Action Progress Parameters
 */
export interface UpdateActionProgressParams {
  actionId: string;
  progressPercentage: number;
}

/**
 * Hook to update progress for a response action
 * Updates progress percentage (0-100)
 *
 * @param options - Callback options and settings
 * @returns Mutation result with mutate function, loading state, error
 *
 * @example
 * ```tsx
 * const updateProgress = useUpdateActionProgress({
 *   onSuccess: (action) => {
 *     console.log(`Progress updated: ${action.progress_percentage}%`);
 *   },
 *   onError: (error) => {
 *     console.error(`Progress update failed: ${error.message}`);
 *   }
 * });
 *
 * updateProgress.mutate({
 *   actionId: 'action-123',
 *   progressPercentage: 75
 * });
 * ```
 */
export function useUpdateActionProgress(options: UseUpdateActionProgressOptions = {}) {
  const queryClient = useQueryClient();
  const { showToast = false, ...callbackOptions } = options;

  return useMutation<ResponseAction, Error, UpdateActionProgressParams>({
    mutationFn: ({ actionId, progressPercentage }: UpdateActionProgressParams) => {
      // Calculate status based on progress
      let status = ActionStatus.IN_PROGRESS;
      if (progressPercentage === 0) {
        status = ActionStatus.PENDING;
      } else if (progressPercentage === 100) {
        status = ActionStatus.COMPLETED;
      }

      return responseClient.updateResponseAction(actionId, {
        status,
        // Note: ResponseActionUpdate doesn't have progress_percentage
        // This would need to be added to the type or handled differently
      });
    },

    onSuccess: (data) => {
      // Invalidate action lists
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.lists(),
      });

      // Invalidate the specific action detail
      if (data.id) {
        queryClient.invalidateQueries({
          queryKey: actionQueryKeys.detail(data.id),
        });
      }

      // Invalidate incident actions
      queryClient.invalidateQueries({
        queryKey: actionQueryKeys.list(data.incident_id),
      });

      // Update the cached action data
      if (data.id) {
        queryClient.setQueryData(actionQueryKeys.detail(data.id), data);
      }

      callbackOptions.onSuccess?.(data);
    },

    onError: (error: Error) => {
      callbackOptions.onError?.(error);
    },

    onSettled: () => {
      callbackOptions.onSettled?.();
    },
  });
}

// ============================================================================
// PREFETCH UTILITIES (3 utilities)
// ============================================================================

/**
 * Prefetch utility for teams list
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href="/response/teams"
 *   onMouseEnter={() => usePrefetchTeams(queryClient)}
 * >
 *   View Teams
 * </Link>
 * ```
 */
export function usePrefetchTeams(queryClient: QueryClient, isActive?: boolean) {
  return queryClient.prefetchQuery({
    queryKey: teamQueryKeys.list(isActive),
    queryFn: () => responseClient.listResponseTeams(isActive),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Prefetch utility for single team
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/response/teams/${teamId}`}
 *   onMouseEnter={() => usePrefetchTeam(queryClient, teamId)}
 * >
 *   View Team Details
 * </Link>
 * ```
 */
export function usePrefetchTeam(queryClient: QueryClient, teamId: string) {
  return queryClient.prefetchQuery({
    queryKey: teamQueryKeys.detail(teamId),
    queryFn: async () => {
      const teams = await responseClient.listResponseTeams();
      const team = teams.find(t => t.id === teamId);
      if (!team) throw new Error('Team not found');
      return team;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Prefetch utility for incident actions
 * Useful for optimistic navigation and hover states
 *
 * @example
 * ```tsx
 * <Link
 *   href={`/response/incidents/${incidentId}/actions`}
 *   onMouseEnter={() => usePrefetchAction(queryClient, incidentId)}
 * >
 *   View Actions
 * </Link>
 * ```
 */
export function usePrefetchAction(queryClient: QueryClient, incidentId: string) {
  return queryClient.prefetchQuery({
    queryKey: actionQueryKeys.list(incidentId),
    queryFn: () => responseClient.listIncidentActions(incidentId),
    staleTime: 3 * 60 * 1000,
  });
}

/**
 * Invalidate all teams and actions caches
 * Useful when performing bulk operations or system-wide updates
 *
 * @example
 * ```tsx
 * const invalidateAll = () => {
 *   useInvalidateTeamsAndActions(queryClient);
 *   toast.success('Cache refreshed');
 * };
 * ```
 */
export function useInvalidateTeamsAndActions(queryClient: QueryClient) {
  // Invalidate all team queries
  queryClient.invalidateQueries({
    queryKey: teamQueryKeys.all,
  });

  // Invalidate all action queries
  queryClient.invalidateQueries({
    queryKey: actionQueryKeys.all,
  });

  // Invalidate incident queries since they reference teams and actions
  queryClient.invalidateQueries({
    queryKey: ['response', 'incidents'],
  });
}
