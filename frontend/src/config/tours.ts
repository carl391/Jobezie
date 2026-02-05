// Tour configuration for Jobezie platform

export interface TourStep {
  id: string;
  element: string;
  title: string;
  description: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

export interface TourConfig {
  id: string;
  name: string;
  description: string;
  steps: TourStep[];
}

// Main platform tour - shown after onboarding
export const MAIN_TOUR: TourConfig = {
  id: 'main',
  name: 'Platform Tour',
  description: 'Get to know the Jobezie platform',
  steps: [
    {
      id: 'welcome',
      element: '[data-tour="dashboard-header"]',
      title: 'Welcome to Jobezie!',
      description: 'Let me show you around. This quick tour will help you get the most out of your AI career assistant.',
      position: 'bottom',
    },
    {
      id: 'career-readiness',
      element: '[data-tour="career-readiness"]',
      title: 'Career Readiness Score',
      description: 'This score shows your overall job search health based on your profile, resume quality, and networking activity. Aim for 80% or higher!',
      position: 'bottom',
    },
    {
      id: 'pipeline-overview',
      element: '[data-tour="pipeline-overview"]',
      title: 'Pipeline Overview',
      description: 'Track all your recruiter relationships at a glance. See who needs follow-up and where each connection stands in your job search journey.',
      position: 'bottom',
    },
    {
      id: 'nav-resumes',
      element: '[data-tour="nav-resumes"]',
      title: 'Resume Management',
      description: 'Upload and manage multiple resumes. Our AI scores them against ATS systems and helps you optimize for specific jobs.',
      position: 'right',
    },
    {
      id: 'nav-recruiters',
      element: '[data-tour="nav-recruiters"]',
      title: 'Recruiter CRM',
      description: 'Keep track of all your recruiter contacts. Track engagement, add notes, and never miss a follow-up opportunity.',
      position: 'right',
    },
    {
      id: 'nav-messages',
      element: '[data-tour="nav-messages"]',
      title: 'Smart Messaging',
      description: 'Compose outreach messages with AI assistance. We score your messages and suggest improvements for better response rates.',
      position: 'right',
    },
    {
      id: 'nav-activity',
      element: '[data-tour="nav-activity"]',
      title: 'Activity Tracking',
      description: 'View all your job search activities in a timeline or Kanban board. Stay organized and track your progress over time.',
      position: 'right',
    },
    {
      id: 'nav-ai-coach',
      element: '[data-tour="nav-ai-coach"]',
      title: 'AI Career Coach',
      description: 'Get personalized career advice anytime. Ask about interview prep, salary negotiation, career strategy, or anything else!',
      position: 'right',
    },
    {
      id: 'nav-interview',
      element: '[data-tour="nav-interview"]',
      title: 'Interview Prep',
      description: 'Practice mock interviews with AI-generated questions tailored to your role. Get feedback and sample answers.',
      position: 'right',
    },
    {
      id: 'nav-linkedin',
      element: '[data-tour="nav-linkedin"]',
      title: 'LinkedIn Tools',
      description: 'Optimize your LinkedIn profile with AI-generated headlines, summaries, and visibility analysis.',
      position: 'right',
    },
    {
      id: 'nav-labor-market',
      element: '[data-tour="nav-labor-market"]',
      title: 'Labor Market Insights',
      description: 'Explore job market trends, salary benchmarks, and skill shortage data to inform your job search strategy.',
      position: 'right',
    },
  ],
};

// Feature-specific tours
export const DASHBOARD_TOUR: TourConfig = {
  id: 'dashboard',
  name: 'Dashboard Tour',
  description: 'Learn about the Dashboard features',
  steps: [
    {
      id: 'career-readiness',
      element: '[data-tour="career-readiness"]',
      title: 'Career Readiness Score',
      description: 'Your overall job search health score. This combines profile completeness, resume quality, and networking activity.',
      position: 'bottom',
    },
    {
      id: 'pipeline-overview',
      element: '[data-tour="pipeline-overview"]',
      title: 'Pipeline Overview',
      description: 'See your recruiters organized by stage - from initial contact through to offer acceptance.',
      position: 'bottom',
    },
    {
      id: 'recent-activity',
      element: '[data-tour="recent-activity"]',
      title: 'Recent Activity',
      description: 'Quick view of your latest job search activities. Click "View all" for the full timeline.',
      position: 'left',
    },
    {
      id: 'follow-ups',
      element: '[data-tour="follow-ups"]',
      title: 'Smart Follow-up Recommendations',
      description: 'AI-powered suggestions for who to follow up with and when, based on engagement patterns.',
      position: 'top',
    },
  ],
};

export const RESUMES_TOUR: TourConfig = {
  id: 'resumes',
  name: 'Resume Tools Tour',
  description: 'Learn about Resume management',
  steps: [
    {
      id: 'upload',
      element: '[data-tour="resume-upload"]',
      title: 'Upload Your Resume',
      description: 'Drag and drop or click to upload your resume. We support PDF and Word documents up to 5MB.',
      position: 'bottom',
    },
    {
      id: 'ats-score',
      element: '[data-tour="resume-ats"]',
      title: 'ATS Score',
      description: 'Each resume gets an ATS compatibility score with a breakdown of 7 key components.',
      position: 'bottom',
    },
    {
      id: 'ai-optimize',
      element: '[data-tour="resume-optimize"]',
      title: 'AI Optimization',
      description: 'Let AI help you tailor your resume for specific jobs and improve your ATS score.',
      position: 'bottom',
    },
  ],
};

export const RECRUITERS_TOUR: TourConfig = {
  id: 'recruiters',
  name: 'Recruiter CRM Tour',
  description: 'Learn about Recruiter management',
  steps: [
    {
      id: 'add-recruiter',
      element: '[data-tour="recruiter-add"]',
      title: 'Add Recruiters',
      description: 'Build your network by adding recruiter contacts. Track their company, specialty, and more.',
      position: 'bottom',
    },
    {
      id: 'pipeline-stages',
      element: '[data-tour="recruiter-pipeline"]',
      title: 'Pipeline Stages',
      description: 'Track each recruiter through 8 stages: New, Researching, Contacted, Responded, Interviewing, Offer, Accepted, or Declined.',
      position: 'bottom',
    },
    {
      id: 'engagement',
      element: '[data-tour="recruiter-engagement"]',
      title: 'Engagement Scores',
      description: 'We calculate engagement and fit scores to help you prioritize your outreach efforts.',
      position: 'bottom',
    },
  ],
};

export const MESSAGES_TOUR: TourConfig = {
  id: 'messages',
  name: 'Messaging Tour',
  description: 'Learn about Smart Messaging',
  steps: [
    {
      id: 'compose',
      element: '[data-tour="message-compose"]',
      title: 'Compose Messages',
      description: 'Create initial outreach, follow-ups, thank-you notes, or check-in messages.',
      position: 'bottom',
    },
    {
      id: 'ai-generate',
      element: '[data-tour="message-ai"]',
      title: 'AI Message Generation',
      description: 'Let AI draft personalized messages based on the recruiter and your background.',
      position: 'bottom',
    },
    {
      id: 'quality-score',
      element: '[data-tour="message-quality"]',
      title: 'Quality Scoring',
      description: 'Every message gets a quality score with specific suggestions for improvement.',
      position: 'bottom',
    },
  ],
};

export const ACTIVITY_TOUR: TourConfig = {
  id: 'activity',
  name: 'Activity Tracking Tour',
  description: 'Learn about Activity tracking',
  steps: [
    {
      id: 'timeline',
      element: '[data-tour="activity-timeline"]',
      title: 'Timeline View',
      description: 'See all your job search activities in chronological order, organized by date.',
      position: 'bottom',
    },
    {
      id: 'kanban',
      element: '[data-tour="activity-kanban"]',
      title: 'Kanban Board',
      description: 'Visualize your pipeline with drag-and-drop cards. Move recruiters between stages with ease.',
      position: 'bottom',
    },
  ],
};

export const AI_COACH_TOUR: TourConfig = {
  id: 'ai-coach',
  name: 'AI Coach Tour',
  description: 'Learn about AI Career Coaching',
  steps: [
    {
      id: 'chat',
      element: '[data-tour="coach-chat"]',
      title: 'Chat Interface',
      description: 'Have a conversation with your AI career coach. Ask anything about your job search.',
      position: 'bottom',
    },
    {
      id: 'prompts',
      element: '[data-tour="coach-prompts"]',
      title: 'Quick Prompts',
      description: 'Use these suggestions to get started, or type your own question.',
      position: 'top',
    },
  ],
};

export const INTERVIEW_PREP_TOUR: TourConfig = {
  id: 'interview-prep',
  name: 'Interview Prep Tour',
  description: 'Learn about Interview Preparation',
  steps: [
    {
      id: 'mode-tabs',
      element: '[data-tour="interview-modes"]',
      title: 'Preparation Modes',
      description: 'Choose between Practice mode for mock questions, Review for analyzing past interviews, and Tips for interview strategies.',
      position: 'bottom',
    },
    {
      id: 'question-settings',
      element: '[data-tour="interview-settings"]',
      title: 'Question Settings',
      description: 'Customize your practice by selecting question type (behavioral, technical, etc.) and difficulty level.',
      position: 'bottom',
    },
    {
      id: 'generate-question',
      element: '[data-tour="interview-generate"]',
      title: 'Generate Questions',
      description: 'Click to get AI-generated interview questions tailored to your target role and experience level.',
      position: 'bottom',
    },
    {
      id: 'answer-practice',
      element: '[data-tour="interview-answer"]',
      title: 'Practice Your Answer',
      description: 'Write or speak your answer, then compare it with the sample answer and get feedback.',
      position: 'top',
    },
  ],
};

export const LINKEDIN_TOUR: TourConfig = {
  id: 'linkedin',
  name: 'LinkedIn Tools Tour',
  description: 'Learn about LinkedIn Optimization',
  steps: [
    {
      id: 'tabs',
      element: '[data-tour="linkedin-tabs"]',
      title: 'LinkedIn Tools',
      description: 'Access three powerful tools: Headline Generator, Summary Writer, and Visibility Analyzer.',
      position: 'bottom',
    },
    {
      id: 'headline',
      element: '[data-tour="linkedin-headline"]',
      title: 'Headline Generator',
      description: 'Create attention-grabbing headlines that include keywords recruiters search for.',
      position: 'bottom',
    },
    {
      id: 'summary',
      element: '[data-tour="linkedin-summary"]',
      title: 'Summary Generator',
      description: 'Generate professional summaries with a strong hook, experience highlights, and call-to-action.',
      position: 'bottom',
    },
    {
      id: 'visibility',
      element: '[data-tour="linkedin-visibility"]',
      title: 'Visibility Score',
      description: 'Analyze your profile\'s visibility and get recommendations to improve your search ranking.',
      position: 'bottom',
    },
  ],
};

export const LABOR_MARKET_TOUR: TourConfig = {
  id: 'labor-market',
  name: 'Labor Market Tour',
  description: 'Learn about Labor Market Insights',
  steps: [
    {
      id: 'overview',
      element: '[data-tour="market-overview"]',
      title: 'Market Overview',
      description: 'See the current state of the job market including employment rates, job openings, and salary trends.',
      position: 'bottom',
    },
    {
      id: 'shortage',
      element: '[data-tour="market-shortage"]',
      title: 'Skill Shortage Score',
      description: 'Find out how in-demand your skills are and where the biggest opportunities exist.',
      position: 'bottom',
    },
    {
      id: 'salary',
      element: '[data-tour="market-salary"]',
      title: 'Salary Benchmarks',
      description: 'Compare salaries for your target roles by experience level and location.',
      position: 'bottom',
    },
    {
      id: 'opportunity',
      element: '[data-tour="market-opportunity"]',
      title: 'Opportunity Analysis',
      description: 'Get personalized recommendations based on market demand and your skill profile.',
      position: 'bottom',
    },
  ],
};

// All tours indexed by ID
export const TOURS: Record<string, TourConfig> = {
  main: MAIN_TOUR,
  dashboard: DASHBOARD_TOUR,
  resumes: RESUMES_TOUR,
  recruiters: RECRUITERS_TOUR,
  messages: MESSAGES_TOUR,
  activity: ACTIVITY_TOUR,
  'ai-coach': AI_COACH_TOUR,
  'interview-prep': INTERVIEW_PREP_TOUR,
  linkedin: LINKEDIN_TOUR,
  'labor-market': LABOR_MARKET_TOUR,
};

// Feature categories for the Learn page
export interface FeatureCategory {
  id: string;
  name: string;
  icon: string;
  description: string;
  features: Feature[];
}

export interface Feature {
  id: string;
  name: string;
  description: string;
  tourId?: string;
  tips?: string[];
}

export const FEATURE_CATEGORIES: FeatureCategory[] = [
  {
    id: 'getting-started',
    name: 'Getting Started',
    icon: 'Rocket',
    description: 'Learn the basics of Jobezie',
    features: [
      {
        id: 'dashboard-overview',
        name: 'Dashboard Overview',
        description: 'Understanding your career readiness score and pipeline overview. Your dashboard is your job search command center.',
        tourId: 'dashboard',
        tips: [
          'Check your Career Readiness score daily',
          'Review recommended follow-ups each morning',
          'Use the pipeline overview to track progress',
        ],
      },
      {
        id: 'navigation',
        name: 'Navigating the App',
        description: 'Learn how to move between different sections of the platform using the sidebar navigation.',
        tourId: 'main',
      },
    ],
  },
  {
    id: 'resume-tools',
    name: 'Resume Tools',
    icon: 'FileText',
    description: 'Optimize your resume for ATS and recruiters',
    features: [
      {
        id: 'upload-resume',
        name: 'Uploading Resumes',
        description: 'How to upload and manage multiple resume versions. Keep a master resume and create tailored versions for specific roles.',
        tourId: 'resumes',
        tips: [
          'Keep one "master" resume with all your experience',
          'Create tailored versions for different job types',
          'Update your resumes regularly as you gain experience',
        ],
      },
      {
        id: 'ats-scoring',
        name: 'ATS Scoring',
        description: 'Understanding your ATS compatibility score and the 7-component breakdown that helps you optimize for applicant tracking systems.',
        tips: [
          'Aim for 80% or higher for best results',
          'Focus on keywords from job descriptions',
          'Use standard section headings (Experience, Education, Skills)',
          'Avoid tables, graphics, and unusual formatting',
        ],
      },
      {
        id: 'ai-optimization',
        name: 'AI Resume Optimization',
        description: 'Let AI help you tailor your resume for specific jobs by analyzing job descriptions and suggesting improvements.',
        tips: [
          'Paste the full job description for best results',
          'Review AI suggestions before accepting',
          'Compare before/after ATS scores',
        ],
      },
    ],
  },
  {
    id: 'recruiter-management',
    name: 'Recruiter Management',
    icon: 'Users',
    description: 'Build and manage your recruiter network',
    features: [
      {
        id: 'adding-recruiters',
        name: 'Adding Recruiters',
        description: 'Track new recruiter connections with their contact information, company, specialty, and more.',
        tourId: 'recruiters',
        tips: [
          'Add LinkedIn URLs for easy reference',
          'Note their specialty areas and industries',
          'Set follow-up reminders',
        ],
      },
      {
        id: 'pipeline-stages',
        name: 'Pipeline Stages',
        description: 'Understanding the 8 stages from New to Accepted/Declined. Track each recruiter relationship as it progresses.',
        tips: [
          'New: Just added to your network',
          'Researching: Learning about them',
          'Contacted: You\'ve reached out',
          'Responded: They\'ve replied',
          'Interviewing: Active interview process',
          'Offer: You have an offer',
          'Accepted/Declined: Final outcome',
        ],
      },
      {
        id: 'engagement-score',
        name: 'Engagement & Fit Scores',
        description: 'How we calculate recruiter engagement (based on response patterns) and job fit (based on role matching).',
        tips: [
          'Higher engagement = more responsive recruiters',
          'Fit score considers your target roles and industries',
          'Focus on high-engagement, high-fit recruiters',
        ],
      },
    ],
  },
  {
    id: 'messaging',
    name: 'Messaging',
    icon: 'MessageSquare',
    description: 'Craft effective outreach messages',
    features: [
      {
        id: 'compose-message',
        name: 'Composing Messages',
        description: 'Create different message types: initial outreach, follow-ups, thank-you notes, and check-ins.',
        tourId: 'messages',
        tips: [
          'Keep initial outreach under 150 words',
          'Personalize with specific details',
          'Include a clear call-to-action',
        ],
      },
      {
        id: 'ai-generation',
        name: 'AI Message Generation',
        description: 'Let AI draft personalized messages based on the recruiter\'s profile and your background.',
        tips: [
          'Review and personalize AI-generated messages',
          'Add specific details AI might not know',
          'Match the tone to your personality',
        ],
      },
      {
        id: 'quality-scoring',
        name: 'Message Quality Scoring',
        description: 'Understanding the 5-component quality score: word count, personalization, metrics, call-to-action, and tone.',
        tips: [
          'Aim for 80+ quality score',
          'Include specific achievements and metrics',
          'End with a clear next step',
        ],
      },
    ],
  },
  {
    id: 'activity-tracking',
    name: 'Activity Tracking',
    icon: 'Activity',
    description: 'Monitor your job search progress',
    features: [
      {
        id: 'timeline-view',
        name: 'Timeline View',
        description: 'See all your activities in chronological order, organized by date with filters for activity type.',
        tourId: 'activity',
        tips: [
          'Filter by activity type to focus',
          'Check daily for recent activities',
          'Use for weekly progress reviews',
        ],
      },
      {
        id: 'kanban-board',
        name: 'Kanban Board',
        description: 'Visualize your pipeline with drag-and-drop cards. Move recruiters between stages with ease.',
        tips: [
          'Drag cards to update stages',
          'Red indicators show urgent follow-ups',
          'Great for weekly planning sessions',
        ],
      },
    ],
  },
  {
    id: 'ai-features',
    name: 'AI Features',
    icon: 'Sparkles',
    description: 'Leverage AI for your job search',
    features: [
      {
        id: 'ai-coach',
        name: 'AI Career Coach',
        description: 'Get personalized career advice through an interactive chat interface. Ask about strategy, preparation, and more.',
        tourId: 'ai-coach',
        tips: [
          'Ask specific questions for better answers',
          'Use quick prompts to get started',
          'Follow up for more detail',
        ],
      },
      {
        id: 'interview-prep',
        name: 'Interview Preparation',
        description: 'Practice with AI-powered mock interviews. Get feedback on your answers and improve your performance.',
        tourId: 'interview-prep',
        tips: [
          'Practice common behavioral questions',
          'Use the STAR method for stories',
          'Record yourself for self-review',
        ],
      },
      {
        id: 'linkedin-tools',
        name: 'LinkedIn Optimization',
        description: 'Improve your LinkedIn profile visibility with headline and summary suggestions based on your target roles.',
        tourId: 'linkedin',
        tips: [
          'Update your headline with keywords',
          'Customize summary for target roles',
          'Add relevant skills and endorsements',
        ],
      },
      {
        id: 'labor-market',
        name: 'Labor Market Insights',
        description: 'Understand job market trends, skill shortages, salary benchmarks, and opportunities in your field.',
        tourId: 'labor-market',
        tips: [
          'Check shortage scores for your target roles',
          'Use salary data for negotiation',
          'Identify skill gaps to work on',
        ],
      },
    ],
  },
];
