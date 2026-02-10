import { useState } from 'react';
import { OccupationAutocomplete } from '../ui/OccupationAutocomplete';
import type { OnboardingData } from '../../types';

interface StepTargetRoleProps {
  data: OnboardingData;
  onSave: (data: Partial<OnboardingData>) => void;
  onNext: () => void;
  onSkip: () => void;
}

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

export function StepTargetRole({ data, onSave, onNext, onSkip }: StepTargetRoleProps) {
  const [targetRoles, setTargetRoles] = useState<string[]>(data.target_roles || []);
  const [targetIndustries, setTargetIndustries] = useState<string[]>(data.target_industries || []);
  const [roleInput, setRoleInput] = useState('');

  const handleAddRole = (title: string) => {
    if (title && !targetRoles.includes(title)) {
      setTargetRoles([...targetRoles, title]);
    }
    setRoleInput('');
  };

  const handleRemoveRole = (role: string) => {
    setTargetRoles(targetRoles.filter(r => r !== role));
  };

  const handleIndustryToggle = (industry: string) => {
    if (targetIndustries.includes(industry)) {
      setTargetIndustries(targetIndustries.filter(i => i !== industry));
    } else if (targetIndustries.length < 3) {
      setTargetIndustries([...targetIndustries, industry]);
    }
  };

  const handleContinue = () => {
    onSave({
      target_roles: targetRoles,
      target_industries: targetIndustries,
    });
    onNext();
  };

  const handleSkip = () => {
    onSave({});
    onSkip();
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        What roles are you targeting?
      </h2>
      <p className="text-gray-600 mb-8">
        Help us find the right opportunities for you
      </p>

      {/* Target Roles with O*NET Autocomplete */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Target Roles</label>
        <OccupationAutocomplete
          value={roleInput}
          onChange={(title) => {
            if (title) handleAddRole(title);
          }}
          placeholder="Search O*NET occupations (e.g., Software Developer)"
          showShortagePreview
        />
        {targetRoles.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {targetRoles.map((role) => (
              <span
                key={role}
                className="inline-flex items-center gap-1 px-3 py-1.5 bg-primary-100 text-primary-700 rounded-full text-sm"
              >
                {role}
                <button
                  onClick={() => handleRemoveRole(role)}
                  className="hover:text-primary-900 ml-1"
                >
                  &times;
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Industry Multi-Select */}
      <div className="mb-8">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Target Industries (select up to 3)
          {targetIndustries.length > 0 && (
            <span className="text-gray-500 font-normal ml-2">
              {targetIndustries.length} selected
            </span>
          )}
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {INDUSTRY_OPTIONS.map((industry) => (
            <button
              key={industry}
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
      </div>

      <button
        onClick={handleContinue}
        className="w-full py-3 bg-gradient-to-r from-primary-600 to-purple-600 text-white rounded-xl font-semibold hover:opacity-90 transition"
      >
        Continue →
      </button>

      <button
        onClick={handleSkip}
        className="w-full mt-3 py-2 text-sm text-gray-500 hover:text-gray-700 transition"
      >
        Skip for now →
      </button>
    </div>
  );
}
