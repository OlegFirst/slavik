'use client';

/**
 * BIAWorkflowWizard Component
 * 7-Step BIA Workflow following BIA Workflow Engine
 * Progressive wizard with validation at each step
 * Integrates DependencyMapper, ImpactAssessmentForm, RecoveryStrategiesBuilder
 */

import { useState, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  ChevronLeft,
  ChevronRight,
  Save,
  CheckCircle2,
  Circle,
  Loader2,
  AlertTriangle,
  FileText,
  Network,
  Clock,
  TrendingDown,
  Users,
  Shield,
  BookOpen,
} from 'lucide-react';
import { biaProcessCreateSchema, type BIAProcessCreateInput } from '@/lib/validations/bia';
import { useCreateBIAProcess } from '@/hooks/bia';
import { CriticalityLevel, IndustryType, GeographicalScope, WHOTier, type Dependency } from '@/types/bia';
import { DependencyMapper } from './DependencyMapper';
import { ImpactAssessmentForm, type ImpactData } from './ImpactAssessmentForm';
import { RecoveryStrategiesBuilder } from './RecoveryStrategiesBuilder';

interface BIAWorkflowWizardProps {
  tenant_id: string;
  onComplete?: (processId: number) => void;
  onCancel?: () => void;
  onSaveDraft?: (data: Partial<BIAProcessCreateInput>) => void;
}

/**
 * 7 Workflow Stages (from BIA Workflow Engine)
 */
enum WizardStep {
  IDENTIFY_PROCESS = 0,      // Step 1: Identify Critical Process
  MAP_DEPENDENCIES = 1,       // Step 2: Map Dependencies
  TIME_OBJECTIVES = 2,        // Step 3: Determine Time Objectives (RTO/RPO/MTPD)
  ASSESS_IMPACT = 3,          // Step 4: Assess Impact
  IDENTIFY_RESOURCES = 4,     // Step 5: Identify Resources
  RECOVERY_STRATEGIES = 5,    // Step 6: Define Recovery Strategies
  REVIEW_DOCUMENT = 6,        // Step 7: Document & Review
}

const WIZARD_STEPS = [
  {
    step: WizardStep.IDENTIFY_PROCESS,
    title: 'Identify Process',
    description: 'Define critical business process',
    icon: FileText,
  },
  {
    step: WizardStep.MAP_DEPENDENCIES,
    title: 'Map Dependencies',
    description: 'Identify process dependencies',
    icon: Network,
  },
  {
    step: WizardStep.TIME_OBJECTIVES,
    title: 'Time Objectives',
    description: 'Set RTO, RPO, MTPD',
    icon: Clock,
  },
  {
    step: WizardStep.ASSESS_IMPACT,
    title: 'Assess Impact',
    description: 'Evaluate business impact',
    icon: TrendingDown,
  },
  {
    step: WizardStep.IDENTIFY_RESOURCES,
    title: 'Identify Resources',
    description: 'Define required resources',
    icon: Users,
  },
  {
    step: WizardStep.RECOVERY_STRATEGIES,
    title: 'Recovery Strategies',
    description: 'Plan recovery approaches',
    icon: Shield,
  },
  {
    step: WizardStep.REVIEW_DOCUMENT,
    title: 'Review & Complete',
    description: 'Finalize BIA documentation',
    icon: BookOpen,
  },
];

