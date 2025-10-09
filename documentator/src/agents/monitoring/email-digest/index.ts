import { BaseAgent } from '../../../core/BaseAgent';
import { ScheduleConfig, ScheduleType, AgentConfig } from '../../../types/AgentInterface';
import { Tool } from '@modelcontextprotocol/sdk/types.js';
import * as fs from 'fs-extra';
import * as path from 'path';
import {
  EmailMessage,
  ClassifiedEmail,
  MeetingSummary,
  EmailDigest,
  EmailAnalysisResult,
  ActionItem,
  EmailDigestConfig,
  EmailDigestAgentConfig,
  EmailCredentials,
  DigestReport,
  EmailCategory,
  EmailPriority
} from './types';
import {
  buildEmailAnalysisPrompt,
  buildDigestPrompt,
  buildMeetingSummaryPrompt,
  buildActionItemsPrompt
} from './prompts/analysis';

export class EmailDigestAgent extends BaseAgent {
  private config: EmailDigestConfig;
  private scheduleConfig: ScheduleConfig;
  private credentials?: EmailCredentials;
  private dataPath: string;
  private meetingSummariesPath: string;

  // Required metadata property for BaseAgent
  public metadata = {
    name: 'Email Digest Agent',
    version: '1.0.0',
    description: 'Щоденний аналіз пошти з класифікацією листів та створенням завдань',
    author: 'Digital Office',
    tags: ['email', 'digest', 'monitoring', 'asana']
  };

  constructor() {
    // Create base agent config
    const baseConfig: AgentConfig = {
      enabled: true,
      name: 'email-digest',
      enableIntegrations: true,
      metadata: {
        name: 'Email Digest Agent',
        version: '1.0.0'
      }
    };

    super(baseConfig);

    // Load agent-specific configuration
    const agentJsonPath = path.join(__dirname, 'agent.json');
    const agentJson = fs.readJsonSync(agentJsonPath) as EmailDigestAgentConfig;

    this.config = agentJson.settings;
    this.scheduleConfig = {
      type: agentJson.schedule.type as ScheduleType,
      cronExpression: agentJson.schedule.cronExpression,
      enabled: agentJson.schedule.enabled,
      stopOnError: false
    };

    this.dataPath = path.join(process.cwd(), 'data', 'agents', 'email-digest');
    this.meetingSummariesPath = path.join(this.dataPath, 'meeting-summaries');
  }

  protected async onInitialize(): Promise<void> {
    // Don't call super.onInitialize() as it's abstract
    // Instead, do initialization work directly

    // Створюємо необхідні директорії
    await fs.ensureDir(this.dataPath);
    await fs.ensureDir(this.meetingSummariesPath);
    await fs.ensureDir(path.join(this.dataPath, 'digests'));
    await fs.ensureDir(path.join(this.dataPath, 'attachments'));

    // Завантажуємо credentials
    await this.loadCredentials();

    this.log('Email Digest Agent ініціалізовано');
  }

  protected async onShutdown(): Promise<void> {
    // Don't call super.onShutdown() as it's abstract
    this.log('Email Digest Agent зупинено');
  }

  public getScheduleConfig(): ScheduleConfig {
    return this.scheduleConfig;
  }

