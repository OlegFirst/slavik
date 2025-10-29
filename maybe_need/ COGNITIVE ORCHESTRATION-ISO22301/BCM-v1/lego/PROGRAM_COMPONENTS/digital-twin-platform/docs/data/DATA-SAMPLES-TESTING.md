# Наборы данных для тестирования Digital Twin System

## 📦 Готовые наборы данных для разных уровней

### 1️⃣ МИНИМАЛЬНЫЙ НАБОР (Quick Start)

```javascript
// Скопируйте и используйте для быстрого теста
const minimalOrganization = {
  // ОБЯЗАТЕЛЬНЫЕ ПОЛЯ
  org_code: "NPO_MIN_001",
  name: "Small Community Foundation",
  type: "non-profit",
  size: 5,                    // минимум 1 сотрудник
  annual_budget: 50000,       // минимум $10,000
  
  // ОПЦИОНАЛЬНЫЕ ПОЛЯ
  mission: "Supporting local community",
  is_active: true
};

// Минимальный Digital Twin
const minimalTwin = {
  twin_id: "TWIN_MIN_001",
  organization_profile_id: "{{org_id}}", // подставить ID организации
  name: "Basic Digital Twin",
  configuration: {
    modules: ["basic"]
  },
  health_score: 0.5,
  efficiency_score: 0.5,
  is_active: true
};

// Минимальные метрики (3 штуки - минимум)
const minimalMetrics = [
  {
    twin_id: "{{twin_id}}",
    metric_type: "budget_utilization",
    value: 0.75,
    unit: "percentage"
  },
  {
    twin_id: "{{twin_id}}",
    metric_type: "staff_productivity",
    value: 0.60,
    unit: "percentage"
  },
  {
    twin_id: "{{twin_id}}",
    metric_type: "program_completion",
    value: 0.80,
    unit: "percentage"
  }
];
```

### 2️⃣ СРЕДНИЙ НАБОР (Рекомендуемый)

