import { useEffect, useState } from 'react';
import { Check, Loader2, PartyPopper } from 'lucide-react';
import { authApi } from '../../lib/api';

interface CompleteStepProps {
  onComplete: () => void;
  isLoading: boolean;
  atsScore: number | null;
  hasRecruiter: boolean;
  hasMessage: boolean;
}

export function CompleteStep({
  onComplete,
  isLoading,
  atsScore,
  hasRecruiter,
  hasMessage,
}: CompleteStepProps) {
  const [showConfetti, setShowConfetti] = useState(false);

  useEffect(() => {
    // Mark onboarding as complete
    const markComplete = async () => {
      try {
        await authApi.updateProfile({
          onboarding_step: 7,
          onboarding_completed: true,
        });
      } catch (err) {
        console.error('Error marking onboarding complete:', err);
      }
    };

    markComplete();

    // Show confetti animation
    setShowConfetti(true);
    const timer = setTimeout(() => setShowConfetti(false), 3000);
    return () => clearTimeout(timer);
  }, []);

  // Calculate readiness score based on completed steps
  const calculateReadiness = () => {
    let score = 20; // Base score for completing onboarding

    if (atsScore !== null && atsScore > 0) {
      score += 25; // Resume uploaded
      if (atsScore >= 60) score += 10; // Good ATS score bonus
    }

    if (hasRecruiter) {
      score += 25; // First recruiter added
    }

    if (hasMessage) {
      score += 10; // First message generated
    }

    return Math.min(score, 100);
  };

  const readinessScore = calculateReadiness();

  const completedItems = [
    { label: 'Profile created', completed: true },
    {
      label: atsScore !== null && atsScore > 0 ? `Resume uploaded (ATS: ${atsScore})` : 'Resume uploaded',
      completed: atsScore !== null && atsScore > 0,
    },
    { label: 'First recruiter added', completed: hasRecruiter },
    { label: 'First message generated', completed: hasMessage },
  ];

  const nextSteps = [
    { label: 'Build recruiter pipeline (0/5)', completed: false },
    { label: 'Send first message', completed: false },
    { label: 'Optimize your LinkedIn profile', completed: false },
  ];

  return (
    <div className="text-center">
      {/* Confetti effect placeholder - in production, use a library like react-confetti */}
      {showConfetti && (
        <div className="fixed inset-0 pointer-events-none flex items-center justify-center">
          <PartyPopper className="w-24 h-24 text-primary-500 animate-bounce" />
        </div>
      )}

      <div className="mb-8">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <Check className="w-10 h-10 text-green-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-3">
          You're all set!
        </h1>
        <p className="text-lg text-gray-600">
          Your Jobezie account is ready to help you land your dream job.
        </p>
      </div>

      {/* Readiness score */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8 max-w-md mx-auto">
        <h2 className="font-semibold text-gray-900 mb-4">
          Career Readiness: {readinessScore}%
        </h2>
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden mb-6">
          <div
            className="h-full bg-primary-600 transition-all duration-500"
            style={{ width: `${readinessScore}%` }}
          />
        </div>

        {/* Completed items */}
        <div className="space-y-3 text-left mb-6">
          {completedItems.map((item, index) => (
            <div key={index} className="flex items-center gap-3">
              {item.completed ? (
                <div className="w-5 h-5 bg-green-100 rounded-full flex items-center justify-center">
                  <Check className="w-3 h-3 text-green-600" />
                </div>
              ) : (
                <div className="w-5 h-5 border-2 border-gray-300 rounded-full" />
              )}
              <span
                className={item.completed ? 'text-gray-900' : 'text-gray-500'}
              >
                {item.label}
              </span>
            </div>
          ))}
        </div>

        {/* Next steps */}
        <div className="border-t border-gray-200 pt-4">
          <h3 className="text-sm font-medium text-gray-500 mb-3">Next steps:</h3>
          <div className="space-y-2 text-left">
            {nextSteps.map((item, index) => (
              <div key={index} className="flex items-center gap-3">
                <div className="w-5 h-5 border-2 border-gray-300 rounded-full" />
                <span className="text-gray-500 text-sm">{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <button
        onClick={onComplete}
        disabled={isLoading}
        className="btn btn-primary px-8 py-3 text-lg flex items-center justify-center gap-2 mx-auto"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Loading...
          </>
        ) : (
          'Go to Dashboard'
        )}
      </button>
    </div>
  );
}
