import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token and handle FormData
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // For FormData, let the browser set the Content-Type with proper boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // If 401 and we haven't retried yet, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
            headers: { Authorization: `Bearer ${refreshToken}` },
          });

          const { access_token } = response.data.data;
          localStorage.setItem('access_token', access_token);

          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return api(originalRequest);
        }
      } catch (_refreshError) {
        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  register: (data: { email: string; password: string; name: string }) => {
    // Split name into first_name and last_name for backend compatibility
    const nameParts = data.name.trim().split(/\s+/);
    const first_name = nameParts[0] || '';
    const last_name = nameParts.slice(1).join(' ') || '';
    return api.post('/auth/register', {
      email: data.email,
      password: data.password,
      first_name,
      last_name,
    });
  },

  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),

  logout: () => api.post('/auth/logout'),

  getMe: () => api.get('/auth/me'),

  changePassword: (data: { current_password: string; new_password: string }) =>
    api.put('/auth/password', data),

  forgotPassword: (email: string) =>
    api.post('/auth/forgot-password', { email }),

  resetPassword: (data: { token: string; password: string }) =>
    api.post('/auth/reset-password', data),

  updateProfile: (data: Record<string, unknown>) =>
    api.put('/auth/profile', data),
};

// Dashboard API
export const dashboardApi = {
  getDashboard: () => api.get('/dashboard'),
  getReadiness: () => api.get('/dashboard/readiness'),
  getWeeklyStats: () => api.get('/dashboard/stats/weekly'),
};

// Resume API
export const resumeApi = {
  list: () => api.get('/resumes'),
  get: (id: string) => api.get(`/resumes/${id}`),
  upload: (formData: FormData) =>
    api.post('/resumes', formData),
  delete: (id: string) => api.delete(`/resumes/${id}`),
  getMaster: () => api.get('/resumes/master'),
  setMaster: (id: string) => api.put(`/resumes/${id}/master`),
  score: (id: string, jobKeywords?: string[], targetRole?: string) =>
    api.post(`/resumes/${id}/score`, { job_keywords: jobKeywords, target_role: targetRole }),
  tailor: (id: string, targetJobTitle: string, targetCompany?: string, optimizedText?: string) =>
    api.post(`/resumes/${id}/tailor`, {
      target_job_title: targetJobTitle,
      target_company: targetCompany,
      optimized_text: optimizedText
    }),
  getSuggestions: (id: string) => api.get(`/resumes/${id}/suggestions`),
  getAnalysis: (id: string) => api.get(`/resumes/${id}/analysis`),
};

// Recruiter API
export const recruiterApi = {
  list: (params?: { status?: string; sort_by?: string; limit?: number }) =>
    api.get('/recruiters', { params }),
  get: (id: string) => api.get(`/recruiters/${id}`),
  create: (data: Record<string, unknown>) => api.post('/recruiters', data),
  update: (id: string, data: Record<string, unknown>) => api.put(`/recruiters/${id}`, data),
  delete: (id: string) => api.delete(`/recruiters/${id}`),
  getStats: () => api.get('/recruiters/stats'),
  getStages: () => api.get('/recruiters/stages'),
  getRecommendations: () => api.get('/recruiters/recommendations'),
  updateStage: (id: string, stage: string) => api.put(`/recruiters/${id}/stage`, { stage }),
  getNotes: (id: string) => api.get(`/recruiters/${id}/notes`),
  addNote: (id: string, content: string) => api.post(`/recruiters/${id}/notes`, { content }),
};

// Message API
export const messageApi = {
  list: (params?: { recruiter_id?: string; status?: string }) =>
    api.get('/messages', { params }),
  get: (id: string) => api.get(`/messages/${id}`),
  create: (data: Record<string, unknown>) => api.post('/messages', data),
  update: (id: string, data: Record<string, unknown>) => api.put(`/messages/${id}`, data),
  delete: (id: string) => api.delete(`/messages/${id}`),
  getStats: () => api.get('/messages/stats'),
  getTips: (messageType: string) => api.get(`/messages/tips/${messageType}`),
  validate: (data: { body: string; message_type?: string }) =>
    api.post('/messages/validate', data),
  getContext: (data: { recruiter_id: string; message_type: string }) =>
    api.post('/messages/context', data),
  markSent: (id: string) => api.post(`/messages/${id}/send`),
  getScore: (id: string) => api.get(`/messages/${id}/score`),
};

