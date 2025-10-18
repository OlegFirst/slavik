/**
 * Documents Service API Client
 * Real integration with backend (port 8024)
 * Comprehensive API client for all Documents Service endpoints
 * Week 4 - Documents Module
 */

import { SERVICES } from '@/config/services';
import type {
  Document,
  DocumentCreate,
  DocumentUpdate,
  DocumentType,
  DocumentStatus,
  DocumentClassification,
  SharePermission,
  ApprovalStatus,
  WorkflowStatus,
  VersionComparison,
  DocumentShare,
  ShareRequest,
  DocumentApproval,
  ApprovalRequest,
  ApprovalResponse,
  RetentionPolicy,
  DocumentAccess,
} from '@/types/documents';

// Re-export types for convenience
export type {
  Document,
  DocumentCreate,
  DocumentUpdate,
  DocumentType,
  DocumentStatus,
  DocumentClassification,
  SharePermission,
  ApprovalStatus,
  WorkflowStatus,
  VersionComparison,
  DocumentShare,
  ShareRequest,
  DocumentApproval,
  ApprovalRequest,
  ApprovalResponse,
  RetentionPolicy,
  DocumentAccess,
};

export interface DocumentFilters {
  tenant_id?: string;
  document_type?: DocumentType;
  status?: DocumentStatus;
  classification?: DocumentClassification;
  owner_id?: string;
  department?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

// ==================== API CLIENT ====================

const DOCUMENTS_BASE_URL = SERVICES.DOCUMENTS.url;

class DocumentsAPIError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: any
  ) {
    super(message);
    this.name = 'DocumentsAPIError';
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${DOCUMENTS_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new DocumentsAPIError(
      error.detail || 'Request failed',
      response.status,
      error
    );
  }

  // Handle empty responses (e.g., DELETE)
  if (response.status === 204 || response.headers.get('content-length') === '0') {
    return {} as T;
  }

  return response.json();
}

