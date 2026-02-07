import { useState, useEffect, useRef, useCallback } from 'react';
import { Search, Loader2, X } from 'lucide-react';
import { laborMarketApi } from '../../lib/api';
import type { SkillResult, SkillsMapData } from '../../types';

interface SelectedSkill {
  name: string;
  category: 'skills' | 'abilities' | 'knowledge';
}

interface SkillsAutocompleteProps {
  selectedSkills: SelectedSkill[];
  onChange: (skills: SelectedSkill[]) => void;
  showMatchPreview?: boolean;
  compact?: boolean;
}

const CATEGORY_COLORS: Record<string, { chip: string; tab: string; activeTab: string }> = {
  skills: {
    chip: 'bg-blue-100 text-blue-700',
    tab: 'text-blue-600 hover:bg-blue-50',
    activeTab: 'bg-blue-600 text-white',
  },
  abilities: {
    chip: 'bg-purple-100 text-purple-700',
    tab: 'text-purple-600 hover:bg-purple-50',
    activeTab: 'bg-purple-600 text-white',
  },
  knowledge: {
    chip: 'bg-green-100 text-green-700',
    tab: 'text-green-600 hover:bg-green-50',
    activeTab: 'bg-green-600 text-white',
  },
};

export function SkillsAutocomplete({
  selectedSkills,
  onChange,
  showMatchPreview = false,
  compact = false,
}: SkillsAutocompleteProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SkillResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [coverageData, setCoverageData] = useState<SkillsMapData | null>(null);
  const [isLoadingCoverage, setIsLoadingCoverage] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch coverage data when skills change (5+ skills)
  useEffect(() => {
    if (showMatchPreview && selectedSkills.length >= 5) {
      setIsLoadingCoverage(true);
      laborMarketApi.getSkillsMap()
        .then((res) => setCoverageData(res.data.data || null))
        .catch(() => setCoverageData(null))
        .finally(() => setIsLoadingCoverage(false));
    }
  }, [showMatchPreview, selectedSkills.length]);

  const searchSkills = useCallback(async (q: string) => {
    if (q.length < 2) {
      setResults([]);
      return;
    }
    setIsLoading(true);
    try {
      const res = await laborMarketApi.searchSkills(q, activeCategory || undefined, 20);
      const data: SkillResult[] = res.data.data || [];
      // Filter out already selected skills
      const selectedNames = new Set(selectedSkills.map((s) => s.name.toLowerCase()));
      setResults(data.filter((s) => !selectedNames.has(s.name.toLowerCase())));
    } catch {
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, [activeCategory, selectedSkills]);

  const handleInputChange = (val: string) => {
    setQuery(val);
    setIsOpen(true);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => searchSkills(val), 300);
  };

  const handleSelect = (skill: SkillResult) => {
    const newSkill: SelectedSkill = { name: skill.name, category: skill.category };
    onChange([...selectedSkills, newSkill]);
    setQuery('');
    setResults([]);
  };

  const handleRemove = (skillName: string) => {
    onChange(selectedSkills.filter((s) => s.name !== skillName));
  };

  const groupedResults = results.reduce<Record<string, SkillResult[]>>((acc, skill) => {
    if (!acc[skill.category]) acc[skill.category] = [];
    acc[skill.category].push(skill);
    return acc;
  }, {});

  const getCoverageBar = (pct: number) => {
    const color = pct >= 71 ? 'bg-green-500' : pct >= 41 ? 'bg-yellow-500' : 'bg-red-500';
    return (
      <div className="flex items-center gap-2">
        <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${pct}%` }} />
        </div>
        <span className="text-xs text-gray-600 w-8 text-right">{pct}%</span>
      </div>
    );
  };

  const skillsByCategory = {
    skills: selectedSkills.filter((s) => s.category === 'skills'),
    abilities: selectedSkills.filter((s) => s.category === 'abilities'),
    knowledge: selectedSkills.filter((s) => s.category === 'knowledge'),
  };

  return (
    <div ref={wrapperRef} className="space-y-3">
      {/* Search input */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => handleInputChange(e.target.value)}
          onFocus={() => query.length >= 2 && setIsOpen(true)}
          placeholder="Search skills, abilities, or knowledge..."
          className="input pl-10"
        />
        {isLoading && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 animate-spin" />
        )}
      </div>

      {/* Category filter tabs */}
      {isOpen && (
        <div className="flex gap-1">
          <button
            type="button"
            onClick={() => { setActiveCategory(null); if (query.length >= 2) searchSkills(query); }}
            className={`px-3 py-1 text-xs rounded-full transition-colors ${
              activeCategory === null ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            All
          </button>
          {(['skills', 'abilities', 'knowledge'] as const).map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => { setActiveCategory(cat); if (query.length >= 2) searchSkills(query); }}
              className={`px-3 py-1 text-xs rounded-full capitalize transition-colors ${
                activeCategory === cat ? CATEGORY_COLORS[cat].activeTab : CATEGORY_COLORS[cat].tab
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {/* Dropdown */}
      {isOpen && Object.keys(groupedResults).length > 0 && (
        <div className="relative z-50 bg-white border border-gray-200 rounded-lg shadow-lg max-h-64 overflow-y-auto">
          {Object.entries(groupedResults).map(([category, items]) => (
            <div key={category}>
              <div className="px-3 py-1.5 bg-gray-50 text-xs font-semibold text-gray-500 uppercase sticky top-0">
                {category}
              </div>
              {items.map((skill) => (
                <button
                  key={skill.id}
                  type="button"
                  onClick={() => handleSelect(skill)}
                  className="w-full text-left px-4 py-2 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${
                      CATEGORY_COLORS[skill.category]?.chip.split(' ')[0] || 'bg-gray-300'
                    }`} />
                    <span className="text-sm text-gray-900">{skill.name}</span>
                  </div>
                </button>
              ))}
            </div>
          ))}
        </div>
      )}

      {isOpen && query.length >= 2 && !isLoading && results.length === 0 && (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-4 text-center text-sm text-gray-500">
          No skills found for "{query}"
        </div>
      )}

      {/* Selected skills grouped by category */}
      {!compact && selectedSkills.length > 0 && (
        <div className="space-y-2">
          {(['skills', 'abilities', 'knowledge'] as const).map((cat) => {
            const catSkills = skillsByCategory[cat];
            if (catSkills.length === 0) return null;
            return (
              <div key={cat}>
                <label className="text-xs font-medium text-gray-500 uppercase mb-1 block">
                  {cat}
                </label>
                <div className="flex flex-wrap gap-1.5">
                  {catSkills.map((skill) => (
                    <span
                      key={skill.name}
                      className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${CATEGORY_COLORS[cat].chip}`}
                    >
                      {skill.name}
                      <button
                        type="button"
                        onClick={() => handleRemove(skill.name)}
                        className="hover:opacity-70"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Compact chip display */}
      {compact && selectedSkills.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {selectedSkills.map((skill) => (
            <span
              key={skill.name}
              className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${CATEGORY_COLORS[skill.category].chip}`}
            >
              {skill.name}
              <button type="button" onClick={() => handleRemove(skill.name)} className="hover:opacity-70">
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Coverage preview */}
      {showMatchPreview && selectedSkills.length >= 5 && (
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-2">
            Skills Coverage ({selectedSkills.length} skills)
          </h4>
          {isLoadingCoverage ? (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Loader2 className="w-3 h-3 animate-spin" /> Calculating coverage...
            </div>
          ) : coverageData ? (
            <div className="space-y-2">
              {Object.entries(coverageData.coverage_by_category).map(([cat, data]) => (
                <div key={cat}>
                  <div className="flex items-center justify-between text-xs text-gray-600 mb-0.5">
                    <span className="capitalize">{cat}</span>
                    <span>{data.matched}/{data.total}</span>
                  </div>
                  {getCoverageBar(data.pct)}
                </div>
              ))}
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
