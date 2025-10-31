// MongoDB Client для BCM Platform
// Документы, логи, файлы и темплейты
// Интеграция с docker-compose.yml архитектурой

interface MongoDocument {
  _id?: string
  title: string
  content: string
  type: 'policy' | 'procedure' | 'template' | 'report' | 'incident_report'
  tenant_id: string
  category?: string
  tags?: string[]
  metadata?: Record<string, any>
  version: number
  status: 'draft' | 'review' | 'approved' | 'archived'
  created_by: string
  updated_by?: string
  created_at: Date
  updated_at: Date
  file_path?: string
  file_size?: number
  mime_type?: string
}

interface AuditLog {
  _id?: string
  user_id: string
  action: string
  resource: string
  resource_id?: string
  tenant_id: string
  details: Record<string, any>
  ip_address?: string
  user_agent?: string
  timestamp: Date
  severity: 'info' | 'warning' | 'error' | 'critical'
  module: string
}

interface DocumentTemplate {
  _id?: string
  name: string
  description: string
  type: 'policy' | 'procedure' | 'form' | 'checklist' | 'report'
  category: string
  content_template: string
  fields: {
    name: string
    type: 'text' | 'number' | 'date' | 'select' | 'textarea'
    required: boolean
    options?: string[]
    default_value?: any
  }[]
  tenant_id?: string  // null for global templates
  is_public: boolean
  created_by: string
  created_at: Date
  updated_at: Date
  usage_count: number
}

interface UploadedFile {
  _id?: string
  filename: string
  original_name: string
  path: string
  size: number
  mime_type: string
  tenant_id: string
  uploaded_by: string
  upload_date: Date
  description?: string
  category?: string
  tags?: string[]
  related_document?: string
  virus_scan_status?: 'pending' | 'clean' | 'infected'
  access_level: 'public' | 'internal' | 'confidential' | 'restricted'
}

export class MongoDBClient {
  private client: any = null
  private db: any = null
  private isConnected = false

  constructor() {
    this.initialize()
  }

  private async initialize() {
    if (typeof window !== 'undefined') {
      // MongoDB is server-side only
      console.warn('MongoDB client should only be used server-side')
      return
    }

    try {
      const mongoUrl = process.env.MONGODB_URL || process.env.NEXT_PUBLIC_MONGODB_URL
      const dbName = process.env.MONGODB_DATABASE || process.env.NEXT_PUBLIC_MONGODB_DATABASE || 'bcm_documents'

      if (!mongoUrl) {
        console.log('MongoDB URL not configured, using fallback storage')
        return
      }

      const { MongoClient } = await import('mongodb')
      this.client = new MongoClient(mongoUrl)

      await this.client.connect()
      this.db = this.client.db(dbName)
      this.isConnected = true

      // Create indexes for better performance
      await this.createIndexes()

      console.log('✅ MongoDB connected:', dbName)
    } catch (error) {
      console.error('MongoDB connection failed:', error)
      this.isConnected = false
    }
  }

  private async createIndexes() {
    if (!this.db) return

    try {
      // Documents collection indexes
      await this.db.collection('documents').createIndexes([
        { key: { tenant_id: 1, type: 1 } },
        { key: { tenant_id: 1, status: 1 } },
        { key: { tenant_id: 1, created_at: -1 } },
        { key: { title: 'text', content: 'text' } },
        { key: { tags: 1 } },
        { key: { 'metadata.department': 1 } }
      ])

      // Audit logs collection indexes
      await this.db.collection('audit_logs').createIndexes([
        { key: { tenant_id: 1, timestamp: -1 } },
        { key: { user_id: 1, timestamp: -1 } },
        { key: { action: 1, resource: 1 } },
        { key: { severity: 1, timestamp: -1 } },
        { key: { module: 1, timestamp: -1 } }
      ])

      // Files collection indexes
      await this.db.collection('uploaded_files').createIndexes([
        { key: { tenant_id: 1, upload_date: -1 } },
        { key: { uploaded_by: 1, upload_date: -1 } },
        { key: { mime_type: 1 } },
        { key: { access_level: 1 } }
      ])

      // Templates collection indexes
      await this.db.collection('document_templates').createIndexes([
        { key: { type: 1, category: 1 } },
        { key: { is_public: 1 } },
        { key: { tenant_id: 1 } },
        { key: { usage_count: -1 } }
      ])

      console.log('✅ MongoDB indexes created')
    } catch (error) {
      console.error('Failed to create MongoDB indexes:', error)
    }
  }

