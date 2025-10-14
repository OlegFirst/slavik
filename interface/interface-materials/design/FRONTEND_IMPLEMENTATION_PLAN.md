# 🎯 Frontend Implementation Plan - 7 User Journeys

**Base Project**: `/interface/admin-control-center/`
**Target**: Transform into **Multi-Journey BCM Platform**
**Timeline**: 12 weeks (3 months MVP)

---

## 🏗️ PROJECT STRUCTURE

```
/interface/admin-control-center/
├── src/
│   ├── app/                          # Route-based pages
│   │   ├── (landing)/
│   │   │   └── page.tsx             # Landing + Journey Selector
│   │   ├── (certification)/         # Journey 1, 4, 7
│   │   │   ├── layout.tsx
│   │   │   ├── gap-analysis/
│   │   │   ├── roadmap/
│   │   │   ├── documents/
│   │   │   ├── readiness/
│   │   │   └── courses/
│   │   ├── (auditor)/               # Journey 2
│   │   │   ├── dashboard/
│   │   │   ├── clients/
│   │   │   └── tools/
│   │   ├── (academy)/               # Journey 3
│   │   │   ├── courses/
│   │   │   ├── case-studies/
│   │   │   ├── ai-tutor/
│   │   │   └── community/
│   │   ├── (digital-twin)/          # Journey 5
│   │   │   ├── builder/
│   │   │   ├── visualize/
│   │   │   └── simulate/
│   │   ├── (crisis)/                # Journey 6
│   │   │   ├── activate/
│   │   │   ├── command-center/
│   │   │   └── recovery-planner/
│   │   ├── marketplace/
│   │   └── profile/
│   ├── components/
│   │   ├── journeys/                # Journey-specific components
│   │   │   ├── certification/
│   │   │   │   ├── GapAnalysisWizard.tsx
│   │   │   │   ├── RoadmapTimeline.tsx
│   │   │   │   ├── DocumentGenerator.tsx
│   │   │   │   └── ReadinessTracker.tsx
│   │   │   ├── auditor/
│   │   │   │   ├── ClientWorkPackage.tsx
│   │   │   │   ├── AutomatedGapAnalyzer.tsx
│   │   │   │   └── ReportGenerator.tsx
│   │   │   ├── academy/
│   │   │   │   ├── CoursePlayer.tsx
│   │   │   │   ├── CaseStudyViewer.tsx
│   │   │   │   └── AITutorChat.tsx
│   │   │   ├── digital-twin/
│   │   │   │   ├── TwinBuilder.tsx
│   │   │   │   ├── ThreeJSVisualizer.tsx
│   │   │   │   └── ScenarioSimulator.tsx
│   │   │   └── crisis/
│   │   │       ├── IncidentActivation.tsx
│   │   │       ├── CommandCenter.tsx
│   │   │       └── RecoveryPlanner.tsx
│   │   ├── marketplace/
│   │   │   ├── AuditorCard.tsx
│   │   │   ├── BookingCalendar.tsx
│   │   │   └── ServiceRequest.tsx
│   │   ├── shared/                  # Reusable components
│   │   │   ├── AIChat.tsx
│   │   │   ├── DocumentViewer.tsx
│   │   │   ├── ProgressTracker.tsx
│   │   │   └── DataTable.tsx
│   │   └── ui/                      # shadcn/ui components (keep existing)
│   ├── services/
│   │   ├── api/
│   │   │   ├── certification.ts     # Journey 1 APIs
│   │   │   ├── auditor.ts           # Journey 2 APIs
│   │   │   ├── academy.ts           # Journey 3 APIs
│   │   │   ├── digital-twin.ts      # Journey 5 APIs
│   │   │   ├── crisis.ts            # Journey 6 APIs
│   │   │   ├── marketplace.ts       # Shared marketplace APIs
│   │   │   ├── system-bcm.ts        # ✅ Already created!
│   │   │   └── ai-orchestrator.ts
│   │   └── external/
│   │       ├── stripe.ts            # Payment integration
│   │       └── supabase.ts          # User data, marketplace
│   ├── stores/
│   │   ├── useAuthStore.ts          # Authentication state
│   │   ├── useJourneyStore.ts       # Current journey context
│   │   ├── useCertificationStore.ts # Journey 1 state
│   │   ├── useAuditorStore.ts       # Journey 2 state
│   │   ├── useAcademyStore.ts       # Journey 3 state
│   │   ├── useTwinStore.ts          # Journey 5 state
│   │   └── useCrisisStore.ts        # Journey 6 state
│   ├── hooks/
│   │   ├── useAIAssistant.ts        # AI tutor/assistant
│   │   ├── useMarketplace.ts        # Marketplace operations
│   │   ├── useDocuments.ts          # Document management
│   │   └── useRealtime.ts           # WebSocket/SSE
│   └── types/
│       ├── journeys.ts              # Journey-specific types
│       ├── marketplace.ts
│       └── platform.ts
└── public/
    └── assets/
```

