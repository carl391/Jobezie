import { useState } from 'react';
import { SkillsAutocomplete } from '../ui/SkillsAutocomplete';
import type { OnboardingData } from '../../types';

interface SelectedSkill {
  name: string;
  category: 'skills' | 'abilities' | 'knowledge';
}

interface StepSkillsProps {
  data: OnboardingData;
  onSave: (data: Partial<OnboardingData>) => void;
  onNext: () => void;
  onSkip: () => void;
}

const SKILL_CATEGORIES = [
  {
    key: 'technical' as const,
    label: 'Technical Skills',
    icon: '💻',
    description: 'Programming languages, tools, frameworks',
  },
  {
    key: 'cognitive' as const,
    label: 'Cognitive Skills',
    icon: '🧠',
    description: 'Thinking, analysis, problem-solving',
  },
  {
    key: 'interpersonal' as const,
    label: 'Interpersonal Skills',
    icon: '🤝',
    description: 'Communication, leadership, teamwork',
  },
];

export function StepSkills({ data, onSave, onNext, onSkip }: StepSkillsProps) {
  const [userSkills, setUserSkills] = useState<SelectedSkill[]>(() => {
    // Reconstruct from saved data
    const skills: SelectedSkill[] = [];
    if (data.technical_skills) {
      data.technical_skills.forEach(s => skills.push({ name: s, category: 'skills' }));
    }
    if (data.soft_skills) {
      data.soft_skills.forEach(s => skills.push({ name: s, category: 'abilities' }));
    }
    return skills;
  });

  const categoriesUsed = new Set(userSkills.map(s => {
    // Map O*NET categories to display categories
    if (s.category === 'skills') return 'technical';
    if (s.category === 'abilities') return 'cognitive';
    return 'interpersonal';
  })).size;

  const handleContinue = () => {
    // Split skills by type for backend
    const technicalSkills = userSkills
      .filter(s => s.category === 'skills')
      .map(s => s.name);
    const softSkills = userSkills
      .filter(s => s.category === 'abilities' || s.category === 'knowledge')
      .map(s => s.name);

    onSave({
      technical_skills: technicalSkills,
      soft_skills: softSkills,
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
        What are your key skills?
      </h2>
      <p className="text-gray-600 mb-8">
        We'll match them against 1,016 occupations and 120 skill dimensions
      </p>

      {/* Category labels */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        {SKILL_CATEGORIES.map(cat => (
          <div key={cat.key} className="text-center p-3 bg-gray-50 rounded-xl">
            <span className="text-2xl">{cat.icon}</span>
            <div className="text-xs font-medium text-gray-700 mt-1">{cat.label}</div>
          </div>
        ))}
      </div>

      {/* Skills autocomplete */}
      <div className="mb-6">
        <SkillsAutocomplete
          selectedSkills={userSkills}
          onChange={setUserSkills}
          showMatchPreview={userSkills.length >= 5}
          compact
        />
      </div>

      {/* Coverage preview */}
      {userSkills.length >= 3 && (
        <div className="p-4 bg-primary-50 rounded-xl mb-6">
          <div className="text-sm font-medium text-primary-800">
            📊 Skills Coverage: {userSkills.length} skills across {categoriesUsed} {categoriesUsed === 1 ? 'category' : 'categories'}
          </div>
          <div className="text-xs text-primary-600 mt-1">
            {categoriesUsed >= 3
              ? 'Great coverage across all categories!'
              : 'Tip: Adding skills from all 3 categories gives you the strongest match scores.'}
          </div>
        </div>
      )}

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
