// Шаблоны документации для соответствия ISO 22301

export interface DocumentTemplate {
  id: string
  name: string
  description: string
  type: 'policy' | 'procedure' | 'plan' | 'record'
  requiredSections: Section[]
  optionalSections: Section[]
  relatedRequirements: string[]
  templateContent: string
}

export interface Section {
  id: string
  title: string
  description: string
  required: boolean
  content?: string
  guidance?: string[]
}

// Шаблон политики непрерывности бизнеса
export const BC_POLICY_TEMPLATE: DocumentTemplate = {
  id: 'BC-POL-001',
  name: 'Business Continuity Policy',
  description: 'Comprehensive business continuity policy template',
  type: 'policy',
  requiredSections: [
    {
      id: 'purpose',
      title: 'Purpose and Scope',
      description: 'Define the purpose and scope of the BC policy',
      required: true,
      guidance: [
        'State the purpose of business continuity management',
        'Define organizational scope and boundaries',
        'Reference relevant standards and regulations'
      ]
    },
    {
      id: 'policy_statement',
      title: 'Policy Statement',
      description: 'High-level commitment to business continuity',
      required: true,
      guidance: [
        'Management commitment to BC',
        'Protection of stakeholder interests',
        'Commitment to continual improvement'
      ]
    },
    {
      id: 'roles_responsibilities',
      title: 'Roles and Responsibilities',
      description: 'Define key roles in BC management',
      required: true,
      guidance: [
        'Top management responsibilities',
        'BC Manager role and authority',
        'Department head responsibilities',
        'Employee obligations'
      ]
    }
  ],
  optionalSections: [
    {
      id: 'definitions',
      title: 'Definitions',
      description: 'Key terms and definitions',
      required: false
    },
    {
      id: 'related_documents',
      title: 'Related Documents',
      description: 'References to related policies and procedures',
      required: false
    }
  ],
  relatedRequirements: ['5.2', '5.3', '7.3'],
  templateContent: `
# Business Continuity Policy

## 1. Purpose and Scope

### 1.1 Purpose
This Business Continuity Policy establishes the framework for ensuring [Organization Name] can continue to deliver critical business functions during and after disruptive events. This policy demonstrates management commitment to:

- Protecting the health, safety and welfare of employees, customers and other stakeholders
- Safeguarding assets, reputation and brand
- Meeting regulatory and legal obligations
- Maintaining stakeholder confidence and trust

### 1.2 Scope
This policy applies to all [Organization Name] operations, processes, personnel, and facilities worldwide. It covers all activities that support the delivery of our products and services.

### 1.3 Authority
This policy is authorized by the Board of Directors and Chief Executive Officer and shall be reviewed annually or following significant organizational changes.

## 2. Policy Statement

[Organization Name] is committed to:

- **Resilience**: Building and maintaining organizational resilience through proactive business continuity management
- **Preparedness**: Ensuring preparedness for potential disruptions through comprehensive planning, testing, and training
- **Response**: Responding effectively to incidents to minimize impact on operations, stakeholders, and reputation
- **Recovery**: Recovering critical business functions within predetermined timeframes
- **Continuous Improvement**: Continuously improving our business continuity capabilities based on lessons learned and changing risks

## 3. Key Principles

### 3.1 Risk-Based Approach
Business continuity management shall be based on understanding of risks that could impact critical business functions.

### 3.2 Business Impact Analysis
Regular analysis shall be conducted to understand the impact of disruptions on business operations and stakeholders.

### 3.3 Proportionate Response
Business continuity strategies and solutions shall be proportionate to the level of risk and potential impact.

### 3.4 Integration
Business continuity management shall be integrated with other organizational management systems and processes.

## 4. Roles and Responsibilities

### 4.1 Board of Directors / Senior Management
- Provide leadership and commitment to business continuity management
- Approve business continuity policy and strategy
- Ensure adequate resources are allocated
- Review business continuity performance regularly

### 4.2 Business Continuity Manager
- Develop and maintain the business continuity management system
- Coordinate business impact analysis and risk assessments
- Facilitate development of business continuity plans
- Manage business continuity exercises and training programs

### 4.3 Department Heads
- Identify critical processes and resources within their departments
- Participate in business impact analysis and risk assessments
- Develop and maintain departmental business continuity plans
- Ensure staff are trained and aware of their BC responsibilities

### 4.4 All Employees
- Understand their role in business continuity arrangements
- Participate in training and exercises as required
- Report potential threats and incidents
- Follow business continuity procedures during incidents

## 5. Framework Components

This policy is supported by:
- Business Continuity Management System procedures
- Business Impact Analysis methodology
- Risk assessment and management processes
- Business continuity strategies and plans
- Training and awareness programs
- Exercise and testing programs
- Performance monitoring and review processes

## 6. Compliance and Review

### 6.1 Compliance
All personnel are required to comply with this policy and supporting procedures. Non-compliance may result in disciplinary action.

### 6.2 Review and Updates
This policy shall be reviewed annually and updated as necessary to ensure continued effectiveness and alignment with organizational objectives.

## 7. Communication

This policy shall be communicated to all relevant stakeholders and made available to interested parties as appropriate.

---
**Document Control**
- Version: 1.0
- Effective Date: [Date]
- Next Review Date: [Date + 1 year]
- Owner: Business Continuity Manager
- Approved by: Chief Executive Officer
  `
}

