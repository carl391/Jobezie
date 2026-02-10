import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { authApi } from '../lib/api';
import { StepCareerStage } from '../components/onboarding/StepCareerStage';
import { StepTargetRole } from '../components/onboarding/StepTargetRole';
import { StepLocation } from '../components/onboarding/StepLocation';
import { StepSkills } from '../components/onboarding/StepSkills';
import { ResumeUploadStep } from '../components/onboarding/ResumeUploadStep';
import { CompleteStep } from '../components/onboarding/CompleteStep';
import type { OnboardingData, Resume } from '../types';

const TOTAL_STEPS = 6;

export function Onboarding() {
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  // Onboarding data state
  const [careerData, setCareerData] = useState<OnboardingData>({});
  const [_uploadedResume, setUploadedResume] = useState<Resume | null>(null);
  const [atsScore, setAtsScore] = useState<number | null>(null);

  // Load saved progress from localStorage
  useEffect(() => {
    const savedStep = localStorage.getItem('onboarding_step');
    const savedCareerData = localStorage.getItem('onboarding_career_data');

    if (savedStep) {
      setCurrentStep(parseInt(savedStep, 10));
    }
    if (savedCareerData) {
      setCareerData(JSON.parse(savedCareerData));
    }
  }, []);

  // If user has completed onboarding, redirect to dashboard
  useEffect(() => {
    if (user?.onboarding_completed) {
      navigate('/dashboard', { replace: true });
    }
  }, [user, navigate]);

  // Save progress to localStorage when step changes
  useEffect(() => {
    localStorage.setItem('onboarding_step', currentStep.toString());
  }, [currentStep]);

  const handleNext = () => {
    if (currentStep < TOTAL_STEPS) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleStepSave = (data: Partial<OnboardingData>) => {
    const updated = { ...careerData, ...data };
    setCareerData(updated);
    localStorage.setItem('onboarding_career_data', JSON.stringify(updated));

    // Persist to backend
    authApi.updateProfile({ ...data, onboarding_step: currentStep }).catch((err) => {
      console.error('Error saving onboarding step:', err);
    });
  };

  const handleResumeComplete = (resume: Resume | null, score: number) => {
    setUploadedResume(resume);
    setAtsScore(score);
    handleNext();
  };

  const handleSkip = () => {
    handleNext();
  };

  const handleComplete = async () => {
    setIsLoading(true);
    try {
      await authApi.updateProfile({
        ...careerData,
        onboarding_completed: true,
      });

      // Clear localStorage onboarding data
      localStorage.removeItem('onboarding_step');
      localStorage.removeItem('onboarding_career_data');

      // Refresh user to get updated onboarding status
      await refreshUser();

      // Navigate to dashboard
      navigate('/dashboard', { replace: true });
    } catch (error) {
      console.error('Error completing onboarding:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <StepCareerStage
            data={careerData}
            onSave={handleStepSave}
            onNext={handleNext}
          />
        );
      case 2:
        return (
          <StepTargetRole
            data={careerData}
            onSave={handleStepSave}
            onNext={handleNext}
            onSkip={handleSkip}
          />
        );
      case 3:
        return (
          <StepLocation
            data={careerData}
            onSave={handleStepSave}
            onNext={handleNext}
            onSkip={handleSkip}
          />
        );
      case 4:
        return (
          <StepSkills
            data={careerData}
            onSave={handleStepSave}
            onNext={handleNext}
            onSkip={handleSkip}
          />
        );
      case 5:
        return (
          <ResumeUploadStep
            onNext={handleResumeComplete}
            onSkip={handleSkip}
          />
        );
      case 6:
        return (
          <CompleteStep
            onComplete={handleComplete}
            isLoading={isLoading}
            atsScore={atsScore}
            userName={user?.first_name || ''}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Progress bar */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">
              Step {currentStep} of {TOTAL_STEPS}
            </span>
            <span className="text-sm text-gray-500">
              {Math.round((currentStep / TOTAL_STEPS) * 100)}% complete
            </span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-600 transition-all duration-300 ease-out"
              style={{ width: `${(currentStep / TOTAL_STEPS) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Step content */}
      <div className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-2xl">{renderStep()}</div>
      </div>
    </div>
  );
}
