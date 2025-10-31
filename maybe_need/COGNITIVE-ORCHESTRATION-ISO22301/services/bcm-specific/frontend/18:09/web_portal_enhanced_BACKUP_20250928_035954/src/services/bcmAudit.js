import { odooService } from './odoo'
import { assistantService } from './assistant'

class BCMAuditService {
  constructor() {
    this.model = 'bcm.audit'
  }

  // Audit Management
  async getAudits(filters = {}) {
    try {
      const domain = this.buildDomain(filters)
      return await odooService.searchRead(this.model, {
        domain,
        fields: [
          'id', 'name', 'audit_type', 'audit_scope', 'status', 'priority',
          'start_date', 'end_date', 'auditor_ids', 'auditee_ids',
          'audit_criteria', 'findings_count', 'nonconformities_count',
          'recommendations_count', 'completion_percentage', 'next_action',
          'create_date', 'write_date'
        ]
      })
    } catch (error) {
      console.error('Error fetching audits:', error)
      throw error
    }
  }

  async getAuditById(id) {
    try {
      const audit = await odooService.read(this.model, [id], {
        fields: [
          'id', 'name', 'audit_type', 'audit_scope', 'status', 'priority',
          'start_date', 'end_date', 'auditor_ids', 'auditee_ids',
          'audit_criteria', 'description', 'objectives', 'methodology',
          'findings_count', 'nonconformities_count', 'recommendations_count',
          'completion_percentage', 'next_action', 'documentation_ids',
          'checklist_ids', 'finding_ids', 'nonconformity_ids',
          'create_date', 'write_date'
        ]
      })
      return audit[0]
    } catch (error) {
      console.error('Error fetching audit:', error)
      throw error
    }
  }

  async createAudit(auditData) {
    try {
      const id = await odooService.create(this.model, auditData)

      // Get AI recommendations for audit planning
      const aiRecommendations = await assistantService.getAuditRecommendations({
        auditType: auditData.audit_type,
        scope: auditData.audit_scope,
        criteria: auditData.audit_criteria
      })

      if (aiRecommendations) {
        await odooService.write(this.model, [id], {
          ai_recommendations: aiRecommendations
        })
      }

      return id
    } catch (error) {
      console.error('Error creating audit:', error)
      throw error
    }
  }

  async updateAudit(id, auditData) {
    try {
      return await odooService.write(this.model, [id], auditData)
    } catch (error) {
      console.error('Error updating audit:', error)
      throw error
    }
  }

  async deleteAudit(id) {
    try {
      return await odooService.unlink(this.model, [id])
    } catch (error) {
      console.error('Error deleting audit:', error)
      throw error
    }
  }

  // Audit Findings Management
  async getAuditFindings(auditId) {
    try {
      return await odooService.searchRead('bcm.audit.finding', {
        domain: [['audit_id', '=', auditId]],
        fields: [
          'id', 'name', 'finding_type', 'severity', 'status',
          'description', 'evidence', 'root_cause', 'corrective_action',
          'responsible_id', 'due_date', 'actual_date',
          'create_date', 'write_date'
        ]
      })
    } catch (error) {
      console.error('Error fetching audit findings:', error)
      throw error
    }
  }

  async createFinding(findingData) {
    try {
      const id = await odooService.create('bcm.audit.finding', findingData)

      // Get AI analysis for root cause and recommendations
      const aiAnalysis = await assistantService.analyzeFinding({
        description: findingData.description,
        evidence: findingData.evidence,
        findingType: findingData.finding_type
      })

      if (aiAnalysis) {
        await odooService.write('bcm.audit.finding', [id], {
          ai_root_cause_analysis: aiAnalysis.rootCause,
          ai_recommendations: aiAnalysis.recommendations
        })
      }

      return id
    } catch (error) {
      console.error('Error creating finding:', error)
      throw error
    }
  }

  // Audit Checklist Management
  async getAuditChecklists(auditId) {
    try {
      return await odooService.searchRead('bcm.audit.checklist', {
        domain: [['audit_id', '=', auditId]],
        fields: [
          'id', 'name', 'requirement', 'evidence_required',
          'status', 'compliance_level', 'notes', 'responsible_id',
          'verification_date', 'create_date', 'write_date'
        ]
      })
    } catch (error) {
      console.error('Error fetching audit checklists:', error)
      throw error
    }
  }

  async updateChecklistItem(id, itemData) {
    try {
      return await odooService.write('bcm.audit.checklist', [id], itemData)
    } catch (error) {
      console.error('Error updating checklist item:', error)
      throw error
    }
  }

  // Audit Reports
  async generateAuditReport(auditId) {
    try {
      return await odooService.callMethod(this.model, 'generate_audit_report', [auditId])
    } catch (error) {
      console.error('Error generating audit report:', error)
      throw error
    }
  }

  async getAuditMetrics(filters = {}) {
    try {
      return await odooService.callMethod(this.model, 'get_audit_metrics', [filters])
    } catch (error) {
      console.error('Error fetching audit metrics:', error)
      throw error
    }
  }

  // Certificate Management
  async getCertificates() {
    try {
      return await odooService.searchRead('bcm.audit.certificate', {
        domain: [],
        fields: [
          'id', 'name', 'certificate_type', 'standard', 'status',
          'issue_date', 'expiry_date', 'certification_body',
          'scope', 'certificate_number', 'next_surveillance_date',
          'create_date', 'write_date'
        ]
      })
    } catch (error) {
      console.error('Error fetching certificates:', error)
      throw error
    }
  }

  async createCertificate(certificateData) {
    try {
      return await odooService.create('bcm.audit.certificate', certificateData)
    } catch (error) {
      console.error('Error creating certificate:', error)
      throw error
    }
  }

  // Utility Methods
  buildDomain(filters) {
    const domain = []

    if (filters.audit_type) {
      domain.push(['audit_type', '=', filters.audit_type])
    }
    if (filters.status) {
      domain.push(['status', 'in', Array.isArray(filters.status) ? filters.status : [filters.status]])
    }
    if (filters.priority) {
      domain.push(['priority', '=', filters.priority])
    }
    if (filters.auditor_id) {
      domain.push(['auditor_ids', 'in', [filters.auditor_id]])
    }
    if (filters.date_from) {
      domain.push(['start_date', '>=', filters.date_from])
    }
    if (filters.date_to) {
      domain.push(['end_date', '<=', filters.date_to])
    }
    if (filters.search) {
      domain.push(['name', 'ilike', filters.search])
    }

    return domain
  }

  // External Audit Integration
  async syncExternalAudits() {
    try {
      return await odooService.callMethod(this.model, 'sync_external_audits', [])
    } catch (error) {
      console.error('Error syncing external audits:', error)
      throw error
    }
  }

  async getAuditTemplates() {
    try {
      return await odooService.searchRead('bcm.audit.template', {
        domain: [],
        fields: ['id', 'name', 'audit_type', 'scope', 'criteria', 'checklist_template_ids']
      })
    } catch (error) {
      console.error('Error fetching audit templates:', error)
      throw error
    }
  }
}

export const bcmAuditService = new BCMAuditService()