  protected async executeAutonomously(): Promise<void> {
    this.log('🚀 Початок щоденного аналізу пошти...');

    try {
      // 1. Отримуємо листи за останні N годин
      const emails = await this.fetchEmails();
      this.log(`📧 Отримано ${emails.length} листів`);

      if (emails.length === 0) {
        this.log('✅ Немає нових листів для аналізу');
        await this.sendEmptyDigest();
        return;
      }

      // 2. Класифікуємо листи
      const analysisResult = await this.analyzeEmails(emails);
      this.log(`📊 Класифіковано: ${analysisResult.emails.length} листів`);

      // 3. Створюємо завдання в Asana для важливих листів
      if (this.config.taskCreation.enabled) {
        await this.createTasksForImportantEmails(analysisResult.emails);
      }

      // 4. Збираємо підсумки зустрічей у MD файл
      let meetingSummariesAttachment: string | undefined;
      if (this.config.digest.includeMeetingSummaries && analysisResult.meetingSummaries.length > 0) {
        meetingSummariesAttachment = await this.compileMeetingSummaries(analysisResult.meetingSummaries);
        this.log(`📄 Створено файл з підсумками зустрічей: ${meetingSummariesAttachment}`);
      }

      // 5. Формуємо дайджест
      const digest = await this.createDigest(analysisResult, meetingSummariesAttachment);

      // 6. Зберігаємо дайджест
      await this.saveDigest(digest);

      // 7. Відправляємо дайджест на пошту
      if (this.config.digest.enabled) {
        await this.sendDigestEmail(digest);
        this.log('✅ Дайджест відправлено на пошту');
      }

      // 8. Публікуємо подію
      await this.emit('email.digest.completed', {
        totalEmails: digest.statistics.totalEmails,
        importantCount: digest.statistics.importantCount,
        meetingSummariesCount: digest.statistics.meetingSummariesCount,
        actionItemsCount: digest.actionItems.length
      });

      this.log('✨ Щоденний аналіз пошти завершено успішно!');

    } catch (error) {
      this.log(`❌ Помилка при аналізі пошти: ${error instanceof Error ? error.message : 'Невідома помилка'}`, 'error');
      throw error;
    }
  }

  // ============= ОСНОВНІ МЕТОДИ =============

  private async fetchEmails(): Promise<EmailMessage[]> {
    this.log('📬 Отримання листів з пошти...');

    // TODO: Інтеграція з реальним email провайдером (Gmail, Outlook, IMAP)
    // Тут буде логіка підключення через MCP email server або безпосередньо через API

    // Поки що заглушка для демонстрації
    const mockEmails: EmailMessage[] = await this.getMockEmails();

    // У реальності тут буде:
    // if (this.credentials?.provider === 'gmail') {
    //   return await this.fetchGmailEmails();
    // } else if (this.credentials?.provider === 'outlook') {
    //   return await this.fetchOutlookEmails();
    // } else {
    //   return await this.fetchImapEmails();
    // }

    return mockEmails;
  }

  private async analyzeEmails(emails: EmailMessage[]): Promise<EmailAnalysisResult> {
    this.log('🔍 Аналіз та класифікація листів...');

    const classifiedEmails: ClassifiedEmail[] = [];
    const meetingSummaries: MeetingSummary[] = [];

    for (const email of emails) {
      try {
        // Класифікуємо лист
        const classified = await this.classifyEmail(email);
        classifiedEmails.push(classified);

        // Якщо це підсумок зустрічі - витягуємо деталі
        if (classified.isMeetingSummary) {
          const summary = await this.extractMeetingSummary(email);
          if (summary) {
            meetingSummaries.push(summary);
          }
        }
      } catch (error) {
        this.log(`⚠️ Помилка класифікації листа "${email.subject}": ${error}`, 'warn');
      }
    }

    // Генеруємо статистику
    const statistics = this.calculateStatistics(classifiedEmails);

    // Генеруємо highlights через AI
    const highlights = await this.generateHighlights(classifiedEmails, statistics);

    return {
      emails: classifiedEmails,
      meetingSummaries,
      statistics,
      highlights
    };
  }

  private async classifyEmail(email: EmailMessage): Promise<ClassifiedEmail> {
    // Спочатку перевіряємо чи це підсумок зустрічі
    const isMeetingSummary = this.isMeetingSummaryEmail(email);
    let meetingService: string | undefined;

    if (isMeetingSummary) {
      meetingService = this.detectMeetingService(email);
    }

    // Використовуємо AI для класифікації (можна інтегрувати Claude API)
    // Поки що використовуємо rule-based підхід
    const classification = await this.classifyEmailWithRules(email);

    return {
      email,
      category: classification.category,
      priority: classification.priority,
      confidence: classification.confidence,
      reasoning: classification.reasoning,
      keywords: classification.keywords,
      actionRequired: classification.actionRequired,
      suggestedAction: classification.suggestedAction,
      isMeetingSummary,
      meetingService
    };
  }