  // Document management
  async createDocument(document: Omit<MongoDocument, '_id' | 'created_at' | 'updated_at' | 'version'>): Promise<string | null> {
    if (!this.isConnected || !this.db) {
      console.warn('MongoDB not available, document not saved')
      return null
    }

    try {
      const docToInsert: MongoDocument = {
        ...document,
        version: 1,
        created_at: new Date(),
        updated_at: new Date()
      }

      const result = await this.db.collection('documents').insertOne(docToInsert)
      return result.insertedId.toString()
    } catch (error) {
      console.error('Failed to create document:', error)
      return null
    }
  }

  async getDocuments(tenantId: string, filters: {
    type?: string
    status?: string
    category?: string
    limit?: number
    skip?: number
  } = {}): Promise<MongoDocument[]> {
    if (!this.isConnected || !this.db) return []

    try {
      const query: any = { tenant_id: tenantId }

      if (filters.type) query.type = filters.type
      if (filters.status) query.status = filters.status
      if (filters.category) query.category = filters.category

      const cursor = this.db.collection('documents')
        .find(query)
        .sort({ updated_at: -1 })

      if (filters.skip) cursor.skip(filters.skip)
      if (filters.limit) cursor.limit(filters.limit)

      return await cursor.toArray()
    } catch (error) {
      console.error('Failed to get documents:', error)
      return []
    }
  }

  async updateDocument(documentId: string, updates: Partial<MongoDocument>): Promise<boolean> {
    if (!this.isConnected || !this.db) return false

    try {
      const { ObjectId } = await import('mongodb')

      const result = await this.db.collection('documents').updateOne(
        { _id: new ObjectId(documentId) },
        {
          $set: {
            ...updates,
            updated_at: new Date()
          },
          $inc: { version: 1 }
        }
      )

      return result.modifiedCount > 0
    } catch (error) {
      console.error('Failed to update document:', error)
      return false
    }
  }

  async searchDocuments(tenantId: string, searchTerm: string, limit: number = 20): Promise<MongoDocument[]> {
    if (!this.isConnected || !this.db) return []

    try {
      return await this.db.collection('documents')
        .find({
          tenant_id: tenantId,
          $text: { $search: searchTerm }
        })
        .limit(limit)
        .toArray()
    } catch (error) {
      console.error('Failed to search documents:', error)
      return []
    }
  }

  // Audit logging
  async logActivity(log: Omit<AuditLog, '_id' | 'timestamp'>): Promise<string | null> {
    if (!this.isConnected || !this.db) {
      console.warn('MongoDB not available, audit log not saved')
      return null
    }

    try {
      const logToInsert: AuditLog = {
        ...log,
        timestamp: new Date()
      }

      const result = await this.db.collection('audit_logs').insertOne(logToInsert)
      return result.insertedId.toString()
    } catch (error) {
      console.error('Failed to log activity:', error)
      return null
    }
  }

  async getAuditLogs(tenantId: string, filters: {
    user_id?: string
    action?: string
    resource?: string
    severity?: string
    start_date?: Date
    end_date?: Date
    limit?: number
    skip?: number
  } = {}): Promise<AuditLog[]> {
    if (!this.isConnected || !this.db) return []

    try {
      const query: any = { tenant_id: tenantId }

      if (filters.user_id) query.user_id = filters.user_id
      if (filters.action) query.action = filters.action
      if (filters.resource) query.resource = filters.resource
      if (filters.severity) query.severity = filters.severity

      if (filters.start_date || filters.end_date) {
        query.timestamp = {}
        if (filters.start_date) query.timestamp.$gte = filters.start_date
        if (filters.end_date) query.timestamp.$lte = filters.end_date
      }

      const cursor = this.db.collection('audit_logs')
        .find(query)
        .sort({ timestamp: -1 })

      if (filters.skip) cursor.skip(filters.skip)
      if (filters.limit) cursor.limit(filters.limit)

      return await cursor.toArray()
    } catch (error) {
      console.error('Failed to get audit logs:', error)
      return []
    }
  }

