import axios from 'axios';

// API Configuration
const ODOO_BASE_URL = '/web/dataset/call_kw/bcm_templates.record';
const DOC_PROCESSOR_BASE_URL = 'http://localhost:8083';
const AI_ORCHESTRATOR_BASE_URL = '/api/ai-orchestrator';

class BCMTemplatesService {
  constructor() {
    this.templates = new Map();
    this.categories = [
      { id: 'bcp', name: 'Business Continuity Plans', icon: '🔄' },
      { id: 'drp', name: 'Disaster Recovery Plans', icon: '🛡️' },
      { id: 'risk', name: 'Risk Assessment', icon: '⚠️' },
      { id: 'incident', name: 'Incident Response', icon: '🚨' },
      { id: 'crisis', name: 'Crisis Management', icon: '🆘' },
      { id: 'audit', name: 'Audit & Compliance', icon: '✅' },
      { id: 'training', name: 'Training & Awareness', icon: '📚' },
      { id: 'communication', name: 'Communication Plans', icon: '📢' }
    ];
  }

  // Template Library Management
  async getTemplates(filters = {}) {
    try {
      const response = await axios.post(ODOO_BASE_URL, {
        model: 'bcm_templates.record',
        method: 'search_read',
        args: [[]],
        kwargs: {
          fields: [
            'id', 'name', 'description', 'category', 'version', 'status',
            'created_by', 'created_date', 'last_modified', 'tags',
            'template_type', 'compliance_framework', 'approval_status',
            'usage_count', 'file_size', 'merge_fields', 'permissions'
          ],
          domain: this._buildFilterDomain(filters)
        }
      });

      return response.data.result.map(template => ({
        ...template,
        size: this._formatFileSize(template.file_size),
        lastModified: new Date(template.last_modified),
        createdDate: new Date(template.created_date)
      }));
    } catch (error) {
      console.error('Error fetching templates:', error);
      throw new Error('Failed to fetch templates');
    }
  }

  async getTemplateById(id) {
    try {
      const response = await axios.post(ODOO_BASE_URL, {
        model: 'bcm_templates.record',
        method: 'read',
        args: [[id]],
        kwargs: {
          fields: [
            'id', 'name', 'description', 'category', 'version', 'status',
            'content', 'merge_fields', 'form_schema', 'approval_workflow',
            'permissions', 'compliance_requirements', 'parent_template'
          ]
        }
      });

      return response.data.result[0];
    } catch (error) {
      console.error('Error fetching template:', error);
      throw new Error('Failed to fetch template details');
    }
  }

  async createTemplate(templateData) {
    try {
      const response = await axios.post(ODOO_BASE_URL, {
        model: 'bcm_templates.record',
        method: 'create',
        args: [templateData],
        kwargs: {}
      });

      return response.data.result;
    } catch (error) {
      console.error('Error creating template:', error);
      throw new Error('Failed to create template');
    }
  }

  async updateTemplate(id, templateData) {
    try {
      const response = await axios.post(ODOO_BASE_URL, {
        model: 'bcm_templates.record',
        method: 'write',
        args: [[id], templateData],
        kwargs: {}
      });

      return response.data.result;
    } catch (error) {
      console.error('Error updating template:', error);
      throw new Error('Failed to update template');
    }
  }

  async deleteTemplate(id) {
    try {
      const response = await axios.post(ODOO_BASE_URL, {
        model: 'bcm_templates.record',
        method: 'unlink',
        args: [[id]],
        kwargs: {}
      });

      return response.data.result;
    } catch (error) {
      console.error('Error deleting template:', error);
      throw new Error('Failed to delete template');
    }
  }

  // Document Generation
  async generateDocument(templateId, data) {
    try {
      const response = await axios.post(`${DOC_PROCESSOR_BASE_URL}/generate`, {
        template_id: templateId,
        data: data,
        format: 'docx'
      });

      return response.data;
    } catch (error) {
      console.error('Error generating document:', error);
      throw new Error('Failed to generate document');
    }
  }