// Шаблон процедуры управления инцидентами
export const INCIDENT_MANAGEMENT_PROCEDURE: DocumentTemplate = {
  id: 'BC-PROC-001',
  name: 'Incident Management Procedure',
  description: 'Step-by-step procedure for managing business continuity incidents',
  type: 'procedure',
  requiredSections: [
    {
      id: 'objective',
      title: 'Objective',
      description: 'Define the objective of the procedure',
      required: true
    },
    {
      id: 'scope',
      title: 'Scope',
      description: 'Define what is covered by this procedure',
      required: true
    },
    {
      id: 'procedure_steps',
      title: 'Procedure Steps',
      description: 'Detailed step-by-step process',
      required: true
    }
  ],
  optionalSections: [
    {
      id: 'flowchart',
      title: 'Process Flowchart',
      description: 'Visual representation of the process',
      required: false
    }
  ],
  relatedRequirements: ['8.3', '8.4'],
  templateContent: `
# Incident Management Procedure

## 1. Objective
To provide a structured approach for detecting, responding to, and managing incidents that could impact business continuity.

## 2. Scope
This procedure applies to all incidents that could potentially disrupt critical business functions, regardless of cause or severity.

## 3. Definitions
- **Incident**: An event that could impact the delivery of critical business functions
- **Business Continuity Incident**: An incident that requires activation of business continuity plans
- **Crisis**: A high-impact incident requiring senior management involvement

## 4. Roles and Responsibilities

### 4.1 Incident Commander
- Overall responsibility for incident response
- Coordinates response activities
- Makes key decisions regarding resource allocation

### 4.2 Communications Manager
- Manages internal and external communications
- Coordinates with media and stakeholders
- Maintains communication logs

## 5. Procedure Steps

### 5.1 Incident Detection and Reporting
1. **Initial Detection**
   - Monitor for potential incidents through various channels
   - Receive incident reports from staff, systems, or external sources
   - Verify incident information

2. **Initial Assessment**
   - Assess potential impact on critical business functions
   - Determine incident severity level
   - Notify appropriate personnel

### 5.2 Incident Classification
Classify incidents based on:
- **Low Impact**: Minimal disruption, normal response procedures
- **Medium Impact**: Significant disruption, departmental response
- **High Impact**: Critical disruption, full BC plan activation
- **Crisis**: Severe impact, executive management involvement

### 5.3 Response Activation
1. Activate appropriate response level based on classification
2. Establish incident command structure
3. Notify response team members
4. Set up incident management center if required

### 5.4 Response Implementation
1. Implement immediate safety measures
2. Assess and document incident impact
3. Activate relevant business continuity plans
4. Coordinate response activities
5. Manage communications

### 5.5 Recovery Operations
1. Monitor response effectiveness
2. Adjust strategies as needed
3. Plan for return to normal operations
4. Coordinate recovery activities

### 5.6 Incident Closure
1. Confirm normal operations are restored
2. Conduct post-incident review
3. Document lessons learned
4. Update plans and procedures as necessary

## 6. Communication Requirements
- All incidents must be reported within 30 minutes of detection
- Regular updates must be provided every 2 hours during active incidents
- Stakeholder notifications must follow established protocols

## 7. Documentation
All incident activities must be documented including:
- Incident timeline
- Actions taken
- Resources utilized
- Decisions made
- Communications sent

## 8. Training
All personnel involved in incident response must receive regular training on this procedure.
  `
}

