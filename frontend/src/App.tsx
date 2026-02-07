import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { AuthProvider } from './contexts/AuthContext';
import { TourProvider } from './contexts/TourContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';

// Pages (lazy loaded)
const Login = lazy(() => import('./pages/Login').then(m => ({ default: m.Login })));
const Register = lazy(() => import('./pages/Register').then(m => ({ default: m.Register })));
const Onboarding = lazy(() => import('./pages/Onboarding').then(m => ({ default: m.Onboarding })));
const Dashboard = lazy(() => import('./pages/Dashboard').then(m => ({ default: m.Dashboard })));
const Resumes = lazy(() => import('./pages/Resumes').then(m => ({ default: m.Resumes })));
const Recruiters = lazy(() => import('./pages/Recruiters').then(m => ({ default: m.Recruiters })));
const Messages = lazy(() => import('./pages/Messages').then(m => ({ default: m.Messages })));
const Activity = lazy(() => import('./pages/Activity').then(m => ({ default: m.Activity })));
const AICoach = lazy(() => import('./pages/AICoach').then(m => ({ default: m.AICoach })));
const Settings = lazy(() => import('./pages/Settings').then(m => ({ default: m.Settings })));
const LinkedIn = lazy(() => import('./pages/LinkedIn').then(m => ({ default: m.LinkedIn })));
const LaborMarket = lazy(() => import('./pages/LaborMarket').then(m => ({ default: m.LaborMarket })));
const InterviewPrep = lazy(() => import('./pages/InterviewPrep').then(m => ({ default: m.InterviewPrep })));
const Learn = lazy(() => import('./pages/Learn').then(m => ({ default: m.Learn })));
const ForgotPassword = lazy(() => import('./pages/ForgotPassword').then(m => ({ default: m.ForgotPassword })));
const ResetPassword = lazy(() => import('./pages/ResetPassword').then(m => ({ default: m.ResetPassword })));
const Landing = lazy(() => import('./pages/Landing').then(m => ({ default: m.Landing })));
const SubscriptionSuccess = lazy(() => import('./pages/SubscriptionSuccess').then(m => ({ default: m.SubscriptionSuccess })));
const SubscriptionCancel = lazy(() => import('./pages/SubscriptionCancel').then(m => ({ default: m.SubscriptionCancel })));

import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

function PageLoader() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-500 text-sm">Loading...</p>
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Toaster richColors position="top-right" />
      <AuthProvider>
        <TourProvider>
          <BrowserRouter>
            <Suspense fallback={<PageLoader />}>
            <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password/:token" element={<ResetPassword />} />

            {/* Onboarding route (protected but doesn't require onboarding completion) */}
            <Route
              path="/onboarding"
              element={
                <ProtectedRoute requireOnboarding={false}>
                  <Onboarding />
                </ProtectedRoute>
              }
            />

            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/resumes"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Resumes />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/recruiters"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Recruiters />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/messages"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Messages />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/activity"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Activity />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/ai-coach"
              element={
                <ProtectedRoute>
                  <Layout>
                    <AICoach />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Settings />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/linkedin"
              element={
                <ProtectedRoute>
                  <Layout>
                    <LinkedIn />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/labor-market"
              element={
                <ProtectedRoute>
                  <Layout>
                    <LaborMarket />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/interview-prep"
              element={
                <ProtectedRoute>
                  <Layout>
                    <InterviewPrep />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/learn"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Learn />
                  </Layout>
                </ProtectedRoute>
              }
            />

            {/* Subscription redirect pages */}
            <Route
              path="/subscription/success"
              element={
                <ProtectedRoute requireOnboarding={false}>
                  <SubscriptionSuccess />
                </ProtectedRoute>
              }
            />
            <Route
              path="/subscription/cancel"
              element={
                <ProtectedRoute requireOnboarding={false}>
                  <SubscriptionCancel />
                </ProtectedRoute>
              }
            />

            {/* Landing page */}
            <Route path="/" element={<Landing />} />

            {/* 404 */}
            <Route
              path="*"
              element={
                <div className="min-h-screen flex items-center justify-center">
                  <div className="text-center">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
                    <p className="text-gray-600 mb-4">Page not found</p>
                    <a href="/dashboard" className="btn btn-primary">
                      Go to Dashboard
                    </a>
                  </div>
                </div>
              }
            />
            </Routes>
            </Suspense>
          </BrowserRouter>
        </TourProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