---

## 🎯 IMPLEMENTATION PHASES

### **PHASE 1: Foundation (Week 1-2)**

#### **Week 1: Project Setup & Authentication**

**Tasks**:
1. ✅ **Multi-Journey Routing**
   ```typescript
   // src/app/layout.tsx
   export default function RootLayout({ children }: { children: React.ReactNode }) {
     return (
       <html lang="en">
         <body>
           <AuthProvider>
             <JourneyProvider>  {/* NEW: Journey context */}
               <MainNavigation /> {/* Journey-aware nav */}
               {children}
               <AIAssistantFAB /> {/* Floating AI button */}
             </JourneyProvider>
           </AuthProvider>
         </body>
       </html>
     )
   }
   ```

2. ✅ **Authentication Integration**
   ```typescript
   // src/services/api/auth.ts
   import { createClient } from '@supabase/supabase-js'

   const supabase = createClient(
     process.env.NEXT_PUBLIC_SUPABASE_URL!,
     process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
   )

   export const authService = {
     // Odoo SSO integration
     async loginWithOdoo(credentials: { email: string; password: string }) {
       // Call Odoo backend for authentication
       const response = await fetch(`${ODOO_API_URL}/auth/login`, {
         method: 'POST',
         body: JSON.stringify(credentials)
       })
       const { token, user } = await response.json()

       // Store in Supabase for frontend session
       await supabase.auth.setSession({ access_token: token })
       return { user, token }
     },

     // Multi-tenancy check
     async checkOrganizationAccess(userId: string, orgId: string) {
       const { data } = await supabase
         .from('user_organizations')
         .select('*')
         .eq('user_id', userId)
         .eq('org_id', orgId)
         .single()
       return !!data
     }
   }
   ```

3. ✅ **Zustand Store Setup**
   ```typescript
   // src/stores/useAuthStore.ts
   import { create } from 'zustand'
   import { persist } from 'zustand/middleware'

   interface AuthState {
     user: User | null
     organization: Organization | null
     role: 'org_admin' | 'auditor' | 'bcm_manager' | 'learner'
     journey: 'certification' | 'auditor' | 'academy' | 'twin' | 'crisis'
     login: (credentials: Credentials) => Promise<void>
     logout: () => void
     switchJourney: (journey: Journey) => void
   }

   export const useAuthStore = create<AuthState>()(
     persist(
       (set) => ({
         user: null,
         organization: null,
         role: 'learner',
         journey: 'certification',
         login: async (credentials) => {
           const { user, token } = await authService.loginWithOdoo(credentials)
           set({ user })
         },
         logout: () => set({ user: null, organization: null }),
         switchJourney: (journey) => set({ journey })
       }),
       { name: 'auth-storage' }
     )
   )
   ```

#### **Week 2: Landing Page & Journey Selector**

**Tasks**:
1. ✅ **Landing Page**
   ```tsx
   // src/app/(landing)/page.tsx
   export default function LandingPage() {
     const { user, switchJourney } = useAuthStore()

     if (!user) return <LoginPage />

     return (
       <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
         <Hero />
         <JourneySelector onSelect={switchJourney} />
         <FeaturesOverview />
         <Testimonials />
       </div>
     )
   }

   function JourneySelector({ onSelect }: { onSelect: (j: Journey) => void }) {
     const journeys = [
       {
         id: 'certification',
         title: 'Get ISO 22301 Certified',
         description: 'Complete certification path with AI assistance',
         icon: Award,
         cta: 'Start Gap Analysis',
         color: 'blue'
       },
       {
         id: 'auditor',
         title: 'Auditor Tools',
         description: 'Find clients, automate audits, earn more',
         icon: Briefcase,
         cta: 'Auditor Dashboard',
         color: 'purple'
       },
       {
         id: 'academy',
         title: 'Learn & Grow',
         description: 'Courses, case studies, community',
         icon: GraduationCap,
         cta: 'Explore Courses',
         color: 'green'
       },
       {
         id: 'twin',
         title: 'Digital Twin',
         description: 'Model scenarios, predict outcomes',
         icon: Building,
         cta: 'Build Twin',
         color: 'orange'
       },
       {
         id: 'crisis',
         title: 'Crisis Recovery',
         description: 'Emergency response & AI planning',
         icon: AlertTriangle,
         cta: 'Activate Crisis Mode',
         color: 'red'
       }
     ]

     return (
       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-8">
         {journeys.map((journey) => (
           <JourneyCard
             key={journey.id}
             {...journey}
             onClick={() => onSelect(journey.id)}
           />
         ))}
       </div>
     )
   }
   ```

