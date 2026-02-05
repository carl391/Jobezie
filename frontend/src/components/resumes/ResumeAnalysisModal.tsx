import { useState, useEffect } from 'react';
import {
  X,
  Loader2,
  FileText,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Lightbulb,
  TrendingUp,
} from 'lucide-react';
import { resumeApi } from '../../lib/api';

interface ResumeAnalysisModalProps {
  isOpen: boolean;
  onClose: () => void;
  resumeId: string;
  resumeName: string;
}

interface AnalysisData {
  overall_score: number;
  sections: Array<{
    name: string;
    score: number;
    max_score: number;
    feedback: string;
  }>;
  strengths: string[];
  weaknesses: string[];
  keywords_found: string[];
  keywords_missing: string[];
}

interface SuggestionsData {
  suggestions: Array<{
    category: string;
    priority: 'high' | 'medium' | 'low';
    suggestion: string;
    example?: string;
  }>;
  quick_wins: string[];
}

export function ResumeAnalysisModal({
  isOpen,
  onClose,
  resumeId,
  resumeName,
}: ResumeAnalysisModalProps) {
  const [activeTab, setActiveTab] = useState<'analysis' | 'suggestions'>('analysis');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [suggestions, setSuggestions] = useState<SuggestionsData | null>(null);

  useEffect(() => {
    if (isOpen && resumeId) {
      fetchData();
    }
  }, [isOpen, resumeId]);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [analysisRes, suggestionsRes] = await Promise.all([
        resumeApi.getAnalysis(resumeId),
        resumeApi.getSuggestions(resumeId),
      ]);
      setAnalysis(analysisRes.data.data);
      setSuggestions(suggestionsRes.data.data);
    } catch (err) {
      console.error('Error fetching analysis:', err);
      setError('Failed to analyze resume. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  const getScoreColor = (score: number, max: number) => {
    const percentage = (score / max) * 100;
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number, max: number) => {
    const percentage = (score / max) * 100;
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-700';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700';
      case 'low':
        return 'bg-green-100 text-green-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={onClose} />

        <div className="relative bg-white rounded-xl shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-primary-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900">{resumeName}</h2>
                <p className="text-sm text-gray-500">Resume Analysis & Suggestions</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Tabs */}
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('analysis')}
              className={`flex-1 py-3 text-sm font-medium transition-colors ${
                activeTab === 'analysis'
                  ? 'text-primary-600 border-b-2 border-primary-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Analysis
            </button>
            <button
              onClick={() => setActiveTab('suggestions')}
              className={`flex-1 py-3 text-sm font-medium transition-colors ${
                activeTab === 'suggestions'
                  ? 'text-primary-600 border-b-2 border-primary-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Suggestions
            </button>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[60vh]">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary-600 mb-4" />
                <p className="text-gray-500">Analyzing your resume...</p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <p className="text-red-600">{error}</p>
                <button onClick={fetchData} className="btn btn-primary mt-4">
                  Try Again
                </button>
              </div>
            ) : activeTab === 'analysis' && analysis ? (
              <div className="space-y-6">
                {/* Overall Score */}
                <div className="text-center p-6 bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl">
                  <div className={`text-5xl font-bold mb-2 ${getScoreColor(analysis.overall_score, 100)}`}>
                    {analysis.overall_score}%
                  </div>
                  <p className="text-primary-800">Overall Resume Score</p>
                </div>

                {/* Section Scores */}
                {analysis.sections && analysis.sections.length > 0 && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-3">Section Breakdown</h3>
                    <div className="space-y-3">
                      {analysis.sections.map((section, idx) => (
                        <div key={idx}>
                          <div className="flex items-center justify-between text-sm mb-1">
                            <span className="text-gray-700">{section.name}</span>
                            <span className={`font-medium ${getScoreColor(section.score, section.max_score)}`}>
                              {section.score}/{section.max_score}
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full transition-all ${getScoreBg(section.score, section.max_score)}`}
                              style={{ width: `${(section.score / section.max_score) * 100}%` }}
                            />
                          </div>
                          {section.feedback && (
                            <p className="text-xs text-gray-500 mt-1">{section.feedback}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Strengths & Weaknesses */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {analysis.strengths && analysis.strengths.length > 0 && (
                    <div className="p-4 bg-green-50 rounded-lg">
                      <h4 className="font-medium text-green-800 mb-2 flex items-center gap-2">
                        <CheckCircle className="w-4 h-4" />
                        Strengths
                      </h4>
                      <ul className="space-y-1">
                        {analysis.strengths.map((s, i) => (
                          <li key={i} className="text-sm text-green-700 flex items-start gap-2">
                            <span className="text-green-500 mt-1">•</span>
                            {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {analysis.weaknesses && analysis.weaknesses.length > 0 && (
                    <div className="p-4 bg-red-50 rounded-lg">
                      <h4 className="font-medium text-red-800 mb-2 flex items-center gap-2">
                        <XCircle className="w-4 h-4" />
                        Areas to Improve
                      </h4>
                      <ul className="space-y-1">
                        {analysis.weaknesses.map((w, i) => (
                          <li key={i} className="text-sm text-red-700 flex items-start gap-2">
                            <span className="text-red-500 mt-1">•</span>
                            {w}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Keywords */}
                {(analysis.keywords_found?.length > 0 || analysis.keywords_missing?.length > 0) && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-3">Keywords Analysis</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {analysis.keywords_found && analysis.keywords_found.length > 0 && (
                        <div>
                          <p className="text-sm text-gray-600 mb-2">Found in Resume</p>
                          <div className="flex flex-wrap gap-2">
                            {analysis.keywords_found.map((kw, i) => (
                              <span key={i} className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                                {kw}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {analysis.keywords_missing && analysis.keywords_missing.length > 0 && (
                        <div>
                          <p className="text-sm text-gray-600 mb-2">Consider Adding</p>
                          <div className="flex flex-wrap gap-2">
                            {analysis.keywords_missing.map((kw, i) => (
                              <span key={i} className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                                {kw}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : activeTab === 'suggestions' && suggestions ? (
              <div className="space-y-6">
                {/* Quick Wins */}
                {suggestions.quick_wins && suggestions.quick_wins.length > 0 && (
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h3 className="font-medium text-blue-800 mb-3 flex items-center gap-2">
                      <TrendingUp className="w-5 h-5" />
                      Quick Wins
                    </h3>
                    <ul className="space-y-2">
                      {suggestions.quick_wins.map((win, i) => (
                        <li key={i} className="text-sm text-blue-700 flex items-start gap-2">
                          <Lightbulb className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
                          {win}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Detailed Suggestions */}
                {suggestions.suggestions && suggestions.suggestions.length > 0 && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-3">Detailed Suggestions</h3>
                    <div className="space-y-4">
                      {suggestions.suggestions.map((s, i) => (
                        <div key={i} className="p-4 bg-gray-50 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-gray-900">{s.category}</span>
                            <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getPriorityColor(s.priority)}`}>
                              {s.priority}
                            </span>
                          </div>
                          <p className="text-sm text-gray-700 mb-2">{s.suggestion}</p>
                          {s.example && (
                            <div className="mt-2 p-2 bg-white rounded border-l-2 border-primary-500">
                              <p className="text-xs text-gray-500 mb-1">Example:</p>
                              <p className="text-sm text-gray-700 italic">{s.example}</p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {!suggestions.quick_wins?.length && !suggestions.suggestions?.length && (
                  <div className="text-center py-8 text-gray-500">
                    <CheckCircle className="w-12 h-12 mx-auto mb-3 text-green-500" />
                    <p>Your resume looks great! No major improvements needed.</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <p>No data available</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
