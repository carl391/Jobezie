import { useState } from 'react';
import type { OnboardingData } from '../../types';

interface StepCareerStageProps {
  data: OnboardingData;
  onSave: (data: Partial<OnboardingData>) => void;
  onNext: () => void;
}

const SEARCH_STATUS_OPTIONS = [
  { value: 'just-starting', label: 'Just starting out', sublabel: "Haven't applied anywhere yet", icon: '🌱' },
  { value: 'actively-searching', label: 'Actively searching', sublabel: 'Applying regularly', icon: '🔍' },
  { value: 'long-search', label: 'Been at it for a while', sublabel: 'Searching for 2+ months', icon: '🏃' },
  { value: 'interviews-lined', label: 'Have interviews lined up', sublabel: 'Need interview prep help', icon: '🎯' },
];

const CAREER_STAGE_OPTIONS = [
  { value: 'student', label: 'Student / New Grad', sublabel: 'Still in school or just graduated', icon: '🎓', years: 0 },
  { value: 'entry_level', label: 'Entry Level', sublabel: '0–2 years experience', icon: '🌱', years: 1 },
  { value: 'mid_level', label: 'Mid-Level', sublabel: '3–7 years experience', icon: '🚀', years: 5 },
  { value: 'senior', label: 'Senior', sublabel: '8–15 years experience', icon: '⭐', years: 10 },
  { value: 'executive', label: 'Executive', sublabel: '15+ years, leadership', icon: '👑', years: 18 },
];

export function StepCareerStage({ data, onSave, onNext }: StepCareerStageProps) {
  const [searchStatus, setSearchStatus] = useState(data.search_status || '');
  const [careerStage, setCareerStage] = useState(data.career_stage || '');

  const handleContinue = () => {
    const experienceOption = CAREER_STAGE_OPTIONS.find(o => o.value === careerStage);
    onSave({
      search_status: searchStatus,
      career_stage: careerStage,
      years_experience: experienceOption?.years || 0,
    });
    onNext();
  };

  return (
    <div>
      {/* Section A: Job Search Status */}
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        Where are you in your job search?
      </h2>
      <p className="text-gray-600 mb-6">
        This helps us personalize your experience
      </p>

      <div className="space-y-3 mb-10">
        {SEARCH_STATUS_OPTIONS.map((option) => (
          <button
            key={option.value}
            onClick={() => setSearchStatus(option.value)}
            className={`w-full text-left p-4 rounded-xl border-2 transition-all duration-200 ${
              searchStatus === option.value
                ? 'border-primary-600 bg-primary-50 shadow-md'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">{option.icon}</span>
              <div className="flex-1">
                <div className="font-semibold text-gray-900">{option.label}</div>
                <div className="text-sm text-gray-500">{option.sublabel}</div>
              </div>
              {searchStatus === option.value && (
                <div className="ml-auto text-primary-600 font-bold">✓</div>
              )}
            </div>
          </button>
        ))}
      </div>

      {/* Section B: Career Stage */}
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        What's your experience level?
      </h2>
      <p className="text-gray-600 mb-6">
        We'll tailor recommendations to your career stage
      </p>

      <div className="space-y-3 mb-8">
        {CAREER_STAGE_OPTIONS.map((option) => (
          <button
            key={option.value}
            onClick={() => setCareerStage(option.value)}
            className={`w-full text-left p-4 rounded-xl border-2 transition-all duration-200 ${
              careerStage === option.value
                ? 'border-primary-600 bg-primary-50 shadow-md'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">{option.icon}</span>
              <div className="flex-1">
                <div className="font-semibold text-gray-900">{option.label}</div>
                <div className="text-sm text-gray-500">{option.sublabel}</div>
              </div>
              {careerStage === option.value && (
                <div className="ml-auto text-primary-600 font-bold">✓</div>
              )}
            </div>
          </button>
        ))}
      </div>

      <button
        onClick={handleContinue}
        disabled={!searchStatus || !careerStage}
        className="w-full py-3 bg-gradient-to-r from-primary-600 to-purple-600 text-white rounded-xl font-semibold disabled:opacity-40 disabled:cursor-not-allowed hover:opacity-90 transition"
      >
        Continue →
      </button>
    </div>
  );
}
