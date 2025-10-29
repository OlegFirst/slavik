import axios from 'axios'

const API_BASE_URL = process.env.VUE_APP_ODOO_URL || 'http://localhost:8069'
const LMS_API_URL = process.env.VUE_APP_LMS_URL || 'http://localhost:8006'
const AI_ORCHESTRATOR_URL = process.env.VUE_APP_AI_ORCHESTRATOR_URL || 'http://localhost:8080'

class BCMTrainingService {
  constructor() {
    this.odooApi = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      }
    })

    this.lmsApi = axios.create({
      baseURL: LMS_API_URL,
      headers: {
        'Content-Type': 'application/json',
      }
    })

    this.aiApi = axios.create({
      baseURL: AI_ORCHESTRATOR_URL,
      headers: {
        'Content-Type': 'application/json',
      }
    })

    // Set up request interceptors for authentication
    this.setupInterceptors()
  }

  setupInterceptors() {
    const token = localStorage.getItem('access_token')

    if (token) {
      this.odooApi.defaults.headers.common['Authorization'] = `Bearer ${token}`
      this.lmsApi.defaults.headers.common['Authorization'] = `Bearer ${token}`
      this.aiApi.defaults.headers.common['Authorization'] = `Bearer ${token}`
    }
  }

  // Training Programs Management
  async getTrainingPrograms(filters = {}) {
    try {
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.training.program/search_read', {
        params: {
          model: 'bcm.training.program',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: [
              'name', 'description', 'category_id', 'duration', 'trainer_id',
              'start_date', 'end_date', 'max_participants', 'enrolled_count',
              'status', 'is_mandatory', 'competency_ids', 'certification_type',
              'prerequisites', 'learning_objectives', 'assessment_criteria'
            ],
            domain: this.buildDomain(filters),
            order: 'start_date desc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error fetching training programs:', error)
      throw new Error('Failed to fetch training programs')
    }
  }

  async createTrainingProgram(programData) {
    try {
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.training.program/create', {
        params: {
          model: 'bcm.training.program',
          method: 'create',
          args: [programData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error creating training program:', error)
      throw new Error('Failed to create training program')
    }
  }

  async updateTrainingProgram(id, programData) {
    try {
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.training.program/write', {
        params: {
          model: 'bcm.training.program',
          method: 'write',
          args: [[id], programData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error updating training program:', error)
      throw new Error('Failed to update training program')
    }
  }

  async deleteTrainingProgram(id) {
    try {
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.training.program/unlink', {
        params: {
          model: 'bcm.training.program',
          method: 'unlink',
          args: [[id]],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error deleting training program:', error)
      throw new Error('Failed to delete training program')
    }
  }

  // Competency and Skill Matrix Management
  async getCompetencies() {
    try {
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.competency/search_read', {
        params: {
          model: 'bcm.competency',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: ['name', 'description', 'category', 'level_ids', 'required_skills']
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error fetching competencies:', error)
      throw new Error('Failed to fetch competencies')
    }
  }

  async getSkillMatrix(employeeId = null) {
    try {
      const domain = employeeId ? [['employee_id', '=', employeeId]] : []
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.skill.matrix/search_read', {
        params: {
          model: 'bcm.skill.matrix',
          method: 'search_read',
          args: [domain],
          kwargs: {
            fields: [
              'employee_id', 'competency_id', 'current_level', 'target_level',
              'assessment_date', 'assessor_id', 'gap_analysis', 'development_plan'
            ]
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error fetching skill matrix:', error)
      throw new Error('Failed to fetch skill matrix')
    }
  }

  async updateSkillAssessment(matrixId, assessmentData) {
    try {
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.skill.matrix/write', {
        params: {
          model: 'bcm.skill.matrix',
          method: 'write',
          args: [[matrixId], assessmentData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error updating skill assessment:', error)
      throw new Error('Failed to update skill assessment')
    }
  }

  // Course Enrollment and Progress Tracking
  async enrollInCourse(programId, employeeId = null) {
    try {
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.training.enrollment/create', {
        params: {
          model: 'bcm.training.enrollment',
          method: 'create',
          args: [{
            program_id: programId,
            employee_id: employeeId,
            enrollment_date: new Date().toISOString().split('T')[0],
            status: 'enrolled'
          }],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error enrolling in course:', error)
      throw new Error('Failed to enroll in course')
    }
  }

  async getEnrollments(employeeId = null) {
    try {
      const domain = employeeId ? [['employee_id', '=', employeeId]] : []
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.training.enrollment/search_read', {
        params: {
          model: 'bcm.training.enrollment',
          method: 'search_read',
          args: [domain],
          kwargs: {
            fields: [
              'program_id', 'employee_id', 'enrollment_date', 'completion_date',
              'status', 'progress_percentage', 'assessment_score', 'feedback',
              'certificate_id', 'attendance_records'
            ]
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error fetching enrollments:', error)
      throw new Error('Failed to fetch enrollments')
    }
  }

  async updateProgress(enrollmentId, progressData) {
    try {
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.training.enrollment/write', {
        params: {
          model: 'bcm.training.enrollment',
          method: 'write',
          args: [[enrollmentId], progressData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error updating progress:', error)
      throw new Error('Failed to update progress')
    }
  }

  // Training Calendar and Scheduling
  async getTrainingCalendar(startDate, endDate) {
    try {
      const domain = [
        ['start_date', '>=', startDate],
        ['end_date', '<=', endDate]
      ]
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.training.schedule/search_read', {
        params: {
          model: 'bcm.training.schedule',
          method: 'search_read',
          args: [domain],
          kwargs: {
            fields: [
              'program_id', 'start_datetime', 'end_datetime', 'location',
              'trainer_id', 'max_participants', 'enrolled_count', 'status',
              'room_id', 'equipment_ids', 'notes'
            ]
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error fetching training calendar:', error)
      throw new Error('Failed to fetch training calendar')
    }
  }

  async scheduleTraining(scheduleData) {
    try {
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.training.schedule/create', {
        params: {
          model: 'bcm.training.schedule',
          method: 'create',
          args: [scheduleData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error scheduling training:', error)
      throw new Error('Failed to schedule training')
    }
  }

  // Certificate Management
  async getCertificates(employeeId = null) {
    try {
      const domain = employeeId ? [['employee_id', '=', employeeId]] : []
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.training.certificate/search_read', {
        params: {
          model: 'bcm.training.certificate',
          method: 'search_read',
          args: [domain],
          kwargs: {
            fields: [
              'employee_id', 'program_id', 'certificate_number', 'issue_date',
              'expiry_date', 'status', 'digital_signature', 'verification_url',
              'issuing_authority', 'certificate_type'
            ]
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error fetching certificates:', error)
      throw new Error('Failed to fetch certificates')
    }
  }

  async issueCertificate(certificateData) {
    try {
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.training.certificate/create', {
        params: {
          model: 'bcm.training.certificate',
          method: 'create',
          args: [certificateData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error issuing certificate:', error)
      throw new Error('Failed to issue certificate')
    }
  }

  // Compliance Tracking
  async getComplianceReport(employeeId = null) {
    try {
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.training.compliance/get_compliance_report', {
        params: {
          model: 'bcm.training.compliance',
          method: 'get_compliance_report',
          args: [employeeId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error fetching compliance report:', error)
      throw new Error('Failed to fetch compliance report')
    }
  }

  async getMandatoryTrainings(employeeId = null) {
    try {
      const domain = [['is_mandatory', '=', true]]
      if (employeeId) {
        domain.push(['target_employees', 'in', [employeeId]])
      }
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.training.program/search_read', {
        params: {
          model: 'bcm.training.program',
          method: 'search_read',
          args: [domain],
          kwargs: {
            fields: [
              'name', 'description', 'due_date', 'frequency', 'grace_period',
              'compliance_status', 'last_completion_date'
            ]
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error fetching mandatory trainings:', error)
      throw new Error('Failed to fetch mandatory trainings')
    }
  }

  // LMS Integration
  async getLMSCourses() {
    try {
      const response = await this.lmsApi.get('/api/courses')
      return response.data
    } catch (error) {
      console.error('Error fetching LMS courses:', error)
      throw new Error('Failed to fetch LMS courses')
    }
  }

  async syncWithLMS(enrollmentId) {
    try {
      const response = await this.lmsApi.post(`/api/sync/enrollment/${enrollmentId}`)
      return response.data
    } catch (error) {
      console.error('Error syncing with LMS:', error)
      throw new Error('Failed to sync with LMS')
    }
  }

  async getLMSProgress(courseId, userId) {
    try {
      const response = await this.lmsApi.get(`/api/progress/${courseId}/${userId}`)
      return response.data
    } catch (error) {
      console.error('Error fetching LMS progress:', error)
      throw new Error('Failed to fetch LMS progress')
    }
  }

  // Training Analytics
  async getTrainingAnalytics(filters = {}) {
    try {
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.training.analytics/get_analytics', {
        params: {
          model: 'bcm.training.analytics',
          method: 'get_analytics',
          args: [filters],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error fetching training analytics:', error)
      throw new Error('Failed to fetch training analytics')
    }
  }

  async getEffectivenessMetrics(programId) {
    try {
      const response = await this.odooApi.post('/web/dataset/call_kw/bcm.training.program/get_effectiveness_metrics', {
        params: {
          model: 'bcm.training.program',
          method: 'get_effectiveness_metrics',
          args: [programId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Error fetching effectiveness metrics:', error)
      throw new Error('Failed to fetch effectiveness metrics')
    }
  }

  // AI-Powered Learning Path Recommendations
  async getLearningPathRecommendations(employeeId, preferences = {}) {
    try {
      const response = await this.aiApi.post('/api/recommendations/learning-path', {
        employee_id: employeeId,
        preferences: preferences,
        context: 'bcm_training'
      })
      return response.data
    } catch (error) {
      console.error('Error fetching learning path recommendations:', error)
      throw new Error('Failed to fetch learning path recommendations')
    }
  }

  async getPersonalizedCourses(employeeId, skillGaps = []) {
    try {
      const response = await this.aiApi.post('/api/recommendations/courses', {
        employee_id: employeeId,
        skill_gaps: skillGaps,
        context: 'bcm_training'
      })
      return response.data
    } catch (error) {
      console.error('Error fetching personalized courses:', error)
      throw new Error('Failed to fetch personalized courses')
    }
  }

  async predictTrainingOutcome(enrollmentData) {
    try {
      const response = await this.aiApi.post('/api/predictions/training-outcome', {
        enrollment_data: enrollmentData
      })
      return response.data
    } catch (error) {
      console.error('Error predicting training outcome:', error)
      throw new Error('Failed to predict training outcome')
    }
  }

  // Utility Methods
  buildDomain(filters) {
    const domain = []

    if (filters.category) {
      domain.push(['category_id', '=', filters.category])
    }

    if (filters.status) {
      domain.push(['status', '=', filters.status])
    }

    if (filters.mandatory !== undefined) {
      domain.push(['is_mandatory', '=', filters.mandatory])
    }

    if (filters.startDate) {
      domain.push(['start_date', '>=', filters.startDate])
    }

    if (filters.endDate) {
      domain.push(['end_date', '<=', filters.endDate])
    }

    if (filters.search) {
      domain.push(['name', 'ilike', filters.search])
    }

    return domain
  }

  // Error handling helper
  handleApiError(error) {
    if (error.response) {
      const status = error.response.status
      const message = error.response.data?.message || error.message

      switch (status) {
        case 401:
          throw new Error('Authentication required. Please log in.')
        case 403:
          throw new Error('Access denied. Insufficient permissions.')
        case 404:
          throw new Error('Resource not found.')
        case 500:
          throw new Error('Server error. Please try again later.')
        default:
          throw new Error(message || 'An unexpected error occurred.')
      }
    } else if (error.request) {
      throw new Error('Network error. Please check your connection.')
    } else {
      throw new Error(error.message || 'An unexpected error occurred.')
    }
  }
}

export default new BCMTrainingService()