  private async classifyEmailWithRules(email: EmailMessage): Promise<Omit<ClassifiedEmail, 'email'>> {
    const subject = email.subject.toLowerCase();
    const body = email.bodyPlain || email.body;
    const bodyLower = body.toLowerCase();
    const from = email.from.toLowerCase();

    // Перевірка на спам
    if (this.isSpam(email)) {
      return {
        category: 'spam',
        priority: 'low',
        confidence: 0.9,
        reasoning: 'Підозріла розсилка або спам',
        actionRequired: false
      };
    }

    // Перевірка на підсумки зустрічей
    if (this.isMeetingSummaryEmail(email)) {
      return {
        category: 'meeting_summary',
        priority: 'medium',
        confidence: 0.95,
        reasoning: 'Підсумок зустрічі від AI сервісу',
        actionRequired: false
      };
    }

    // Перевірка на розсилку
    if (bodyLower.includes('unsubscribe') || bodyLower.includes('відписатися')) {
      return {
        category: 'newsletter',
        priority: 'low',
        confidence: 0.85,
        reasoning: 'Містить посилання для відписки - розсилка',
        actionRequired: false
      };
    }

    // Перевірка на рекламу
    const adKeywords = ['sale', 'discount', 'offer', 'buy now', 'знижка', 'акція', 'купити'];
    if (adKeywords.some(kw => bodyLower.includes(kw) || subject.includes(kw))) {
      return {
        category: 'advertisement',
        priority: 'low',
        confidence: 0.8,
        reasoning: 'Рекламний контент',
        actionRequired: false
      };
    }

    // Перевірка на сповіщення від систем
    const notificationSources = ['github', 'jira', 'slack', 'asana', 'trello', 'notifications@', 'noreply@'];
    if (notificationSources.some(src => from.includes(src))) {
      return {
        category: 'notification',
        priority: 'low',
        confidence: 0.9,
        reasoning: 'Автоматичне сповіщення від системи',
        actionRequired: false
      };
    }

    // Перевірка на терміновість
    const urgentKeywords = ['urgent', 'asap', 'deadline', 'терміново', 'важливо', 'action required'];
    const isUrgent = urgentKeywords.some(kw => subject.includes(kw) || bodyLower.includes(kw));

    // Перевірка на запитання
    const hasQuestion = body.includes('?') && (bodyLower.includes('чи можете') || bodyLower.includes('будь ласка') || bodyLower.includes('could you') || bodyLower.includes('please'));

    // Важливі відправники
    const isPrioritySender = this.config.filters.prioritySenders.some(sender => from.includes(sender.toLowerCase()));

    if (isUrgent || isPrioritySender) {
      return {
        category: 'important',
        priority: isUrgent ? 'urgent' : 'high',
        confidence: 0.85,
        reasoning: isUrgent ? 'Містить термінові ключові слова' : 'Від пріоритетного відправника',
        keywords: urgentKeywords.filter(kw => subject.includes(kw) || bodyLower.includes(kw)),
        actionRequired: true,
        suggestedAction: hasQuestion ? 'Відповісти на запитання' : 'Переглянути та прийняти рішення'
      };
    }

    if (hasQuestion) {
      return {
        category: 'important',
        priority: 'medium',
        confidence: 0.75,
        reasoning: 'Містить запитання, яке потребує відповіді',
        actionRequired: true,
        suggestedAction: 'Відповісти на запитання'
      };
    }

    // За замовчуванням - особистий лист середнього пріоритету
    return {
      category: 'personal',
      priority: 'medium',
      confidence: 0.6,
      reasoning: 'Звичайний особистий лист',
      actionRequired: false
    };
  }