// Шаблон плана непрерывности бизнеса
export const BC_PLAN_TEMPLATE: DocumentTemplate = {
  id: 'BC-PLAN-001',
  name: 'Business Continuity Plan',
  description: 'Comprehensive business continuity plan template',
  type: 'plan',
  requiredSections: [
    {
      id: 'plan_overview',
      title: 'Plan Overview',
      description: 'High-level overview of the plan',
      required: true
    },
    {
      id: 'activation_criteria',
      title: 'Plan Activation Criteria',
      description: 'When and how the plan is activated',
      required: true
    },
    {
      id: 'response_teams',
      title: 'Response Team Structure',
      description: 'Organization and roles of response teams',
      required: true
    }
  ],
  optionalSections: [],
  relatedRequirements: ['8.2', '8.3'],
  templateContent: `
# Business Continuity Plan
## [Department/Function Name]

### Plan Summary
- **Plan Owner**: [Name and Title]
- **Last Updated**: [Date]
- **Next Review**: [Date]
- **Classification**: [Confidential/Internal Use]

## 1. Plan Overview

### 1.1 Purpose
This Business Continuity Plan provides procedures and information needed to ensure [Department/Function] can continue critical operations during and after a disruptive event.

### 1.2 Scope
This plan covers:
- Critical business functions within [Department/Function]
- Key personnel and their responsibilities
- Essential resources and systems
- Recovery procedures and timelines

## 2. Critical Function Analysis

### 2.1 Critical Business Functions
| Function | Description | RTO | RPO | Dependencies |
|----------|-------------|-----|-----|--------------|
| [Function 1] | [Description] | [Time] | [Time] | [List] |
| [Function 2] | [Description] | [Time] | [Time] | [List] |

### 2.2 Impact Analysis
- **Financial Impact**: [Description]
- **Operational Impact**: [Description] 
- **Regulatory Impact**: [Description]
- **Reputational Impact**: [Description]

## 3. Plan Activation

### 3.1 Activation Criteria
This plan should be activated when:
- [Specific condition 1]
- [Specific condition 2]
- [Specific condition 3]

### 3.2 Activation Authority
- **Primary**: [Name, Title, Contact]
- **Secondary**: [Name, Title, Contact]

## 4. Response Team Structure

### 4.1 Team Leader
- **Name**: [Name]
- **Role**: Overall coordination and decision making
- **Contact**: [Phone/Email]

### 4.2 Team Members
| Name | Role | Contact | Backup |
|------|------|---------|--------|
| [Name] | [Role] | [Contact] | [Name] |

## 5. Recovery Procedures

### 5.1 Immediate Response (0-4 hours)
1. Ensure safety of personnel
2. Assess damage and impact
3. Activate team notifications
4. Establish temporary operations center
5. Implement immediate workarounds

### 5.2 Short-term Recovery (4-24 hours)
1. Set up alternate work locations
2. Restore critical systems
3. Implement manual processes
4. Coordinate with suppliers/vendors
5. Maintain stakeholder communications

### 5.3 Long-term Recovery (1-30 days)
1. Restore full operations
2. Return to primary location
3. Replenish resources
4. Update plans based on lessons learned

## 6. Resource Requirements

### 6.1 Personnel
- [Number] staff members required
- Skills: [List required skills]
- Training: [Training requirements]

### 6.2 Technology
- Hardware: [List requirements]
- Software: [List requirements]
- Communications: [Requirements]

### 6.3 Facilities
- Space requirements: [Description]
- Location options: [List alternatives]
- Setup time: [Time estimate]

## 7. Communication Plan

### 7.1 Internal Communications
| Stakeholder | Contact Method | Frequency | Responsible |
|-------------|---------------|-----------|-------------|
| Staff | Email/Phone | Every 4 hours | Team Leader |
| Management | Phone/Email | Every 2 hours | Team Leader |

### 7.2 External Communications
| Stakeholder | Contact Method | Message Owner | Approval Required |
|-------------|---------------|---------------|-------------------|
| Customers | Email/Website | Communications Mgr | Yes |
| Suppliers | Phone/Email | Team Leader | No |

## 8. Testing and Maintenance

### 8.1 Testing Schedule
- **Desktop Review**: Quarterly
- **Functional Test**: Semi-annually  
- **Full Exercise**: Annually

### 8.2 Plan Updates
This plan will be reviewed and updated:
- After each test or exercise
- Following any significant organizational changes
- At least annually

---
**Emergency Contacts**
[List of emergency contacts and phone numbers]
  `
}

