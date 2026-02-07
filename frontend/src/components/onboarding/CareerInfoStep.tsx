import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ChevronLeft, Briefcase, GraduationCap, TrendingUp, Award, Crown } from 'lucide-react';
import { authApi } from '../../lib/api';
import { OccupationAutocomplete } from '../ui/OccupationAutocomplete';
import { SkillsAutocomplete } from '../ui/SkillsAutocomplete';
import type { OnboardingData, OccupationResult } from '../../types';

const careerInfoSchema = z.object({
  search_status: z.string().min(1, 'Please select your job search status'),
  career_stage: z.string().min(1, 'Please select your experience level'),
  current_role: z.string().optional(),
  target_roles: z.array(z.string()).min(1, 'Please enter at least one target role'),
  target_industries: z.array(z.string()).min(1, 'Please select at least one industry'),
});

type CareerInfoFormData = z.infer<typeof careerInfoSchema>;

interface CareerInfoStepProps {
  onNext: (data: OnboardingData) => void;
  onBack: () => void;
  initialData: OnboardingData;
}

const SEARCH_STATUS_OPTIONS = [
  { value: 'just-starting', label: 'Just starting out', sublabel: "Haven't applied anywhere yet", icon: '🌱' },
  { value: 'actively-searching', label: 'Actively searching', sublabel: 'Applying regularly', icon: '🔍' },
  { value: 'long-search', label: 'Been at it for a while', sublabel: 'Searching for 2+ months', icon: '🏃' },
  { value: 'interviews-lined', label: 'Have interviews lined up', sublabel: 'Need interview prep help', icon: '🎯' },
];

const EXPERIENCE_OPTIONS = [
  { value: 'student', label: 'Student/New Grad', sublabel: 'Still in school or just graduated', icon: GraduationCap, years: 0 },
  { value: 'entry_level', label: 'Entry Level', sublabel: '0-2 years experience', icon: Briefcase, years: 1 },
  { value: 'mid_level', label: 'Mid-Level', sublabel: '3-7 years experience', icon: TrendingUp, years: 5 },
  { value: 'senior', label: 'Senior', sublabel: '8-15 years experience', icon: Award, years: 10 },
  { value: 'executive', label: 'Executive', sublabel: '15+ years, leadership', icon: Crown, years: 18 },
];

const INDUSTRY_OPTIONS = [
  'Technology',
  'Healthcare',
  'Finance',
  'Retail/E-commerce',
  'Manufacturing',
  'Consulting',
  'Media/Entertainment',
  'Education',
  'Government',
  'Nonprofit',
  'Real Estate',
  'Other',
];

interface SelectedSkill {
  name: string;
  category: 'skills' | 'abilities' | 'knowledge';
}

