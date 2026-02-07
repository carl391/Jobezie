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
  unemployment_rate: number;
  market_condition: string;
  trending_industries: Array<{ name: string; growth_rate: number }>;
  high_demand_roles: string[];
  updated_at: string;
}

interface ShortageData {
  total_score: number;
  interpretation: string;
  components: Record<string, number>;
  weights: Record<string, number>;
  role: string;
  normalized_role: string;
  industry?: string;
  projected_growth: string;
}

interface SalaryData {
  role: string;
  experience_level: string;
  base_salary: number;
  adjusted_salary: number;
  location?: string;
  location_adjustment: string;
  range: { low: number; median: number; high: number };
  all_levels: Record<string, number>;
}

interface OpportunityData {
  total_score: number;
  interpretation: string;
  components: { user_match: number; shortage: number };
  target_role: string;
  matching_skills: string[];
  missing_skills: string[];
  recommendations: string[];
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
    if (score >= 71) return 'text-green-600';
    if (score >= 41) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 71) return 'bg-green-100';
    if (score >= 41) return 'bg-yellow-100';
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
              <p className="text-sm text-blue-600 font-medium">Unemployment Rate</p>
              <p className="text-2xl font-bold text-blue-900">{overview.unemployment_rate ?? 0}%</p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-green-600 font-medium">Market Condition</p>
              <p className="text-2xl font-bold text-green-900 capitalize flex items-center gap-1">
                {overview.market_condition?.toLowerCase() === 'strong' && <ArrowUp className="w-5 h-5 text-green-500" />}
                {(overview.market_condition?.toLowerCase() === 'challenging' || overview.market_condition?.toLowerCase() === 'difficult') && <ArrowDown className="w-5 h-5 text-red-500" />}
                {overview.market_condition?.toLowerCase() === 'moderate' && <Minus className="w-5 h-5 text-yellow-500" />}
                {overview.market_condition || 'N/A'}
              </p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-purple-600 font-medium">Trending Industries</p>
              <p className="text-2xl font-bold text-purple-900">{overview.trending_industries?.length ?? 0}</p>
            </div>
            <div className="p-4 bg-orange-50 rounded-lg">
              <p className="text-sm text-orange-600 font-medium">High Demand Roles</p>
              <p className="text-2xl font-bold text-orange-900">{overview.high_demand_roles?.length ?? 0}</p>
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
                  <div className={`text-3xl font-bold ${getScoreColor(shortageData.total_score)}`}>
                    {shortageData.total_score}
                  </div>
                </div>
                <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getScoreBg(shortageData.total_score)} ${getScoreColor(shortageData.total_score)}`}>
                  {shortageData.interpretation}
                </div>
                <div className="mt-4 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Projected Growth:</span>
                    <span className="font-medium">{shortageData.projected_growth}</span>
                  </div>
                  {shortageData.components && (
                    <div className="mt-3 space-y-2">
                      {Object.entries(shortageData.components).map(([key, value]) => (
                        <div key={key}>
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-gray-600 capitalize">{key}</span>
                            <span className="font-medium">{value}/100</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div
                              className={`h-full rounded-full ${value >= 80 ? 'bg-green-500' : value >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
                              style={{ width: `${value}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
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
                  <p className="text-3xl font-bold text-green-600">{formatSalary(salaryData.range?.median ?? salaryData.adjusted_salary)}</p>
                  <p className="text-sm text-gray-500">{salaryData.role} ({salaryData.experience_level})</p>
                  {salaryData.location && (
                    <p className="text-xs text-gray-400 mt-1">{salaryData.location} ({salaryData.location_adjustment})</p>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div className="p-3 bg-white rounded-lg">
                    <p className="text-xs text-gray-500">Minimum</p>
                    <p className="font-semibold text-gray-700">{formatSalary(salaryData.range?.low ?? 0)}</p>
                  </div>
                  <div className="p-3 bg-white rounded-lg">
                    <p className="text-xs text-gray-500">Maximum</p>
                    <p className="font-semibold text-gray-700">{formatSalary(salaryData.range?.high ?? 0)}</p>
                  </div>
                </div>
                {salaryData.all_levels && Object.keys(salaryData.all_levels).length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-700 mb-2">By Experience Level</p>
                    <div className="space-y-2">
                      {Object.entries(salaryData.all_levels).map(([level, salary]) => (
                        <div key={level} className="flex items-center justify-between text-sm">
                          <span className="text-gray-600 capitalize">{level.replace(/_/g, ' ')}</span>
                          <span className="font-medium">{formatSalary(salary)}</span>
                        </div>
                      ))}
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
              <div className={`text-5xl font-bold ${getScoreColor(opportunityData.total_score)} mb-2`}>
                {opportunityData.total_score}%
              </div>
              <div className="text-lg font-medium text-orange-800">{opportunityData.interpretation}</div>
              {opportunityData.target_role && (
                <p className="text-sm text-orange-600 mt-1 capitalize">{opportunityData.target_role.replace(/_/g, ' ')}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <h3 className="font-medium text-gray-900 mb-3">Match Factors</h3>
              <div className="space-y-2">
                {opportunityData.components && Object.entries(opportunityData.components).map(([name, score]) => (
                  <div key={name}>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-700 capitalize">{name.replace(/_/g, ' ')}</span>
                      <span className="font-medium">{score}/100</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-orange-500 h-2 rounded-full transition-all"
                        style={{ width: `${score}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {opportunityData.missing_skills?.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Skills to Develop</h4>
                  <div className="flex flex-wrap gap-2">
                    {opportunityData.missing_skills.map((skill: string, i: number) => (
                      <span key={i} className="px-2 py-1 bg-red-50 text-red-700 text-xs rounded-full">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {opportunityData.matching_skills?.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Your In-Demand Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {opportunityData.matching_skills.map((skill: string, i: number) => (
                      <span key={i} className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded-full">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {opportunityData.recommendations?.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Recommendations</h4>
                  <ul className="space-y-1 text-sm text-gray-600">
                    {opportunityData.recommendations.slice(0, 3).map((rec: string, i: number) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-primary-600">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
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
