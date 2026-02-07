// User types
export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  full_name: string;
  subscription_tier: 'basic' | 'pro' | 'expert' | 'career_keeper';
  created_at: string;
  // Career info
  years_experience?: number;
  career_stage?: string;
  current_role?: string;
  target_roles?: string[];
  target_industries?: string[];
  // Onboarding
  onboarding_completed: boolean;
  onboarding_step?: number;
  // Tour tracking
  tour_completed?: boolean;
  completed_tours?: string[];
}

// Onboarding types
export interface OnboardingData {
  search_status?: string;
  years_experience?: number;
  career_stage?: string;
  current_role?: string;
  target_roles?: string[];
  target_industries?: string[];
}

export interface ProfileUpdateData {
  first_name?: string;
  last_name?: string;
  phone?: string;
  location?: string;
  linkedin_url?: string;
  years_experience?: number;
  career_stage?: string;
  current_role?: string;
  target_roles?: string[];
  target_industries?: string[];
  onboarding_step?: number;
  onboarding_completed?: boolean;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

// Resume types
export interface Resume {
  id: string;
  title: string;
  file_name: string;
  file_type: string;
  file_size: number;
  word_count?: number;
  is_master: boolean;
  is_tailored?: boolean;
  target_job_title?: string;
  parse_status: string;
  ats_total_score?: number;
  analyzed_at?: string;
  created_at: string;
  updated_at: string;
  // Extended fields (when include_analysis=true)
  ats_breakdown?: ATSBreakdown;
  recommendations?: string[];
  missing_keywords?: string[];
  weak_sections?: string[];
}

export interface ATSBreakdown {
  total: number;
  components: {
    compatibility: { score: number; weight: number };
    keywords: { score: number; weight: number };
    achievements: { score: number; weight: number };
    formatting: { score: number; weight: number };
    progression: { score: number; weight: number };
    completeness: { score: number; weight: number };
    fit: { score: number; weight: number };
  };
}

// Legacy ATSScore interface for backwards compatibility
export interface ATSScore {
  overall_score: number;
  keyword_score: number;
  format_score: number;
  section_score: number;
  experience_score: number;
  education_score: number;
  skills_score: number;
  ats_compatibility_score: number;
}

// Recruiter types
export interface Recruiter {
  id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email?: string;
  phone?: string;
  company?: string;
  title?: string;
  linkedin_url?: string;
  status: string;
  priority_score: number;
  messages_sent: number;
  messages_opened?: number;
  responses_received: number;
  has_responded: boolean;
  engagement_score: number;
  fit_score: number;
  response_rate: number;
  days_since_contact: number;
  needs_follow_up: boolean;
  last_contact_date?: string;
  next_action?: string;
  next_action_date?: string;
  source?: string;
  specialty?: string;
  industries?: string[];
  locations?: string[];
  tags?: string[];
  created_at: string;
  updated_at: string;
  // Convenience alias for backwards compatibility with frontend components
  name?: string;
  company_name?: string;
  stage?: string;
  responses?: number;
  last_contact?: string;
}

export interface RecruiterNote {
  id: string;
  content: string;
  created_at: string;
}

// Message types
export interface Message {
  id: string;
  recruiter_id: string;
  subject?: string;
  body: string;
  message_type: 'initial_outreach' | 'follow_up' | 'thank_you' | 'check_in';
  status: 'draft' | 'ready' | 'sent' | 'opened' | 'responded';
  quality_score?: number;
  created_at: string;
  updated_at: string;
}

export interface MessageQualityScore {
  overall_score: number;
  word_count_score: number;
  personalization_score: number;
  metrics_score: number;
  cta_score: number;
  tone_score: number;
  suggestions: string[];
}

// Activity types
export interface Activity {
  id: string;
  activity_type: string;
  description?: string;
  recruiter_id?: string;
  resume_id?: string;
  message_id?: string;
  created_at: string;
}

export interface PipelineItem {
  id: string;
  stage: string;
  position: number;
  recruiter?: Recruiter;
  last_activity?: string;
  days_in_stage: number;
  is_urgent: boolean;
}

// Dashboard types
export interface DashboardData {
  career_readiness: CareerReadiness;
  pipeline_summary: PipelineSummary;
  recent_activities: Activity[];
  usage_stats: UsageStats;
  follow_up_recommendations: FollowUpRecommendation[];
}

export interface CareerReadiness {
  overall_score: number;
  profile_completeness: number;
  resume_score: number;
  networking_score: number;
  application_activity: number;
}

export interface PipelineSummary {
  total: number;
  by_stage: Record<string, number>;
  response_rate: number;
  avg_days_to_response: number;
}

export interface UsageStats {
  messages_sent_this_week: number;
  resumes_tailored_this_month: number;
  ai_coaching_sessions: number;
  tier_limits: {
    messages: { used: number; limit: number };
    resumes: { used: number; limit: number };
    coaching: { used: number; limit: number };
  };
}

export interface FollowUpRecommendation {
  recruiter_id: string;
  recruiter_name: string;
  company: string;
  reason: string;
  priority: 'high' | 'medium' | 'low';
  suggested_action: string;
}

// Labor Market types
export interface OccupationResult {
  id: string;
  title: string;
  description?: string;
  job_zone?: number;
  bright_outlook?: boolean;
  green?: boolean;
  shortage_score?: number;
  demand_level?: string;
}

export interface SkillResult {
  id: string;
  name: string;
  category: 'skills' | 'abilities' | 'knowledge';
  description?: string;
}

export interface SkillsMapData {
  skills: string[];
  abilities: string[];
  knowledge: string[];
  total_matched: number;
  coverage_by_category: {
    [key: string]: {
      matched: number;
      total: number;
      pct: number;
    };
  };
}

export interface SkillsGapData {
  role: string;
  occupation_title: string;
  categories: {
    [key: string]: {
      matched: number;
      total: number;
      pct: number;
      matched_items: string[];
      missing_items: string[];
    };
  };
  overall: {
    matched: number;
    total: number;
    pct: number;
  };
}

export interface OpportunityData {
  total_score: number;
  interpretation: string;
  components: {
    user_match: number;
    shortage: number;
  };
  target_role: string;
  matching_skills: string[];
  missing_skills: string[];
  recommendations: string[];
}

// Form types
export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
  name: string;
}

// API Response types
export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
}