  // File management
  async saveFileMetadata(file: Omit<UploadedFile, '_id' | 'upload_date'>): Promise<string | null> {
    if (!this.isConnected || !this.db) return null

    try {
      const fileToInsert: UploadedFile = {
        ...file,
        upload_date: new Date()
      }

      const result = await this.db.collection('uploaded_files').insertOne(fileToInsert)
      return result.insertedId.toString()
    } catch (error) {
      console.error('Failed to save file metadata:', error)
      return null
    }
  }

  async getFiles(tenantId: string, filters: {
    uploaded_by?: string
    mime_type?: string
    category?: string
    access_level?: string
    limit?: number
    skip?: number
  } = {}): Promise<UploadedFile[]> {
    if (!this.isConnected || !this.db) return []

    try {
      const query: any = { tenant_id: tenantId }

      if (filters.uploaded_by) query.uploaded_by = filters.uploaded_by
      if (filters.mime_type) query.mime_type = filters.mime_type
      if (filters.category) query.category = filters.category
      if (filters.access_level) query.access_level = filters.access_level

      const cursor = this.db.collection('uploaded_files')
        .find(query)
        .sort({ upload_date: -1 })

      if (filters.skip) cursor.skip(filters.skip)
      if (filters.limit) cursor.limit(filters.limit)

      return await cursor.toArray()
    } catch (error) {
      console.error('Failed to get files:', error)
      return []
    }
  }

  // Template management
  async createTemplate(template: Omit<DocumentTemplate, '_id' | 'created_at' | 'updated_at' | 'usage_count'>): Promise<string | null> {
    if (!this.isConnected || !this.db) return null

    try {
      const templateToInsert: DocumentTemplate = {
        ...template,
        usage_count: 0,
        created_at: new Date(),
        updated_at: new Date()
      }

      const result = await this.db.collection('document_templates').insertOne(templateToInsert)
      return result.insertedId.toString()
    } catch (error) {
      console.error('Failed to create template:', error)
      return null
    }
  }

  async getTemplates(filters: {
    type?: string
    category?: string
    tenant_id?: string
    is_public?: boolean
    limit?: number
  } = {}): Promise<DocumentTemplate[]> {
    if (!this.isConnected || !this.db) return []

    try {
      const query: any = {}

      if (filters.type) query.type = filters.type
      if (filters.category) query.category = filters.category
      if (filters.is_public !== undefined) query.is_public = filters.is_public
      if (filters.tenant_id) {
        query.$or = [
          { tenant_id: filters.tenant_id },
          { is_public: true }
        ]
      }

      const cursor = this.db.collection('document_templates')
        .find(query)
        .sort({ usage_count: -1, created_at: -1 })

      if (filters.limit) cursor.limit(filters.limit)

      return await cursor.toArray()
    } catch (error) {
      console.error('Failed to get templates:', error)
      return []
    }
  }

  async incrementTemplateUsage(templateId: string): Promise<boolean> {
    if (!this.isConnected || !this.db) return false

    try {
      const { ObjectId } = await import('mongodb')

      const result = await this.db.collection('document_templates').updateOne(
        { _id: new ObjectId(templateId) },
        { $inc: { usage_count: 1 } }
      )

      return result.modifiedCount > 0
    } catch (error) {
      console.error('Failed to increment template usage:', error)
      return false
    }
  }

