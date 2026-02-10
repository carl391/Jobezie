import { useEffect, useState } from 'react';
import { Check, Loader2, TrendingUp } from 'lucide-react';
import confetti from 'canvas-confetti';
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
  userName?: string;
}

export function CompleteStep({
  onComplete,
  isLoading,
  atsScore,
  userName,
}: CompleteStepProps) {
  const [realReadiness, setRealReadiness] = useState<number | null>(null);
  const [opportunities, setOpportunities] = useState<OpportunityPreview[]>([]);

  useEffect(() => {
    // Fire confetti
    confetti({
      particleCount: 120,
      spread: 80,
      origin: { y: 0.6 },
    });

    const markComplete = async () => {
      try {
        await authApi.updateProfile({
          onboarding_step: 6,
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
  }, []);

  const calculateReadiness = () => {
    let score = 30; // profile + career stage completed
    if (atsScore !== null && atsScore > 0) {
      score += 25;
      if (atsScore >= 60) score += 10;
    }
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
    { label: 'Target roles configured', completed: true },
    {
      label: atsScore !== null && atsScore > 0 ? `Resume uploaded (ATS: ${atsScore}/100)` : 'Upload resume',
      completed: atsScore !== null && atsScore > 0,
    },
  ];

  const nextSteps = [
    { label: 'Build your recruiter pipeline' },
    { label: 'Send your first outreach message' },
    { label: 'Try the AI Career Coach' },
    { label: 'Optimize your LinkedIn profile' },
  ].slice(0, 3);

  return (
    <div className="text-center">
      <div className="mb-8">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <Check className="w-10 h-10 text-green-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-3">
          {userName ? `You're all set, ${userName}!` : "You're all set!"}
        </h1>
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
        className="w-full max-w-md mx-auto py-3 bg-gradient-to-r from-primary-600 to-purple-600 text-white rounded-xl font-semibold hover:opacity-90 transition flex items-center justify-center gap-2"
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
