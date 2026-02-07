import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { authApi } from '../lib/api';
import { WelcomeStep } from '../components/onboarding/WelcomeStep';
import { CareerInfoStep } from '../components/onboarding/CareerInfoStep';
import { ResumeUploadStep } from '../components/onboarding/ResumeUploadStep';
import { ATSResultsStep } from '../components/onboarding/ATSResultsStep';
import { FirstRecruiterStep } from '../components/onboarding/FirstRecruiterStep';
import { FirstMessageStep } from '../components/onboarding/FirstMessageStep';
import { CompleteStep } from '../components/onboarding/CompleteStep';
import type { OnboardingData, Resume, Recruiter } from '../types';

const TOTAL_STEPS = 7;

export function Onboarding() {
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  // Onboarding data state
  const [careerData, setCareerData] = useState<OnboardingData>({});
  const [uploadedResume, setUploadedResume] = useState<Resume | null>(null);
  const [atsScore, setAtsScore] = useState<number | null>(null);
  const [firstRecruiter, setFirstRecruiter] = useState<Recruiter | null>(null);
  const [generatedMessage, setGeneratedMessage] = useState<string | null>(null);

  // Load saved progress from localStorage
  useEffect(() => {
    const savedStep = localStorage.getItem('onboarding_step');
    const savedCareerData = localStorage.getItem('onboarding_career_data');
    const savedResumeId = localStorage.getItem('onboarding_resume_id');

    if (savedStep) {
      setCurrentStep(parseInt(savedStep, 10));
    }
    if (savedCareerData) {
      setCareerData(JSON.parse(savedCareerData));
    }
    if (savedResumeId) {
      // Could fetch resume details here if needed
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

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    // If skipping Step 3 (Resume Upload), also skip Step 4 (ATS Results)
    // since there's no resume to score
    if (currentStep === 3) {
      setCurrentStep(5);
      return;
    }
    handleNext();
  };

  const handleCareerDataSave = (data: OnboardingData) => {
    setCareerData(data);
    localStorage.setItem('onboarding_career_data', JSON.stringify(data));
    handleNext();
  };

  const handleResumeUploaded = (resume: Resume) => {
    setUploadedResume(resume);
    localStorage.setItem('onboarding_resume_id', resume.id);
    handleNext();
  };

  const handleATSScoreReceived = (score: number) => {
    setAtsScore(score);
    handleNext();
  };

  const handleRecruiterAdded = (recruiter: Recruiter) => {
    setFirstRecruiter(recruiter);
    handleNext();
  };

  const handleMessageGenerated = (message: string) => {
    setGeneratedMessage(message);
    handleNext();
  };

  const handleComplete = async () => {
    setIsLoading(true);
    try {
      // Save career data and mark onboarding as complete
      await authApi.updateProfile({
        ...careerData,
        onboarding_completed: true,
      });

      // Clear localStorage onboarding data
      localStorage.removeItem('onboarding_step');
      localStorage.removeItem('onboarding_career_data');
      localStorage.removeItem('onboarding_resume_id');

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
        return <WelcomeStep onNext={handleNext} userName={user?.first_name || ''} />;
      case 2:
        return (
          <CareerInfoStep
            onNext={handleCareerDataSave}
            onBack={handleBack}
            initialData={careerData}
          />
        );
      case 3:
        return (
          <ResumeUploadStep
            onNext={handleResumeUploaded}
            onBack={handleBack}
            onSkip={handleSkip}
          />
        );
      case 4:
        return (
          <ATSResultsStep
            onNext={handleATSScoreReceived}
            onBack={handleBack}
            resume={uploadedResume}
          />
        );
      case 5:
        return (
          <FirstRecruiterStep
            onNext={handleRecruiterAdded}
            onBack={handleBack}
            onSkip={handleSkip}
          />
        );
      case 6:
        return (
          <FirstMessageStep
            onNext={handleMessageGenerated}
            onBack={handleBack}
            onSkip={handleSkip}
            recruiter={firstRecruiter}
          />
        );
      case 7:
        return (
          <CompleteStep
            onComplete={handleComplete}
            isLoading={isLoading}
            atsScore={atsScore}
            hasRecruiter={!!firstRecruiter}
            hasMessage={!!generatedMessage}
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
