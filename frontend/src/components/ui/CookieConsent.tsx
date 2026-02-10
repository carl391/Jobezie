import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Cookie, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const STORAGE_KEY = 'jobezie_cookie_consent';

type ConsentStatus = 'accepted' | 'declined' | null;

function getConsentStatus(): ConsentStatus {
  try {
    return localStorage.getItem(STORAGE_KEY) as ConsentStatus;
  } catch {
    return null;
  }
}

function setConsentStatus(status: 'accepted' | 'declined'): void {
  try {
    localStorage.setItem(STORAGE_KEY, status);
  } catch {
    // localStorage unavailable
  }
}

export function CookieConsent({ privacyPolicyUrl = '/privacy' }: { privacyPolicyUrl?: string }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!getConsentStatus()) {
      const timer = setTimeout(() => setVisible(true), 1200);
      return () => clearTimeout(timer);
    }
  }, []);

  if (!visible) return null;

  const handleAccept = () => {
    setConsentStatus('accepted');
    setVisible(false);
    try {
      if ((window as any).posthog) {
        (window as any).posthog.opt_in_capturing();
      }
    } catch { /* noop */ }
  };

  const handleDecline = () => {
    setConsentStatus('declined');
    setVisible(false);
    try {
      if ((window as any).posthog) {
        (window as any).posthog.opt_out_capturing();
      }
    } catch { /* noop */ }
  };

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          className="fixed bottom-0 inset-x-0 z-50 p-4 sm:p-6 pointer-events-none"
          role="dialog"
          aria-label="Cookie consent"
        >
          <div className="pointer-events-auto mx-auto max-w-2xl rounded-xl border border-gray-200 bg-white shadow-2xl">
            <div className="p-4 sm:p-5">
              <div className="flex items-start gap-3">
                <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-purple-100">
                  <Cookie className="h-4 w-4 text-purple-600" />
                </div>

                <div className="min-w-0 flex-1">
                  <p className="text-sm text-gray-700">
                    Jobezie uses cookies and similar technologies to improve your
                    experience, analyze usage, and personalize content.{' '}
                    <Link
                      to={privacyPolicyUrl}
                      className="font-medium text-primary-600 underline hover:text-primary-800"
                    >
                      Privacy Policy
                    </Link>
                  </p>

                  <div className="mt-3 flex flex-wrap items-center gap-3">
                    <button
                      onClick={handleAccept}
                      className="rounded-lg bg-gradient-to-r from-primary-600 to-purple-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:from-primary-700 hover:to-purple-700 transition-all"
                    >
                      Accept all
                    </button>
                    <button
                      onClick={handleDecline}
                      className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      Essential only
                    </button>
                  </div>
                </div>

                {/* Mobile close button */}
                <button
                  onClick={handleDecline}
                  className="shrink-0 rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors sm:hidden"
                  aria-label="Close cookie banner"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
