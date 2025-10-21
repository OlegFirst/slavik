/**
 * Supabase Database Types
 * Auto-generated types for Supabase tables
 *
 * Run `npx supabase gen types typescript` to regenerate
 */

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      // User Profiles
      user_profiles: {
        Row: {
          id: string
          email: string
          name: string
          avatar: string | null
          role: string
          organization_id: string | null
          bio: string | null
          created_at: string
          last_login: string | null
        }
        Insert: {
          id: string
          email: string
          name: string
          avatar?: string | null
          role: string
          organization_id?: string | null
          bio?: string | null
          created_at?: string
          last_login?: string | null
        }
        Update: {
          id?: string
          email?: string
          name?: string
          avatar?: string | null
          role?: string
          organization_id?: string | null
          bio?: string | null
          last_login?: string | null
        }
      }

      // Organizations
      organizations: {
        Row: {
          id: string
          name: string
          industry: string
          size: string
          subscription_tier: string
          created_at: string
        }
        Insert: {
          id?: string
          name: string
          industry: string
          size: string
          subscription_tier: string
          created_at?: string
        }
        Update: {
          name?: string
          industry?: string
          size?: string
          subscription_tier?: string
        }
      }

      // User Organizations (many-to-many)
      user_organizations: {
        Row: {
          user_id: string
          org_id: string
          role_in_org: string
          created_at: string
        }
        Insert: {
          user_id: string
          org_id: string
          role_in_org: string
          created_at?: string
        }
        Update: {
          role_in_org?: string
        }
      }

      // Gap Analysis Results (Journey 1)
      gap_analysis: {
        Row: {
          id: string
          organization_id: string
          standard: string
          overall_score: number
          compliance_percentage: number
          identified_gaps: Json
          recommendations: Json
          timeline_weeks: number
          estimated_cost: number
          created_at: string
        }
        Insert: {
          id?: string
          organization_id: string
          standard: string
          overall_score: number
          compliance_percentage: number
          identified_gaps: Json
          recommendations: Json
          timeline_weeks: number
          estimated_cost: number
          created_at?: string
        }
        Update: {
          overall_score?: number
          compliance_percentage?: number
          identified_gaps?: Json
          recommendations?: Json
        }
      }

      // Certification Roadmaps (Journey 1)
      certification_roadmaps: {
        Row: {
          id: string
          analysis_id: string
          organization_id: string
          current_score: number
          target_score: number
          timeline_weeks: number
          estimated_cost: number
          phases: Json
          created_at: string
        }
        Insert: {
          id?: string
          analysis_id: string
          organization_id: string
          current_score: number
          target_score: number
          timeline_weeks: number
          estimated_cost: number
          phases: Json
          created_at?: string
        }
        Update: {
          current_score?: number
          phases?: Json
        }
      }

      // Auditor Profiles (Journey 2)
      auditor_profiles: {
        Row: {
          id: string
          user_id: string
          bio: string
          certifications: string[]
          experience_years: number
          industry_experience: string[]
          rating: number
          reviews_count: number
          completed_audits: number
          pricing: Json
          availability: Json
          services_offered: string[]
          portfolio: Json
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          bio: string
          certifications: string[]
          experience_years: number
          industry_experience: string[]
          rating?: number
          reviews_count?: number
          completed_audits?: number
          pricing: Json
          availability: Json
          services_offered: string[]
          portfolio?: Json
          created_at?: string
        }
        Update: {
          bio?: string
          certifications?: string[]
          experience_years?: number
          industry_experience?: string[]
          rating?: number
          reviews_count?: number
          completed_audits?: number
          pricing?: Json
          availability?: Json
        }
      }

      // Service Requests (Marketplace)
      service_requests: {
        Row: {
          id: string
          client_id: string
          auditor_id: string
          service_type: string
          status: string
          description: string
          requested_date: string
          scheduled_date: string | null
          duration_hours: number | null
          price: number
          payment_status: string
          created_at: string
        }
        Insert: {
          id?: string
          client_id: string
          auditor_id: string
          service_type: string
          status?: string
          description: string
          requested_date: string
          scheduled_date?: string | null
          duration_hours?: number | null
          price: number
          payment_status?: string
          created_at?: string
        }
        Update: {
          status?: string
          scheduled_date?: string | null
          price?: number
          payment_status?: string
        }
      }

      // Reviews (Marketplace)
      reviews: {
        Row: {
          id: string
          request_id: string
          reviewer_id: string
          auditor_id: string
          rating: number
          comment: string
          categories: Json
          created_at: string
        }
        Insert: {
          id?: string
          request_id: string
          reviewer_id: string
          auditor_id: string
          rating: number
          comment: string
          categories: Json
          created_at?: string
        }
        Update: {
          rating?: number
          comment?: string
          categories?: Json
        }
      }

      // Courses (Journey 3)
      courses: {
        Row: {
          id: string
          title: string
          description: string
          category: string
          level: string
          duration_hours: number
          format: string
          certification: boolean
          auditor_approved: boolean
          price: number
          modules: Json
          instructor_id: string | null
          rating: number
          enrolled_count: number
          completion_rate: number
          created_at: string
        }
        Insert: {
          id?: string
          title: string
          description: string
          category: string
          level: string
          duration_hours: number
          format: string
          certification: boolean
          auditor_approved: boolean
          price: number
          modules: Json
          instructor_id?: string | null
          rating?: number
          enrolled_count?: number
          completion_rate?: number
          created_at?: string
        }
        Update: {
          title?: string
          description?: string
          price?: number
          modules?: Json
          rating?: number
          enrolled_count?: number
          completion_rate?: number
        }
      }

      // Learning Progress (Journey 3)
      learning_progress: {
        Row: {
          user_id: string
          courses_enrolled: string[]
          courses_completed: string[]
          total_hours: number
          certificates_earned: Json
          current_streak_days: number
          gamification: Json
          updated_at: string
        }
        Insert: {
          user_id: string
          courses_enrolled?: string[]
          courses_completed?: string[]
          total_hours?: number
          certificates_earned?: Json
          current_streak_days?: number
          gamification?: Json
          updated_at?: string
        }
        Update: {
          courses_enrolled?: string[]
          courses_completed?: string[]
          total_hours?: number
          certificates_earned?: Json
          current_streak_days?: number
          gamification?: Json
          updated_at?: string
        }
      }

      // Case Studies (Journey 3)
      case_studies: {
        Row: {
          id: string
          title: string
          industry: string
          incident_type: string
          severity: string
          description: string
          timeline: Json
          outcomes: string[]
          lessons_learned: string[]
          discussion_points: string[]
          is_anonymized: boolean
          created_at: string
        }
        Insert: {
          id?: string
          title: string
          industry: string
          incident_type: string
          severity: string
          description: string
          timeline: Json
          outcomes: string[]
          lessons_learned: string[]
          discussion_points: string[]
          is_anonymized?: boolean
          created_at?: string
        }
        Update: {
          title?: string
          description?: string
          timeline?: Json
        }
      }

      // Digital Twins (Journey 5)
      digital_twins: {
        Row: {
          id: string
          organization_id: string
          name: string
          description: string
          components: Json
          metadata: Json
          created_at: string
          last_updated: string
        }
        Insert: {
          id?: string
          organization_id: string
          name: string
          description: string
          components: Json
          metadata: Json
          created_at?: string
          last_updated?: string
        }
        Update: {
          name?: string
          description?: string
          components?: Json
          metadata?: Json
          last_updated?: string
        }
      }

      // Scenarios (Journey 5)
      scenarios: {
        Row: {
          id: string
          name: string
          category: string
          description: string
          severity: string
          initial_conditions: Json
          parameters: Json
          is_template: boolean
          created_by: string
          created_at: string
        }
        Insert: {
          id?: string
          name: string
          category: string
          description: string
          severity: string
          initial_conditions: Json
          parameters: Json
          is_template?: boolean
          created_by: string
          created_at?: string
        }
        Update: {
          name?: string
          description?: string
          initial_conditions?: Json
          parameters?: Json
        }
      }

      // Simulation Results (Journey 5)
      simulation_results: {
        Row: {
          id: string
          scenario_id: string
          twin_id: string
          executed_at: string
          duration_seconds: number
          impact_analysis: Json
          recommendations: Json
          timeline: Json
        }
        Insert: {
          id?: string
          scenario_id: string
          twin_id: string
          executed_at: string
          duration_seconds: number
          impact_analysis: Json
          recommendations: Json
          timeline: Json
        }
        Update: {
          impact_analysis?: Json
          recommendations?: Json
        }
      }

      // Incidents (Journey 6)
      incidents: {
        Row: {
          id: string
          organization_id: string
          type: string
          severity: string
          status: string
          title: string
          description: string
          activated_at: string
          resolved_at: string | null
          crisis_team: Json
          timeline: Json
          recovery_plan_id: string | null
        }
        Insert: {
          id?: string
          organization_id: string
          type: string
          severity: string
          status?: string
          title: string
          description: string
          activated_at: string
          resolved_at?: string | null
          crisis_team: Json
          timeline: Json
          recovery_plan_id?: string | null
        }
        Update: {
          status?: string
          severity?: string
          resolved_at?: string | null
          timeline?: Json
        }
      }

      // Recovery Plans (Journey 6)
      recovery_plans: {
        Row: {
          id: string
          incident_id: string
          generated_by: string
          generated_at: string
          similar_cases: string[]
          phases: Json
          budget_projection: Json
          forecasts: Json
        }
        Insert: {
          id?: string
          incident_id: string
          generated_by: string
          generated_at: string
          similar_cases: string[]
          phases: Json
          budget_projection: Json
          forecasts: Json
        }
        Update: {
          phases?: Json
          budget_projection?: Json
          forecasts?: Json
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
}
