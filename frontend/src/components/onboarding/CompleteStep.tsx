import { useEffect, useState } from 'react';
import { Check, Loader2, PartyPopper, TrendingUp } from 'lucide-react';
import { authApi, dashboardApi, laborMarketApi } from '../../lib/api';

interface OpportunityPreview {
  total_score: number;
  target_role: string;
  components: { user_match: number; shortage: number };
  interpretation: string;
}

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
  const [realReadiness, setRealReadiness] = useState<number | null>(null);
  const [opportunities, setOpportunities] = useState<OpportunityPreview[]>([]);

  useEffect(() => {
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

    const fetchReadiness = async () => {
      try {
        const res = await dashboardApi.getReadiness();
        const data = res.data.data || res.data;
        if (data?.total_score !== undefined) {
          setRealReadiness(Math.round(data.total_score));
        }
      } catch {
        // fallback handled below
      }
    };

    const fetchOpportunities = async () => {
      try {
        const res = await laborMarketApi.getOpportunity({});
        const data = res.data.data;
        if (data) {
          setOpportunities([data]);
        }
      } catch {
        // optional
      }
    };

    markComplete();
    fetchReadiness();
    fetchOpportunities();

    setShowConfetti(true);
    const timer = setTimeout(() => setShowConfetti(false), 3000);
    return () => clearTimeout(timer);
  }, []);

  const calculateReadiness = () => {
    let score = 20;
    if (atsScore !== null && atsScore > 0) {
      score += 25;
      if (atsScore >= 60) score += 10;
    }
    if (hasRecruiter) score += 25;
    if (hasMessage) score += 10;
    return Math.min(score, 100);
  };

  const readinessScore = realReadiness ?? calculateReadiness();

  const getScoreColor = (score: number) => {
    if (score >= 71) return 'text-green-600';
    if (score >= 41) return 'text-yellow-600';
    return 'text-red-600';
  };

  const completedItems = [
    { label: 'Profile created', completed: true },
    { label: 'Career stage set', completed: true },
    {
      label: atsScore !== null && atsScore > 0 ? `Resume uploaded (ATS: ${atsScore}/100)` : 'Upload resume',
      completed: atsScore !== null && atsScore > 0,
    },
    { label: 'First recruiter added', completed: hasRecruiter },
    { label: 'First message generated', completed: hasMessage },
  ];

  const nextSteps = [
    ...(atsScore === null || atsScore === 0 ? [{ label: 'Upload your resume' }] : []),
    ...(!hasRecruiter ? [{ label: 'Add your first recruiter' }] : []),
    ...(!hasMessage ? [{ label: 'Send your first message' }] : []),
    { label: 'Optimize your LinkedIn profile' },
  ].slice(0, 3);

  return (
    <div className="text-center">
      {showConfetti && (
        <div className="fixed inset-0 pointer-events-none flex items-center justify-center">
          <PartyPopper className="w-24 h-24 text-primary-500 animate-bounce" />
        </div>
      )}

      <div className="mb-8">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <Check className="w-10 h-10 text-green-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-3">You're all set!</h1>
        <p className="text-lg text-gray-600">
          Your Jobezie account is ready to help you land your dream job.
        </p>
      </div>

      {/* Readiness score */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6 max-w-md mx-auto">
        <h2 className="font-semibold text-gray-900 mb-4">
          Career Readiness: <span className={getScoreColor(readinessScore)}>{readinessScore}%</span>
        </h2>
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden mb-6">
          <div
            className={`h-full transition-all duration-500 ${
              readinessScore >= 71 ? 'bg-green-500' : readinessScore >= 41 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${readinessScore}%` }}
          />
        </div>

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
              <span className={item.completed ? 'text-gray-900' : 'text-gray-500'}>
                {item.label}
              </span>
            </div>
          ))}
        </div>

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

      {/* Hot Job Markets Preview */}
      {opportunities.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8 max-w-md mx-auto text-left">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-primary-600" />
            Your Top Opportunity
          </h3>
          {opportunities.map((opp, i) => (
            <div key={i} className="p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-gray-900">{opp.target_role}</span>
                <span className={`text-sm font-bold ${getScoreColor(opp.total_score)}`}>
                  {opp.total_score}/100
                </span>
              </div>
              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span>Match: {opp.components.user_match}</span>
                <span>Shortage: {opp.components.shortage}</span>
              </div>
              <p className="text-xs text-gray-600 mt-1">{opp.interpretation}</p>
            </div>
          ))}
        </div>
      )}

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
          'Go to Dashboard →'
        )}
      </button>
    </div>
  );
}