export function CareerInfoStep({ onNext, onBack, initialData }: CareerInfoStepProps) {
  const [step, setStep] = useState<'status' | 'experience' | 'details'>('status');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [targetRoleInput, setTargetRoleInput] = useState('');
  const [userSkills, setUserSkills] = useState<SelectedSkill[]>([]);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<CareerInfoFormData>({
    resolver: zodResolver(careerInfoSchema),
    defaultValues: {
      search_status: initialData.search_status || '',
      career_stage: initialData.career_stage || '',
      current_role: initialData.current_role || '',
      target_roles: initialData.target_roles || [],
      target_industries: initialData.target_industries || [],
    },
  });

  const searchStatus = watch('search_status');
  const careerStage = watch('career_stage');
  const targetRoles = watch('target_roles');
  const targetIndustries = watch('target_industries');

  const handleSearchStatusSelect = (value: string) => {
    setValue('search_status', value);
    setStep('experience');
  };

  const handleExperienceSelect = (value: string, years: number) => {
    setValue('career_stage', value);
    setStep('details');
  };

  const handleAddTargetRole = () => {
    if (targetRoleInput.trim() && !targetRoles.includes(targetRoleInput.trim())) {
      setValue('target_roles', [...targetRoles, targetRoleInput.trim()]);
      setTargetRoleInput('');
    }
  };

  const handleRemoveTargetRole = (role: string) => {
    setValue('target_roles', targetRoles.filter((r) => r !== role));
  };

  const handleIndustryToggle = (industry: string) => {
    if (targetIndustries.includes(industry)) {
      setValue('target_industries', targetIndustries.filter((i) => i !== industry));
    } else if (targetIndustries.length < 3) {
      setValue('target_industries', [...targetIndustries, industry]);
    }
  };

  const onSubmit = async (data: CareerInfoFormData) => {
    setIsSubmitting(true);
    try {
      const experienceOption = EXPERIENCE_OPTIONS.find((o) => o.value === data.career_stage);
      const skillNames = userSkills.map((s) => s.name);

      await authApi.updateProfile({
        career_stage: data.career_stage,
        years_experience: experienceOption?.years || 0,
        current_role: data.current_role,
        target_roles: data.target_roles,
        target_industries: data.target_industries,
        technical_skills: skillNames,
        onboarding_step: 2,
      });

      onNext({
        search_status: data.search_status,
        career_stage: data.career_stage,
        current_role: data.current_role,
        target_roles: data.target_roles,
        target_industries: data.target_industries,
      });
    } catch (error) {
      console.error('Error saving career info:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInternalBack = () => {
    if (step === 'details') {
      setStep('experience');
    } else if (step === 'experience') {
      setStep('status');
    } else {
      onBack();
    }
  };

  // Render job search status selection
  if (step === 'status') {
    return (
      <div>
        <button
          onClick={handleInternalBack}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ChevronLeft className="w-5 h-5 mr-1" />
          Back
        </button>

        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Where are you in your job search?
        </h2>
        <p className="text-gray-600 mb-8">
          This helps us personalize your experience
        </p>

        <div className="space-y-3">
          {SEARCH_STATUS_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => handleSearchStatusSelect(option.value)}
              className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
                searchStatus === option.value
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300 bg-white'
              }`}
            >
              <div className="flex items-center gap-4">
                <span className="text-2xl">{option.icon}</span>
                <div>
                  <div className="font-medium text-gray-900">{option.label}</div>
                  <div className="text-sm text-gray-500">{option.sublabel}</div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    );
  }

  // Render experience level selection
  if (step === 'experience') {
    return (
      <div>
        <button
          onClick={handleInternalBack}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ChevronLeft className="w-5 h-5 mr-1" />
          Back
        </button>

        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          What's your experience level?
        </h2>
        <p className="text-gray-600 mb-8">
          We'll tailor recommendations to your career stage
        </p>

        <div className="space-y-3">
          {EXPERIENCE_OPTIONS.map((option) => {
            const Icon = option.icon;
            return (
              <button
                key={option.value}
                onClick={() => handleExperienceSelect(option.value, option.years)}
                className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
                  careerStage === option.value
                    ? 'border-primary-600 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                }`}
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                    <Icon className="w-5 h-5 text-gray-600" />
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{option.label}</div>
                    <div className="text-sm text-gray-500">{option.sublabel}</div>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  // Render target roles and industries
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <button
        type="button"
        onClick={handleInternalBack}
        className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
      >
        <ChevronLeft className="w-5 h-5 mr-1" />
        Back
      </button>

      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        What roles are you targeting?
      </h2>
      <p className="text-gray-600 mb-8">
        Help us find the right opportunities for you
      </p>

      {/* Current Role */}
      <div className="mb-6">
        <label className="label">Current Role (optional)</label>
        <input
          type="text"
          {...register('current_role')}
          placeholder="e.g., Software Engineer"
          className="input"
        />
      </div>

      {/* Target Roles */}
      <div className="mb-6">
        <label className="label">Target Roles *</label>
        <OccupationAutocomplete
          value={targetRoleInput}
          onChange={(title, occupation) => {
            if (title && !targetRoles.includes(title)) {
              setValue('target_roles', [...targetRoles, title]);
            }
            setTargetRoleInput('');
          }}
          placeholder="Search O*NET occupations (e.g., Software Developer)"
          showShortagePreview
        />
        {targetRoles.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {targetRoles.map((role) => (
              <span
                key={role}
                className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
              >
                {role}
                <button
                  type="button"
                  onClick={() => handleRemoveTargetRole(role)}
                  className="hover:text-primary-900"
                >
                  &times;
                </button>
              </span>
            ))}
          </div>
        )}
        {errors.target_roles && (
          <p className="error-text mt-1">{errors.target_roles.message}</p>
        )}
      </div>

      {/* Target Industries */}
      <div className="mb-6">
        <label className="label">Target Industries * (select up to 3)</label>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {INDUSTRY_OPTIONS.map((industry) => (
            <button
              key={industry}
              type="button"
              onClick={() => handleIndustryToggle(industry)}
              className={`px-3 py-2 rounded-lg border text-sm transition-all ${
                targetIndustries.includes(industry)
                  ? 'border-primary-600 bg-primary-50 text-primary-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
              } ${
                !targetIndustries.includes(industry) && targetIndustries.length >= 3
                  ? 'opacity-50 cursor-not-allowed'
                  : ''
              }`}
              disabled={
                !targetIndustries.includes(industry) && targetIndustries.length >= 3
              }
            >
              {industry}
            </button>
          ))}
        </div>
        {errors.target_industries && (
          <p className="error-text mt-1">{errors.target_industries.message}</p>
        )}
      </div>

      {/* Skills */}
      <div className="mb-8">
        <label className="label">Your Skills</label>
        <p className="text-xs text-gray-500 mb-2">
          Add your top skills — we'll match them against 1,016 occupations and 120 skill dimensions
        </p>
        <SkillsAutocomplete
          selectedSkills={userSkills}
          onChange={setUserSkills}
          showMatchPreview={userSkills.length >= 5}
          compact
        />
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="btn btn-primary w-full py-3"
      >
        {isSubmitting ? 'Saving...' : 'Continue'}
      </button>
    </form>
  );
}