  async processTemplate(file, category) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('category', category);

      const response = await axios.post(`${DOC_PROCESSOR_BASE_URL}/process-template`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      return response.data;
    } catch (error) {
      console.error('Error processing template:', error);
      throw new Error('Failed to process template');
    }
  }

  // Version Management
  async getTemplateVersions(templateId) {
    try {
      const response = await axios.post(ODOO_BASE_URL, {
        model: 'bcm_templates.version',
        method: 'search_read',
        args: [[]],
        kwargs: {
          fields: ['id', 'version', 'created_date', 'created_by', 'changes', 'status'],
          domain: [['template_id', '=', templateId]],
          order: 'version desc'
        }
      });

      return response.data.result;
    } catch (error) {
      console.error('Error fetching template versions:', error);
      throw new Error('Failed to fetch template versions');
    }
  }

  async createVersion(templateId, changes) {
    try {
      const response = await axios.post(ODOO_BASE_URL, {
        model: 'bcm_templates.version',
        method: 'create',
        args: [{
          template_id: templateId,
          changes: changes,
          status: 'draft'
        }],
        kwargs: {}
      });

      return response.data.result;
    } catch (error) {
      console.error('Error creating version:', error);
      throw new Error('Failed to create version');
    }
  }

  // Approval Workflow
  async submitForApproval(templateId) {
    try {
      const response = await axios.post(`${ODOO_BASE_URL}/submit_approval`, {
        template_id: templateId
      });

      return response.data;
    } catch (error) {
      console.error('Error submitting for approval:', error);
      throw new Error('Failed to submit for approval');
    }
  }

  async approveTemplate(templateId, comments = '') {
    try {
      const response = await axios.post(`${ODOO_BASE_URL}/approve`, {
        template_id: templateId,
        comments: comments
      });

      return response.data;
    } catch (error) {
      console.error('Error approving template:', error);
      throw new Error('Failed to approve template');
    }
  }

  async rejectTemplate(templateId, reason) {
    try {
      const response = await axios.post(`${ODOO_BASE_URL}/reject`, {
        template_id: templateId,
        reason: reason
      });

      return response.data;
    } catch (error) {
      console.error('Error rejecting template:', error);
      throw new Error('Failed to reject template');
    }
  }

  // AI Integration
  async getAITemplateSuggestions(category, context = '') {
    try {
      const response = await axios.post(`${AI_ORCHESTRATOR_BASE_URL}/template-suggestions`, {
        category: category,
        context: context,
        frameworks: ['ISO-22301', 'NIST', 'COBIT']
      });

      return response.data.suggestions;
    } catch (error) {
      console.error('Error getting AI suggestions:', error);
      throw new Error('Failed to get AI template suggestions');
    }
  }

  async analyzeTemplateCompliance(templateId, framework = 'ISO-22301') {
    try {
      const response = await axios.post(`${AI_ORCHESTRATOR_BASE_URL}/compliance-check`, {
        template_id: templateId,
        framework: framework
      });

      return response.data;
    } catch (error) {
      console.error('Error analyzing compliance:', error);
      throw new Error('Failed to analyze template compliance');
    }
  }

  async enhanceTemplateWithAI(templateId, enhancement_type = 'content') {
    try {
      const response = await axios.post(`${AI_ORCHESTRATOR_BASE_URL}/enhance-template`, {
        template_id: templateId,
        enhancement_type: enhancement_type
      });

      return response.data;
    } catch (error) {
      console.error('Error enhancing template:', error);
      throw new Error('Failed to enhance template with AI');
    }
  }

  // Form Builder
  async getFormSchema(templateId) {
    try {
      const template = await this.getTemplateById(templateId);
      return JSON.parse(template.form_schema || '{}');
    } catch (error) {
      console.error('Error getting form schema:', error);
      throw new Error('Failed to get form schema');
    }
  }

  async updateFormSchema(templateId, schema) {
    try {
      return await this.updateTemplate(templateId, {
        form_schema: JSON.stringify(schema)
      });
    } catch (error) {
      console.error('Error updating form schema:', error);
      throw new Error('Failed to update form schema');
    }
  }

  // Permissions and Sharing
  async updatePermissions(templateId, permissions) {
    try {
      return await this.updateTemplate(templateId, {
        permissions: JSON.stringify(permissions)
      });
    } catch (error) {
      console.error('Error updating permissions:', error);
      throw new Error('Failed to update permissions');
    }
  }

  async shareTemplate(templateId, userIds, permission = 'read') {
    try {
      const response = await axios.post(`${ODOO_BASE_URL}/share`, {
        template_id: templateId,
        user_ids: userIds,
        permission: permission
      });

      return response.data;
    } catch (error) {
      console.error('Error sharing template:', error);
      throw new Error('Failed to share template');
    }
  }

  // File Management
  async uploadFile(file, templateId = null) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      if (templateId) {
        formData.append('template_id', templateId);
      }

      const response = await axios.post(`${DOC_PROCESSOR_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          this._notifyUploadProgress(percentCompleted);
        }
      });

      return response.data;
    } catch (error) {
      console.error('Error uploading file:', error);
      throw new Error('Failed to upload file');
    }
  }

  async downloadTemplate(templateId, format = 'docx') {
    try {
      const response = await axios.get(`${DOC_PROCESSOR_BASE_URL}/download/${templateId}`, {
        params: { format },
        responseType: 'blob'
      });

      return response.data;
    } catch (error) {
      console.error('Error downloading template:', error);
      throw new Error('Failed to download template');
    }
  }

  // Utility Methods
  _buildFilterDomain(filters) {
    const domain = [];

    if (filters.category) {
      domain.push(['category', '=', filters.category]);
    }

    if (filters.status) {
      domain.push(['status', '=', filters.status]);
    }

    if (filters.search) {
      domain.push('|', ['name', 'ilike', filters.search], ['description', 'ilike', filters.search]);
    }

    if (filters.tags && filters.tags.length > 0) {
      domain.push(['tags', 'in', filters.tags]);
    }

    return domain;
  }

  _formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  _notifyUploadProgress(percent) {
    // This can be connected to a global event bus for upload progress updates
    window.dispatchEvent(new CustomEvent('upload-progress', {
      detail: { percent }
    }));
  }

  // Categories and Metadata
  getCategories() {
    return this.categories;
  }

  getCategoryById(id) {
    return this.categories.find(cat => cat.id === id);
  }

  // Search and Filtering
  async searchTemplates(query, filters = {}) {
    return await this.getTemplates({
      ...filters,
      search: query
    });
  }

  async getRecentTemplates(limit = 10) {
    try {
      const response = await axios.post(ODOO_BASE_URL, {
        model: 'bcm_templates.record',
        method: 'search_read',
        args: [[]],
        kwargs: {
          fields: ['id', 'name', 'last_modified', 'category'],
          order: 'last_modified desc',
          limit: limit
        }
      });

      return response.data.result;
    } catch (error) {
      console.error('Error fetching recent templates:', error);
      throw new Error('Failed to fetch recent templates');
    }
  }

  async getPopularTemplates(limit = 10) {
    try {
      const response = await axios.post(ODOO_BASE_URL, {
        model: 'bcm_templates.record',
        method: 'search_read',
        args: [[]],
        kwargs: {
          fields: ['id', 'name', 'usage_count', 'category'],
          order: 'usage_count desc',
          limit: limit
        }
      });

      return response.data.result;
    } catch (error) {
      console.error('Error fetching popular templates:', error);
      throw new Error('Failed to fetch popular templates');
    }
  }
}

export default new BCMTemplatesService();