```javascript
// Полноценная организация среднего размера
const mediumOrganization = {
  org_code: "NPO_MED_001",
  name: "Regional Education Initiative",
  type: "non-profit",
  mission: "Improving education access for underserved communities",
  vision: "Every child has access to quality education",
  size: 25,
  annual_budget: 250000,
  
  // Контактная информация
  website: "https://education-initiative.org",
  contact_info: {
    email: "contact@education-initiative.org",
    phone: "+1-555-0123",
    address: {
      street: "123 Education Way",
      city: "Boston",
      state: "MA",
      zip: "02101",
      country: "USA"
    },
    social_media: {
      twitter: "@EduInitiative",
      linkedin: "education-initiative",
      facebook: "educationinitiative"
    }
  },
  
  // Метаданные организации
  metadata: {
    founded_year: 2015,
    tax_exempt_status: "501(c)(3)",
    ein: "12-3456789",
    certifications: ["GuideStar Gold", "BBB Accredited"],
    board_size: 9,
    volunteer_count: 50,
    
    // Структура отделов
    departments: [
      {
        name: "Programs",
        size: 10,
        budget_allocation: 0.40,
        manager: "Jane Smith"
      },
      {
        name: "Development",
        size: 5,
        budget_allocation: 0.20,
        manager: "John Doe"
      },
      {
        name: "Operations",
        size: 7,
        budget_allocation: 0.25,
        manager: "Mary Johnson"
      },
      {
        name: "Administration",
        size: 3,
        budget_allocation: 0.15,
        manager: "Bob Wilson"
      }
    ],
    
    // Программы организации
    programs: [
      {
        id: "PROG_001",
        name: "After-School Tutoring",
        budget: 75000,
        beneficiaries: 250,
        staff_assigned: 4,
        success_rate: 0.85
      },
      {
        id: "PROG_002",
        name: "Summer Learning Camp",
        budget: 50000,
        beneficiaries: 150,
        staff_assigned: 3,
        success_rate: 0.90
      },
      {
        id: "PROG_003",
        name: "Teacher Training",
        budget: 35000,
        beneficiaries: 50,
        staff_assigned: 2,
        success_rate: 0.95
      }
    ],
    
    // Финансовая структура
    financial_breakdown: {
      revenue: {
        grants: {
          government: 75000,
          foundation: 100000
        },
        donations: {
          individual: 50000,
          corporate: 25000
        },
        events: 15000,
        other: 10000
      },
      expenses: {
        programs: 150000,
        salaries: 75000,
        operations: 30000,
        fundraising: 15000,
        admin: 5000
      }
    }
  }
};

// Расширенный Digital Twin
const mediumTwin = {
  twin_id: "TWIN_MED_001",
  organization_profile_id: "{{org_id}}",
  name: "Education Initiative Digital Twin",
  description: "Complete digital representation with analytics",
  
  configuration: {
    modules: ["basic", "analytics", "predictions", "simulations"],
    update_frequency: "daily",
    data_sources: ["manual", "api", "integrations"],
    
    simulation_scenarios: [
      "budget_optimization",
      "crisis_management",
      "scaling_analysis",
      "grant_impact"
    ],
    
    kpi_tracking: [
      "cost_per_beneficiary",
      "program_roi",
      "donor_retention",
      "volunteer_engagement",
      "overhead_ratio"
    ]
  },
  
  state: {
    last_updated: new Date().toISOString(),
    data_quality_score: 0.75,
    integration_status: {
      crm: true,
      accounting: true,
      email: false,
      social: false
    }
  },
  
  health_score: 0.78,
  efficiency_score: 0.82,
  sustainability_score: 0.71,
  impact_score: 0.85,
  
  predictions: {
    budget_forecast_6m: 275000,
    beneficiary_growth_1y: 1.35,
    risk_score: 0.25,
    opportunity_score: 0.80
  },
  
  is_active: true
};

// Детальные метрики (10+ штук)
const mediumMetrics = [
  // Финансовые метрики
  {
    twin_id: "{{twin_id}}",
    metric_type: "budget_utilization",
    value: 0.92,
    unit: "percentage",
    target: 0.95,
    trend: "stable"
  },
  {
    twin_id: "{{twin_id}}",
    metric_type: "cost_per_beneficiary",
    value: 275,
    unit: "dollars",
    target: 300,
    trend: "improving"
  },
  {
    twin_id: "{{twin_id}}",
    metric_type: "fundraising_roi",
    value: 4.2,
    unit: "ratio",
    target: 4.0,
    trend: "improving"
  },
  
  // Операционные метрики
  {
    twin_id: "{{twin_id}}",
    metric_type: "program_efficiency",
    value: 0.85,
    unit: "percentage",
    target: 0.80,
    trend: "stable"
  },
  {
    twin_id: "{{twin_id}}",
    metric_type: "staff_retention",
    value: 0.88,
    unit: "percentage",
    target: 0.85,
    trend: "improving"
  },
  {
    twin_id: "{{twin_id}}",
    metric_type: "volunteer_hours",
    value: 2500,
    unit: "hours",
    target: 2000,
    trend: "improving"
  },
  
  // Импакт метрики
  {
    twin_id: "{{twin_id}}",
    metric_type: "beneficiary_satisfaction",
    value: 4.3,
    unit: "score",
    target: 4.0,
    trend: "stable"
  },
  {
    twin_id: "{{twin_id}}",
    metric_type: "program_completion_rate",
    value: 0.87,
    unit: "percentage",
    target: 0.85,
    trend: "improving"
  },
  {
    twin_id: "{{twin_id}}",
    metric_type: "community_reach",
    value: 450,
    unit: "families",
    target: 400,
    trend: "growing"
  },
  
  // Технологические метрики
  {
    twin_id: "{{twin_id}}",
    metric_type: "digital_engagement",
    value: 0.65,
    unit: "percentage",
    target: 0.70,
    trend: "improving"
  }
];

// Симуляции
const mediumSimulations = [
  {
    simulation_id: "SIM_001",
    twin_id: "{{twin_id}}",
    scenario: "budget_optimization",
    parameters: {
      target_reduction: 0.15,
      preserve_programs: true,
      timeline_months: 6
    },
    status: "completed",
    results: {
      achievable_reduction: 0.12,
      affected_programs: 1,
      staff_impact: 2,
      savings: 30000,
      recommendations: [
        "Merge administrative functions",
        "Negotiate vendor contracts",
        "Implement volunteer program"
      ]
    }
  },
  {
    simulation_id: "SIM_002",
    twin_id: "{{twin_id}}",
    scenario: "scaling_analysis",
    parameters: {
      growth_target: 1.5,
      timeline_months: 12,
      maintain_quality: true
    },
    status: "completed",
    results: {
      feasible_growth: 1.35,
      required_budget: 337500,
      required_staff: 34,
      risk_level: "moderate",
      critical_factors: [
        "Funding sustainability",
        "Staff recruitment",
        "Program quality"
      ]
    }
  }
];
```