---

### **PHASE 2: Journey 1 - Certification (Week 3-6)**

#### **Week 3: Gap Analysis Wizard**

**Component**: `GapAnalysisWizard.tsx`

```tsx
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { certificationApi } from '@/services/api/certification'

export function GapAnalysisWizard() {
  const [step, setStep] = useState(1)
  const [answers, setAnswers] = useState<GapAnalysisAnswers>({})

  const analysisMutation = useMutation({
    mutationFn: (data: GapAnalysisAnswers) =>
      certificationApi.runGapAnalysis(data),
    onSuccess: (result) => {
      // Navigate to roadmap with results
      router.push(`/certification/roadmap?analysisId=${result.id}`)
    }
  })

  const iso22301Clauses = [
    {
      id: '4',
      title: 'Context of the Organization',
      questions: [
        {
          id: '4.1',
          text: 'Has the organization identified internal and external issues relevant to BCM?',
          type: 'yes_no_evidence',
          helpText: 'This includes SWOT analysis, stakeholder analysis'
        },
        {
          id: '4.2',
          text: 'Are interested parties and their requirements documented?',
          type: 'yes_no_evidence'
        }
      ]
    },
    {
      id: '5',
      title: 'Leadership',
      questions: [...]
    },
    // ... 10 clauses total
  ]

  return (
    <Wizard
      steps={iso22301Clauses.map((clause) => ({
        title: `${clause.id} ${clause.title}`,
        content: <ClauseQuestions clause={clause} onChange={setAnswers} />
      }))}
      onComplete={() => analysisMutation.mutate(answers)}
    />
  )
}

function ClauseQuestions({ clause, onChange }: ClauseQuestionsProps) {
  return (
    <div className="space-y-6">
      {clause.questions.map((q) => (
        <div key={q.id} className="border p-4 rounded-lg">
          <Label>{q.id} {q.text}</Label>
          {q.helpText && (
            <p className="text-sm text-muted-foreground">{q.helpText}</p>
          )}

          <RadioGroup onValueChange={(val) => onChange(q.id, val)}>
            <RadioGroupItem value="yes">Yes - Full compliance</RadioGroupItem>
            <RadioGroupItem value="partial">Partial compliance</RadioGroupItem>
            <RadioGroupItem value="no">No - Gap identified</RadioGroupItem>
          </RadioGroup>

          <Textarea
            placeholder="Provide evidence or explain gap..."
            className="mt-2"
          />
        </div>
      ))}
    </div>
  )
}
```

**API Service**:
```typescript
// src/services/api/certification.ts
export const certificationApi = {
  async runGapAnalysis(answers: GapAnalysisAnswers) {
    // 1. Call backend to analyze
    const response = await apiClient.post('/api/v1/compliance/gap-analysis', {
      standard: 'ISO_22301',
      answers
    })

    // 2. Use AI to generate recommendations
    const aiAnalysis = await aiClient.post('/api/v1/ai/analyze-gaps', {
      gapReport: response.data
    })

    return {
      id: response.data.id,
      score: response.data.compliance_percentage,
      gaps: response.data.identified_gaps,
      recommendations: aiAnalysis.data.recommendations,
      estimatedTimeline: aiAnalysis.data.timeline_weeks
    }
  },

  async generateRoadmap(analysisId: string) {
    const response = await apiClient.post(
      `/api/v1/compliance/gap-analysis/${analysisId}/roadmap`
    )
    return response.data
  }
}
```

#### **Week 4: Roadmap Timeline & Document Generator**

**Component**: `RoadmapTimeline.tsx`