  private isMeetingSummaryEmail(email: EmailMessage): boolean {
    const subject = email.subject.toLowerCase();
    const from = email.from.toLowerCase();

    const meetingKeywords = [
      'meeting summary', 'meeting notes', 'meeting recording',
      'recap', 'підсумок зустрічі', 'transcript', 'meeting highlights'
    ];

    return this.config.meetingSummaryServices.some(service =>
      from.includes(service.toLowerCase())
    ) || meetingKeywords.some(kw => subject.includes(kw));
  }

  private detectMeetingService(email: EmailMessage): string | undefined {
    const from = email.from.toLowerCase();
    return this.config.meetingSummaryServices.find(service =>
      from.includes(service.toLowerCase())
    );
  }

  private isSpam(email: EmailMessage): boolean {
    const subject = email.subject.toLowerCase();
    const from = email.from.toLowerCase();

    const spamKeywords = ['viagra', 'casino', 'lottery', 'winner', 'claim now', 'free money'];
    return spamKeywords.some(kw => subject.includes(kw) || from.includes(kw));
  }

  private async extractMeetingSummary(email: EmailMessage): Promise<MeetingSummary | null> {
    try {
      // Тут можна використати Claude API для витягування структурованої інформації
      // Поки що використовуємо базовий парсинг

      const service = this.detectMeetingService(email) || 'unknown';

      return {
        service,
        meetingTitle: email.subject.replace(/meeting summary|recap|notes/gi, '').trim(),
        meetingDate: email.date,
        summary: this.extractSummaryFromBody(email.body),
        keyPoints: this.extractKeyPoints(email.body),
        actionItems: this.extractActionItemsFromBody(email.body),
        sourceEmail: email
      };
    } catch (error) {
      this.log(`⚠️ Помилка витягування підсумку зустрічі: ${error}`, 'warn');
      return null;
    }
  }

  private extractSummaryFromBody(body: string): string {
    // Базовий метод витягування підсумку
    const lines = body.split('\n').filter(l => l.trim().length > 0);
    return lines.slice(0, 5).join(' ').substring(0, 500);
  }

  private extractKeyPoints(body: string): string[] {
    // Шукаємо bullet points або нумеровані списки
    const matches = body.match(/[-•*]\s*(.+)/g) || [];
    return matches.slice(0, 10).map(m => m.replace(/[-•*]\s*/, '').trim());
  }

  private extractActionItemsFromBody(body: string): string[] {
    // Шукаємо секцію action items
    const actionSection = body.match(/action items?:?([\s\S]*?)(?:\n\n|$)/i);
    if (actionSection) {
      const matches = actionSection[1].match(/[-•*]\s*(.+)/g) || [];
      return matches.map(m => m.replace(/[-•*]\s*/, '').trim());
    }
    return [];
  }

  private calculateStatistics(emails: ClassifiedEmail[]): EmailDigest['statistics'] {
    const byCategory: Record<EmailCategory, number> = {
      important: 0,
      newsletter: 0,
      advertisement: 0,
      spam: 0,
      meeting_summary: 0,
      notification: 0,
      personal: 0,
      automated: 0,
      unknown: 0
    };

    const byPriority: Record<EmailPriority, number> = {
      urgent: 0,
      high: 0,
      medium: 0,
      low: 0
    };

    let unreadCount = 0;
    let importantCount = 0;
    let meetingSummariesCount = 0;

    for (const email of emails) {
      byCategory[email.category]++;
      byPriority[email.priority]++;

      if (!email.email.isRead) unreadCount++;
      if (email.category === 'important') importantCount++;
      if (email.isMeetingSummary) meetingSummariesCount++;
    }

    return {
      totalEmails: emails.length,
      byCategory,
      byPriority,
      unreadCount,
      importantCount,
      meetingSummariesCount
    };
  }

