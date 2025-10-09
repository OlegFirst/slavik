export interface EmailMessage {
  id: string;
  from: string;
  fromName?: string;
  to: string[];
  cc?: string[];
  subject: string;
  body: string;
  bodyPlain?: string;
  date: Date;
  hasAttachments: boolean;
  attachments?: EmailAttachment[];
  labels?: string[];
  isRead: boolean;
  isImportant: boolean;
  threadId?: string;
}

export interface EmailAttachment {
  filename: string;
  mimeType: string;
  size: number;
  contentId?: string;
  data?: Buffer | string;
}

export type EmailCategory =
  | 'important'
  | 'newsletter'
  | 'advertisement'
  | 'spam'
  | 'meeting_summary'
  | 'notification'
  | 'personal'
  | 'automated'
  | 'unknown';

export type EmailPriority = 'urgent' | 'high' | 'medium' | 'low';

export interface ClassifiedEmail {
  email: EmailMessage;
  category: EmailCategory;
  priority: EmailPriority;
  confidence: number; // 0-1
  reasoning?: string;
  keywords?: string[];
  actionRequired?: boolean;
  suggestedAction?: string;
  isMeetingSummary?: boolean;
  meetingService?: string;
}

export interface MeetingSummary {
  service: string; // 'otter.ai', 'read.ai', etc.
  meetingTitle: string;
  meetingDate: Date;
  duration?: string;
  participants?: string[];
  summary: string;
  keyPoints?: string[];
  actionItems?: string[];
  decisions?: string[];
  transcriptUrl?: string;
  recordingUrl?: string;
  attachmentName?: string;
  sourceEmail: EmailMessage;
}

export interface EmailDigest {
  date: Date;
  period: {
    from: Date;
    to: Date;
  };
  statistics: {
    totalEmails: number;
    byCategory: Record<EmailCategory, number>;
    byPriority: Record<EmailPriority, number>;
    unreadCount: number;
    importantCount: number;
    meetingSummariesCount: number;
  };
  importantEmails: ClassifiedEmail[];
  meetingSummaries: MeetingSummary[];
  highlights: string[];
  actionItems: ActionItem[];
  attachmentPath?: string; // Path to combined meeting summaries MD file
}

export interface ActionItem {
  title: string;
  description: string;
  source: string; // Email subject or meeting title
  priority: EmailPriority;
  dueDate?: Date;
  assignee?: string;
  createdFrom: 'email' | 'meeting_summary';
  relatedEmailId?: string;
}

export interface DigestReport {
  html: string;
  markdown: string;
  plainText: string;
}

export interface EmailAnalysisResult {
  emails: ClassifiedEmail[];
  meetingSummaries: MeetingSummary[];
  statistics: EmailDigest['statistics'];
  highlights: string[];
}

export interface EmailDigestConfig {
  emailProvider: string;
  lookbackHours: number;
  classification: {
    enabled: boolean;
    categories: EmailCategory[];
  };
  taskCreation: {
    enabled: boolean;
    taskProvider: string;
    createTasksFor: EmailCategory[];
    priorityMapping: Record<EmailPriority, string>;
  };
  digest: {
    enabled: boolean;
    sendTo: string;
    includeAttachments: boolean;
    includeMeetingSummaries: boolean;
    format: 'html' | 'markdown' | 'plain';
  };
  meetingSummaryServices: string[];
  filters: {
    excludeSenders: string[];
    excludeDomains: string[];
    prioritySenders: string[];
    priorityDomains: string[];
  };
}

export interface EmailDigestAgentConfig {
  schedule: {
    type: string;
    cronExpression: string;
    timezone: string;
    enabled: boolean;
  };
  settings: EmailDigestConfig;
}

export interface EmailCredentials {
  provider: 'gmail' | 'outlook' | 'imap';
  email: string;
  // For Gmail
  clientId?: string;
  clientSecret?: string;
  refreshToken?: string;
  accessToken?: string;
  // For Outlook
  tenantId?: string;
  // For IMAP
  host?: string;
  port?: number;
  secure?: boolean;
  username?: string;
  password?: string;
}