export const documentsAPI = {
  // ==================== CRUD OPERATIONS ====================

  /**
   * Create new document metadata
   * POST /api/documents
   */
  async createDocument(data: DocumentCreate): Promise<Document> {
    return request<Document>(
      '/api/documents',
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  },

  /**
   * Upload file to existing document
   * POST /api/documents/{documentId}/upload
   * Uses FormData for file upload with auto-process option
   */
  async uploadFile(
    documentId: number,
    file: File,
    userId: string,
    autoProcess: boolean = true
  ): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);

    const queryParams = new URLSearchParams();
    queryParams.append('auto_process', String(autoProcess));

    return request<Document>(
      `/api/documents/${documentId}/upload?${queryParams.toString()}`,
      {
        method: 'POST',
        headers: {
          // Remove Content-Type header to let browser set it with boundary
        } as HeadersInit,
        body: formData,
      }
    );
  },

  /**
   * Get single document by ID
   * GET /api/documents/{documentId}
   * Automatically logs access
   */
  async getDocument(documentId: number, userId: string): Promise<Document> {
    const queryParams = new URLSearchParams();
    queryParams.append('user_id', userId);

    return request<Document>(
      `/api/documents/${documentId}?${queryParams.toString()}`
    );
  },

  /**
   * List documents with optional filters
   * GET /api/documents
   */
  async listDocuments(filters?: DocumentFilters): Promise<{ documents: Document[]; total: number }> {
    const queryParams = new URLSearchParams();

    if (filters?.tenant_id) queryParams.append('tenant_id', filters.tenant_id);
    if (filters?.document_type) queryParams.append('document_type', filters.document_type);
    if (filters?.status) queryParams.append('status', filters.status);
    if (filters?.classification) queryParams.append('classification', filters.classification);
    if (filters?.owner_id) queryParams.append('owner_id', filters.owner_id);
    if (filters?.department) queryParams.append('department', filters.department);
    if (filters?.search) queryParams.append('search', filters.search);
    if (filters?.skip !== undefined) queryParams.append('skip', String(filters.skip));
    if (filters?.limit !== undefined) queryParams.append('limit', String(filters.limit));

    return request<{ documents: Document[]; total: number }>(
      `/api/documents?${queryParams.toString()}`
    );
  },

  /**
   * Update document metadata
   * PATCH /api/documents/{documentId}
   */
  async updateDocument(documentId: number, data: DocumentUpdate): Promise<Document> {
    return request<Document>(
      `/api/documents/${documentId}`,
      {
        method: 'PATCH',
        body: JSON.stringify(data),
      }
    );
  },

  /**
   * Delete document (soft delete - sets status to ARCHIVED)
   * DELETE /api/documents/{documentId}
   */
  async deleteDocument(documentId: number, userId: string): Promise<void> {
    const queryParams = new URLSearchParams();
    queryParams.append('user_id', userId);

    return request<void>(
      `/api/documents/${documentId}?${queryParams.toString()}`,
      {
        method: 'DELETE',
      }
    );
  },

  /**
   * Download document file
   * GET /api/documents/{documentId}/download
   * Returns Blob for file download
   */
  async downloadDocument(documentId: number, userId: string): Promise<Blob> {
    const queryParams = new URLSearchParams();
    queryParams.append('user_id', userId);

    const url = `${DOCUMENTS_BASE_URL}/api/documents/${documentId}/download?${queryParams.toString()}`;

    const response = await fetch(url);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new DocumentsAPIError(
        error.detail || 'Download failed',
        response.status,
        error
      );
    }

    return response.blob();
  },

  // ==================== LIFECYCLE WORKFLOW ====================

  /**
   * Execute workflow action on document
   * POST /api/documents/{documentId}/workflow/{action}
   * Actions: submit_for_review, approve, reject, publish, archive, supersede, mark_obsolete, restore, revise
   */
  async executeWorkflowAction(
    documentId: number,
    action: string,
    userId: string,
    notes?: string
  ): Promise<WorkflowStatus> {
    const body: Record<string, string> = { user_id: userId };
    if (notes) body.notes = notes;

    return request<WorkflowStatus>(
      `/api/documents/${documentId}/workflow/${action}`,
      {
        method: 'POST',
        body: JSON.stringify(body),
      }
    );
  },

  /**
   * Get current workflow status
   * GET /api/documents/{documentId}/workflow/status
   */
  async getWorkflowStatus(documentId: number): Promise<WorkflowStatus> {
    return request<WorkflowStatus>(
      `/api/documents/${documentId}/workflow/status`
    );
  },

  // ==================== VERSION CONTROL ====================

  /**
   * Create new version of document
   * POST /api/documents/{documentId}/version
   */
  async createVersion(
    documentId: number,
    userId: string,
    versionNotes?: string
  ): Promise<Document> {
    const body: Record<string, string> = { user_id: userId };
    if (versionNotes) body.version_notes = versionNotes;

    return request<Document>(
      `/api/documents/${documentId}/version`,
      {
        method: 'POST',
        body: JSON.stringify(body),
      }
    );
  },

  /**
   * Get all versions of a document
   * GET /api/documents/{documentId}/versions
   */
  async getVersions(documentId: number): Promise<Document[]> {
    return request<Document[]>(
      `/api/documents/${documentId}/versions`
    );
  },

  /**
   * Compare two document versions
   * POST /api/documents/compare
   */
  async compareVersions(
    sourceId: number,
    targetId: number,
    userId: string
  ): Promise<VersionComparison> {
    return request<VersionComparison>(
      '/api/documents/compare',
      {
        method: 'POST',
        body: JSON.stringify({
          source_id: sourceId,
          target_id: targetId,
          user_id: userId,
        }),
      }
    );
  },

  // ==================== SHARING & COLLABORATION ====================

  /**
   * Share document with user, role, or department
   * POST /api/documents/{documentId}/share
   */
  async shareDocument(
    documentId: number,
    shareData: ShareRequest
  ): Promise<DocumentShare> {
    return request<DocumentShare>(
      `/api/documents/${documentId}/share`,
      {
        method: 'POST',
        body: JSON.stringify(shareData),
      }
    );
  },

  /**
   * Get all shares for a document
   * GET /api/documents/{documentId}/shares
   */
  async getShares(documentId: number): Promise<DocumentShare[]> {
    return request<DocumentShare[]>(
      `/api/documents/${documentId}/shares`
    );
  },

  // ==================== APPROVAL WORKFLOW ====================

  /**
   * Request approval for document
   * POST /api/documents/{documentId}/approvals
   */
  async requestApproval(
    documentId: number,
    approvalData: ApprovalRequest
  ): Promise<DocumentApproval> {
    return request<DocumentApproval>(
      `/api/documents/${documentId}/approvals`,
      {
        method: 'POST',
        body: JSON.stringify(approvalData),
      }
    );
  },

  /**
   * Respond to approval request
   * POST /api/documents/approvals/{approvalId}/respond
   */
  async respondToApproval(
    approvalId: number,
    response: ApprovalResponse
  ): Promise<DocumentApproval> {
    return request<DocumentApproval>(
      `/api/documents/approvals/${approvalId}/respond`,
      {
        method: 'POST',
        body: JSON.stringify(response),
      }
    );
  },

  /**
   * Get all approvals for a document
   * GET /api/documents/{documentId}/approvals
   */
  async getApprovals(documentId: number): Promise<DocumentApproval[]> {
    return request<DocumentApproval[]>(
      `/api/documents/${documentId}/approvals`
    );
  },

  // ==================== RETENTION POLICIES ====================

  /**
   * Create retention policy
   * POST /api/documents/retention-policies
   */
  async createRetentionPolicy(policyData: Omit<RetentionPolicy, 'id' | 'created_at' | 'updated_at'>): Promise<RetentionPolicy> {
    return request<RetentionPolicy>(
      '/api/documents/retention-policies',
      {
        method: 'POST',
        body: JSON.stringify(policyData),
      }
    );
  },

  /**
   * Get retention policies for tenant
   * GET /api/documents/retention-policies
   */
  async getRetentionPolicies(tenantId: string): Promise<RetentionPolicy[]> {
    const queryParams = new URLSearchParams();
    queryParams.append('tenant_id', tenantId);

    return request<RetentionPolicy[]>(
      `/api/documents/retention-policies?${queryParams.toString()}`
    );
  },

  /**
   * Get retention status for document
   * GET /api/documents/{documentId}/retention
   */
  async getRetentionStatus(documentId: number): Promise<{
    document_id: number;
    policy: RetentionPolicy | null;
    retention_date: string | null;
    days_until_action: number | null;
    legal_hold: boolean;
  }> {
    return request(
      `/api/documents/${documentId}/retention`
    );
  },

  // ==================== INTEGRATION ====================

  /**
   * Get documents linked to a plan
   * GET /api/documents/plans/{planId}/documents
   */
  async getPlanDocuments(planId: number): Promise<Document[]> {
    return request<Document[]>(
      `/api/documents/plans/${planId}/documents`
    );
  },

  /**
   * Get ISO coverage analysis
   * GET /api/documents/iso-coverage
   */
  async getISOCoverage(tenantId: string): Promise<{
    tenant_id: string;
    total_clauses: number;
    covered_clauses: number;
    coverage_percentage: number;
    clause_details: Array<{
      clause: string;
      document_count: number;
      documents: Document[];
    }>;
  }> {
    const queryParams = new URLSearchParams();
    queryParams.append('tenant_id', tenantId);

    return request(
      `/api/documents/iso-coverage?${queryParams.toString()}`
    );
  },

  // ==================== AUDIT ====================

  /**
   * Get access log for document
   * GET /api/documents/{documentId}/access-log
   */
  async getAccessLog(
    documentId: number,
    filters?: {
      action_type?: string;
      user_id?: string;
      skip?: number;
      limit?: number;
    }
  ): Promise<{ logs: DocumentAccess[]; total: number }> {
    const queryParams = new URLSearchParams();

    if (filters?.action_type) queryParams.append('action_type', filters.action_type);
    if (filters?.user_id) queryParams.append('user_id', filters.user_id);
    if (filters?.skip !== undefined) queryParams.append('skip', String(filters.skip));
    if (filters?.limit !== undefined) queryParams.append('limit', String(filters.limit));

    return request<{ logs: DocumentAccess[]; total: number }>(
      `/api/documents/${documentId}/access-log?${queryParams.toString()}`
    );
  },

  // ==================== AI/WORKFLOW INTELLIGENCE ====================

  /**
   * Get AI-powered advice for document
   * GET /api/v1/documents/{documentId}/ai-advice
   */
  async getAIAdvice(documentId: number, userId: string): Promise<{
    document_id: number;
    advice: string;
    suggestions: Array<{
      category: string;
      priority: 'HIGH' | 'MEDIUM' | 'LOW';
      suggestion: string;
      rationale: string;
    }>;
    compliance_check: {
      iso_alignment: string[];
      missing_elements: string[];
      recommendations: string[];
    };
    confidence: number;
    generated_at: string;
  }> {
    const queryParams = new URLSearchParams();
    queryParams.append('user_id', userId);

    return request(
      `/api/v1/documents/${documentId}/ai-advice?${queryParams.toString()}`
    );
  },

  /**
   * Get document benchmarks and analytics
   * GET /api/v1/documents/benchmarks
   */
  async getBenchmarks(tenantId: string): Promise<{
    tenant_id: string;
    total_documents: number;
    by_type: Record<DocumentType, number>;
    by_status: Record<DocumentStatus, number>;
    by_classification: Record<DocumentClassification, number>;
    avg_review_time_days: number;
    compliance_score: number;
    trends: {
      created_last_30_days: number;
      approved_last_30_days: number;
      pending_reviews: number;
    };
  }> {
    const queryParams = new URLSearchParams();
    queryParams.append('tenant_id', tenantId);

    return request(
      `/api/v1/documents/benchmarks?${queryParams.toString()}`
    );
  },

  // ==================== SYSTEM ====================

  /**
   * Check Documents service health
   * GET /health
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return request('/health');
  },

  /**
   * Check compliance status
   * GET /api/compliance/check
   */
  async checkCompliance(tenantId: string): Promise<{
    tenant_id: string;
    compliant: boolean;
    checks: Array<{
      check_name: string;
      passed: boolean;
      details: string;
      severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
    }>;
    overall_score: number;
    recommendations: string[];
    checked_at: string;
  }> {
    const queryParams = new URLSearchParams();
    queryParams.append('tenant_id', tenantId);

    return request(
      `/api/compliance/check?${queryParams.toString()}`
    );
  },
};

export { DocumentsAPIError };