// Экспорт всех шаблонов
export const DOCUMENT_TEMPLATES = {
  BC_POLICY_TEMPLATE,
  INCIDENT_MANAGEMENT_PROCEDURE,
  BC_PLAN_TEMPLATE
}

// Утилиты для работы с шаблонами
export class TemplateGenerator {
  
  static generateDocument(templateId: string, customizations: Record<string, string> = {}): string {
    const template = this.getTemplate(templateId)
    if (!template) {
      throw new Error(`Template ${templateId} not found`)
    }

    let content = template.templateContent
    
    // Заменяем плейсхолдеры
    for (const [key, value] of Object.entries(customizations)) {
      const placeholder = `[${key}]`
      content = content.replaceAll(placeholder, value)
    }

    return content
  }

  static getTemplate(templateId: string): DocumentTemplate | undefined {
    return Object.values(DOCUMENT_TEMPLATES).find(t => t.id === templateId)
  }

  static getTemplatesByType(type: DocumentTemplate['type']): DocumentTemplate[] {
    return Object.values(DOCUMENT_TEMPLATES).filter(t => t.type === type)
  }

  static validateTemplateCompletion(templateId: string, content: string): TemplateValidation {
    const template = this.getTemplate(templateId)
    if (!template) {
      return { valid: false, errors: ['Template not found'] }
    }

    const errors: string[] = []
    const warnings: string[] = []
    
    // Проверяем обязательные секции
    template.requiredSections.forEach(section => {
      if (!content.includes(section.title)) {
        errors.push(`Missing required section: ${section.title}`)
      }
    })

    // Проверяем наличие плейсхолдеров
    const placeholders = content.match(/\[.*?\]/g) || []
    if (placeholders.length > 0) {
      warnings.push(`Document contains ${placeholders.length} unfilled placeholders`)
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
      completionRate: this.calculateCompletionRate(template, content)
    }
  }

  private static calculateCompletionRate(template: DocumentTemplate, content: string): number {
    const allSections = [...template.requiredSections, ...template.optionalSections]
    const foundSections = allSections.filter(section => content.includes(section.title))
    
    return allSections.length > 0 ? (foundSections.length / allSections.length) * 100 : 0
  }
}

export interface TemplateValidation {
  valid: boolean
  errors: string[]
  warnings?: string[]
  completionRate?: number
}