  private async generateHighlights(emails: ClassifiedEmail[], statistics: any): Promise<string[]> {
    // Генеруємо короткі highlights
    const highlights: string[] = [];

    // Загальна статистика
    highlights.push(
      `Отримано ${statistics.totalEmails} листів: ` +
      `${statistics.importantCount} важливих, ` +
      `${statistics.byCategory.newsletter} розсилок, ` +
      `${statistics.byCategory.notification} сповіщень, ` +
      `${statistics.byCategory.personal} особистих`
    );

    // Термінові листи
    const urgentEmails = emails.filter(e => e.priority === 'urgent');
    if (urgentEmails.length > 0) {
      highlights.push(
        `⚠️ ${urgentEmails.length} терміновий${urgentEmails.length === 1 ? '' : 'і'} лист${urgentEmails.length === 1 ? '' : 'и'}: ` +
        urgentEmails.map(e => `"${e.email.subject}"`).slice(0, 2).join(', ')
      );
    }

    // Підсумки зустрічей
    if (statistics.meetingSummariesCount > 0) {
      highlights.push(
        `📹 ${statistics.meetingSummariesCount} підсум${statistics.meetingSummariesCount === 1 ? 'ок' : 'ки'} зустрічей - ` +
        `зібрано в окремому MD файлі`
      );
    }

    // Листи що потребують дій
    const actionRequiredEmails = emails.filter(e => e.actionRequired);
    if (actionRequiredEmails.length > 0) {
      highlights.push(
        `✅ ${actionRequiredEmails.length} лист${actionRequiredEmails.length === 1 ? '' : 'ів'} потребує${actionRequiredEmails.length === 1 ? '' : 'ють'} дії`
      );
    }

    return highlights;
  }

  private async createTasksForImportantEmails(emails: ClassifiedEmail[]): Promise<void> {
    const importantEmails = emails.filter(e =>
      this.config.taskCreation.createTasksFor.includes(e.category) &&
      e.actionRequired
    );

    this.log(`📋 Створення ${importantEmails.length} завдань в Asana...`);

    for (const email of importantEmails) {
      try {
        const taskTitle = `📧 ${email.email.subject}`;
        const taskDescription =
          `**Від:** ${email.email.from}\n` +
          `**Дата:** ${email.email.date.toLocaleDateString('uk-UA')}\n` +
          `**Пріоритет:** ${email.priority}\n\n` +
          `**Запропонована дія:** ${email.suggestedAction || 'Переглянути та відповісти'}\n\n` +
          `**Превью:**\n${email.email.bodyPlain?.substring(0, 500) || email.email.body.substring(0, 500)}...`;

        await this.createTask(
          taskTitle,
          taskDescription,
          email.priority,
          this.calculateDueDate(email.priority)
        );

        this.log(`✅ Створено завдання: "${taskTitle}"`);
      } catch (error) {
        this.log(`⚠️ Помилка створення завдання для листа "${email.email.subject}": ${error}`, 'warn');
      }
    }
  }

  private calculateDueDate(priority: EmailPriority): Date {
    const now = new Date();
    switch (priority) {
      case 'urgent':
        // Сьогодні до кінця дня
        now.setHours(23, 59, 59);
        return now;
      case 'high':
        // Завтра
        now.setDate(now.getDate() + 1);
        return now;
      case 'medium':
        // Через 3 дні
        now.setDate(now.getDate() + 3);
        return now;
      case 'low':
        // Через тиждень
        now.setDate(now.getDate() + 7);
        return now;
    }
  }