```tsx
import { useQuery } from '@tanstack/react-query'
import { certificationApi } from '@/services/api/certification'

export function RoadmapTimeline({ analysisId }: { analysisId: string }) {
  const { data: roadmap } = useQuery({
    queryKey: ['roadmap', analysisId],
    queryFn: () => certificationApi.getRoadmap(analysisId)
  })

  if (!roadmap) return <Skeleton />

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-4 gap-4">
        <MetricCard
          title="Compliance Score"
          value={`${roadmap.current_score}%`}
          trend="+12%"
        />
        <MetricCard
          title="Estimated Timeline"
          value={`${roadmap.timeline_weeks} weeks`}
        />
        <MetricCard
          title="Critical Gaps"
          value={roadmap.critical_gaps_count}
        />
        <MetricCard
          title="Budget Est."
          value={`$${roadmap.estimated_cost}`}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Certification Roadmap</CardTitle>
        </CardHeader>
        <CardContent>
          <Timeline>
            {roadmap.phases.map((phase, index) => (
              <TimelineItem
                key={phase.id}
                title={phase.title}
                description={phase.description}
                duration={`${phase.duration_weeks} weeks`}
                tasks={phase.tasks}
                status={phase.status}
              />
            ))}
          </Timeline>
        </CardContent>
      </Card>

      <div className="flex justify-end gap-4">
        <Button variant="outline">Download PDF</Button>
        <Button onClick={() => router.push('/certification/documents')}>
          Start Creating Documents →
        </Button>
      </div>
    </div>
  )
}
```

**Document Generator**:
```tsx
// src/components/journeys/certification/DocumentGenerator.tsx
export function DocumentGenerator() {
  const [selectedTemplate, setSelectedTemplate] = useState<string>()
  const [generationMode, setGenerationMode] = useState<'ai' | 'manual'>('ai')

  const templates = [
    {
      id: 'bcm_policy',
      title: 'BCM Policy',
      clause: '5.3',
      aiGeneration: true,
      estimatedTime: '30 minutes with AI'
    },
    {
      id: 'bia_report',
      title: 'Business Impact Analysis',
      clause: '8.2',
      aiGeneration: true,
      estimatedTime: '2 hours with AI'
    },
    // ... more templates
  ]

  const generateMutation = useMutation({
    mutationFn: async (templateId: string) => {
      // AI-powered generation
      const response = await certificationApi.generateDocument({
        templateId,
        organizationId: user.organization_id,
        useAI: generationMode === 'ai'
      })
      return response
    },
    onSuccess: (doc) => {
      router.push(`/documents/${doc.id}/edit`)
    }
  })

  return (
    <div>
      <Tabs value={generationMode} onValueChange={setGenerationMode}>
        <TabsList>
          <TabsTrigger value="ai">🤖 AI-Assisted</TabsTrigger>
          <TabsTrigger value="manual">📝 Manual Template</TabsTrigger>
        </TabsList>

        <TabsContent value="ai">
          <AIDocumentWizard
            templates={templates}
            onGenerate={(id) => generateMutation.mutate(id)}
          />
        </TabsContent>

        <TabsContent value="manual">
          <TemplateLibrary templates={templates} />
        </TabsContent>
      </Tabs>
    </div>
  )
}

function AIDocumentWizard({ templates, onGenerate }: Props) {
  const [currentStep, setCurrentStep] = useState<'select' | 'interview' | 'generate'>('select')
  const [responses, setResponses] = useState<Record<string, string>>({})

  return (
    <div className="space-y-6">
      {currentStep === 'select' && (
        <TemplateGrid templates={templates} onSelect={setSelectedTemplate} />
      )}

      {currentStep === 'interview' && (
        <AIInterviewSession
          template={selectedTemplate!}
          onComplete={(data) => {
            setResponses(data)
            setCurrentStep('generate')
          }}
        />
      )}

      {currentStep === 'generate' && (
        <GenerationProgress onComplete={() => onGenerate(selectedTemplate!)} />
      )}
    </div>
  )
}
```

#### **Week 5-6: Readiness Tracker & Marketplace**

