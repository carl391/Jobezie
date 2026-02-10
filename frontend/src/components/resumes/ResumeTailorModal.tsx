import { useState } from 'react';
import {
  X,
  Loader2,
  Target,
  Sparkles,
  Copy,
  Check,
  Building2,
  Briefcase,
} from 'lucide-react';
import { resumeApi } from '../../lib/api';

interface ResumeTailorModalProps {
  isOpen: boolean;
  onClose: () => void;
  resumeId: string;
  resumeName: string;
  onTailored?: () => void;
}

interface TailorResult {
  original_score: number;
  tailored_score: number;
  improvements: string[];
  tailored_content: {
    summary?: string;
    experience?: Array<{
      title: string;
      company: string;
      bullets: string[];
    }>;
    skills?: string[];
  };
  keywords_added: string[];
}

export function ResumeTailorModal({
  isOpen,
  onClose,
  resumeId,
  resumeName,
  onTailored,
}: ResumeTailorModalProps) {
  const [step, setStep] = useState<'input' | 'result'>('input');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    targetJobTitle: '',
    targetCompany: '',
    jobDescription: '',
  });

  const [result, setResult] = useState<TailorResult | null>(null);

  const handleTailor = async () => {
    if (!formData.targetJobTitle) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await resumeApi.tailor(
        resumeId,
        formData.targetJobTitle,
        formData.targetCompany || undefined,
        formData.jobDescription || undefined
      );
      setResult(response.data.data);
      setStep('result');
      onTailored?.();
    } catch (err: unknown) {
      console.error('Error tailoring resume:', err);
      const axiosErr = err as { response?: { data?: { message?: string } } };
      setError(axiosErr?.response?.data?.message || 'Failed to tailor resume. Please try again.');
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

  const handleReset = () => {
    setStep('input');
    setResult(null);
    setFormData({ targetJobTitle: '', targetCompany: '', jobDescription: '' });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={onClose} />

        <div className="relative bg-white rounded-xl shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                <Target className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Tailor Resume</h2>
                <p className="text-sm text-gray-500">{resumeName}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[70vh]">
            {step === 'input' ? (
              <div className="space-y-6">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-700">
                    Tailor your resume for a specific job to improve your chances.
                    The AI will optimize your resume content to match the target role.
                  </p>
                </div>

                <div>
                  <label className="label">Target Job Title *</label>
                  <div className="relative">
                    <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      className="input pl-10"
                      placeholder="e.g., Senior Software Engineer"
                      value={formData.targetJobTitle}
                      onChange={(e) => setFormData({ ...formData, targetJobTitle: e.target.value })}
                    />
                  </div>
                </div>

                <div>
                  <label className="label">Target Company</label>
                  <div className="relative">
                    <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      className="input pl-10"
                      placeholder="e.g., Google, Amazon"
                      value={formData.targetCompany}
                      onChange={(e) => setFormData({ ...formData, targetCompany: e.target.value })}
                    />
                  </div>
                </div>

                <div>
                  <label className="label">Job Description (Optional)</label>
                  <textarea
                    className="input min-h-[150px]"
                    placeholder="Paste the job description here for more accurate tailoring..."
                    value={formData.jobDescription}
                    onChange={(e) => setFormData({ ...formData, jobDescription: e.target.value })}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Including the job description helps the AI match keywords and requirements
                  </p>
                </div>

                {error && (
                  <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                    {error}
                  </div>
                )}

                <button
                  onClick={handleTailor}
                  disabled={!formData.targetJobTitle || isLoading}
                  className="btn btn-primary w-full"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Tailoring Resume...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Tailor Resume
                    </>
                  )}
                </button>
              </div>
            ) : result ? (
              <div className="space-y-6">
                {/* Score Comparison */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Original Score</p>
                    <p className="text-3xl font-bold text-gray-500">{result.original_score}%</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <p className="text-sm text-green-600 mb-1">Tailored Score</p>
                    <p className="text-3xl font-bold text-green-600">{result.tailored_score}%</p>
                  </div>
                </div>

                {/* Improvements Made */}
                {result.improvements && result.improvements.length > 0 && (
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h3 className="font-medium text-blue-800 mb-2">Improvements Made</h3>
                    <ul className="space-y-1">
                      {result.improvements.map((improvement, i) => (
                        <li key={i} className="text-sm text-blue-700 flex items-start gap-2">
                          <Check className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
                          {improvement}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Keywords Added */}
                {result.keywords_added && result.keywords_added.length > 0 && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Keywords Added</h3>
                    <div className="flex flex-wrap gap-2">
                      {result.keywords_added.map((kw, i) => (
                        <span key={i} className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                          {kw}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Tailored Content */}
                {result.tailored_content && (
                  <div className="space-y-4">
                    <h3 className="font-medium text-gray-900">Tailored Content</h3>

                    {result.tailored_content.summary && (
                      <div className="relative p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-700">Summary</span>
                          <button
                            onClick={() => copyToClipboard(result.tailored_content.summary!, 'summary')}
                            className="text-gray-400 hover:text-gray-600"
                          >
                            {copied === 'summary' ? (
                              <Check className="w-4 h-4 text-green-500" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )}
                          </button>
                        </div>
                        <p className="text-sm text-gray-700">{result.tailored_content.summary}</p>
                      </div>
                    )}

                    {result.tailored_content.experience && result.tailored_content.experience.length > 0 && (
                      <div className="space-y-3">
                        <span className="text-sm font-medium text-gray-700">Experience</span>
                        {result.tailored_content.experience.map((exp, i) => (
                          <div key={i} className="relative p-4 bg-gray-50 rounded-lg">
                            <div className="flex items-center justify-between mb-2">
                              <div>
                                <p className="font-medium text-gray-900">{exp.title}</p>
                                <p className="text-sm text-gray-500">{exp.company}</p>
                              </div>
                              <button
                                onClick={() => copyToClipboard(exp.bullets.join('\n'), `exp-${i}`)}
                                className="text-gray-400 hover:text-gray-600"
                              >
                                {copied === `exp-${i}` ? (
                                  <Check className="w-4 h-4 text-green-500" />
                                ) : (
                                  <Copy className="w-4 h-4" />
                                )}
                              </button>
                            </div>
                            <ul className="space-y-1">
                              {exp.bullets.map((bullet, j) => (
                                <li key={j} className="text-sm text-gray-700 flex items-start gap-2">
                                  <span className="text-gray-400 mt-1">•</span>
                                  {bullet}
                                </li>
                              ))}
                            </ul>
                          </div>
                        ))}
                      </div>
                    )}

                    {result.tailored_content.skills && result.tailored_content.skills.length > 0 && (
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-700">Skills</span>
                          <button
                            onClick={() => copyToClipboard(result.tailored_content.skills!.join(', '), 'skills')}
                            className="text-gray-400 hover:text-gray-600"
                          >
                            {copied === 'skills' ? (
                              <Check className="w-4 h-4 text-green-500" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )}
                          </button>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {result.tailored_content.skills.map((skill, i) => (
                            <span key={i} className="px-2 py-1 bg-primary-100 text-primary-700 text-sm rounded-full">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3 pt-4 border-t">
                  <button onClick={handleReset} className="btn btn-outline flex-1">
                    Tailor for Another Job
                  </button>
                  <button onClick={onClose} className="btn btn-primary flex-1">
                    Done
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