  private async compileMeetingSummaries(summaries: MeetingSummary[]): Promise<string> {
    const date = new Date();
    const dateStr = date.toISOString().split('T')[0];
    const filename = `meeting-summaries-${dateStr}.md`;
    const filepath = path.join(this.meetingSummariesPath, filename);

    let mdContent = `# Підсумки зустрічей - ${date.toLocaleDateString('uk-UA', { day: 'numeric', month: 'long', year: 'numeric' })}\n\n`;
    mdContent += `Зібрано ${summaries.length} підсум${summaries.length === 1 ? 'ок' : 'ків'} зустрічей.\n\n`;
    mdContent += `---\n\n`;

    for (let i = 0; i < summaries.length; i++) {
      const summary = summaries[i];
      mdContent += `## ${i + 1}. ${summary.meetingTitle}\n\n`;
      mdContent += `**Сервіс:** ${summary.service}\n`;
      mdContent += `**Дата:** ${summary.meetingDate.toLocaleDateString('uk-UA', { day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' })}\n`;
      if (summary.duration) mdContent += `**Тривалість:** ${summary.duration}\n`;
      if (summary.participants && summary.participants.length > 0) {
        mdContent += `**Учасники:** ${summary.participants.join(', ')}\n`;
      }
      mdContent += `\n### Підсумок\n\n${summary.summary}\n\n`;

      if (summary.keyPoints && summary.keyPoints.length > 0) {
        mdContent += `### Ключові моменти\n\n`;
        summary.keyPoints.forEach(point => {
          mdContent += `- ${point}\n`;
        });
        mdContent += `\n`;
      }

      if (summary.actionItems && summary.actionItems.length > 0) {
        mdContent += `### Завдання (Action Items)\n\n`;
        summary.actionItems.forEach(item => {
          mdContent += `- [ ] ${item}\n`;
        });
        mdContent += `\n`;
      }

      if (summary.decisions && summary.decisions.length > 0) {
        mdContent += `### Прийняті рішення\n\n`;
        summary.decisions.forEach(decision => {
          mdContent += `- ${decision}\n`;
        });
        mdContent += `\n`;
      }

      if (summary.transcriptUrl || summary.recordingUrl) {
        mdContent += `### Посилання\n\n`;
        if (summary.transcriptUrl) mdContent += `- [Транскрипт](${summary.transcriptUrl})\n`;
        if (summary.recordingUrl) mdContent += `- [Запис зустрічі](${summary.recordingUrl})\n`;
        mdContent += `\n`;
      }

      mdContent += `---\n\n`;
    }

    await fs.writeFile(filepath, mdContent, 'utf-8');
    return filepath;
  }

  private async createDigest(analysis: EmailAnalysisResult, meetingSummariesPath?: string): Promise<EmailDigest> {
    const now = new Date();
    const period = {
      from: new Date(now.getTime() - this.config.lookbackHours * 60 * 60 * 1000),
      to: now
    };

    // Витягуємо action items
    const actionItems: ActionItem[] = [];

    for (const email of analysis.emails.filter(e => e.actionRequired)) {
      actionItems.push({
        title: email.suggestedAction || `Переглянути: ${email.email.subject}`,
        description: email.email.bodyPlain?.substring(0, 200) || email.email.body.substring(0, 200),
        source: email.email.subject,
        priority: email.priority,
        createdFrom: 'email',
        relatedEmailId: email.email.id
      });
    }

    return {
      date: now,
      period,
      statistics: analysis.statistics,
      importantEmails: analysis.emails.filter(e => e.category === 'important' || e.priority === 'urgent' || e.priority === 'high'),
      meetingSummaries: analysis.meetingSummaries,
      highlights: analysis.highlights,
      actionItems,
      attachmentPath: meetingSummariesPath
    };
  }

  private async saveDigest(digest: EmailDigest): Promise<void> {
    const dateStr = digest.date.toISOString().split('T')[0];
    const filepath = path.join(this.dataPath, 'digests', `digest-${dateStr}.json`);
    await fs.writeJson(filepath, digest, { spaces: 2 });
    this.log(`💾 Дайджест збережено: ${filepath}`);
  }