**Readiness Tracker**:
```tsx
// src/components/journeys/certification/ReadinessTracker.tsx
export function ReadinessTracker() {
  const { data: readiness } = useQuery({
    queryKey: ['certification', 'readiness'],
    queryFn: certificationApi.getReadinessStatus,
    refetchInterval: 60000 // Re-check every minute
  })

  const sections = [
    {
      id: 'documentation',
      title: 'Documentation',
      weight: 40,
      status: readiness?.documentation
    },
    {
      id: 'processes',
      title: 'Processes & Procedures',
      weight: 25,
      status: readiness?.processes
    },
    {
      id: 'training',
      title: 'Training & Awareness',
      weight: 15,
      status: readiness?.training
    },
    {
      id: 'exercises',
      title: 'Exercises & Testing',
      weight: 10,
      status: readiness?.exercises
    },
    {
      id: 'reviews',
      title: 'Reviews & Audits',
      weight: 10,
      status: readiness?.reviews
    }
  ]

  const overallScore = sections.reduce(
    (acc, s) => acc + (s.status?.completeness || 0) * (s.weight / 100),
    0
  )

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Overall Certification Readiness</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center">
            <CircularProgress value={overallScore} size="xl" />
            <p className="text-4xl font-bold mt-4">{overallScore}%</p>
            <p className="text-muted-foreground">Ready for Audit</p>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4">
        {sections.map((section) => (
          <ReadinessSection key={section.id} {...section} />
        ))}
      </div>

      {overallScore >= 80 && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertTitle>Ready for Certification!</AlertTitle>
          <AlertDescription>
            You've achieved {overallScore}% readiness. Time to find an auditor!
            <Button className="mt-2" onClick={() => router.push('/marketplace')}>
              Find Auditor →
            </Button>
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}
```

**Marketplace Integration**:
```tsx
// src/components/marketplace/AuditorMarketplace.tsx
export function AuditorMarketplace() {
  const [filters, setFilters] = useState<AuditorFilters>({
    certifications: [],
    industry: undefined,
    priceRange: [0, 10000],
    rating: 4.0
  })

  const { data: auditors } = useQuery({
    queryKey: ['marketplace', 'auditors', filters],
    queryFn: () => marketplaceApi.searchAuditors(filters)
  })

  return (
    <div className="grid grid-cols-4 gap-6">
      {/* Filters Sidebar */}
      <Card className="col-span-1">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <AuditorFilters value={filters} onChange={setFilters} />
        </CardContent>
      </Card>

      {/* Auditor List */}
      <div className="col-span-3 space-y-4">
        {auditors?.map((auditor) => (
          <AuditorCard
            key={auditor.id}
            auditor={auditor}
            onBook={() => router.push(`/marketplace/auditor/${auditor.id}/book`)}
          />
        ))}
      </div>
    </div>
  )
}

function AuditorCard({ auditor, onBook }: AuditorCardProps) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-start gap-4">
          <Avatar className="h-16 w-16">
            <AvatarImage src={auditor.avatar} />
            <AvatarFallback>{auditor.initials}</AvatarFallback>
          </Avatar>

          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h3 className="text-xl font-semibold">{auditor.name}</h3>
              <Badge variant="secondary">{auditor.certifications[0]}</Badge>
            </div>

            <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                {auditor.rating} ({auditor.reviews_count} reviews)
              </span>
              <span>{auditor.completed_audits}+ audits</span>
              <span>{auditor.industry_experience.join(', ')}</span>
            </div>

            <p className="mt-2 line-clamp-2">{auditor.bio}</p>

            <div className="mt-4 flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Starting from</p>
                <p className="text-2xl font-bold">${auditor.pricing.consultation}/hr</p>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  View Profile
                </Button>
                <Button size="sm" onClick={onBook}>
                  Book Consultation
                </Button>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
```

---

## 🎯 SUCCESS CRITERIA

### **Phase 1 (Week 1-2)**
- ✅ Authentication working with Odoo SSO
- ✅ Multi-journey routing configured
- ✅ Landing page with journey selector
- ✅ Role-based access control

### **Phase 2 (Week 3-6)**
- ✅ Gap Analysis wizard (10 ISO clauses)
- ✅ AI-generated gap report
- ✅ Personalized roadmap timeline
- ✅ AI document generator (5+ templates)
- ✅ Readiness tracker (live metrics)
- ✅ Auditor marketplace (search + book)

---

## 📊 METRICS TO TRACK

```typescript
interface DevelopmentMetrics {
  codeQuality: {
    typeScriptCoverage: "100% typed"
    testCoverage: ">80%"
    eslintErrors: "0"
  }

  performance: {
    pageLoadTime: "<2s"
    apiResponseTime: "<500ms"
    bundleSize: "<500KB gzipped"
  }

  userExperience: {
    accessibilityScore: ">90 (Lighthouse)"
    mobileResponsive: "100%"
    errorRate: "<1%"
  }
}
```

---

**Готово к имплементации партнер! 🚀**

**Следующий шаг**: Начинаем Week 1 - создаем landing page + journey selector?