### 3️⃣ ПОЛНЫЙ НАБОР (Enterprise)

```javascript
// Крупная организация с полными данными
const fullOrganization = {
  org_code: "NPO_FULL_001",
  name: "National Health & Wellness Foundation",
  type: "non-profit",
  mission: "Advancing health equity through innovation and community partnerships",
  vision: "A world where everyone has access to quality healthcare",
  values: ["Equity", "Innovation", "Collaboration", "Integrity", "Excellence"],
  
  size: 150,
  annual_budget: 5000000,
  
  // Детальная контактная информация
  website: "https://healthwellness.org",
  contact_info: {
    headquarters: {
      address: {
        street: "1000 Health Plaza",
        city: "New York",
        state: "NY",
        zip: "10001",
        country: "USA"
      },
      phone: "+1-212-555-0100",
      fax: "+1-212-555-0101"
    },
    regional_offices: [
      {
        region: "West Coast",
        city: "San Francisco",
        phone: "+1-415-555-0200"
      },
      {
        region: "Midwest",
        city: "Chicago",
        phone: "+1-312-555-0300"
      },
      {
        region: "South",
        city: "Atlanta",
        phone: "+1-404-555-0400"
      }
    ],
    digital_presence: {
      email: "info@healthwellness.org",
      support: "support@healthwellness.org",
      press: "media@healthwellness.org",
      social_media: {
        twitter: "@HealthWellnessOrg",
        linkedin: "health-wellness-foundation",
        facebook: "HealthWellnessFoundation",
        instagram: "@healthwellness",
        youtube: "HealthWellnessChannel"
      }
    }
  },
  
  // Комплексные метаданные
  metadata: {
    // Организационная информация
    founded_year: 2005,
    tax_exempt_status: "501(c)(3)",
    ein: "98-7654321",
    duns_number: "123456789",
    
    // Сертификации и рейтинги
    certifications: [
      "GuideStar Platinum",
      "BBB Accredited",
      "Charity Navigator 4-Star",
      "ISO 9001:2015",
      "HIPAA Compliant"
    ],
    
    ratings: {
      charity_navigator: 95,
      guidestar: "Platinum",
      bbb: "A+",
      glassdoor: 4.2,
      indeed: 4.0
    },
    
    // Управление
    governance: {
      board_size: 21,
      board_meetings_per_year: 6,
      committees: [
        {
          name: "Executive Committee",
          members: 7,
          meetings_per_year: 12
        },
        {
          name: "Finance Committee",
          members: 5,
          meetings_per_year: 8
        },
        {
          name: "Program Committee",
          members: 6,
          meetings_per_year: 6
        },
        {
          name: "Audit Committee",
          members: 4,
          meetings_per_year: 4
        },
        {
          name: "Development Committee",
          members: 8,
          meetings_per_year: 6
        }
      ],
      
      key_policies: [
        "Conflict of Interest Policy",
        "Whistleblower Policy",
        "Document Retention Policy",
        "Gift Acceptance Policy",
        "Investment Policy"
      ]
    },
    
    // Полная структура отделов
    departments: [
      {
        id: "DEPT_001",
        name: "Programs & Services",
        size: 60,
        budget_allocation: 0.45,
        sub_departments: [
          {
            name: "Direct Services",
            size: 35,
            focus: "Patient care and support"
          },
          {
            name: "Community Outreach",
            size: 15,
            focus: "Education and prevention"
          },
          {
            name: "Research & Innovation",
            size: 10,
            focus: "New program development"
          }
        ]
      },
      {
        id: "DEPT_002",
        name: "Development & Fundraising",
        size: 25,
        budget_allocation: 0.15,
        sub_departments: [
          {
            name: "Major Gifts",
            size: 8,
            focus: "Individual donors $10k+"
          },
          {
            name: "Corporate Partnerships",
            size: 7,
            focus: "Business relationships"
          },
          {
            name: "Grants",
            size: 6,
            focus: "Foundation and government"
          },
          {
            name: "Events",
            size: 4,
            focus: "Fundraising events"
          }
        ]
      },
      {
        id: "DEPT_003",
        name: "Operations",
        size: 30,
        budget_allocation: 0.20,
        sub_departments: [
          {
            name: "Finance",
            size: 10,
            focus: "Financial management"
          },
          {
            name: "HR",
            size: 8,
            focus: "Human resources"
          },
          {
            name: "IT",
            size: 7,
            focus: "Technology systems"
          },
          {
            name: "Facilities",
            size: 5,
            focus: "Building management"
          }
        ]
      },
      {
        id: "DEPT_004",
        name: "Marketing & Communications",
        size: 20,
        budget_allocation: 0.10,
        sub_departments: [
          {
            name: "Digital Marketing",
            size: 8,
            focus: "Online presence"
          },
          {
            name: "Public Relations",
            size: 6,
            focus: "Media relations"
          },
          {
            name: "Content Creation",
            size: 6,
            focus: "Materials and messaging"
          }
        ]
      },
      {
        id: "DEPT_005",
        name: "Executive & Admin",
        size: 15,
        budget_allocation: 0.10,
        sub_departments: [
          {
            name: "Executive Office",
            size: 5,
            focus: "Leadership"
          },
          {
            name: "Legal & Compliance",
            size: 4,
            focus: "Regulatory compliance"
          },
          {
            name: "Strategy & Planning",
            size: 6,
            focus: "Strategic initiatives"
          }
        ]
      }
    ],
    
    // Детальные программы
    programs: [
      {
        id: "PROG_ADV_001",
        name: "Community Health Centers",
        category: "Direct Services",
        budget: 1500000,
        start_date: "2020-01-01",
        
        objectives: [
          "Provide primary care to 10,000 patients",
          "Reduce ER visits by 30%",
          "Improve health outcomes in underserved areas"
        ],
        
        metrics: {
          patients_served: 9500,
          er_reduction: 0.28,
          satisfaction_score: 4.5,
          cost_per_patient: 150
        },
        
        staff: {
          full_time: 20,
          part_time: 10,
          volunteers: 50
        },
        
        partners: [
          "Local Hospital Network",
          "State Health Department",
          "Community Clinics Association"
        ],
        
        funding_sources: [
          {
            source: "Federal Grant",
            amount: 800000
          },
          {
            source: "State Grant",
            amount: 400000
          },
          {
            source: "Private Foundations",
            amount: 300000
          }
        ]
      },
      // ... добавить еще 5-10 программ
    ],
    
    // Финансовые данные за 3 года
    financial_history: [
      {
        year: 2023,
        revenue: 4500000,
        expenses: 4200000,
        surplus: 300000,
        assets: 8000000,
        liabilities: 1500000
      },
      {
        year: 2022,
        revenue: 4200000,
        expenses: 4000000,
        surplus: 200000,
        assets: 7500000,
        liabilities: 1600000
      },
      {
        year: 2021,
        revenue: 3800000,
        expenses: 3700000,
        surplus: 100000,
        assets: 7000000,
        liabilities: 1700000
      }
    ],
    
    // Стейкхолдеры
    stakeholders: {
      major_donors: 150,
      regular_donors: 5000,
      corporate_partners: 50,
      foundation_partners: 25,
      government_contracts: 8,
      volunteers: 500,
      beneficiaries: 50000,
      staff: 150,
      board_members: 21
    },
    
    // Внешние интеграции
    integrations: {
      crm: "Salesforce Nonprofit Cloud",
      accounting: "QuickBooks Nonprofit",
      hr: "BambooHR",
      email: "Mailchimp",
      analytics: "Google Analytics 4",
      donations: "Stripe + PayPal",
      grants: "Fluxx Grantmaker",
      volunteer: "VolunteerHub"
    }
  }
};

// Продвинутые симуляции с Machine Learning
const fullSimulations = [
  {
    simulation_id: "SIM_ADV_001",
    twin_id: "{{twin_id}}",
    scenario: "pandemic_response",
    type: "crisis_management",
    
    parameters: {
      crisis_severity: 0.8,
      duration_months: 18,
      funding_impact: -0.30,
      demand_increase: 2.5,
      staff_availability: 0.70
    },
    
    ml_models: [
      "demand_forecasting",
      "resource_optimization",
      "donor_behavior_prediction"
    ],
    
    results: {
      survival_probability: 0.92,
      critical_decisions: [
        {
          month: 1,
          action: "Shift to digital services",
          impact: "Maintain 80% service delivery"
        },
        {
          month: 3,
          action: "Emergency fundraising campaign",
          impact: "Raise $500k emergency funds"
        },
        {
          month: 6,
          action: "Merge non-critical programs",
          impact: "Reduce costs by 25%"
        }
      ],
      
      resource_allocation: {
        programs: 0.60,
        reserves: 0.20,
        fundraising: 0.15,
        operations: 0.05
      },
      
      projected_outcomes: {
        beneficiaries_served: 35000,
        staff_retained: 0.85,
        donor_retention: 0.75,
        program_effectiveness: 0.70
      },
      
      risk_mitigation: [
        "Build 6-month reserve fund",
        "Diversify funding sources",
        "Develop crisis response plan",
        "Train staff for remote work"
      ]
    }
  },
  
  {
    simulation_id: "SIM_ADV_002",
    twin_id: "{{twin_id}}",
    scenario: "national_expansion",
    type: "growth_strategy",
    
    parameters: {
      target_states: 10,
      timeline_years: 3,
      investment_required: 10000000,
      target_beneficiaries: 200000
    },
    
    ml_models: [
      "market_opportunity_analysis",
      "competitive_landscape",
      "funding_prediction",
      "talent_acquisition"
    ],
    
    phases: [
      {
        phase: 1,
        year: 1,
        states: 3,
        investment: 3000000,
        milestones: [
          "Establish regional hubs",
          "Hire local teams",
          "Launch pilot programs"
        ]
      },
      {
        phase: 2,
        year: 2,
        states: 5,
        investment: 4000000,
        milestones: [
          "Scale successful programs",
          "Build partnerships",
          "Achieve break-even"
        ]
      },
      {
        phase: 3,
        year: 3,
        states: 2,
        investment: 3000000,
        milestones: [
          "Full national coverage",
          "Sustainability achieved",
          "Impact measurement"
        ]
      }
    ],
    
    success_probability: 0.78,
    roi_projection: 3.5,
    break_even_month: 30
  }
];
```

