// User types
export interface User {
  id: string;
  email: string;
  name: string;
  subscription_tier: 'basic' | 'pro' | 'expert' | 'career_keeper';
  created_at: string;
  profile_completed: boolean;
  target_role?: string;
  target_industry?: string;
  experience_level?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

// Resume types
export interface Resume {
  id: string;
  name: string;
  file_type: string;
  file_size: number;
  is_master: boolean;
  parse_status: string;
  created_at: string;
  updated_at: string;
  ats_score?: ATSScore;
}

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
  name: string;
  email?: string;
  phone?: string;
  company_name?: string;
  title?: string;
  linkedin_url?: string;
  stage: string;
  priority_score: number;
  messages_sent: number;
  messages_opened: number;
  responses: number;
  last_contact?: string;
  next_action?: string;
  next_action_date?: string;
  created_at: string;
  updated_at: string;
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
