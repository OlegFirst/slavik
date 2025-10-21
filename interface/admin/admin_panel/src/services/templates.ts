// BCM Template Management Service Architecture
// Интеграция: Admin Panel ↔ Document Processor ↔ Odoo ↔ File System

import { API_ENDPOINTS } from './bcm';

export interface Template {
  id: string;
  name: string;
  category: 'policy' | 'procedure' | 'plan' | 'assessment' | 'report' | 'form';
  description: string;
  file_type: 'docx' | 'pdf' | 'xlsx' | 'html';
  file_url: string;
  version: string;
  status: 'draft' | 'active' | 'archived';
  created_by: string;
  created_date: string;
  last_modified: string;
  usage_count: number;
  tags: string[];
  odoo_id?: number;
}

export interface TemplateCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  template_count: number;
}

export const templateService = {

  // ======================================
  // LAYER 1: Admin Panel Template Management
  // ======================================

  // Get all templates for admin management
  async getAdminTemplates(): Promise<Template[]> {
    try {
      console.log(' Fetching templates for admin management...');

      // Get templates from multiple sources in parallel
      const [odooTemplates, processorTemplates, fileSystemTemplates] = await Promise.allSettled([
        this.getOdooTemplates(),
        this.getProcessorTemplates(),
        this.getFileSystemTemplates()
      ]);

      // Merge and deduplicate templates
      const allTemplates = [
        ...(odooTemplates.status === 'fulfilled' ? odooTemplates.value : []),
        ...(processorTemplates.status === 'fulfilled' ? processorTemplates.value : []),
        ...(fileSystemTemplates.status === 'fulfilled' ? fileSystemTemplates.value : [])
      ];

      return this.deduplicateTemplates(allTemplates);
    } catch (error) {
      console.error(' Failed to fetch admin templates:', error);
      return this.getFallbackTemplates();
    }
  },

  // Upload new template through admin panel
  async uploadTemplate(file: File, metadata: Partial<Template>): Promise<boolean> {
    try {
      console.log(' Uploading template through admin panel...');

      // Step 1: Process through Document Processor (8083)
      const processedTemplate = await this.processTemplateFile(file, metadata);
      if (!processedTemplate) return false;

      // Step 2: Save to Odoo bcm_document module
      const odooSaved = await this.saveToOdoo(processedTemplate);
      if (!odooSaved) return false;

      // Step 3: Store file in file system
      const fileStored = await this.storeTemplateFile(file, processedTemplate.id);

      return fileStored;
    } catch (error) {
      console.error(' Template upload failed:', error);
      return false;
    }
  },

  // ======================================
  // LAYER 2: Document Processor Integration
  // ======================================

  // Process template file through AI
  async processTemplateFile(file: File, metadata: Partial<Template>): Promise<Template | null> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('metadata', JSON.stringify(metadata));

      const response = await fetch(`${API_ENDPOINTS.DOCUMENT_PROCESSOR || 'http://localhost:8083'}/process-template`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        return result.template;
      }
      return null;
    } catch (error) {
      console.warn('Document processor unavailable, using fallback processing');
      return this.fallbackProcessTemplate(file, metadata);
    }
  },

  // Get processed templates from Document Processor
  async getProcessorTemplates(): Promise<Template[]> {
    try {
      const response = await fetch(`${API_ENDPOINTS.DOCUMENT_PROCESSOR || 'http://localhost:8083'}/templates`);
      if (response.ok) {
        const result = await response.json();
        return result.templates || [];
      }
      return [];
    } catch (error) {
      console.warn('Document Processor templates unavailable:', error);
      return [];
    }
  },

  // ======================================
  // LAYER 3: Odoo BCM Integration
  // ======================================

  // Get templates from Odoo bcm_document module
  async getOdooTemplates(): Promise<Template[]> {
    try {
      const response = await fetch(`${API_ENDPOINTS.ODOO_BCM}/web/dataset/call_kw/bcm.document.template/search_read`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          params: {
            domain: [['template_type', '=', 'bcm_template']],
            fields: [
              'name', 'description', 'category', 'file_type', 'file_url',
              'version', 'status', 'created_by', 'create_date', 'write_date',
              'usage_count', 'tags'
            ]
          }
        })
      });

      if (response.ok) {
        const result = await response.json();
        return (result.result || []).map(this.mapOdooToTemplate);
      }
      return [];
    } catch (error) {
      console.warn('Odoo templates unavailable:', error);
      return [];
    }
  },

  // Save template to Odoo
  async saveToOdoo(template: Template): Promise<boolean> {
    try {
      const response = await fetch(`${API_ENDPOINTS.ODOO_BCM}/web/dataset/call_kw/bcm.document.template/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          params: {
            vals: {
              name: template.name,
              description: template.description,
              category: template.category,
              file_type: template.file_type,
              file_url: template.file_url,
              version: template.version,
              status: template.status,
              tags: template.tags.join(',')
            }
          }
        })
      });

      return response.ok;
    } catch (error) {
      console.error('Failed to save template to Odoo:', error);
      return false;
    }
  },

  // ======================================
  // LAYER 4: File System Storage
  // ======================================

  // Get templates from file system
  async getFileSystemTemplates(): Promise<Template[]> {
    try {
      // This would typically be handled by a backend API
      const response = await fetch('/api/templates/filesystem');
      if (response.ok) {
        const result = await response.json();
        return result.templates || [];
      }
      return [];
    } catch (error) {
      console.warn('File system templates unavailable:', error);
      return [];
    }
  },

  // Store template file
  async storeTemplateFile(file: File, templateId: string): Promise<boolean> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('templateId', templateId);

      const response = await fetch('/api/templates/upload', {
        method: 'POST',
        body: formData
      });

      return response.ok;
    } catch (error) {
      console.error('Failed to store template file:', error);
      return false;
    }
  },

  // ======================================
  // LAYER 5: Template Categories & Metadata
  // ======================================

  // Get template categories
  async getTemplateCategories(): Promise<TemplateCategory[]> {
    return [
      {
        id: 'policy',
        name: 'BCM Policies',
        description: 'Business Continuity Management policies and governance documents',
        icon: 'Shield',
        template_count: 0
      },
      {
        id: 'procedure',
        name: 'Procedures',
        description: 'Step-by-step procedures for BCM processes',
        icon: 'FileText',
        template_count: 0
      },
      {
        id: 'plan',
        name: 'Continuity Plans',
        description: 'Business continuity and recovery plans',
        icon: 'Map',
        template_count: 0
      },
      {
        id: 'assessment',
        name: 'Assessment Forms',
        description: 'Risk assessments and BIA templates',
        icon: 'ClipboardCheck',
        template_count: 0
      },
      {
        id: 'report',
        name: 'Reports',
        description: 'Compliance reports and audit documentation',
        icon: 'BarChart3',
        template_count: 0
      },
      {
        id: 'form',
        name: 'Forms',
        description: 'Incident forms and data collection templates',
        icon: 'FileInput',
        template_count: 0
      }
    ];
  },

  // ======================================
  // UTILITY FUNCTIONS
  // ======================================

  // Map Odoo record to Template interface
  mapOdooToTemplate(odooRecord: any): Template {
    return {
      id: odooRecord.id.toString(),
      name: odooRecord.name,
      category: odooRecord.category || 'form',
      description: odooRecord.description || '',
      file_type: odooRecord.file_type || 'docx',
      file_url: odooRecord.file_url || '',
      version: odooRecord.version || '1.0',
      status: odooRecord.status || 'active',
      created_by: odooRecord.created_by || 'System',
      created_date: odooRecord.create_date,
      last_modified: odooRecord.write_date,
      usage_count: odooRecord.usage_count || 0,
      tags: odooRecord.tags ? odooRecord.tags.split(',') : [],
      odoo_id: odooRecord.id
    };
  },

  // Remove duplicate templates
  deduplicateTemplates(templates: Template[]): Template[] {
    const seen = new Set();
    return templates.filter(template => {
      const key = `${template.name}-${template.version}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  },

  // Fallback template processing
  fallbackProcessTemplate(file: File, metadata: Partial<Template>): Template {
    return {
      id: Date.now().toString(),
      name: metadata.name || file.name,
      category: metadata.category || 'form',
      description: metadata.description || 'Uploaded template',
      file_type: file.name.split('.').pop() as any || 'docx',
      file_url: '',
      version: metadata.version || '1.0',
      status: 'draft',
      created_by: 'Admin',
      created_date: new Date().toISOString(),
      last_modified: new Date().toISOString(),
      usage_count: 0,
      tags: metadata.tags || [],
    };
  },

  // Fallback templates when all sources fail
  getFallbackTemplates(): Template[] {
    return [
      {
        id: '1',
        name: 'BCM Policy Template',
        category: 'policy',
        description: 'Standard business continuity management policy template',
        file_type: 'docx',
        file_url: '/templates/bcm-policy-template.docx',
        version: '2.1',
        status: 'active',
        created_by: 'System',
        created_date: '2024-01-15T00:00:00Z',
        last_modified: '2024-09-01T00:00:00Z',
        usage_count: 45,
        tags: ['policy', 'iso22301', 'governance']
      },
      {
        id: '2',
        name: 'Incident Response Plan',
        category: 'plan',
        description: 'Template for incident response and crisis management plans',
        file_type: 'docx',
        file_url: '/templates/incident-response-plan.docx',
        version: '1.5',
        status: 'active',
        created_by: 'System',
        created_date: '2024-02-01T00:00:00Z',
        last_modified: '2024-08-15T00:00:00Z',
        usage_count: 32,
        tags: ['incident', 'response', 'crisis']
      }
    ];
  }
};

// Export for admin panel integration
export default templateService;