import { useState, useEffect } from 'react';
import { Bot, Info, X } from 'lucide-react';

interface AIDisclosureProps {
  featureId: string;
}

function getStorageKey(featureId: string) {
  return `jobezie_ai_disclosure_${featureId}`;
}

export function AIDisclosure({ featureId }: AIDisclosureProps) {
  const [dismissed, setDismissed] = useState(true);
  const [tooltipOpen, setTooltipOpen] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(getStorageKey(featureId));
    setDismissed(stored === 'dismissed');
  }, [featureId]);

  const handleDismiss = () => {
    localStorage.setItem(getStorageKey(featureId), 'dismissed');
    setDismissed(true);
  };

  // After dismissal, show compact info icon
  if (dismissed) {
    return (
      <div className="relative inline-flex mb-2">
        <button
          onClick={() => setTooltipOpen(!tooltipOpen)}
          className="inline-flex items-center gap-1 text-xs text-blue-500 hover:text-blue-600 transition-colors"
          aria-label="AI disclosure info"
        >
          <Info className="w-3.5 h-3.5" />
          <span>AI-powered</span>
        </button>
        {tooltipOpen && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setTooltipOpen(false)} />
            <div className="absolute top-full left-0 mt-1 z-50 w-72 p-3 bg-white rounded-lg shadow-lg border border-gray-200 text-xs text-gray-600">
              This feature uses AI (Claude and GPT-4) to generate suggestions. Results are guidance only and should be reviewed before use.
            </div>
          </>
        )}
      </div>
    );
  }

  // Full banner on first use
  return (
    <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-xl">
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
          <Bot className="w-4 h-4 text-blue-600" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-blue-900">AI-Powered Feature</p>
          <p className="text-sm text-blue-700 mt-1">
            This feature uses AI (Claude and GPT-4) to generate suggestions. AI-generated content is guidance only and should be reviewed before use.
          </p>
        </div>
        <button
          onClick={handleDismiss}
          className="flex-shrink-0 p-1 hover:bg-blue-100 rounded-lg transition-colors"
          aria-label="Dismiss AI disclosure"
        >
          <X className="w-4 h-4 text-blue-400" />
        </button>
      </div>
      <div className="mt-3 flex justify-end">
        <button
          onClick={handleDismiss}
          className="px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-100 hover:bg-blue-200 rounded-lg transition-colors"
        >
          I Understand
        </button>
      </div>
    </div>
  );
}
