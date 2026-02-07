import { useState, useEffect, useRef, useCallback } from 'react';
import { Search, Loader2, TrendingUp, Sparkles, X } from 'lucide-react';
import { laborMarketApi } from '../../lib/api';
import type { OccupationResult } from '../../types';

interface OccupationAutocompleteProps {
  value: string;
  onChange: (title: string, occupation?: OccupationResult) => void;
  placeholder?: string;
  showShortagePreview?: boolean;
  className?: string;
}

export function OccupationAutocomplete({
  value,
  onChange,
  placeholder = 'Search occupations (e.g., Software Developer)',
  showShortagePreview = true,
  className = '',
}: OccupationAutocompleteProps) {
  const [query, setQuery] = useState(value || '');
  const [results, setResults] = useState<OccupationResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedOccupation, setSelectedOccupation] = useState<OccupationResult | null>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    setQuery(value || '');
  }, [value]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const searchOccupations = useCallback(async (q: string) => {
    if (q.length < 2) {
      setResults([]);
      return;
    }
    setIsLoading(true);
    try {
      const res = await laborMarketApi.searchOccupations(q, 8);
      setResults(res.data.data || []);
    } catch {
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleInputChange = (val: string) => {
    setQuery(val);
    setSelectedOccupation(null);
    setIsOpen(true);

    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => searchOccupations(val), 300);
  };

  const handleSelect = (occ: OccupationResult) => {
    setQuery(occ.title);
    setSelectedOccupation(occ);
    setIsOpen(false);
    onChange(occ.title, occ);
  };

  const handleClear = () => {
    setQuery('');
    setSelectedOccupation(null);
    onChange('');
  };

  const getScoreColor = (score: number) => {
    if (score >= 71) return 'text-green-600 bg-green-50';
    if (score >= 41) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <div ref={wrapperRef} className={`relative ${className}`}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => handleInputChange(e.target.value)}
          onFocus={() => query.length >= 2 && setIsOpen(true)}
          placeholder={placeholder}
          className="input pl-10 pr-10"
        />
        {isLoading && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 animate-spin" />
        )}
        {query && !isLoading && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Dropdown */}
      {isOpen && results.length > 0 && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-72 overflow-y-auto">
          {results.map((occ) => (
            <button
              key={occ.id}
              type="button"
              onClick={() => handleSelect(occ)}
              className="w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900 truncate">{occ.title}</span>
                    {occ.bright_outlook && (
                      <Sparkles className="w-3.5 h-3.5 text-yellow-500 flex-shrink-0" />
                    )}
                  </div>
                  {occ.job_zone && (
                    <span className="text-xs text-gray-500">Zone {occ.job_zone}</span>
                  )}
                </div>
                {occ.shortage_score !== undefined && (
                  <span className={`text-xs font-medium px-2 py-1 rounded-full ${getScoreColor(occ.shortage_score)}`}>
                    {occ.shortage_score}/100
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>
      )}

      {isOpen && query.length >= 2 && !isLoading && results.length === 0 && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg p-4 text-center text-sm text-gray-500">
          No occupations found for "{query}"
        </div>
      )}

      {/* Shortage preview */}
      {showShortagePreview && selectedOccupation && selectedOccupation.shortage_score !== undefined && (
        <div className={`mt-2 flex items-center gap-2 px-3 py-2 rounded-lg ${getScoreColor(selectedOccupation.shortage_score)}`}>
          <TrendingUp className="w-4 h-4" />
          <span className="text-sm font-medium">
            {selectedOccupation.title}: {selectedOccupation.shortage_score}/100 shortage score
          </span>
          <span className="text-xs opacity-75">
            {selectedOccupation.shortage_score >= 71 ? '— high demand!' : selectedOccupation.shortage_score >= 41 ? '— moderate demand' : '— competitive market'}
          </span>
        </div>
      )}
    </div>
  );
}
