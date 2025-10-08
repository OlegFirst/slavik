'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useScenarios, useAIScenarioGeneration, useOrganizations } from '@/lib/api/queries';
import { AdvancedAIRequest, ScenarioTemplate } from '@/lib/api/types';
import { Sparkles, Loader2, Plus, Brain, Calendar, Target } from 'lucide-react';

export default function ScenariosPage() {
  const [showAIForm, setShowAIForm] = useState(false);
  const [generatedScenario, setGeneratedScenario] = useState<ScenarioTemplate | null>(null);

  const { data: scenarios, isLoading: scenariosLoading } = useScenarios();
  const { data: organizations } = useOrganizations();
  const { mutate: generateAI, isPending: isGenerating } = useAIScenarioGeneration();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<AdvancedAIRequest>({
    defaultValues: {
      base_category: 'cyber',
      difficulty: 'intermediate',
      duration_minutes: 120,
      include_historical_context: true,
      complexity_level: 5,
      focus_areas: [],
    },
  });

  const onSubmit = (data: AdvancedAIRequest) => {
    // Convert comma-separated focus areas to array
    const focusAreasInput = (document.getElementById('focus_areas') as HTMLInputElement).value;
    const focus_areas = focusAreasInput.split(',').map(s => s.trim()).filter(Boolean);

    generateAI(
      { ...data, focus_areas },
      {
        onSuccess: (scenario) => {
          setGeneratedScenario(scenario);
          setShowAIForm(false);
        },
      }
    );
  };

  const complexityLevel = watch('complexity_level');

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Scenario Templates</h1>
          <p className="text-gray-600 mt-1">AI-powered BCM exercise scenarios</p>
        </div>
        <button
          onClick={() => setShowAIForm(!showAIForm)}
          className="flex items-center gap-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all font-medium"
        >
          <Sparkles size={20} />
          <span>Generate AI Scenario</span>
        </button>
      </div>

      {/* AI Generation Form */}
      {showAIForm && (
        <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg shadow-lg border-2 border-purple-200">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-6">
              <Brain className="text-purple-600" size={32} />
              <div>
                <h2 className="text-2xl font-bold text-gray-900">AI Scenario Generator</h2>
                <p className="text-gray-600">Let AI create a sophisticated BCM exercise scenario</p>
              </div>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Organization */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Organization *
                </label>
                <select
                  {...register('organization_id', { required: true })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="">Select organization</option>
                  {organizations?.map((org) => (
                    <option key={org.id} value={org.id}>
                      {org.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Category & Difficulty */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category *
                  </label>
                  <select
                    {...register('base_category', { required: true })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="cyber">Cyber Attack</option>
                    <option value="natural_disaster">Natural Disaster</option>
                    <option value="pandemic">Pandemic</option>
                    <option value="supply_chain">Supply Chain</option>
                    <option value="technology_failure">Technology Failure</option>
                    <option value="human_error">Human Error</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Difficulty *
                  </label>
                  <select
                    {...register('difficulty', { required: true })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                    <option value="expert">Expert</option>
                  </select>
                </div>
              </div>

              {/* Focus Areas */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Focus Areas
                </label>
                <input
                  id="focus_areas"
                  type="text"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="e.g., ransomware, phishing, incident response (comma-separated)"
                />
                <p className="text-xs text-gray-500 mt-1">Enter keywords separated by commas</p>
              </div>

              {/* Duration */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Duration (minutes)
                </label>
                <input
                  type="number"
                  step="30"
                  {...register('duration_minutes', { required: true, valueAsNumber: true, min: 30, max: 480 })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="120"
                />
              </div>

              {/* Complexity Slider */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Complexity Level: {complexityLevel}/10
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  {...register('complexity_level', { valueAsNumber: true })}
                  className="w-full h-2 bg-purple-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Simple</span>
                  <span>Extremely Complex</span>
                </div>
              </div>

              {/* Historical Context */}
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="historical_context"
                  {...register('include_historical_context')}
                  className="w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-500"
                />
                <label htmlFor="historical_context" className="text-sm font-medium text-gray-700">
                  Use Historical Context (AI will learn from past exercises)
                </label>
              </div>

              {/* Submit */}
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={isGenerating}
                  className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 px-6 rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed font-medium transition-all flex items-center justify-center gap-2"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="animate-spin" size={20} />
                      <span>Generating Scenario...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles size={20} />
                      <span>Generate AI Scenario</span>
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => setShowAIForm(false)}
                  className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Generated Scenario */}
      {generatedScenario && (
        <div className="bg-white rounded-lg shadow-lg border-2 border-purple-200">
          <div className="p-6">
            <div className="flex items-start justify-between mb-6">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h2 className="text-2xl font-bold text-gray-900">{generatedScenario.name}</h2>
                  <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium flex items-center gap-1">
                    <Sparkles size={14} />
                    AI Generated
                  </span>
                </div>
                {generatedScenario.metadata?.confidence_score && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <span>Confidence:</span>
                    <div className="flex-1 max-w-xs h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-purple-600 rounded-full"
                        style={{ width: `${generatedScenario.metadata.confidence_score * 100}%` }}
                      />
                    </div>
                    <span className="font-medium">
                      {(generatedScenario.metadata.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
              </div>
              <div className="flex gap-2">
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Save
                </button>
                <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                  Edit
                </button>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <Target className="text-gray-600" size={16} />
                  <p className="text-sm text-gray-600">Category</p>
                </div>
                <p className="font-semibold capitalize">{generatedScenario.category.replace('_', ' ')}</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <Calendar className="text-gray-600" size={16} />
                  <p className="text-sm text-gray-600">Duration</p>
                </div>
                <p className="font-semibold">{generatedScenario.estimated_duration_minutes} minutes</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Difficulty</p>
                <p className="font-semibold capitalize">{generatedScenario.difficulty}</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-2">
                  Description
                </h3>
                <p className="text-gray-700 leading-relaxed">{generatedScenario.description}</p>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-2">
                  Objectives ({generatedScenario.objectives.length})
                </h3>
                <ul className="space-y-2">
                  {generatedScenario.objectives.map((obj, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-blue-600 font-bold mt-0.5">✓</span>
                      <span className="text-gray-700">{obj}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-2">
                  Injects ({generatedScenario.injects.length})
                </h3>
                <div className="space-y-3">
                  {generatedScenario.injects.slice(0, 5).map((inject, i) => (
                    <div key={inject.id} className="p-4 bg-gray-50 rounded-lg border-l-4 border-blue-500">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-medium text-gray-500">
                            T+{inject.time_offset_minutes}m
                          </span>
                          <h4 className="font-semibold text-gray-900">{inject.title}</h4>
                        </div>
                        <span
                          className={`px-2 py-1 rounded text-xs font-medium ${
                            inject.severity === 'critical'
                              ? 'bg-red-100 text-red-800'
                              : inject.severity === 'high'
                              ? 'bg-orange-100 text-orange-800'
                              : inject.severity === 'medium'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-green-100 text-green-800'
                          }`}
                        >
                          {inject.severity}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700">{inject.description}</p>
                    </div>
                  ))}
                  {generatedScenario.injects.length > 5 && (
                    <p className="text-sm text-gray-500 text-center">
                      + {generatedScenario.injects.length - 5} more injects
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Existing Scenarios List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Existing Scenarios</h2>
          {scenariosLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin text-blue-600" size={32} />
            </div>
          ) : scenarios && scenarios.length > 0 ? (
            <div className="grid gap-4">
              {scenarios.map((scenario) => (
                <div key={scenario.id} className="p-4 border rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all cursor-pointer">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-gray-900">{scenario.name}</h3>
                        {scenario.ai_generated && (
                          <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs font-medium flex items-center gap-1">
                            <Sparkles size={12} />
                            AI
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{scenario.description}</p>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span className="capitalize">{scenario.category.replace('_', ' ')}</span>
                        <span>•</span>
                        <span className="capitalize">{scenario.difficulty}</span>
                        <span>•</span>
                        <span>{scenario.estimated_duration_minutes} min</span>
                        <span>•</span>
                        <span>{scenario.injects.length} injects</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-600 mb-4">No scenarios yet. Generate your first AI scenario!</p>
              <button
                onClick={() => setShowAIForm(true)}
                className="inline-flex items-center gap-2 bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors"
              >
                <Sparkles size={20} />
                <span>Generate AI Scenario</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
