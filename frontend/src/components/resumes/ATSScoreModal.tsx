import { useState, useEffect } from 'react';
import {
  Loader2,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  XCircle,
  TrendingUp,
  FileText,
  Target,
  Sparkles,
  Copy,
  Check,
  Save,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { toast } from 'sonner';
import { Modal, ModalFooter } from '../ui/Modal';
import { ScoreCircle, ScoreBar } from '../ui/ScoreCircle';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/Tabs';
import { resumeApi, aiApi } from '../../lib/api';
import type { Resume, ATSBreakdown } from '../../types';

interface ATSScoreData {
  total_score: number;
  components: {
    compatibility: number;
    keywords: number;
    achievements: number;
    formatting: number;
    progression: number;
    completeness: number;
    fit: number;
  };
  recommendations?: string[];
  weak_sections?: string[];
  missing_keywords?: string[];
}

interface ATSScoreModalProps {
  isOpen: boolean;
  onClose: () => void;
  resumeId: string;
  resumeName: string;
  initialScore?: number;
  onScoreUpdated?: (score: number) => void;
}

interface DetailedAnalysis {
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  keyword_analysis?: {
    present: string[];
    missing: string[];
  };
}

export function ATSScoreModal({
  isOpen,
  onClose,
  resumeId,
  resumeName,
  initialScore,
  onScoreUpdated,
}: ATSScoreModalProps) {
  const [score, setScore] = useState<ATSScoreData | null>(null);
  const [analysis, setAnalysis] = useState<DetailedAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRescoring, setIsRescoring] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizedResume, setOptimizedResume] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [copied, setCopied] = useState(false);
  const [jobDescription, setJobDescription] = useState('');
  const [showJobInput, setShowJobInput] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && resumeId) {
      fetchScore();
    }
  }, [isOpen, resumeId]);

  const fetchScore = async (jobDesc?: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const analysisRes = await resumeApi.getAnalysis(resumeId);
      const analysisData = analysisRes.data?.data?.ats_analysis || analysisRes.data?.ats_analysis;

      if (analysisData) {
        const scoreData: ATSScoreData = {
          total_score: analysisData.total_score,
          components: analysisData.components,
          recommendations: analysisData.recommendations,
          weak_sections: analysisData.weak_sections,
          missing_keywords: analysisData.missing_keywords,
        };
        setScore(scoreData);
        setAnalysis({
          strengths: [],
          weaknesses: analysisData.weak_sections || [],
          recommendations: analysisData.recommendations || [],
        });
        onScoreUpdated?.(analysisData.total_score);
      }
    } catch (err) {
      console.error('Error fetching ATS score:', err);
      setError('Failed to load ATS score');
    } finally {
      setIsLoading(false);
      setIsRescoring(false);
    }
  };

  const handleRescore = async () => {
    setIsRescoring(true);
    setShowJobInput(false);
    await fetchScore(jobDescription || undefined);
  };

  const handleOptimize = async () => {
    setIsOptimizing(true);
    setOptimizedResume(null);
    setIsSaved(false);

    try {
      const response = await aiApi.optimizeResume({
        resume_id: resumeId,
        target_role: jobDescription || undefined,
        weak_sections: score?.weak_sections,
      });

      const resData = response.data?.data || response.data;
      const raw = resData?.ai_suggestions || resData?.suggestions || '';
      const text = Array.isArray(raw) ? raw.join('\n') : String(raw);
      setOptimizedResume(text || null);
    } catch (err) {
      console.error('Error optimizing resume:', err);
      setOptimizedResume(null);
      setError('Failed to generate optimized resume. Please try again.');
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleCopy = async () => {
    if (!optimizedResume) return;
    try {
      await navigator.clipboard.writeText(optimizedResume);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleSave = async () => {
    if (!optimizedResume) return;
    setIsSaving(true);
    try {
      await resumeApi.tailor(
        resumeId,
        jobDescription || 'ATS Optimized',
        undefined,
        optimizedResume,
      );
      setIsSaved(true);
      toast.success('Optimized resume saved! You can find it in your Resumes.');
    } catch (err) {
      console.error('Error saving optimized resume:', err);
      toast.error('Failed to save optimized resume.');
    } finally {
      setIsSaving(false);
    }
  };

  const getScoreIcon = (percentage: number) => {
    if (percentage >= 80) return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (percentage >= 60) return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    return <XCircle className="w-5 h-5 text-red-500" />;
  };

  const getScoreLabel = (percentage: number) => {
    if (percentage >= 80) return 'Excellent';
    if (percentage >= 60) return 'Good';
    if (percentage >= 40) return 'Needs Improvement';
    return 'Poor';
  };

  const scoreCategories = score ? [
    { label: 'ATS Compatibility', score: score.components.compatibility, description: 'How well the resume parses in ATS systems' },
    { label: 'Keywords', score: score.components.keywords, description: 'Relevant industry keywords and phrases' },
    { label: 'Achievements', score: score.components.achievements, description: 'Quantified accomplishments and impact' },
    { label: 'Formatting', score: score.components.formatting, description: 'Clear sections and professional layout' },
    { label: 'Career Progression', score: score.components.progression, description: 'Career growth and advancement' },
    { label: 'Completeness', score: score.components.completeness, description: 'All essential resume sections present' },
    { label: 'Role Fit', score: score.components.fit, description: 'Alignment with target role' },
  ] : [];

  if (isLoading) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="ATS Score Analysis" size="lg">
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="w-10 h-10 text-primary-600 animate-spin mb-4" />
          <p className="text-gray-600">Analyzing your resume...</p>
          <p className="text-sm text-gray-500 mt-1">This may take a moment</p>
        </div>
      </Modal>
    );
  }

  if (error || !score) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="ATS Score Analysis" size="lg">
        <div className="text-center py-12">
          <XCircle className="w-12 h-12 mx-auto text-red-400 mb-4" />
          <p className="text-red-600">{error || 'Unable to analyze resume'}</p>
          <div className="mt-4 space-x-3">
            <button onClick={() => fetchScore()} className="btn btn-primary">
              Try Again
            </button>
            <button onClick={onClose} className="btn btn-outline">
              Close
            </button>
          </div>
        </div>
      </Modal>
    );
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="" size="lg" showCloseButton>
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 text-gray-600 mb-4">
            <FileText className="w-5 h-5" />
            <span className="font-medium">{resumeName}</span>
          </div>

          <div className="inline-flex flex-col items-center">
            <ScoreCircle score={score.total_score} size="xl" />
            <div className="mt-3 flex items-center gap-2">
              {getScoreIcon(score.total_score)}
              <span className="text-lg font-semibold text-gray-900">
                {getScoreLabel(score.total_score)}
              </span>
            </div>
          </div>
        </div>

        {/* Job Description targeting */}
        {showJobInput ? (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <Target className="w-5 h-5 text-blue-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-blue-900 mb-2">
                  Target a specific job
                </p>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description here to get a targeted ATS score..."
                  rows={4}
                  className="input resize-none mb-3"
                />
                <div className="flex gap-2">
                  <button
                    onClick={handleRescore}
                    disabled={!jobDescription.trim()}
                    className="btn btn-primary btn-sm"
                  >
                    <TrendingUp className="w-4 h-4 mr-1" />
                    Analyze Match
                  </button>
                  <button
                    onClick={() => setShowJobInput(false)}
                    className="btn btn-outline btn-sm"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex justify-center gap-3">
            <button
              onClick={() => setShowJobInput(true)}
              className="btn btn-outline btn-sm"
            >
              <Target className="w-4 h-4 mr-1" />
              Target Job
            </button>
            <button
              onClick={() => handleRescore()}
              disabled={isRescoring}
              className="btn btn-outline btn-sm"
            >
              {isRescoring ? (
                <Loader2 className="w-4 h-4 animate-spin mr-1" />
              ) : (
                <RefreshCw className="w-4 h-4 mr-1" />
              )}
              Rescore
            </button>
          </div>
        )}

        {/* Tabs for different views */}
        <Tabs defaultValue="breakdown">
          <TabsList className="w-full">
            <TabsTrigger value="breakdown">Score Breakdown</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
            {analysis?.keyword_analysis && (
              <TabsTrigger value="keywords">Keywords</TabsTrigger>
            )}
          </TabsList>

          <TabsContent value="breakdown" className="mt-4">
            <div className="space-y-4">
              {scoreCategories.map((category) => (
                <div key={category.label}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">
                      {category.label}
                    </span>
                    <span className={`text-sm font-bold ${
                      category.score >= 80 ? 'text-green-600' :
                      category.score >= 60 ? 'text-blue-600' :
                      category.score >= 40 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {category.score}%
                    </span>
                  </div>
                  <ScoreBar score={category.score} showValue={false} size="sm" />
                  <p className="text-xs text-gray-500 mt-1">{category.description}</p>
                </div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="analysis" className="mt-4">
            <div className="space-y-4">
              {/* Strengths */}
              {analysis?.strengths && analysis.strengths.length > 0 && (
                <div>
                  <h4 className="flex items-center gap-2 text-sm font-semibold text-green-700 mb-2">
                    <CheckCircle className="w-4 h-4" />
                    Strengths
                  </h4>
                  <ul className="space-y-1.5">
                    {analysis.strengths.map((item, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                        <span className="text-green-500 mt-1">+</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Weaknesses */}
              {analysis?.weaknesses && analysis.weaknesses.length > 0 && (
                <div>
                  <h4 className="flex items-center gap-2 text-sm font-semibold text-red-700 mb-2">
                    <AlertTriangle className="w-4 h-4" />
                    Areas to Improve
                  </h4>
                  <ul className="space-y-1.5">
                    {analysis.weaknesses.map((item, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                        <span className="text-red-500 mt-1">-</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommendations */}
              {analysis?.recommendations && analysis.recommendations.length > 0 && (
                <div>
                  <h4 className="flex items-center gap-2 text-sm font-semibold text-blue-700 mb-2">
                    <Sparkles className="w-4 h-4" />
                    Recommendations
                  </h4>
                  <ul className="space-y-1.5">
                    {analysis.recommendations.map((item, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-gray-700 bg-blue-50 rounded-lg p-2">
                        <span className="text-blue-500 font-bold">{index + 1}.</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {!analysis && (
                <div className="text-center py-8 text-gray-500">
                  <p>Detailed analysis not available</p>
                  <p className="text-sm mt-1">Target a specific job to get personalized recommendations</p>
                </div>
              )}
            </div>
          </TabsContent>

          {analysis?.keyword_analysis && (
            <TabsContent value="keywords" className="mt-4">
              <div className="space-y-4">
                {/* Present keywords */}
                {analysis.keyword_analysis.present.length > 0 && (
                  <div>
                    <h4 className="flex items-center gap-2 text-sm font-semibold text-green-700 mb-2">
                      <CheckCircle className="w-4 h-4" />
                      Keywords Found ({analysis.keyword_analysis.present.length})
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {analysis.keyword_analysis.present.map((keyword, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Missing keywords */}
                {analysis.keyword_analysis.missing.length > 0 && (
                  <div>
                    <h4 className="flex items-center gap-2 text-sm font-semibold text-red-700 mb-2">
                      <XCircle className="w-4 h-4" />
                      Missing Keywords ({analysis.keyword_analysis.missing.length})
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {analysis.keyword_analysis.missing.map((keyword, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded-full"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      Consider adding these keywords to improve your match rate
                    </p>
                  </div>
                )}
              </div>
            </TabsContent>
          )}
        </Tabs>

        {/* AI Optimized Resume */}
        {optimizedResume && (
          <div className="border border-purple-200 rounded-lg overflow-hidden">
            <div className="flex items-center justify-between bg-purple-50 px-4 py-3 border-b border-purple-200">
              <h4 className="flex items-center gap-2 text-sm font-semibold text-purple-700">
                <Sparkles className="w-4 h-4" />
                AI Optimized Resume
              </h4>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1 px-2 py-1 text-xs text-purple-600 hover:bg-purple-100 rounded transition-colors"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
                <button
                  onClick={handleSave}
                  disabled={isSaving || isSaved}
                  className="flex items-center gap-1 px-2 py-1 text-xs text-purple-600 hover:bg-purple-100 rounded transition-colors disabled:opacity-50"
                >
                  {isSaving ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : isSaved ? (
                    <Check className="w-3.5 h-3.5 text-green-500" />
                  ) : (
                    <Save className="w-3.5 h-3.5" />
                  )}
                  {isSaving ? 'Saving...' : isSaved ? 'Saved' : 'Save'}
                </button>
              </div>
            </div>
            <div className="p-4 max-h-96 overflow-y-auto">
              <div className="prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5 prose-headings:my-2">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{optimizedResume}</ReactMarkdown>
              </div>
            </div>
          </div>
        )}

        <ModalFooter>
          <button onClick={onClose} className="btn btn-outline">
            Close
          </button>
          <button
            onClick={handleOptimize}
            disabled={isOptimizing}
            className="btn btn-primary"
          >
            {isOptimizing ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Sparkles className="w-4 h-4 mr-2" />
            )}
            {isOptimizing ? 'Optimizing...' : 'AI Optimize'}
          </button>
        </ModalFooter>
      </div>
    </Modal>
  );
}
