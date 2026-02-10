/**
 * Sentry error monitoring initialization for Jobezie frontend.
 *
 * Setup:
 *   1. npm install @sentry/react
 *   2. Set VITE_SENTRY_DSN in .env
 *   3. Call initSentry() in main.tsx BEFORE React renders
 *
 * Usage:
 *   import { captureException, captureMessage } from './monitoring';
 *
 *   try { riskyOp(); } catch (e) { captureException(e); }
 */

import * as Sentry from '@sentry/react';

// Feature flag — Sentry only active when DSN is configured
const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN || '';
const IS_ENABLED = !!SENTRY_DSN;

/**
 * Initialize Sentry. Call once in main.tsx before ReactDOM.createRoot().
 *
 * Env vars (set in .env or CI):
 *   VITE_SENTRY_DSN            — Sentry project DSN
 *   VITE_SENTRY_ENVIRONMENT    — 'production' | 'staging' | 'development'
 *   VITE_GIT_SHA               — Release version (git commit hash)
 */
export function initSentry(): void {
  if (!IS_ENABLED) {
    console.info('[Sentry] Disabled — VITE_SENTRY_DSN not set');
    return;
  }

  const environment = import.meta.env.VITE_SENTRY_ENVIRONMENT || 'development';
  const release = import.meta.env.VITE_GIT_SHA || 'dev';

  Sentry.init({
    dsn: SENTRY_DSN,
    environment,
    release,

    integrations: [
      // Automatic performance monitoring
      Sentry.browserTracingIntegration(),
      // Session replay for debugging (1% of sessions, 100% on error)
      Sentry.replayIntegration({
        maskAllText: true,     // Privacy: mask all text in replays
        blockAllMedia: true,   // Privacy: block images/videos
      }),
    ],

    // Performance: sample 10% of transactions in production
    tracesSampleRate: environment === 'production' ? 0.1 : 1.0,

    // Replay: 1% of sessions normally, 100% when error occurs
    replaysSessionSampleRate: 0.01,
    replaysOnErrorSampleRate: 1.0,

    // Don't send PII (CCPA compliance)
    beforeSend(event) {
      // Strip email/name from user context
      if (event.user) {
        delete event.user.email;
        delete event.user.username;
        delete event.user.ip_address;
      }

      // Strip auth tokens from breadcrumbs
      if (event.breadcrumbs) {
        event.breadcrumbs = event.breadcrumbs.map((crumb) => {
          if (crumb.category === 'xhr' || crumb.category === 'fetch') {
            if (crumb.data?.url?.includes('token')) {
              crumb.data.url = '[REDACTED]';
            }
          }
          return crumb;
        });
      }

      return event;
    },

    // Skip noisy errors
    ignoreErrors: [
      // Browser extensions
      'ResizeObserver loop',
      'Non-Error promise rejection captured',
      // Network errors (user is offline)
      'Failed to fetch',
      'NetworkError',
      'Load failed',
      // Auth redirects (expected behavior)
      'Unauthorized',
    ],

    // Skip third-party script errors
    denyUrls: [
      /extensions\//i,
      /^chrome:\/\//i,
      /^moz-extension:\/\//i,
    ],
  });

  console.info(`[Sentry] Initialized: env=${environment}, release=${release}`);
}

// ———————————————————————————————————————————
// Convenience wrappers
// ———————————————————————————————————————————

/**
 * Send an exception to Sentry. Safe to call even if Sentry is disabled.
 */
export function captureException(error: unknown, context?: Record<string, unknown>): void {
  console.error('[Error]', error);
  if (IS_ENABLED) {
    Sentry.captureException(error, { extra: context });
  }
}

/**
 * Send a message to Sentry.
 */
export function captureMessage(message: string, level: Sentry.SeverityLevel = 'info'): void {
  if (IS_ENABLED) {
    Sentry.captureMessage(message, level);
  }
}

/**
 * Set user context for Sentry events (ID + tier only, no PII).
 * Call after login.
 */
export function setUserContext(userId: string, tier?: string): void {
  if (IS_ENABLED) {
    Sentry.setUser({ id: userId });
    if (tier) {
      Sentry.setTag('user.tier', tier);
    }
  }
}

/**
 * Clear user context. Call on logout.
 */
export function clearUserContext(): void {
  if (IS_ENABLED) {
    Sentry.setUser(null);
  }
}

/**
 * Sentry ErrorBoundary component. Use in App.tsx to wrap the app.
 * Falls back to a passthrough when Sentry is disabled.
 */
export const SentryErrorBoundary = IS_ENABLED
  ? Sentry.ErrorBoundary
  : ({ children }: { children: React.ReactNode; fallback?: React.ReactNode }) => children;

// Re-export for use in components
export { IS_ENABLED as isSentryEnabled };
