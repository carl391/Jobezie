import { useState } from 'react';
import { Mail, X, Loader2 } from 'lucide-react';

interface EmailVerificationBannerProps {
  onResend: () => void;
  isResending: boolean;
}

const DISMISS_KEY = 'jobezie_hide_verification_banner';

export function EmailVerificationBanner({ onResend, isResending }: EmailVerificationBannerProps) {
  const [hidden, setHidden] = useState(() => localStorage.getItem(DISMISS_KEY) === 'true');

  if (hidden) return null;

  const handleDismiss = () => {
    localStorage.setItem(DISMISS_KEY, 'true');
    setHidden(true);
  };

  return (
    <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center flex-shrink-0">
          <Mail className="w-4 h-4 text-amber-600" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-amber-900">
            Please verify your email address
          </p>
          <p className="text-xs text-amber-700 mt-0.5">
            Check your inbox for the verification link, or request a new one.
          </p>
        </div>
        <button
          onClick={onResend}
          disabled={isResending}
          className="px-3 py-1.5 text-xs font-medium text-amber-700 bg-amber-100 hover:bg-amber-200 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-1 flex-shrink-0"
        >
          {isResending ? (
            <>
              <Loader2 className="w-3 h-3 animate-spin" />
              Sending...
            </>
          ) : (
            'Resend'
          )}
        </button>
        <button
          onClick={handleDismiss}
          className="p-1 hover:bg-amber-100 rounded-lg transition-colors flex-shrink-0"
          aria-label="Dismiss"
        >
          <X className="w-4 h-4 text-amber-400" />
        </button>
      </div>
    </div>
  );
}