  // Health check
  async checkHealth(): Promise<{
    status: 'healthy' | 'degraded' | 'offline'
    response_time: number
    collections: {
      documents: number
      audit_logs: number
      uploaded_files: number
      document_templates: number
    }
  }> {
    const startTime = Date.now()

    if (!this.isConnected || !this.db) {
      return {
        status: 'offline',
        response_time: Date.now() - startTime,
        collections: {
          documents: 0,
          audit_logs: 0,
          uploaded_files: 0,
          document_templates: 0
        }
      }
    }

    try {
      // Test connection with admin ping
      await this.db.admin().ping()

      // Get collection counts
      const [documentsCount, logsCount, filesCount, templatesCount] = await Promise.all([
        this.db.collection('documents').countDocuments(),
        this.db.collection('audit_logs').countDocuments(),
        this.db.collection('uploaded_files').countDocuments(),
        this.db.collection('document_templates').countDocuments()
      ])

      return {
        status: 'healthy',
        response_time: Date.now() - startTime,
        collections: {
          documents: documentsCount,
          audit_logs: logsCount,
          uploaded_files: filesCount,
          document_templates: templatesCount
        }
      }
    } catch (error) {
      return {
        status: 'degraded',
        response_time: Date.now() - startTime,
        collections: {
          documents: 0,
          audit_logs: 0,
          uploaded_files: 0,
          document_templates: 0
        }
      }
    }
  }

  // Cleanup old logs (retention policy)
  async cleanupOldLogs(tenantId: string, retentionDays: number = 90): Promise<number> {
    if (!this.isConnected || !this.db) return 0

    try {
      const cutoffDate = new Date()
      cutoffDate.setDate(cutoffDate.getDate() - retentionDays)

      const result = await this.db.collection('audit_logs').deleteMany({
        tenant_id: tenantId,
        timestamp: { $lt: cutoffDate },
        severity: { $nin: ['error', 'critical'] } // Keep error logs longer
      })

      return result.deletedCount
    } catch (error) {
      console.error('Failed to cleanup old logs:', error)
      return 0
    }
  }

  // Get statistics
  async getStatistics(tenantId: string): Promise<{
    documents_by_type: Record<string, number>
    recent_activity: number
    file_storage_used: number
    top_users: { user_id: string; activity_count: number }[]
  }> {
    if (!this.isConnected || !this.db) {
      return {
        documents_by_type: {},
        recent_activity: 0,
        file_storage_used: 0,
        top_users: []
      }
    }

    try {
      const [docsByType, recentActivity, storageUsed, topUsers] = await Promise.all([
        // Documents by type
        this.db.collection('documents').aggregate([
          { $match: { tenant_id: tenantId } },
          { $group: { _id: '$type', count: { $sum: 1 } } }
        ]).toArray(),

        // Recent activity (last 24 hours)
        this.db.collection('audit_logs').countDocuments({
          tenant_id: tenantId,
          timestamp: { $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) }
        }),

        // File storage used
        this.db.collection('uploaded_files').aggregate([
          { $match: { tenant_id: tenantId } },
          { $group: { _id: null, total_size: { $sum: '$size' } } }
        ]).toArray(),

        // Top users by activity
        this.db.collection('audit_logs').aggregate([
          { $match: { tenant_id: tenantId } },
          { $group: { _id: '$user_id', activity_count: { $sum: 1 } } },
          { $sort: { activity_count: -1 } },
          { $limit: 10 }
        ]).toArray()
      ])

      return {
        documents_by_type: docsByType.reduce((acc, item) => {
          acc[item._id] = item.count
          return acc
        }, {}),
        recent_activity: recentActivity,
        file_storage_used: storageUsed[0]?.total_size || 0,
        top_users: topUsers.map(user => ({
          user_id: user._id,
          activity_count: user.activity_count
        }))
      }
    } catch (error) {
      console.error('Failed to get statistics:', error)
      return {
        documents_by_type: {},
        recent_activity: 0,
        file_storage_used: 0,
        top_users: []
      }
    }
  }

  // Close connection
  async close(): Promise<void> {
    if (this.client) {
      await this.client.close()
      this.isConnected = false
    }
  }
}

// Export singleton instance
export const mongoClient = new MongoDBClient()

// Export types
export type { MongoDocument, AuditLog, DocumentTemplate, UploadedFile }