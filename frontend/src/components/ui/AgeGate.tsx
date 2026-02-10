import { useState } from 'react';

interface AgeGateProps {
  value: string;
  onChange: (year: string) => void;
  error?: string;
}

const CURRENT_YEAR = new Date().getFullYear();
const MIN_AGE = 13;
const MAX_AGE = 100;

const YEAR_OPTIONS = Array.from(
  { length: MAX_AGE - MIN_AGE + 1 },
  (_, i) => CURRENT_YEAR - MIN_AGE - i
);

/**
 * AgeGate — Birth year selector with COPPA age validation.
 * Year-only collection (privacy minimization). Blocks under-13 users.
 */
export function AgeGate({ value, onChange, error: externalError }: AgeGateProps) {
  const [internalError, setInternalError] = useState('');
  const isUnder13 = value !== '' && CURRENT_YEAR - parseInt(value) < MIN_AGE;
  const displayError = externalError || internalError;

  const handleChange = (year: string) => {
    setInternalError('');
    onChange(year);

    if (year && CURRENT_YEAR - parseInt(year) < MIN_AGE) {
      setInternalError('You must be at least 13 years old to use Jobezie.');
    }
  };

  if (isUnder13) {
    return (
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          Birth Year <span className="text-red-500">*</span>
        </label>
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-5 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-amber-100">
            <span className="text-2xl" role="img" aria-label="Lock">
              &#128274;
            </span>
          </div>
          <h3 className="text-base font-semibold text-amber-900">
            Age Requirement
          </h3>
          <p className="mt-2 text-sm text-amber-700">
            Jobezie is designed for users who are 13 years of age or older. We
            take the safety and privacy of young people seriously.
          </p>
          <button
            type="button"
            onClick={() => onChange('')}
            className="mt-4 text-sm text-amber-600 underline hover:text-amber-800"
          >
            Go back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <label
        htmlFor="jobezie-birth-year"
        className="block text-sm font-medium text-gray-700"
      >
        Birth Year <span className="text-red-500">*</span>
      </label>

      <select
        id="jobezie-birth-year"
        value={value}
        onChange={(e) => handleChange(e.target.value)}
        required
        className={`mt-1 block w-full rounded-lg border px-3 py-2.5 text-sm
          ${
            displayError
              ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
              : 'border-gray-300 focus:border-primary-500 focus:ring-primary-500'
          }
          bg-white text-gray-900 focus:outline-none focus:ring-2 transition-colors`}
      >
        <option value="">Select your birth year</option>
        {YEAR_OPTIONS.map((year) => (
          <option key={year} value={year}>
            {year}
          </option>
        ))}
      </select>

      {displayError && !isUnder13 && (
        <p className="mt-1.5 text-sm text-red-600">
          {displayError}
        </p>
      )}

      <p className="mt-1 text-xs text-gray-500">
        Required for account verification. Only your birth year is stored.
      </p>
    </div>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function validateBirthYear(birthYear: string): { valid: boolean; error?: string } {
  if (!birthYear) {
    return { valid: false, error: 'Birth year is required' };
  }

  const year = parseInt(birthYear);
  if (isNaN(year)) {
    return { valid: false, error: 'Invalid birth year' };
  }

  const age = CURRENT_YEAR - year;
  if (age < MIN_AGE) {
    return { valid: false, error: 'You must be at least 13 years old to use Jobezie.' };
  }

  if (year < CURRENT_YEAR - MAX_AGE || year > CURRENT_YEAR) {
    return { valid: false, error: 'Invalid birth year' };
  }

  return { valid: true };
}
