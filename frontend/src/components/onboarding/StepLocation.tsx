import { useState, useRef } from 'react';
import { X, MapPin } from 'lucide-react';
import type { OnboardingData } from '../../types';

interface StepLocationProps {
  data: OnboardingData;
  onSave: (data: Partial<OnboardingData>) => void;
  onNext: () => void;
  onSkip: () => void;
}

export function StepLocation({ data, onSave, onNext, onSkip }: StepLocationProps) {
  const [locations, setLocations] = useState<string[]>(data.location_preferences || []);
  const [remoteOpen, setRemoteOpen] = useState(data.remote_preference ?? false);
  const [relocationOpen, setRelocationOpen] = useState(data.relocation_open ?? false);
  const inputRef = useRef<HTMLInputElement>(null);

  const addLocation = (loc: string) => {
    const trimmed = loc.trim();
    if (trimmed && !locations.includes(trimmed)) {
      setLocations([...locations, trimmed]);
    }
  };

  const removeLocation = (loc: string) => {
    setLocations(locations.filter(l => l !== loc));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const value = e.currentTarget.value.trim();
      if (value) {
        addLocation(value);
        e.currentTarget.value = '';
      }
    }
  };

  const handleContinue = () => {
    onSave({
      location_preferences: locations,
      remote_preference: remoteOpen,
      relocation_open: relocationOpen,
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
        Where do you want to work?
      </h2>
      <p className="text-gray-600 mb-8">
        Add your preferred locations and work preferences
      </p>

      {/* Location input */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Preferred Locations
        </label>
        <div className="relative">
          <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            ref={inputRef}
            type="text"
            placeholder="e.g., San Francisco, CA (press Enter to add)"
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            onKeyDown={handleKeyDown}
          />
        </div>

        {/* Location tags */}
        {locations.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {locations.map(loc => (
              <span
                key={loc}
                className="inline-flex items-center gap-1 px-3 py-1.5 bg-primary-100 text-primary-800 rounded-full text-sm"
              >
                {loc}
                <button onClick={() => removeLocation(loc)} className="text-primary-600 hover:text-primary-800">
                  <X className="w-3.5 h-3.5" />
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Toggle switches */}
      <div className="space-y-3 mb-8">
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
          <div>
            <div className="font-medium text-gray-900">Open to remote work</div>
            <div className="text-sm text-gray-500">Include fully remote opportunities</div>
          </div>
          <button
            role="switch"
            aria-checked={remoteOpen}
            onClick={() => setRemoteOpen(!remoteOpen)}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              remoteOpen ? 'bg-primary-600' : 'bg-gray-300'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                remoteOpen ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
          <div>
            <div className="font-medium text-gray-900">Open to relocation</div>
            <div className="text-sm text-gray-500">Willing to move for the right role</div>
          </div>
          <button
            role="switch"
            aria-checked={relocationOpen}
            onClick={() => setRelocationOpen(!relocationOpen)}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              relocationOpen ? 'bg-primary-600' : 'bg-gray-300'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                relocationOpen ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
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