export function BIAWorkflowWizard({
  tenant_id,
  onComplete,
  onCancel,
  onSaveDraft,
}: BIAWorkflowWizardProps) {
  const [currentStep, setCurrentStep] = useState<WizardStep>(WizardStep.IDENTIFY_PROCESS);
  const [completedSteps, setCompletedSteps] = useState<Set<WizardStep>>(new Set());

  // Form state
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
    trigger,
  } = useForm<BIAProcessCreateInput>({
    resolver: zodResolver(biaProcessCreateSchema),
    defaultValues: {
      tenant_id,
      criticality: CriticalityLevel.MODERATE,
      rto_hours: 24,
      rpo_hours: 4,
      mtpd_hours: 72,
    },
    mode: 'onChange',
  });

  // Extended state for complex sections
  const [dependencies, setDependencies] = useState<Dependency[]>([]);
  const [impactData, setImpactData] = useState<ImpactData | null>(null);
  const [recoveryStrategies, setRecoveryStrategies] = useState<any[]>([]);
  const [resourceNotes, setResourceNotes] = useState({
    personnel: '',
    facilities: '',
    technology: '',
    information: '',
  });

  // Mutation
  const createMutation = useCreateBIAProcess({
    onSuccess: (data) => {
      onComplete?.(data.id!);
    },
  });

  // Navigation
  const canGoNext = useCallback(() => {
    switch (currentStep) {
      case WizardStep.IDENTIFY_PROCESS:
        return !!watch('name') && !!watch('criticality');
      case WizardStep.MAP_DEPENDENCIES:
        return dependencies.length >= 1; // At least 1 dependency
      case WizardStep.TIME_OBJECTIVES:
        const rto = watch('rto_hours');
        const rpo = watch('rpo_hours');
        const mtpd = watch('mtpd_hours');
        return rto >= rpo && mtpd >= rto;
      case WizardStep.ASSESS_IMPACT:
        return impactData !== null;
      case WizardStep.IDENTIFY_RESOURCES:
        return true; // Optional step
      case WizardStep.RECOVERY_STRATEGIES:
        return recoveryStrategies.length >= 1;
      case WizardStep.REVIEW_DOCUMENT:
        return true;
      default:
        return false;
    }
  }, [currentStep, watch, dependencies, impactData, recoveryStrategies]);

  const handleNext = async () => {
    // Validate current step
    const isValid = await trigger();
    if (!isValid) return;

    if (!canGoNext()) {
      return;
    }

    // Mark current step as completed
    setCompletedSteps((prev) => new Set(prev).add(currentStep));

    // Move to next step
    if (currentStep < WizardStep.REVIEW_DOCUMENT) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > WizardStep.IDENTIFY_PROCESS) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSaveDraft = () => {
    const formData = watch();
    const draftData = {
      ...formData,
      dependencies,
      ...(impactData || {}),
      recovery_strategies: recoveryStrategies,
      personnel_requirements: resourceNotes.personnel ? { notes: resourceNotes.personnel } : undefined,
      facility_requirements: resourceNotes.facilities ? { notes: resourceNotes.facilities } : undefined,
      technology_requirements: resourceNotes.technology ? { notes: resourceNotes.technology } : undefined,
      information_requirements: resourceNotes.information ? { notes: resourceNotes.information } : undefined,
    };
    onSaveDraft?.(draftData);
  };

  const handleComplete = handleSubmit(async (data) => {
    const completeData = {
      ...data,
      dependencies,
      ...(impactData || {}),
      recovery_strategies: recoveryStrategies,
      personnel_requirements: resourceNotes.personnel ? { notes: resourceNotes.personnel } : undefined,
      facility_requirements: resourceNotes.facilities ? { notes: resourceNotes.facilities } : undefined,
      technology_requirements: resourceNotes.technology ? { notes: resourceNotes.technology } : undefined,
      information_requirements: resourceNotes.information ? { notes: resourceNotes.information } : undefined,
    };

    createMutation.mutate(completeData as any);
  });

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">BIA Workflow Wizard</h1>
          <p className="text-gray-600 mt-2">
            Complete the 7-step Business Impact Analysis workflow
          </p>
        </div>

        {/* Progress Stepper */}
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between">
            {WIZARD_STEPS.map((step, index) => {
              const Icon = step.icon;
              const isActive = currentStep === step.step;
              const isCompleted = completedSteps.has(step.step);

              return (
                <div key={step.step} className="flex items-center flex-1">
                  {/* Step Circle */}
                  <div className="flex flex-col items-center">
                    <div
                      className={`
                        w-12 h-12 rounded-full flex items-center justify-center transition-all
                        ${isCompleted ? 'bg-green-500 text-white' : ''}
                        ${isActive && !isCompleted ? 'bg-orange-500 text-white ring-4 ring-orange-200' : ''}
                        ${!isActive && !isCompleted ? 'bg-gray-200 text-gray-500' : ''}
                      `}
                    >
                      {isCompleted ? (
                        <CheckCircle2 className="w-6 h-6" />
                      ) : (
                        <Icon className="w-6 h-6" />
                      )}
                    </div>
                    <div className="text-center mt-2">
                      <p
                        className={`text-xs font-medium ${
                          isActive ? 'text-orange-600' : 'text-gray-600'
                        }`}
                      >
                        Step {index + 1}
                      </p>
                      <p className="text-xs text-gray-500 hidden sm:block">{step.title}</p>
                    </div>
                  </div>

                  {/* Connector Line */}
                  {index < WIZARD_STEPS.length - 1 && (
                    <div
                      className={`flex-1 h-1 mx-2 ${
                        isCompleted ? 'bg-green-500' : 'bg-gray-200'
                      }`}
                    />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white rounded-xl border-2 border-gray-200 p-8 mb-6">
          {/* Step 1: Identify Process */}
          {currentStep === WizardStep.IDENTIFY_PROCESS && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Identify Critical Process
                </h2>
                <p className="text-gray-600">
                  Define the business process for analysis. Provide clear identification and context.
                </p>
              </div>

              {/* Process Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Process Name *
                </label>
                <input
                  {...register('name')}
                  type="text"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  placeholder="e.g., Patient Admission Process"
                />
                {errors.name && (
                  <p className="text-red-600 text-sm mt-1">{errors.name.message}</p>
                )}
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  {...register('description')}
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  placeholder="Describe what this process does, its scope, and why it's critical..."
                />
              </div>

              {/* Department & Owner */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Department
                  </label>
                  <input
                    {...register('department')}
                    type="text"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    placeholder="e.g., Emergency Care"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Process Owner
                  </label>
                  <input
                    {...register('process_owner')}
                    type="text"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    placeholder="e.g., Dr. Smith"
                  />
                </div>
              </div>

              {/* Criticality & Context */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Criticality Level *
                  </label>
                  <select
                    {...register('criticality')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  >
                    <option value={CriticalityLevel.CRITICAL}>Critical</option>
                    <option value={CriticalityLevel.HIGH}>High</option>
                    <option value={CriticalityLevel.MODERATE}>Moderate</option>
                    <option value={CriticalityLevel.MINOR}>Minor</option>
                    <option value={CriticalityLevel.LOW}>Low</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Industry
                  </label>
                  <select
                    {...register('industry')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  >
                    <option value="">Select...</option>
                    <option value={IndustryType.HEALTHCARE}>Healthcare</option>
                    <option value={IndustryType.FINANCIAL}>Financial</option>
                    <option value={IndustryType.MANUFACTURING}>Manufacturing</option>
                    <option value={IndustryType.RETAIL}>Retail</option>
                    <option value={IndustryType.IT}>IT</option>
                    <option value={IndustryType.ENERGY}>Energy</option>
                    <option value={IndustryType.TRANSPORT}>Transport</option>
                    <option value={IndustryType.GOVERNMENT}>Government</option>
                    <option value={IndustryType.EDUCATION}>Education</option>
                    <option value={IndustryType.OTHER}>Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Geographical Scope
                  </label>
                  <select
                    {...register('geographical_scope')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  >
                    <option value="">Select...</option>
                    <option value={GeographicalScope.LOCAL}>Local</option>
                    <option value={GeographicalScope.REGIONAL}>Regional</option>
                    <option value={GeographicalScope.NATIONAL}>National</option>
                    <option value={GeographicalScope.GLOBAL}>Global</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    WHO Tier (Healthcare)
                  </label>
                  <select
                    {...register('who_tier')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  >
                    <option value="">Not applicable</option>
                    <option value={WHOTier.TIER_1}>Tier 1 - Immediate</option>
                    <option value={WHOTier.TIER_2}>Tier 2 - Urgent</option>
                    <option value={WHOTier.TIER_3}>Tier 3 - Important</option>
                    <option value={WHOTier.TIER_4}>Tier 4 - Normal</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Map Dependencies */}
          {currentStep === WizardStep.MAP_DEPENDENCIES && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Map Dependencies</h2>
                <p className="text-gray-600">
                  Identify all dependencies for this process (technology, people, facilities, suppliers).
                </p>
              </div>

              <DependencyMapper
                dependencies={dependencies}
                processName={watch('name') || 'Process'}
                onDependenciesChange={setDependencies}
                onAIDiscovery={() => {
                  // TODO: Integrate AI dependency discovery
                  console.log('AI Dependency Discovery');
                }}
              />

              {dependencies.length === 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-2">
                  <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-yellow-800">No dependencies added yet</strong>
                    <p className="text-yellow-700 text-sm mt-1">
                      Add at least one dependency to continue.
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 3: Time Objectives */}
          {currentStep === WizardStep.TIME_OBJECTIVES && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Time Objectives</h2>
                <p className="text-gray-600">
                  Define Recovery Time Objective (RTO), Recovery Point Objective (RPO), and Maximum Tolerable Period of Disruption (MTPD).
                </p>
              </div>

              {/* Business Rules Alert */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-2">
                <AlertTriangle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-blue-800">
                  <strong>Business Rules:</strong> RTO ≥ RPO, MTPD ≥ RTO
                </div>
              </div>

              <div className="grid grid-cols-3 gap-6">
                {/* RTO */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    RTO (Recovery Time Objective) *
                  </label>
                  <p className="text-xs text-gray-500 mb-2">
                    Maximum acceptable downtime
                  </p>
                  <div className="relative">
                    <input
                      {...register('rto_hours', { valueAsNumber: true })}
                      type="number"
                      step="0.5"
                      min="0"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    />
                    <span className="absolute right-4 top-2 text-gray-500">hours</span>
                  </div>
                  {errors.rto_hours && (
                    <p className="text-red-600 text-sm mt-1">{errors.rto_hours.message}</p>
                  )}
                </div>

                {/* RPO */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    RPO (Recovery Point Objective) *
                  </label>
                  <p className="text-xs text-gray-500 mb-2">
                    Maximum acceptable data loss
                  </p>
                  <div className="relative">
                    <input
                      {...register('rpo_hours', { valueAsNumber: true })}
                      type="number"
                      step="0.5"
                      min="0"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    />
                    <span className="absolute right-4 top-2 text-gray-500">hours</span>
                  </div>
                  {errors.rpo_hours && (
                    <p className="text-red-600 text-sm mt-1">{errors.rpo_hours.message}</p>
                  )}
                </div>

                {/* MTPD */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    MTPD (Maximum Tolerable Period) *
                  </label>
                  <p className="text-xs text-gray-500 mb-2">
                    Time before irreversible damage
                  </p>
                  <div className="relative">
                    <input
                      {...register('mtpd_hours', { valueAsNumber: true })}
                      type="number"
                      step="0.5"
                      min="0"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    />
                    <span className="absolute right-4 top-2 text-gray-500">hours</span>
                  </div>
                  {errors.mtpd_hours && (
                    <p className="text-red-600 text-sm mt-1">{errors.mtpd_hours.message}</p>
                  )}
                </div>
              </div>

              {/* Visual Summary */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-900 mb-3">Time Objectives Summary</h4>
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="text-xs text-gray-600 mb-1">RPO</div>
                    <div className="text-lg font-bold text-gray-900">{watch('rpo_hours') || 0}h</div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                  <div className="flex-1">
                    <div className="text-xs text-gray-600 mb-1">RTO</div>
                    <div className="text-lg font-bold text-orange-600">{watch('rto_hours') || 0}h</div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                  <div className="flex-1">
                    <div className="text-xs text-gray-600 mb-1">MTPD</div>
                    <div className="text-lg font-bold text-red-600">{watch('mtpd_hours') || 0}h</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Assess Impact */}
          {currentStep === WizardStep.ASSESS_IMPACT && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Assess Impact</h2>
                <p className="text-gray-600">
                  Evaluate the impact of process disruption across multiple dimensions.
                </p>
              </div>

              <ImpactAssessmentForm
                initialData={impactData as any}
                onComplete={(data) => {
                  setImpactData(data);
                  console.log('Impact data updated:', data);
                }}
                onAICalculate={() => {
                  // TODO: Integrate AI impact calculation
                  console.log('AI Impact Calculation');
                }}
              />

              {!impactData && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-2">
                  <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-yellow-800">Impact assessment incomplete</strong>
                    <p className="text-yellow-700 text-sm mt-1">
                      Complete the impact assessment to continue.
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 5: Identify Resources */}
          {currentStep === WizardStep.IDENTIFY_RESOURCES && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Identify Resources</h2>
                <p className="text-gray-600">
                  Define resources required for this process to operate.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Personnel */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    👥 Personnel Requirements
                  </label>
                  <textarea
                    value={resourceNotes.personnel}
                    onChange={(e) => setResourceNotes({ ...resourceNotes, personnel: e.target.value })}
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    placeholder="Staff roles, skills, count..."
                  />
                </div>

                {/* Facilities */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    🏢 Facility Requirements
                  </label>
                  <textarea
                    value={resourceNotes.facilities}
                    onChange={(e) => setResourceNotes({ ...resourceNotes, facilities: e.target.value })}
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    placeholder="Office space, equipment, utilities..."
                  />
                </div>

                {/* Technology */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    💻 Technology Requirements
                  </label>
                  <textarea
                    value={resourceNotes.technology}
                    onChange={(e) => setResourceNotes({ ...resourceNotes, technology: e.target.value })}
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    placeholder="Systems, software, hardware..."
                  />
                </div>

                {/* Information */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    📄 Information Requirements
                  </label>
                  <textarea
                    value={resourceNotes.information}
                    onChange={(e) => setResourceNotes({ ...resourceNotes, information: e.target.value })}
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    placeholder="Data, documents, records..."
                  />
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-blue-800 text-sm">
                  💡 <strong>Tip:</strong> Resource identification is optional but recommended for comprehensive BIA documentation.
                </p>
              </div>
            </div>
          )}

          {/* Step 6: Recovery Strategies */}
          {currentStep === WizardStep.RECOVERY_STRATEGIES && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Recovery Strategies</h2>
                <p className="text-gray-600">
                  Define strategies to recover this process within the target RTO.
                </p>
              </div>

              <RecoveryStrategiesBuilder
                strategies={recoveryStrategies}
                processRTO={watch('rto_hours') || 24}
                onStrategiesChange={setRecoveryStrategies}
                onAISuggest={() => {
                  // TODO: Integrate AI strategy suggestions
                  console.log('AI Strategy Suggestions');
                }}
              />

              {recoveryStrategies.length === 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-2">
                  <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-yellow-800">No recovery strategies defined</strong>
                    <p className="text-yellow-700 text-sm mt-1">
                      Add at least one recovery strategy to continue.
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 7: Review & Document */}
          {currentStep === WizardStep.REVIEW_DOCUMENT && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Review & Complete</h2>
                <p className="text-gray-600">
                  Review your BIA documentation and finalize the assessment.
                </p>
              </div>

              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Process Info */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Process Information</h4>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-gray-600">Name:</span>
                      <span className="ml-2 font-medium">{watch('name') || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Department:</span>
                      <span className="ml-2 font-medium">{watch('department') || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Owner:</span>
                      <span className="ml-2 font-medium">{watch('process_owner') || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Criticality:</span>
                      <span className="ml-2 font-medium">{watch('criticality')}</span>
                    </div>
                  </div>
                </div>

                {/* Dependencies */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Dependencies</h4>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-gray-600">Total:</span>
                      <span className="ml-2 font-medium">{dependencies.length}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Required:</span>
                      <span className="ml-2 font-medium">
                        {dependencies.filter(d => d.required).length}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Time Objectives */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Time Objectives</h4>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-gray-600">RTO:</span>
                      <span className="ml-2 font-medium">{watch('rto_hours')}h</span>
                    </div>
                    <div>
                      <span className="text-gray-600">RPO:</span>
                      <span className="ml-2 font-medium">{watch('rpo_hours')}h</span>
                    </div>
                    <div>
                      <span className="text-gray-600">MTPD:</span>
                      <span className="ml-2 font-medium">{watch('mtpd_hours')}h</span>
                    </div>
                  </div>
                </div>

                {/* Impact Assessment */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Impact Assessment</h4>
                  <div className="text-sm">
                    {impactData ? (
                      <CheckCircle2 className="w-5 h-5 text-green-600" />
                    ) : (
                      <Circle className="w-5 h-5 text-gray-400" />
                    )}
                    <span className="ml-2">
                      {impactData ? 'Completed' : 'Not completed'}
                    </span>
                  </div>
                </div>

                {/* Resources */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Resources</h4>
                  <div className="text-sm">
                    <div>
                      <span className="text-gray-600">Documented:</span>
                      <span className="ml-2 font-medium">
                        {Object.values(resourceNotes).filter(n => n.length > 0).length}/4
                      </span>
                    </div>
                  </div>
                </div>

                {/* Recovery Strategies */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Recovery Strategies</h4>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-gray-600">Total:</span>
                      <span className="ml-2 font-medium">{recoveryStrategies.length}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Meets RTO:</span>
                      <span className="ml-2 font-medium">
                        {recoveryStrategies.some(s => s.rto_capability_hours <= (watch('rto_hours') || 24)) ? 'Yes' : 'No'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Completion Checklist */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-semibold text-blue-900 mb-3">Completion Checklist</h4>
                <div className="space-y-2">
                  {[
                    { label: 'Process identified', completed: !!watch('name') },
                    { label: 'Dependencies mapped', completed: dependencies.length >= 1 },
                    { label: 'Time objectives set', completed: !!watch('rto_hours') },
                    { label: 'Impact assessed', completed: !!impactData },
                    { label: 'Recovery strategies defined', completed: recoveryStrategies.length >= 1 },
                  ].map((item, i) => (
                    <div key={i} className="flex items-center gap-2">
                      {item.completed ? (
                        <CheckCircle2 className="w-5 h-5 text-green-600" />
                      ) : (
                        <Circle className="w-5 h-5 text-gray-400" />
                      )}
                      <span className={item.completed ? 'text-green-800' : 'text-gray-600'}>
                        {item.label}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Error Display */}
              {createMutation.error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
                  <strong>Error:</strong> {createMutation.error.message}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Navigation Footer */}
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center justify-between">
            {/* Back Button */}
            <button
              onClick={handleBack}
              disabled={currentStep === WizardStep.IDENTIFY_PROCESS}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <ChevronLeft className="w-4 h-4" />
              Back
            </button>

            {/* Save Draft */}
            <button
              onClick={handleSaveDraft}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save Draft
            </button>

            {/* Next / Complete Button */}
            {currentStep < WizardStep.REVIEW_DOCUMENT ? (
              <button
                onClick={handleNext}
                disabled={!canGoNext()}
                className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleComplete}
                disabled={createMutation.isPending || !canGoNext()}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {createMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
                Complete BIA
                <CheckCircle2 className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Cancel */}
          {onCancel && (
            <div className="mt-4 text-center">
              <button
                onClick={onCancel}
                className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                Cancel Wizard
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