## 🧪 Тестовые сценарии

### Сценарий 1: Быстрый тест (5 минут)
```bash
# 1. Создать организацию
curl -X POST http://localhost:3000/api/organizations \
  -H "Content-Type: application/json" \
  -d '{
    "org_code": "TEST_QUICK_001",
    "name": "Quick Test NPO",
    "type": "non-profit",
    "size": 10,
    "annual_budget": 100000
  }'

# 2. Проверить создание
curl http://localhost:3000/api/organizations

# 3. Создать Digital Twin
curl -X POST http://localhost:3000/api/digital-twins \
  -H "Content-Type: application/json" \
  -d '{
    "twin_id": "TWIN_TEST_001",
    "organization_profile_id": "{{полученный_id}}",
    "name": "Test Twin",
    "health_score": 0.75
  }'
```

### Сценарий 2: Полный цикл симуляции (15 минут)
```javascript
// test-full-cycle.js
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

async function runFullCycle() {
  // 1. Создать организацию
  const { data: org } = await supabase
    .from('organization_profiles')
    .insert(mediumOrganization)
    .select()
    .single();
  
  // 2. Создать Digital Twin
  const twinData = { ...mediumTwin, organization_profile_id: org.id };
  const { data: twin } = await supabase
    .from('digital_twins')
    .insert(twinData)
    .select()
    .single();
  
  // 3. Добавить метрики
  const metricsData = mediumMetrics.map(m => ({
    ...m,
    twin_id: twin.id
  }));
  await supabase.from('metrics').insert(metricsData);
  
  // 4. Запустить симуляцию
  const simData = {
    ...mediumSimulations[0],
    twin_id: twin.id
  };
  const { data: sim } = await supabase
    .from('simulations')
    .insert(simData)
    .select()
    .single();
  
  // 5. Создать отчет
  const report = {
    twin_id: twin.id,
    report_type: 'comprehensive',
    title: 'Full Cycle Test Report',
    content: {
      organization: org,
      twin: twin,
      metrics: metricsData,
      simulation: sim
    },
    format: 'json'
  };
  
  await supabase.from('reports').insert(report);
  
  console.log('Full cycle completed!');
  console.log('Organization ID:', org.id);
  console.log('Digital Twin ID:', twin.id);
  console.log('Simulation ID:', sim.id);
}

runFullCycle();
```

