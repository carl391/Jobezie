import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '../contexts/AuthContext';
import { subscriptionApi } from '../lib/api';
import { Eye, EyeOff, Loader2, Check, X, Target, Sparkles, TrendingUp, CreditCard } from 'lucide-react';
import clsx from 'clsx';

const PLAN_INFO: Record<string, { name: string; price: number; period: string }> = {
  basic: { name: 'Basic', price: 0, period: 'Free forever' },
  pro: { name: 'Pro', price: 19, period: '/month' },
  expert: { name: 'Expert', price: 39, period: '/month' },
  career_keeper: { name: 'Career Keeper', price: 9, period: '/month' },
};

const registerSchema = z
  .object({
    name: z.string().min(2, 'Name must be at least 2 characters'),
    email: z.string().email('Please enter a valid email'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Password must contain at least one number'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

const BENEFITS = [
  { icon: Target, title: 'Smart ATS Scoring', desc: '7-component resume analysis powered by AI' },
  { icon: Sparkles, title: 'AI Career Coach', desc: 'Get personalized guidance from Claude & GPT-4' },
  { icon: TrendingUp, title: 'Market Intelligence', desc: 'Real-time salary data & demand insights' },
];

export function Register() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const selectedPlan = searchParams.get('plan') || 'basic';
  const planInfo = PLAN_INFO[selectedPlan] || PLAN_INFO.basic;
  const isPaidPlan = selectedPlan !== 'basic' && planInfo.price > 0;

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const password = watch('password', '');

  const passwordRequirements = [
    { label: 'At least 8 characters', met: password.length >= 8 },
    { label: 'One uppercase letter', met: /[A-Z]/.test(password) },
    { label: 'One lowercase letter', met: /[a-z]/.test(password) },
    { label: 'One number', met: /[0-9]/.test(password) },
  ];

  const onSubmit = async (data: RegisterFormData) => {
    setError(null);
    try {
      await registerUser(data.email, data.password, data.name);

      if (isPaidPlan) {
        // Redirect to Stripe checkout for paid plans
        try {
          const response = await subscriptionApi.createCheckout(selectedPlan);
          const checkoutUrl = response.data.data?.checkout_url || response.data.checkout_url;
          if (checkoutUrl) {
            window.location.href = checkoutUrl;
            return;
          }
        } catch {
          // If checkout fails, still go to dashboard — user can upgrade from Settings
        }
      }

      navigate('/dashboard');
    } catch (err: unknown) {
      const error = err as { response?: { data?: { message?: string } } };
      setError(error.response?.data?.message || 'Failed to create account. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Brand Panel - Left Side */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-600 via-primary-700 to-purple-700 relative overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute top-0 left-0 w-full h-full">
          <div className="absolute top-32 right-10 w-80 h-80 bg-white/5 rounded-full blur-3xl" />
          <div className="absolute bottom-10 left-10 w-64 h-64 bg-purple-400/10 rounded-full blur-3xl" />
        </div>

        <div className="relative z-10 flex flex-col justify-center px-12 xl:px-16 text-white">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-12">
            <svg width="44" height="44" viewBox="0 0 1024 1024" className="flex-shrink-0">
              <rect width="1024" height="1024" rx="228" fill="rgba(255,255,255,0.2)"/>
              <text x="512" y="712" textAnchor="middle" style={{ fontSize: 546, fontFamily: 'system-ui, -apple-system, sans-serif', fontWeight: 700, fill: '#FFFFFF' }}>J</text>
            </svg>
            <svg width="120" height="38" viewBox="0 0 320 100">
              <text x="160" y="65" textAnchor="middle" style={{ fontSize: 64, fontFamily: 'system-ui, -apple-system, sans-serif', fontWeight: 700, fill: '#FFFFFF', letterSpacing: '-0.03em' }}>Jobezie</text>
            </svg>
          </div>

          <h2 className="text-3xl xl:text-4xl font-bold mb-4 leading-tight">
            Start your career
            <br />
            acceleration today
          </h2>
          <p className="text-lg text-white/80 mb-10 max-w-md">
            Free to get started. No credit card required. Upgrade anytime as your career grows.
          </p>

          {/* Benefits */}
          <div className="space-y-6">
            {BENEFITS.map((benefit, i) => (
              <div key={i} className="flex items-start gap-4">
                <div className="w-12 h-12 bg-white/15 backdrop-blur-sm rounded-xl flex items-center justify-center flex-shrink-0">
                  <benefit.icon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="font-semibold text-white">{benefit.title}</p>
                  <p className="text-sm text-white/70 mt-0.5">{benefit.desc}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Testimonial-style quote */}
          <div className="mt-12 p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/10">
            <p className="text-white/90 italic text-sm leading-relaxed">
              "The AI scoring told me exactly what to fix. I went from a 42 to an 87 ATS score and got 3x more callbacks."
            </p>
            <p className="mt-3 text-xs text-white/50">-- Built with evidence-based career science</p>
          </div>
        </div>
      </div>

      {/* Form Panel - Right Side */}
      <div className="flex-1 flex items-center justify-center bg-gray-50 px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-md w-full">
          {/* Mobile logo */}
          <div className="lg:hidden text-center mb-8">
            <div className="inline-flex items-center gap-2">
              <svg width="36" height="36" viewBox="0 0 1024 1024" className="flex-shrink-0">
                <defs><linearGradient id="regMobGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stopColor="#2563EB"/><stop offset="100%" stopColor="#7C3AED"/></linearGradient></defs>
                <rect width="1024" height="1024" rx="228" fill="url(#regMobGrad)"/>
                <text x="512" y="712" textAnchor="middle" style={{ fontSize: 546, fontFamily: 'system-ui, -apple-system, sans-serif', fontWeight: 700, fill: '#FFFFFF' }}>J</text>
              </svg>
              <svg width="110" height="34" viewBox="0 0 320 100">
                <defs><linearGradient id="regMobWord" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stopColor="#2563EB"/><stop offset="100%" stopColor="#7C3AED"/></linearGradient></defs>
                <text x="160" y="65" textAnchor="middle" style={{ fontSize: 64, fontFamily: 'system-ui, -apple-system, sans-serif', fontWeight: 700, fill: 'url(#regMobWord)', letterSpacing: '-0.03em' }}>Jobezie</text>
              </svg>
            </div>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900">Create your account</h2>
            <p className="mt-2 text-gray-600">Start optimizing your job search today</p>
          </div>

          {/* Selected plan indicator */}
          {isPaidPlan ? (
            <div className="mb-4 p-3 rounded-xl bg-gradient-to-r from-primary-50 to-purple-50 border border-primary-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CreditCard className="w-4 h-4 text-primary-600" />
                <span className="text-sm font-medium text-gray-900">
                  {planInfo.name} plan — <span className="text-primary-600">${planInfo.price}{planInfo.period}</span>
                </span>
              </div>
              <Link to="/#pricing" className="text-xs text-primary-600 hover:text-primary-700 font-medium">
                Change
              </Link>
            </div>
          ) : (
            <div className="mb-4 p-3 rounded-xl bg-gray-50 border border-gray-200 flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Free plan — no credit card required</span>
              <Link to="/#pricing" className="text-xs text-primary-600 hover:text-primary-700 font-medium">
                View plans
              </Link>
            </div>
          )}

          <div className="card">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
              {error && (
                <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-600">
                  {error}
                </div>
              )}

              <div>
                <label htmlFor="name" className="label">
                  Full name
                </label>
                <input
                  {...register('name')}
                  type="text"
                  id="name"
                  autoComplete="name"
                  className={clsx('input', errors.name && 'input-error')}
                  placeholder="John Doe"
                />
                {errors.name && <p className="error-text">{errors.name.message}</p>}
              </div>

              <div>
                <label htmlFor="email" className="label">
                  Email address
                </label>
                <input
                  {...register('email')}
                  type="email"
                  id="email"
                  autoComplete="email"
                  className={clsx('input', errors.email && 'input-error')}
                  placeholder="you@example.com"
                />
                {errors.email && <p className="error-text">{errors.email.message}</p>}
              </div>

              <div>
                <label htmlFor="password" className="label">
                  Password
                </label>
                <div className="relative">
                  <input
                    {...register('password')}
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    autoComplete="new-password"
                    className={clsx('input pr-10', errors.password && 'input-error')}
                    placeholder="Create a strong password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                {password && (
                  <div className="mt-2 space-y-1">
                    {passwordRequirements.map((req, index) => (
                      <div key={index} className="flex items-center text-xs">
                        {req.met ? (
                          <Check className="w-3 h-3 text-green-500 mr-1" />
                        ) : (
                          <X className="w-3 h-3 text-gray-300 mr-1" />
                        )}
                        <span className={req.met ? 'text-green-600' : 'text-gray-500'}>
                          {req.label}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <label htmlFor="confirmPassword" className="label">
                  Confirm password
                </label>
                <div className="relative">
                  <input
                    {...register('confirmPassword')}
                    type={showConfirmPassword ? 'text' : 'password'}
                    id="confirmPassword"
                    autoComplete="new-password"
                    className={clsx('input pr-10', errors.confirmPassword && 'input-error')}
                    placeholder="Confirm your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
                {errors.confirmPassword && (
                  <p className="error-text">{errors.confirmPassword.message}</p>
                )}
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full flex items-center justify-center px-4 py-3 rounded-xl text-white font-medium bg-gradient-to-r from-primary-600 to-purple-600 hover:from-primary-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-primary-500/25"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    {isPaidPlan ? 'Creating account...' : 'Creating account...'}
                  </>
                ) : isPaidPlan ? (
                  `Create account & continue to payment`
                ) : (
                  'Create free account'
                )}
              </button>

              <p className="text-xs text-center text-gray-400">
                By creating an account, you agree to our Terms of Service and Privacy Policy
              </p>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Already have an account?{' '}
                <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
                  Sign in
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
