import { useState, useEffect } from 'react';
import {
  TrendingUp,
  DollarSign,
  Target,
  BarChart3,
  Loader2,
  AlertCircle,
  ArrowUp,
  ArrowDown,
  Minus,
  Briefcase,
  MapPin,
  Building2,
} from 'lucide-react';
import { laborMarketApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

interface MarketOverview {
  employment_rate: number;
  job_openings: number;
  avg_salary_growth: number;
  remote_percentage: number;
  top_industries: Array<{ name: string; growth: number }>;
  market_sentiment: 'bullish' | 'neutral' | 'bearish';
}

interface ShortageData {
  score: number;
  grade: string;
  demand_level: string;
  supply_level: string;
  factors: Array<{ name: string; impact: string; score: number }>;
  recommendations: string[];
}

interface SalaryData {
  role: string;
  experience_level: string;
  location?: string;
  min_salary: number;
  median_salary: number;
  max_salary: number;
  percentiles: { p25: number; p50: number; p75: number; p90: number };
  comparison_to_market: number;
}

interface OpportunityData {
  score: number;
  grade: string;
  match_factors: Array<{ name: string; score: number; max: number }>;
  recommendations: string[];
  skill_gaps: string[];
  in_demand_skills: string[];
}

export function LaborMarket() {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Overview State
  const [overview, setOverview] = useState<MarketOverview | null>(null);
  const [overviewLoading, setOverviewLoading] = useState(true);

  // Shortage State
  const [shortageForm, setShortageForm] = useState({
    role: user?.target_roles?.[0] || user?.current_role || '',
    industry: user?.target_industries?.[0] || '',
    location: user?.location || '',
  });
  const [shortageData, setShortageData] = useState<ShortageData | null>(null);

  // Salary State
  const [salaryForm, setSalaryForm] = useState({
    role: user?.target_roles?.[0] || user?.current_role || '',
    experience: 'mid',
    location: user?.location || '',
  });
  const [salaryData, setSalaryData] = useState<SalaryData | null>(null);

  // Opportunity State
  const [opportunityData, setOpportunityData] = useState<OpportunityData | null>(null);

  useEffect(() => {
    fetchOverview();
  }, []);

  const fetchOverview = async () => {
    setOverviewLoading(true);
    try {
      const response = await laborMarketApi.getOverview();
      setOverview(response.data.data);
    } catch (err) {
      console.error('Error fetching overview:', err);
    } finally {
      setOverviewLoading(false);
    }
  };

  const handleShortageSearch = async () => {
    if (!shortageForm.role) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await laborMarketApi.getShortage({
        role: shortageForm.role,
        industry: shortageForm.industry || undefined,
        location: shortageForm.location || undefined,
      });
      setShortageData(response.data.data);
    } catch (err) {
      console.error('Error fetching shortage data:', err);
      setError('Failed to fetch shortage data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSalarySearch = async () => {
    if (!salaryForm.role) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await laborMarketApi.getSalary({
        role: salaryForm.role,
        experience: salaryForm.experience,
        location: salaryForm.location || undefined,
      });
      setSalaryData(response.data.data);
    } catch (err) {
      console.error('Error fetching salary data:', err);
      setError('Failed to fetch salary data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpportunityAnalysis = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await laborMarketApi.getOpportunity({
        target_role: user?.target_roles?.[0],
        target_industry: user?.target_industries?.[0],
        skills: user?.technical_skills,
      });
      setOpportunityData(response.data.data);
    } catch (err) {
      console.error('Error analyzing opportunity:', err);
      setError('Failed to analyze opportunity. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const formatSalary = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-primary-600" />
          Labor Market Intelligence
        </h1>
        <p className="text-gray-600 mt-1">
          Understand market trends, salary benchmarks, and opportunities for your career
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Market Overview */}
      <div className="card" data-tour="market-overview">
        <h2 className="text-lg font-semibold mb-4">Market Overview</h2>
        {overviewLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
          </div>
        ) : overview ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-600 font-medium">Job Openings</p>
              <p className="text-2xl font-bold text-blue-900">{(overview.job_openings / 1000000).toFixed(1)}M</p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-green-600 font-medium">Avg. Salary Growth</p>
              <p className="text-2xl font-bold text-green-900 flex items-center gap-1">
                <ArrowUp className="w-5 h-5" />
                {overview.avg_salary_growth}%
              </p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-purple-600 font-medium">Remote Jobs</p>
              <p className="text-2xl font-bold text-purple-900">{overview.remote_percentage}%</p>
            </div>
            <div className="p-4 bg-orange-50 rounded-lg">
              <p className="text-sm text-orange-600 font-medium">Market Sentiment</p>
              <p className="text-2xl font-bold text-orange-900 capitalize flex items-center gap-1">
                {overview.market_sentiment === 'bullish' && <ArrowUp className="w-5 h-5 text-green-500" />}
                {overview.market_sentiment === 'bearish' && <ArrowDown className="w-5 h-5 text-red-500" />}
                {overview.market_sentiment === 'neutral' && <Minus className="w-5 h-5 text-gray-500" />}
                {overview.market_sentiment}
              </p>
            </div>
          </div>
        ) : (
          <p className="text-center text-gray-500 py-8">Unable to load market overview</p>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Labor Shortage Analysis */}
        <div className="card" data-tour="market-shortage">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary-600" />
            Labor Shortage Score
          </h2>
          <div className="space-y-4">
            <div>
              <label className="label">Job Role *</label>
              <div className="relative">
                <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  className="input pl-10"
                  placeholder="e.g., Software Engineer"
                  value={shortageForm.role}
                  onChange={(e) => setShortageForm({ ...shortageForm, role: e.target.value })}
                />
              </div>
            </div>
            <div>
              <label className="label">Industry</label>
              <div className="relative">
                <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  className="input pl-10"
                  placeholder="e.g., Technology"
                  value={shortageForm.industry}
                  onChange={(e) => setShortageForm({ ...shortageForm, industry: e.target.value })}
                />
              </div>
            </div>
            <div>
              <label className="label">Location</label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  className="input pl-10"
                  placeholder="e.g., San Francisco, CA"
                  value={shortageForm.location}
                  onChange={(e) => setShortageForm({ ...shortageForm, location: e.target.value })}
                />
              </div>
            </div>
            <button
              onClick={handleShortageSearch}
              disabled={!shortageForm.role || isLoading}
              className="btn btn-primary w-full"
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Analyze Shortage'}
            </button>

            {shortageData && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm text-gray-600">Shortage Score</span>
                  <div className={`text-3xl font-bold ${getScoreColor(shortageData.score)}`}>
                    {shortageData.score}
                  </div>
                </div>
                <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getScoreBg(shortageData.score)} ${getScoreColor(shortageData.score)}`}>
                  {shortageData.grade}
                </div>
                <div className="mt-4 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Demand Level:</span>
                    <span className="font-medium">{shortageData.demand_level}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Supply Level:</span>
                    <span className="font-medium">{shortageData.supply_level}</span>
                  </div>
                </div>
                {shortageData.recommendations?.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-700 mb-2">Recommendations</p>
                    <ul className="space-y-1 text-sm text-gray-600">
                      {shortageData.recommendations.slice(0, 3).map((rec, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-primary-600">•</span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Salary Benchmark */}
        <div className="card" data-tour="market-salary">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-green-600" />
            Salary Benchmark
          </h2>
          <div className="space-y-4">
            <div>
              <label className="label">Job Role *</label>
              <input
                type="text"
                className="input"
                placeholder="e.g., Software Engineer"
                value={salaryForm.role}
                onChange={(e) => setSalaryForm({ ...salaryForm, role: e.target.value })}
              />
            </div>
            <div>
              <label className="label">Experience Level</label>
              <select
                className="input"
                value={salaryForm.experience}
                onChange={(e) => setSalaryForm({ ...salaryForm, experience: e.target.value })}
              >
                <option value="entry">Entry Level (0-2 years)</option>
                <option value="mid">Mid Level (3-5 years)</option>
                <option value="senior">Senior (6-10 years)</option>
                <option value="executive">Executive (10+ years)</option>
              </select>
            </div>
            <div>
              <label className="label">Location</label>
              <input
                type="text"
                className="input"
                placeholder="e.g., New York, NY"
                value={salaryForm.location}
                onChange={(e) => setSalaryForm({ ...salaryForm, location: e.target.value })}
              />
            </div>
            <button
              onClick={handleSalarySearch}
              disabled={!salaryForm.role || isLoading}
              className="btn btn-primary w-full"
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Get Salary Data'}
            </button>

            {salaryData && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <div className="text-center mb-4">
                  <p className="text-sm text-gray-600 mb-1">Median Salary</p>
                  <p className="text-3xl font-bold text-green-600">{formatSalary(salaryData.median_salary)}</p>
                  <p className="text-sm text-gray-500">{salaryData.role} ({salaryData.experience_level})</p>
                </div>
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div className="p-3 bg-white rounded-lg">
                    <p className="text-xs text-gray-500">Minimum</p>
                    <p className="font-semibold text-gray-700">{formatSalary(salaryData.min_salary)}</p>
                  </div>
                  <div className="p-3 bg-white rounded-lg">
                    <p className="text-xs text-gray-500">Maximum</p>
                    <p className="font-semibold text-gray-700">{formatSalary(salaryData.max_salary)}</p>
                  </div>
                </div>
                {salaryData.percentiles && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-700 mb-2">Percentiles</p>
                    <div className="grid grid-cols-4 gap-2 text-center text-sm">
                      <div>
                        <p className="text-gray-500">25th</p>
                        <p className="font-medium">{formatSalary(salaryData.percentiles.p25)}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">50th</p>
                        <p className="font-medium">{formatSalary(salaryData.percentiles.p50)}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">75th</p>
                        <p className="font-medium">{formatSalary(salaryData.percentiles.p75)}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">90th</p>
                        <p className="font-medium">{formatSalary(salaryData.percentiles.p90)}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Opportunity Analysis */}
      <div className="card" data-tour="market-opportunity">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Target className="w-5 h-5 text-orange-600" />
            Your Opportunity Score
          </h2>
          <button
            onClick={handleOpportunityAnalysis}
            disabled={isLoading}
            className="btn btn-outline btn-sm"
          >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Analyze My Opportunity'}
          </button>
        </div>

        {opportunityData ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl">
              <div className={`text-5xl font-bold ${getScoreColor(opportunityData.score)} mb-2`}>
                {opportunityData.score}%
              </div>
              <div className="text-lg font-medium text-orange-800">{opportunityData.grade}</div>
            </div>

            <div className="md:col-span-2">
              <h3 className="font-medium text-gray-900 mb-3">Match Factors</h3>
              <div className="space-y-2">
                {opportunityData.match_factors?.map((factor, index) => (
                  <div key={index}>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-700">{factor.name}</span>
                      <span className="font-medium">{factor.score}/{factor.max}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-orange-500 h-2 rounded-full transition-all"
                        style={{ width: `${(factor.score / factor.max) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {opportunityData.skill_gaps?.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Skills to Develop</h4>
                  <div className="flex flex-wrap gap-2">
                    {opportunityData.skill_gaps.map((skill, i) => (
                      <span key={i} className="px-2 py-1 bg-red-50 text-red-700 text-xs rounded-full">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {opportunityData.in_demand_skills?.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Your In-Demand Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {opportunityData.in_demand_skills.map((skill, i) => (
                      <span key={i} className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded-full">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Target className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Click "Analyze My Opportunity" to see how you match current market demands</p>
            <p className="text-sm mt-1">Based on your profile: target roles, industry, and skills</p>
          </div>
        )}
      </div>
    </div>
  );
}