### Сценарий 3: Стресс-тест (30 минут)
```javascript
// stress-test.js
async function stressTest() {
  const promises = [];
  
  // Создать 100 организаций
  for (let i = 0; i < 100; i++) {
    const org = {
      org_code: `STRESS_ORG_${i}`,
      name: `Test Organization ${i}`,
      type: 'non-profit',
      size: Math.floor(Math.random() * 100) + 10,
      annual_budget: Math.floor(Math.random() * 1000000) + 50000
    };
    
    promises.push(
      supabase.from('organization_profiles').insert(org)
    );
  }
  
  const results = await Promise.all(promises);
  console.log(`Created ${results.length} organizations`);
  
  // Для каждой организации создать twin и метрики
  // ... продолжение теста
}
```

## 📋 Валидация данных

### Обязательные поля для работы системы:
```javascript
const requiredFields = {
  organization: {
    required: ['org_code', 'name', 'type', 'size', 'annual_budget'],
    minimum_values: {
      size: 1,
      annual_budget: 10000
    }
  },
  
  digital_twin: {
    required: ['twin_id', 'organization_profile_id', 'name'],
    minimum_values: {
      health_score: 0,
      efficiency_score: 0
    }
  },
  
  metrics: {
    required: ['twin_id', 'metric_type', 'value'],
    minimum_count: 3
  }
};
```

### Формулы для автоматического расчета:
```javascript
// Health Score
health_score = (
  budget_utilization * 0.25 +
  staff_retention * 0.20 +
  program_effectiveness * 0.30 +
  donor_satisfaction * 0.25
);

// Efficiency Score
efficiency_score = (
  (1 - overhead_ratio) * 0.30 +
  program_roi * 0.35 +
  cost_per_beneficiary_ratio * 0.35
);

// Sustainability Score
sustainability_score = (
  funding_diversity * 0.30 +
  reserve_ratio * 0.25 +
  donor_retention * 0.25 +
  growth_rate * 0.20
);
```

## 🎯 Быстрые команды для тестирования

```bash
# Минимальный тест
npm test

# Создать 10 тестовых организаций
node scripts/create-test-data.js --count=10 --level=minimal

# Создать полный набор данных
node scripts/create-test-data.js --count=1 --level=full

# Очистить тестовые данные
node scripts/clean-test-data.js
```

---
*Используйте эти наборы данных для тестирования различных сценариев и уровней функциональности системы Digital Twin*