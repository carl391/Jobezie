import { useState, useEffect } from 'react';
import { ChevronLeft, Loader2, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { resumeApi, authApi } from '../../lib/api';
import type { Resume } from '../../types';

interface ATSResultsStepProps {
  onNext: (score: number) => void;
  onBack: () => void;
  resume: Resume | null;
}

interface ATSIssue {
  severity: 'high' | 'medium' | 'low';
  message: string;
  suggestion: string;
}

interface ATSAnalysisData {
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
}

export function ATSResultsStep({ onNext, onBack, resume }: ATSResultsStepProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [atsData, setAtsData] = useState<ATSAnalysisData | null>(null);
  const [issues, setIssues] = useState<ATSIssue[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchScore = async () => {
      if (!resume) {
        // No resume uploaded, skip to next step with 0 score
        onNext(0);
        return;
      }

      try {
        setIsLoading(true);
        // Use getAnalysis endpoint which doesn't require job keywords
        const response = await resumeApi.getAnalysis(resume.id);
        const analysisData = response.data.ats_analysis;

        setAtsData(analysisData);

        // Generate issues based on score components
        const generatedIssues: ATSIssue[] = [];

        if (analysisData.components.keywords < 60) {
          generatedIssues.push({
            severity: 'high',
            message: 'Missing key industry keywords',
            suggestion: 'Add relevant keywords from job descriptions you\'re targeting',
          });
        }

        if (analysisData.components.formatting < 60) {
          generatedIssues.push({
            severity: 'medium',
            message: 'Formatting issues detected',
            suggestion: 'Use standard section headers and consistent bullet formatting',
          });
        }

        if (analysisData.components.achievements < 60) {
          generatedIssues.push({
            severity: 'high',
            message: 'Missing quantified achievements',
            suggestion: 'Add metrics and numbers to demonstrate impact (%, $, time saved)',
          });
        }

        if (analysisData.components.completeness < 60) {
          generatedIssues.push({
            severity: 'low',
            message: 'Some sections could be improved',
            suggestion: 'Ensure you have clear sections for Summary, Experience, Education, and Skills',
          });
        }

        // Add recommendations from the analysis
        if (analysisData.recommendations) {
          analysisData.recommendations.forEach((rec: string) => {
            if (generatedIssues.length < 3) {
              generatedIssues.push({
                severity: 'medium',
                message: rec,
                suggestion: '',
              });
            }
          });
        }

        setIssues(generatedIssues.slice(0, 3)); // Show top 3 issues
      } catch (err) {
        console.error('Error fetching ATS score:', err);
        setError('Failed to analyze resume. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchScore();
  }, [resume, onNext]);

  const handleContinue = async () => {
    try {
      await authApi.updateProfile({ onboarding_step: 4 });
      onNext(atsData?.total_score || 0);
    } catch (err) {
      console.error('Error updating onboarding step:', err);
      onNext(atsData?.total_score || 0);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number): string => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-blue-100';
    if (score >= 40) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const getScoreLabel = (score: number): string => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Needs Improvement';
    return 'Critical Issues';
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'medium':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-blue-500" />;
    }
  };

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <Loader2 className="w-12 h-12 text-primary-600 mx-auto mb-4 animate-spin" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Analyzing your resume...
        </h2>
        <p className="text-gray-600">
          This usually takes just a few seconds
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <button
          onClick={onBack}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ChevronLeft className="w-5 h-5 mr-1" />
          Back
        </button>

        <div className="text-center py-8">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">{error}</h2>
          <button onClick={onBack} className="btn btn-primary mt-4">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const score = atsData?.total_score || 0;

  return (
    <div>
      <button
        onClick={onBack}
        className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
      >
        <ChevronLeft className="w-5 h-5 mr-1" />
        Back
      </button>

      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Your ATS Score
        </h2>
        <p className="text-gray-600">
          Here's how your resume performs with Applicant Tracking Systems
        </p>
      </div>

      {/* Score display */}
      <div className={`${getScoreBgColor(score)} rounded-xl p-8 text-center mb-8`}>
        <div className={`text-6xl font-bold ${getScoreColor(score)} mb-2`}>
          {score}
          <span className="text-2xl">/100</span>
        </div>
        <div className={`text-lg font-medium ${getScoreColor(score)}`}>
          {getScoreLabel(score)}
        </div>
      </div>

      {/* Issues */}
      {issues.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-4">Top Issues to Fix:</h3>
          <div className="space-y-4">
            {issues.map((issue, index) => (
              <div key={index} className="flex gap-3">
                {getSeverityIcon(issue.severity)}
                <div>
                  <p className="font-medium text-gray-900">{issue.message}</p>
                  <p className="text-sm text-gray-600">{issue.suggestion}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Encouragement message */}
      <div className="flex items-start gap-3 bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
        <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <p className="text-blue-800 text-sm">
          Don't worry! We'll help you improve your score with AI-powered suggestions
          and tailored recommendations for each job application.
        </p>
      </div>

      <button onClick={handleContinue} className="btn btn-primary w-full py-3">
        Continue
      </button>
    </div>
  );
}
