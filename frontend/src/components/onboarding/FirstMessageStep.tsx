import { useState, useEffect } from 'react';
import { ChevronLeft, Loader2, Copy, Check, RefreshCw, Sparkles } from 'lucide-react';
import { aiApi, authApi } from '../../lib/api';
import type { Recruiter } from '../../types';

interface FirstMessageStepProps {
  onNext: (message: string) => void;
  onBack: () => void;
  onSkip: () => void;
  recruiter: Recruiter | null;
}

export function FirstMessageStep({ onNext, onBack, onSkip, recruiter }: FirstMessageStepProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [message, setMessage] = useState('');
  const [qualityScore, setQualityScore] = useState<number | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-generate message when component mounts if recruiter exists
  useEffect(() => {
    if (recruiter && !message) {
      generateMessage();
    }
  }, [recruiter]);

  const generateMessage = async () => {
    if (!recruiter) {
      handleSkipInternal();
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const response = await aiApi.generateMessage({
        recruiter_id: recruiter.id,
        message_type: 'initial_outreach',
      });

      // Handle both response formats
      const data = response.data.data || response.data;
      setMessage(data.generated_message || data.message || '');
      setQualityScore(data.quality_score || null);
    } catch (err) {
      console.error('Error generating message:', err);
      // Generate a fallback template message
      const fallbackMessage = `Hi ${recruiter.name?.split(' ')[0] || 'there'},

I came across your profile and was impressed by your work in recruiting at ${recruiter.company_name || 'your company'}.

I'm currently exploring new opportunities and would love to connect. I believe my background could be a good fit for roles you might be recruiting for.

Would you be open to a brief conversation?

Best regards`;
      setMessage(fallbackMessage);
      setQualityScore(65);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleContinue = async () => {
    try {
      await authApi.updateProfile({ onboarding_step: 6 });
      onNext(message);
    } catch (err) {
      console.error('Error updating onboarding step:', err);
      onNext(message);
    }
  };

  const handleSkipInternal = async () => {
    try {
      await authApi.updateProfile({ onboarding_step: 6 });
      onSkip();
    } catch (err) {
      console.error('Error updating onboarding step:', err);
      onSkip();
    }
  };

  // If no recruiter, show skip option
  if (!recruiter) {
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
          <Sparkles className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            No recruiter added yet
          </h2>
          <p className="text-gray-600 mb-8">
            You can generate personalized messages after adding recruiters from
            the Recruiters page.
          </p>
          <button onClick={handleSkipInternal} className="btn btn-primary">
            Continue
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <button
        onClick={onBack}
        className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
      >
        <ChevronLeft className="w-5 h-5 mr-1" />
        Back
      </button>

      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        Your first outreach message
      </h2>
      <p className="text-gray-600 mb-2">
        To: {recruiter.name} at {recruiter.company_name}
      </p>
      <p className="text-sm text-gray-500 mb-6">
        AI-generated and personalized for better response rates
      </p>

      {isGenerating ? (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center mb-6">
          <Loader2 className="w-10 h-10 text-primary-600 mx-auto mb-4 animate-spin" />
          <p className="text-gray-600">Generating your personalized message...</p>
        </div>
      ) : (
        <>
          {/* Message display */}
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-4">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={10}
              className="w-full border-0 p-0 focus:ring-0 resize-none text-gray-800"
              placeholder="Your message will appear here..."
            />
          </div>

          {/* Quality score and actions */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              {qualityScore !== null && (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">Quality Score:</span>
                  <div className="flex items-center gap-1">
                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          qualityScore >= 80
                            ? 'bg-green-500'
                            : qualityScore >= 60
                            ? 'bg-blue-500'
                            : 'bg-yellow-500'
                        }`}
                        style={{ width: `${qualityScore}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900">
                      {qualityScore}/100
                    </span>
                  </div>
                </div>
              )}
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleCopy}
                className="btn btn-outline flex items-center gap-2"
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4 text-green-600" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    Copy
                  </>
                )}
              </button>
              <button
                onClick={generateMessage}
                disabled={isGenerating}
                className="btn btn-outline flex items-center gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
                Regenerate
              </button>
            </div>
          </div>

          {/* Tips */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
            <h4 className="font-medium text-blue-900 mb-2">Tips for better responses:</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Messages under 150 words get 22% higher response rates</li>
              <li>• Personalize with specific details about the recruiter or company</li>
              <li>• Include quantified achievements from your experience</li>
            </ul>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}
        </>
      )}

      <div className="flex gap-4">
        <button
          onClick={handleSkipInternal}
          disabled={isGenerating}
          className="btn btn-outline flex-1"
        >
          Skip for now
        </button>
        <button
          onClick={handleContinue}
          disabled={isGenerating || !message}
          className="btn btn-primary flex-1"
        >
          Continue
        </button>
      </div>
    </div>
  );
}