  private async sendDigestEmail(digest: EmailDigest): Promise<void> {
    // TODO: Інтеграція з email сервісом для відправки
    // Поки що зберігаємо HTML версію локально

    const report = this.generateDigestReport(digest);
    const dateStr = digest.date.toISOString().split('T')[0];
    const htmlPath = path.join(this.dataPath, 'digests', `digest-${dateStr}.html`);
    await fs.writeFile(htmlPath, report.html, 'utf-8');

    this.log(`📧 HTML дайджест створено: ${htmlPath}`);
    this.log(`📬 Відправка на ${this.config.digest.sendTo}...`);

    // У реальності тут буде відправка через email API або MCP email server
    // await this.sendEmail({
    //   to: this.config.digest.sendTo,
    //   subject: `📊 Щоденний дайджест пошти - ${digest.date.toLocaleDateString('uk-UA')}`,
    //   html: report.html,
    //   attachments: digest.attachmentPath ? [{ path: digest.attachmentPath }] : []
    // });
  }

  private generateDigestReport(digest: EmailDigest): DigestReport {
    const html = this.generateHtmlDigest(digest);
    const markdown = this.generateMarkdownDigest(digest);
    const plainText = this.generatePlainTextDigest(digest);

    return { html, markdown, plainText };
  }

  private generateHtmlDigest(digest: EmailDigest): string {
    return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Щоденний дайджест пошти</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
    h1 { color: #2c3e50; }
    .stats { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; }
    .highlight { background: #e3f2fd; padding: 10px; border-left: 4px solid #2196f3; margin: 10px 0; }
    .email-item { border-bottom: 1px solid #eee; padding: 15px 0; }
    .priority-urgent { color: #d32f2f; font-weight: bold; }
    .priority-high { color: #f57c00; }
    .priority-medium { color: #1976d2; }
    .priority-low { color: #616161; }
  </style>
</head>
<body>
  <h1>📊 Щоденний дайджест пошти</h1>
  <p>${digest.date.toLocaleDateString('uk-UA', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>

  <div class="stats">
    <h2>Статистика</h2>
    <ul>
      <li><strong>Всього листів:</strong> ${digest.statistics.totalEmails}</li>
      <li><strong>Важливих:</strong> ${digest.statistics.importantCount}</li>
      <li><strong>Розсилок:</strong> ${digest.statistics.byCategory.newsletter}</li>
      <li><strong>Сповіщень:</strong> ${digest.statistics.byCategory.notification}</li>
      <li><strong>Підсумків зустрічей:</strong> ${digest.statistics.meetingSummariesCount}</li>
    </ul>
  </div>

  <h2>Основні моменти</h2>
  ${digest.highlights.map(h => `<div class="highlight">${h}</div>`).join('')}

  ${digest.importantEmails.length > 0 ? `
    <h2>Важливі листи</h2>
    ${digest.importantEmails.map(e => `
      <div class="email-item">
        <div class="priority-${e.priority}">[${e.priority.toUpperCase()}]</div>
        <strong>${e.email.subject}</strong><br>
        <small>Від: ${e.email.from} | ${e.email.date.toLocaleString('uk-UA')}</small>
        ${e.suggestedAction ? `<p>💡 Запропонована дія: ${e.suggestedAction}</p>` : ''}
      </div>
    `).join('')}
  ` : ''}

  ${digest.actionItems.length > 0 ? `
    <h2>Завдання</h2>
    <ul>
      ${digest.actionItems.map(item => `<li><strong>${item.title}</strong> - ${item.source}</li>`).join('')}
    </ul>
  ` : ''}

  ${digest.attachmentPath ? `
    <p>📎 <strong>Додаток:</strong> Підсумки зустрічей зібрано в окремому файлі</p>
  ` : ''}

  <hr>
  <p><small>Згенеровано Digital Office Email Digest Agent</small></p>
</body>
</html>`;
  }

  private generateMarkdownDigest(digest: EmailDigest): string {
    let md = `# 📊 Щоденний дайджест пошти\n\n`;
    md += `${digest.date.toLocaleDateString('uk-UA', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}\n\n`;
    md += `## Статистика\n\n`;
    md += `- **Всього листів:** ${digest.statistics.totalEmails}\n`;
    md += `- **Важливих:** ${digest.statistics.importantCount}\n`;
    md += `- **Розсилок:** ${digest.statistics.byCategory.newsletter}\n`;
    md += `- **Сповіщень:** ${digest.statistics.byCategory.notification}\n`;
    md += `- **Підсумків зустрічей:** ${digest.statistics.meetingSummariesCount}\n\n`;

    md += `## Основні моменти\n\n`;
    digest.highlights.forEach(h => {
      md += `> ${h}\n\n`;
    });

    if (digest.importantEmails.length > 0) {
      md += `## Важливі листи\n\n`;
      digest.importantEmails.forEach(e => {
        md += `### [${e.priority.toUpperCase()}] ${e.email.subject}\n\n`;
        md += `**Від:** ${e.email.from}  \n`;
        md += `**Дата:** ${e.email.date.toLocaleString('uk-UA')}\n\n`;
        if (e.suggestedAction) md += `💡 **Запропонована дія:** ${e.suggestedAction}\n\n`;
      });
    }

    return md;
  }

  private generatePlainTextDigest(digest: EmailDigest): string {
    let text = `ЩОДЕННИЙ ДАЙДЖЕСТ ПОШТИ\n`;
    text += `${digest.date.toLocaleDateString('uk-UA')}\n\n`;
    text += `СТАТИСТИКА:\n`;
    text += `Всього листів: ${digest.statistics.totalEmails}\n`;
    text += `Важливих: ${digest.statistics.importantCount}\n\n`;
    text += `ОСНОВНІ МОМЕНТИ:\n`;
    digest.highlights.forEach(h => {
      text += `- ${h}\n`;
    });
    return text;
  }

  private async sendEmptyDigest(): Promise<void> {
    this.log('📭 Відправка порожнього дайджесту...');
    // Відправляємо коротке повідомлення що немає нових листів
  }

  private async loadCredentials(): Promise<void> {
    const credPath = path.join(process.cwd(), 'data', 'config', 'email-credentials.json');
    if (await fs.pathExists(credPath)) {
      this.credentials = await fs.readJson(credPath);
      this.log('✅ Email credentials завантажено');
    } else {
      this.log('⚠️ Email credentials не знайдено. Створіть файл: ' + credPath, 'warn');
    }
  }

  // Метод для тестування (mock дані)
  private async getMockEmails(): Promise<EmailMessage[]> {
    return [
      {
        id: '1',
        from: 'boss@company.com',
        fromName: 'Керівник проекту',
        to: ['me@company.com'],
        subject: 'URGENT: Потрібен звіт до кінця дня',
        body: 'Доброго дня! Терміново потрібен звіт про прогрес проекту. Дедлайн - сьогодні 18:00.',
        bodyPlain: 'Доброго дня! Терміново потрібен звіт про прогрес проекту. Дедлайн - сьогодні 18:00.',
        date: new Date(),
        hasAttachments: false,
        isRead: false,
        isImportant: true
      },
      {
        id: '2',
        from: 'noreply@read.ai',
        to: ['me@company.com'],
        subject: 'Meeting Recap: Sprint Planning Q4',
        body: 'Meeting Summary...\n\nKey Points:\n- Feature X priority\n- Launch date set\n\nAction Items:\n- Complete API docs\n- User testing',
        date: new Date(),
        hasAttachments: true,
        isRead: false,
        isImportant: false
      }
    ];
  }

  public getTools(): Tool[] {
    return [
      {
        name: 'trigger_digest',
        description: 'Вручну запустити створення email дайджесту',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      }
    ];
  }

  public async handleToolCall(toolName: string, args: any): Promise<any> {
    if (toolName === 'trigger_digest') {
      await this.executeOnce();
      return {
        content: [{
          type: 'text',
          text: '✅ Email дайджест створено вручну'
        }]
      };
    }

    return super.handleToolCall(toolName, args);
  }
}
