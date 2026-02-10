import { useState, useCallback } from 'react';
import { Upload, FileText, X, Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { resumeApi, authApi } from '../../lib/api';
import type { Resume } from '../../types';

interface ResumeUploadStepProps {
  onNext: (resume: Resume | null, atsScore: number) => void;
  onSkip: () => void;
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
}

type UploadState = 'idle' | 'uploading' | 'analyzing' | 'complete' | 'error';

const ACCEPTED_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

const ATS_CATEGORIES = [
  { label: 'Achievements', max: 25, key: 'achievements' },
  { label: 'Compatibility', max: 15, key: 'compatibility' },
  { label: 'Keywords', max: 15, key: 'keywords' },
  { label: 'Formatting', max: 15, key: 'formatting' },
  { label: 'Progression', max: 15, key: 'progression' },
  { label: 'Completeness', max: 10, key: 'completeness' },
  { label: 'Fit', max: 5, key: 'fit' },
];

export function ResumeUploadStep({ onNext, onSkip }: ResumeUploadStepProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState<UploadState>('idle');
  const [uploadedResume, setUploadedResume] = useState<Resume | null>(null);
  const [atsData, setAtsData] = useState<ATSAnalysisData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const validateFile = (file: File): string | null => {
    if (!ACCEPTED_TYPES.includes(file.type)) {
      return 'Please upload a PDF, DOC, or DOCX file';
    }
    if (file.size > MAX_FILE_SIZE) {
      return 'File size must be less than 10MB';
    }
    return null;
  };

  const handleFile = useCallback((file: File) => {
    setError(null);
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }
    setSelectedFile(file);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleUpload = async () => {
    if (!selectedFile) return;

    setError(null);
    setUploadState('uploading');

    try {
      // 1. Upload the resume
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('is_master', 'true');

      const response = await resumeApi.upload(formData);
      const resume = response.data.data?.resume || response.data.resume;
      setUploadedResume(resume);

      setUploadState('analyzing');

      // 2. Get ATS analysis
      const analysisRes = await resumeApi.getAnalysis(resume.id);
      const analysis = analysisRes.data.data?.ats_analysis || analysisRes.data.ats_analysis;
      setAtsData(analysis);

      // 3. Update onboarding step
      await authApi.updateProfile({ onboarding_step: 5 });

      setUploadState('complete');
    } catch (err) {
      console.error('Upload error:', err);
      setError('Failed to upload or analyze resume. Please try again.');
      setUploadState('error');
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setError(null);
    setUploadState('idle');
    setAtsData(null);
    setUploadedResume(null);
  };

  const handleContinue = () => {
    onNext(uploadedResume, atsData?.total_score || 0);
  };

  const handleSkip = async () => {
    try {
      await authApi.updateProfile({ onboarding_step: 5 });
    } catch {
      // continue anyway
    }
    onSkip();
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-primary-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-primary-100';
    if (score >= 40) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Needs Improvement';
    return 'Critical Issues';
  };

  // Uploading state
  if (uploadState === 'uploading') {
    return (
      <div className="text-center py-12">
        <Loader2 className="w-12 h-12 text-primary-600 mx-auto mb-4 animate-spin" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Uploading your resume...</h2>
        <p className="text-gray-600">This will just take a moment</p>
      </div>
    );
  }

  // Analyzing state
  if (uploadState === 'analyzing') {
    return (
      <div className="text-center py-12">
        <Loader2 className="w-12 h-12 text-primary-600 mx-auto mb-4 animate-spin" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Analyzing with ATS scoring...</h2>
        <p className="text-gray-600">This takes 2–3 seconds</p>
      </div>
    );
  }

  // ATS Results state
  if (uploadState === 'complete' && atsData) {
    const score = atsData.total_score;

    return (
      <div>
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Your ATS Score</h2>
          <p className="text-gray-600">Here's how your resume performs with Applicant Tracking Systems</p>
        </div>

        {/* Overall score */}
        <div className={`${getScoreBgColor(score)} rounded-xl p-8 text-center mb-8`}>
          <div className={`text-5xl font-bold ${getScoreColor(score)} mb-1`}>
            {score}
            <span className="text-xl">/100</span>
          </div>
          <div className={`text-lg font-medium ${getScoreColor(score)}`}>
            {getScoreLabel(score)}
          </div>
        </div>

        {/* 7-category breakdown */}
        <div className="space-y-2 mb-8">
          {ATS_CATEGORIES.map(cat => {
            const val = atsData.components[cat.key as keyof typeof atsData.components] || 0;
            return (
              <div key={cat.key} className="flex items-center gap-3">
                <div className="w-28 text-sm text-gray-600">{cat.label}</div>
                <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-primary-500 to-purple-500 rounded-full"
                    style={{ width: `${(val / cat.max) * 100}%` }}
                  />
                </div>
                <div className="w-12 text-sm text-right text-gray-700">
                  {val}/{cat.max}
                </div>
              </div>
            );
          })}
        </div>

        {/* Encouragement */}
        <div className="flex items-start gap-3 bg-primary-50 border border-primary-200 rounded-lg p-4 mb-8">
          <CheckCircle className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
          <p className="text-primary-800 text-sm">
            Don't worry! Jobezie will help you improve your score with AI-powered suggestions and tailored recommendations.
          </p>
        </div>

        <button
          onClick={handleContinue}
          className="w-full py-3 bg-gradient-to-r from-primary-600 to-purple-600 text-white rounded-xl font-semibold hover:opacity-90 transition"
        >
          Continue →
        </button>
      </div>
    );
  }

  // Default: upload zone
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        Upload your current resume
      </h2>
      <p className="text-gray-600 mb-8">
        We'll analyze it and give you an instant ATS compatibility score
      </p>

      {/* Upload zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all cursor-pointer ${
          isDragOver
            ? 'border-primary-500 bg-primary-50'
            : selectedFile
            ? 'border-green-500 bg-green-50'
            : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
        }`}
      >
        {selectedFile ? (
          <div className="flex items-center justify-center gap-4">
            <FileText className="w-12 h-12 text-green-600" />
            <div className="text-left">
              <p className="font-medium text-gray-900">{selectedFile.name}</p>
              <p className="text-sm text-gray-500">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <button
              onClick={(e) => { e.stopPropagation(); handleRemoveFile(); }}
              className="p-2 text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        ) : (
          <>
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="font-semibold text-gray-900 mb-1">
              Drag & drop your resume here
            </p>
            <p className="text-sm text-gray-500 mb-3">or click to browse</p>
            <p className="text-xs text-gray-400">PDF, DOCX (max 10MB)</p>
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={handleFileSelect}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
          </>
        )}
      </div>

      {error && (
        <div className="flex items-start gap-2 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mt-4">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      <div className="flex gap-4 mt-6">
        <button
          onClick={handleSkip}
          className="flex-1 py-3 border border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition"
        >
          Skip for now
        </button>
        <button
          onClick={handleUpload}
          disabled={!selectedFile}
          className="flex-1 py-3 bg-gradient-to-r from-primary-600 to-purple-600 text-white rounded-xl font-semibold disabled:opacity-40 disabled:cursor-not-allowed hover:opacity-90 transition flex items-center justify-center gap-2"
        >
          Upload & Analyze
        </button>
      </div>
    </div>
  );
}