// Activity API
export const activityApi = {
  list: (params?: { limit?: number; activity_type?: string; recruiter_id?: string }) =>
    api.get('/activities', { params }),
  log: (data: Record<string, unknown>) => api.post('/activities', data),
  getRecent: (limit?: number) => api.get('/activities/recent', { params: { limit } }),
  getCounts: () => api.get('/activities/counts'),
  getTimeline: (days?: number) => api.get('/activities/timeline', { params: { days } }),
  getWeeklySummary: () => api.get('/activities/weekly-summary'),
  getPipeline: () => api.get('/activities/pipeline'),
  getPipelineStats: () => api.get('/activities/pipeline/stats'),
  movePipelineItem: (id: string, stage: string, position?: number) =>
    api.put(`/activities/pipeline/${id}/move`, { stage, position }),
};

// AI API
export const aiApi = {
  getStatus: () => api.get('/ai/status'),
  generateMessage: (data: Record<string, unknown>) => api.post('/ai/generate-message', data),
  optimizeResume: (data: Record<string, unknown>) => api.post('/ai/optimize-resume', data),
  careerCoach: (data: { question: string; context?: Record<string, unknown> }) =>
    api.post('/ai/career-coach', data),
  interviewPrep: (data: Record<string, unknown>) => api.post('/ai/interview-prep', data),
  improveMessage: (data: { message: string; improvement_type?: string }) =>
    api.post('/ai/improve-message', data),
};

// Subscription API
export const subscriptionApi = {
  getTiers: () => api.get('/subscription/tiers'),
  getStatus: () => api.get('/subscription/status'),
  createCheckout: (tier: string) =>
    api.post('/subscription/checkout', { tier }),
  getPortal: () => api.post('/subscription/portal'),
  cancel: () => api.post('/subscription/cancel'),
  reactivate: () => api.post('/subscription/reactivate'),
};

// LinkedIn API
export const linkedinApi = {
  analyzeProfile: (data: {
    headline?: string;
    summary?: string;
    experience?: Array<{ title: string; company: string; description: string }>;
    skills?: string[];
    education?: Array<{ school: string; degree: string }>;
    photo?: boolean;
    location?: string;
    industry?: string;
  }) => api.post('/linkedin/analyze', data),

  generateHeadline: (data: {
    current_role?: string;
    target_role?: string;
    industry?: string;
    key_skills?: string[];
    achievements?: string[];
  }) => api.post('/linkedin/headline/generate', data),

  generateSummary: (data: {
    current_role?: string;
    years_experience?: number;
    industry?: string;
    key_skills?: string[];
    achievements?: string[];
    career_goals?: string;
  }) => api.post('/linkedin/summary/generate', data),

  optimizeExperience: (data: {
    title: string;
    company: string;
    description: string;
    target_keywords?: string[];
  }) => api.post('/linkedin/experience/optimize', data),

  getVisibility: (data: {
    headline?: string;
    summary?: string;
    experience?: Array<{ title: string; company: string; description: string }>;
    skills?: string[];
    photo?: boolean;
    location?: string;
    industry?: string;
  }) => api.post('/linkedin/visibility', data),

  getKeywords: (industry: string) => api.get(`/linkedin/keywords/${industry}`),
};

// Notification API
export const notificationApi = {
  list: (params?: { limit?: number; offset?: number; unread_only?: boolean }) =>
    api.get('/notifications', { params }),
  getUnreadCount: () => api.get('/notifications/unread-count'),
  markRead: (id: string) => api.put(`/notifications/${id}/read`),
  markAllRead: () => api.put('/notifications/read-all'),
  generate: () => api.post('/notifications/generate'),
};

// Labor Market API
export const laborMarketApi = {
  getOverview: () => api.get('/labor-market/overview'),

  getShortage: (params: { role: string; industry?: string; location?: string }) =>
    api.get('/labor-market/shortage', { params }),

  getSalary: (params: { role: string; experience?: string; location?: string }) =>
    api.get('/labor-market/salary', { params }),

  getOpportunity: (data: {
    target_role?: string;
    target_industry?: string;
    skills?: string[];
  }) => api.post('/labor-market/opportunity', data),

  getTrends: (params: { role?: string; industry?: string }) =>
    api.get('/labor-market/trends', { params }),

  getSkillsMap: () => api.get('/labor-market/skills-map'),

  getSkillsGap: (data: { target_role?: string; skills?: string[] }) =>
    api.post('/labor-market/skills-gap', data),

  searchOccupations: (query: string, limit?: number) =>
    api.get('/labor-market/occupations', { params: { q: query, limit: limit || 10 } }),

  searchSkills: (query: string, category?: string, limit?: number) =>
    api.get('/labor-market/skills', { params: { q: query, category, limit: limit || 20 } }),

  getHighDemandRoles: () => api.get('/labor-market/roles/high-demand'),
};

export default api;
