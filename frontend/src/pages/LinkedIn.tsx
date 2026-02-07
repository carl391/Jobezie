import { useState } from 'react';
import {
  Linkedin,
  Loader2,
  Sparkles,
  Eye,
  FileText,
  Briefcase,
  Copy,
  Check,
  AlertCircle,
  TrendingUp,
} from 'lucide-react';
import { linkedinApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

type TabType = 'headline' | 'summary' | 'visibility';

interface HeadlineOption {
  headline: string;
  score: number;
  reasoning: string;
}

interface SummaryResult {
  summary: string;
  word_count: number;
  sections: {
    hook: string;
    experience: string;
    skills: string;
    call_to_action: string;
  };
}

interface VisibilityResult {
  score: number;
  grade: string;
  factors: Array<{
    name: string;
    score: number;
    max_score: number;
    recommendation: string;
  }>;
  improvements: string[];
}

export function LinkedIn() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('headline');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  // Headline Generator State
  const [headlineForm, setHeadlineForm] = useState({
    current_role: user?.current_role || '',
    target_role: user?.target_roles?.[0] || '',
    industry: user?.target_industries?.[0] || '',
    key_skills: user?.technical_skills?.slice(0, 3).join(', ') || '',
    achievements: '',
  });
  const [headlineResults, setHeadlineResults] = useState<HeadlineOption[]>([]);

  // Summary Generator State
  const [summaryForm, setSummaryForm] = useState({
    current_role: user?.current_role || '',
    years_experience: user?.years_experience?.toString() || '',
    industry: user?.target_industries?.[0] || '',
    key_skills: user?.technical_skills?.slice(0, 5).join(', ') || '',
    achievements: '',
    career_goals: '',
  });
  const [summaryResult, setSummaryResult] = useState<SummaryResult | null>(null);

  // Visibility State
  const [visibilityForm, setVisibilityForm] = useState({
    headline: '',
    summary: '',
    skills: '',
    location: user?.location || '',
    industry: user?.target_industries?.[0] || '',
    photo: true,
  });
  const [visibilityResult, setVisibilityResult] = useState<VisibilityResult | null>(null);

  const handleGenerateHeadlines = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await linkedinApi.generateHeadline({
        current_role: headlineForm.current_role,
        target_role: headlineForm.target_role || undefined,
        industry: headlineForm.industry || undefined,
        key_skills: headlineForm.key_skills ? headlineForm.key_skills.split(',').map(s => s.trim()) : undefined,
        achievements: headlineForm.achievements ? headlineForm.achievements.split(',').map(s => s.trim()) : undefined,
      });
      setHeadlineResults(response.data.data?.headlines || []);
    } catch (err) {
      console.error('Error generating headlines:', err);
      setError('Failed to generate headlines. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateSummary = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await linkedinApi.generateSummary({
        current_role: summaryForm.current_role,
        years_experience: parseInt(summaryForm.years_experience) || undefined,
        industry: summaryForm.industry || undefined,
        key_skills: summaryForm.key_skills ? summaryForm.key_skills.split(',').map(s => s.trim()) : undefined,
        achievements: summaryForm.achievements ? summaryForm.achievements.split(',').map(s => s.trim()) : undefined,
        career_goals: summaryForm.career_goals || undefined,
      });
      setSummaryResult(response.data.data);
    } catch (err) {
      console.error('Error generating summary:', err);
      setError('Failed to generate summary. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzeVisibility = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await linkedinApi.getVisibility({
        headline: visibilityForm.headline || undefined,
        summary: visibilityForm.summary || undefined,
        skills: visibilityForm.skills ? visibilityForm.skills.split(',').map(s => s.trim()) : undefined,
        location: visibilityForm.location || undefined,
        industry: visibilityForm.industry || undefined,
        photo: visibilityForm.photo,
      });
      setVisibilityResult(response.data.data);
    } catch (err) {
      console.error('Error analyzing visibility:', err);
      setError('Failed to analyze visibility. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(id);
      setTimeout(() => setCopied(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const tabs = [
    { id: 'headline' as const, label: 'Headline Generator', icon: Briefcase, tourId: 'linkedin-headline' },
    { id: 'summary' as const, label: 'Summary Generator', icon: FileText, tourId: 'linkedin-summary' },
    { id: 'visibility' as const, label: 'Visibility Score', icon: Eye, tourId: 'linkedin-visibility' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Linkedin className="w-6 h-6 text-[#0A66C2]" />
          LinkedIn Optimizer
        </h1>
        <p className="text-gray-600 mt-1">
          Optimize your LinkedIn profile to increase visibility and attract recruiters
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200" data-tour="linkedin-tabs">
        <div className="flex gap-4 -mb-px">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              data-tour={tab.tourId}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Headline Generator Tab */}
      {activeTab === 'headline' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Generate Headlines</h2>
            <div className="space-y-4">
              <div>
                <label className="label">Current Role *</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., Senior Software Engineer"
                  value={headlineForm.current_role}
                  onChange={(e) => setHeadlineForm({ ...headlineForm, current_role: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Target Role</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., Engineering Manager"
                  value={headlineForm.target_role}
                  onChange={(e) => setHeadlineForm({ ...headlineForm, target_role: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Industry</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., FinTech, Healthcare"
                  value={headlineForm.industry}
                  onChange={(e) => setHeadlineForm({ ...headlineForm, industry: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Key Skills (comma-separated)</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., Python, Machine Learning, AWS"
                  value={headlineForm.key_skills}
                  onChange={(e) => setHeadlineForm({ ...headlineForm, key_skills: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Achievements (comma-separated)</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., 10x revenue growth, Led team of 20"
                  value={headlineForm.achievements}
                  onChange={(e) => setHeadlineForm({ ...headlineForm, achievements: e.target.value })}
                />
              </div>
              <button
                onClick={handleGenerateHeadlines}
                disabled={!headlineForm.current_role || isLoading}
                className="btn btn-primary w-full"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate Headlines
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Generated Headlines</h2>
            {headlineResults.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <Briefcase className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Fill in the form and click Generate to create headlines</p>
              </div>
            ) : (
              <div className="space-y-4">
                {headlineResults.map((option, index) => (
                  <div key={index} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-start justify-between gap-2">
                      <p className="font-medium text-gray-900">{option.headline}</p>
                      <button
                        onClick={() => copyToClipboard(option.headline, `headline-${index}`)}
                        className="text-gray-400 hover:text-gray-600 flex-shrink-0"
                      >
                        {copied === `headline-${index}` ? (
                          <Check className="w-4 h-4 text-green-500" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      <div className="flex items-center gap-1 text-sm">
                        <TrendingUp className="w-4 h-4 text-green-500" />
                        <span className="font-medium">{option.score}%</span>
                      </div>
                      <span className="text-gray-400">|</span>
                      <p className="text-sm text-gray-600">{option.reasoning}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Summary Generator Tab */}
      {activeTab === 'summary' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Generate Summary</h2>
            <div className="space-y-4">
              <div>
                <label className="label">Current Role *</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., Senior Software Engineer"
                  value={summaryForm.current_role}
                  onChange={(e) => setSummaryForm({ ...summaryForm, current_role: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Years of Experience *</label>
                <input
                  type="number"
                  className="input"
                  placeholder="e.g., 5"
                  value={summaryForm.years_experience}
                  onChange={(e) => setSummaryForm({ ...summaryForm, years_experience: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Industry *</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., FinTech, Healthcare"
                  value={summaryForm.industry}
                  onChange={(e) => setSummaryForm({ ...summaryForm, industry: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Key Skills (comma-separated) *</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., Python, Machine Learning, AWS"
                  value={summaryForm.key_skills}
                  onChange={(e) => setSummaryForm({ ...summaryForm, key_skills: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Achievements (comma-separated)</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., 10x revenue growth, Led team of 20"
                  value={summaryForm.achievements}
                  onChange={(e) => setSummaryForm({ ...summaryForm, achievements: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Career Goals</label>
                <textarea
                  className="input"
                  rows={2}
                  placeholder="What are you looking for in your next role?"
                  value={summaryForm.career_goals}
                  onChange={(e) => setSummaryForm({ ...summaryForm, career_goals: e.target.value })}
                />
              </div>
              <button
                onClick={handleGenerateSummary}
                disabled={!summaryForm.current_role || !summaryForm.years_experience || !summaryForm.industry || !summaryForm.key_skills || isLoading}
                className="btn btn-primary w-full"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate Summary
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Generated Summary</h2>
            {!summaryResult ? (
              <div className="text-center py-12 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Fill in the form and click Generate to create a summary</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="relative">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="whitespace-pre-wrap text-gray-800">{summaryResult.summary}</p>
                  </div>
                  <button
                    onClick={() => copyToClipboard(summaryResult.summary, 'summary')}
                    className="absolute top-2 right-2 p-2 text-gray-400 hover:text-gray-600 bg-white rounded-lg shadow-sm"
                  >
                    {copied === 'summary' ? (
                      <Check className="w-4 h-4 text-green-500" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span>{summaryResult.word_count} words</span>
                  <span className="text-green-600">Optimal length for LinkedIn</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Visibility Score Tab */}
      {activeTab === 'visibility' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Analyze Profile Visibility</h2>
            <div className="space-y-4">
              <div>
                <label className="label">Your Headline</label>
                <input
                  type="text"
                  className="input"
                  placeholder="Paste your current LinkedIn headline"
                  value={visibilityForm.headline}
                  onChange={(e) => setVisibilityForm({ ...visibilityForm, headline: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Your Summary/About</label>
                <textarea
                  className="input"
                  rows={4}
                  placeholder="Paste your LinkedIn summary"
                  value={visibilityForm.summary}
                  onChange={(e) => setVisibilityForm({ ...visibilityForm, summary: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Skills (comma-separated)</label>
                <input
                  type="text"
                  className="input"
                  placeholder="List your LinkedIn skills"
                  value={visibilityForm.skills}
                  onChange={(e) => setVisibilityForm({ ...visibilityForm, skills: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Location</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., San Francisco Bay Area"
                  value={visibilityForm.location}
                  onChange={(e) => setVisibilityForm({ ...visibilityForm, location: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Industry</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., Technology"
                  value={visibilityForm.industry}
                  onChange={(e) => setVisibilityForm({ ...visibilityForm, industry: e.target.value })}
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="hasPhoto"
                  checked={visibilityForm.photo}
                  onChange={(e) => setVisibilityForm({ ...visibilityForm, photo: e.target.checked })}
                  className="w-4 h-4 text-primary-600 rounded"
                />
                <label htmlFor="hasPhoto" className="text-sm text-gray-700">
                  I have a professional profile photo
                </label>
              </div>
              <button
                onClick={handleAnalyzeVisibility}
                disabled={isLoading}
                className="btn btn-primary w-full"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Eye className="w-4 h-4" />
                    Analyze Visibility
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Visibility Analysis</h2>
            {!visibilityResult ? (
              <div className="text-center py-12 text-gray-500">
                <Eye className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Fill in your profile details and click Analyze</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Overall Score */}
                <div className="text-center p-6 bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl">
                  <div className="text-5xl font-bold text-primary-600 mb-2">
                    {visibilityResult.score}%
                  </div>
                  <div className="text-lg font-medium text-primary-800">
                    {visibilityResult.grade}
                  </div>
                </div>

                {/* Factor Breakdown */}
                <div>
                  <h3 className="font-medium text-gray-900 mb-3">Score Breakdown</h3>
                  <div className="space-y-3">
                    {visibilityResult.factors?.map((factor, index) => (
                      <div key={index}>
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span className="text-gray-700">{factor.name}</span>
                          <span className="font-medium">{factor.score ?? 0}/{factor.max_score ?? 0}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full transition-all"
                            style={{ width: `${factor.max_score ? (factor.score / factor.max_score) * 100 : 0}%` }}
                          />
                        </div>
                        {factor.recommendation && (
                          <p className="text-xs text-gray-500 mt-1">{factor.recommendation}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Improvements */}
                {visibilityResult.improvements?.length > 0 && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-3">Top Improvements</h3>
                    <ul className="space-y-2">
                      {visibilityResult.improvements.map((improvement, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm">
                          <TrendingUp className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                          <span className="text-gray-700">{improvement}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
