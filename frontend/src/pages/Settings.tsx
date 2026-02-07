import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  User,
  Lock,
  CreditCard,
  Loader2,
  Save,
  CheckCircle,
  AlertCircle,
  Eye,
  EyeOff,
  Crown,
  Sparkles,
  Zap,
  ExternalLink,
  HelpCircle,
  Compass,
  BookOpen,
} from 'lucide-react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/Tabs';
import { Badge } from '../components/ui/Badge';
import { SkillsAutocomplete } from '../components/ui/SkillsAutocomplete';
import { authApi, subscriptionApi, dashboardApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { useTour } from '../contexts/TourContext';

// Profile form schema
const profileSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  phone: z.string().optional(),
  location: z.string().optional(),
  linkedin_url: z.string().url('Invalid URL').optional().or(z.literal('')),
  current_role: z.string().optional(),
  years_experience: z.coerce.number().min(0).max(50).optional(),
  career_stage: z.string().optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

// Password form schema
const passwordSchema = z.object({
  current_password: z.string().min(1, 'Current password is required'),
  new_password: z.string().min(8, 'Password must be at least 8 characters'),
  confirm_password: z.string(),
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
});

type PasswordFormData = z.infer<typeof passwordSchema>;

const CAREER_STAGES = [
  { value: '', label: 'Select career stage...' },
  { value: 'entry_level', label: 'Entry Level (0-2 years)' },
  { value: 'early_career', label: 'Early Career (2-5 years)' },
  { value: 'mid_career', label: 'Mid Career (5-10 years)' },
  { value: 'senior', label: 'Senior (10-15 years)' },
  { value: 'executive', label: 'Executive (15+ years)' },
  { value: 'career_change', label: 'Career Changer' },
];

const SUBSCRIPTION_TIERS = [
  {
    id: 'basic',
    name: 'Basic',
    price: 0,
    description: 'Get started with essential features',
    features: ['5 recruiter contacts', '2 resume uploads', 'Basic ATS scoring', 'Email support'],
    icon: <User className="w-5 h-5" />,
    color: 'bg-gray-100 text-gray-700',
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 19,
    description: 'For serious job seekers',
    features: ['50 recruiter contacts', '10 resume uploads', 'Advanced ATS scoring', 'AI message generation', 'Priority support'],
    icon: <Zap className="w-5 h-5" />,
    color: 'bg-blue-100 text-blue-700',
    popular: true,
  },
  {
    id: 'expert',
    name: 'Expert',
    price: 39,
    description: 'Maximum career acceleration',
    features: ['Unlimited recruiter contacts', 'Unlimited resumes', 'Full AI coaching', 'Interview prep', 'Dedicated support'],
    icon: <Crown className="w-5 h-5" />,
    color: 'bg-purple-100 text-purple-700',
  },
];

interface SelectedSkill {
  name: string;
  category: 'skills' | 'abilities' | 'knowledge';
}

interface UsageData {
  recruiters?: { used: number; limit: number };
  messages?: { used: number; limit: number };
  resumes?: { used: number; limit: number };
  research?: { used: number; limit: number };
  tailored_resumes?: { used: number; limit: number };
}

export function Settings() {
  const { user, refreshUser } = useAuth();
  const { startTour, hasCompletedTour } = useTour();
  const [activeTab, setActiveTab] = useState('profile');
  const [isUpdatingProfile, setIsUpdatingProfile] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [skills, setSkills] = useState<SelectedSkill[]>([]);
  const [usageData, setUsageData] = useState<UsageData | null>(null);
  const [subscriptionStatus, setSubscriptionStatus] = useState<{
    tier: string;
    status: string;
    current_period_end?: string;
  } | null>(null);
  const [isLoadingSubscription, setIsLoadingSubscription] = useState(false);

  // Profile form
  const {
    register: registerProfile,
    handleSubmit: handleSubmitProfile,
    reset: resetProfile,
    formState: { errors: profileErrors },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      phone: '',
      location: '',
      linkedin_url: '',
      current_role: user?.current_role || '',
      years_experience: user?.years_experience || 0,
      career_stage: user?.career_stage || '',
    },
  });

  // Password form
  const {
    register: registerPassword,
    handleSubmit: handleSubmitPassword,
    reset: resetPassword,
    formState: { errors: passwordErrors },
  } = useForm<PasswordFormData>({
    resolver: zodResolver(passwordSchema),
  });

  // Load subscription status and usage data
  useEffect(() => {
    fetchSubscriptionStatus();
    fetchUsageData();
  }, []);

  // Reset profile form when user changes
  useEffect(() => {
    if (user) {
      resetProfile({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: '',
        location: '',
        linkedin_url: '',
        current_role: user.current_role || '',
        years_experience: user.years_experience || 0,
        career_stage: user.career_stage || '',
      });
    }
  }, [user, resetProfile]);

  const fetchSubscriptionStatus = async () => {
    setIsLoadingSubscription(true);
    try {
      const response = await subscriptionApi.getStatus();
      setSubscriptionStatus(response.data.data?.subscription || response.data.subscription);
    } catch (err) {
      console.error('Error fetching subscription:', err);
    } finally {
      setIsLoadingSubscription(false);
    }
  };

  const fetchUsageData = async () => {
    try {
      const response = await dashboardApi.getDashboard();
      const usage = response.data.data?.usage || response.data.usage;
      if (usage) setUsageData(usage);
    } catch (err) {
      console.error('Error fetching usage data:', err);
    }
  };

  const handleProfileSubmit = async (data: ProfileFormData) => {
    setIsUpdatingProfile(true);
    setProfileSuccess(false);
    setError(null);

    try {
      const skillNames = skills.map((s) => s.name);
      await authApi.updateProfile({
        ...data,
        technical_skills: skillNames,
      });
      await refreshUser();
      setProfileSuccess(true);
      setTimeout(() => setProfileSuccess(false), 3000);
    } catch (err) {
      console.error('Error updating profile:', err);
      setError('Failed to update profile. Please try again.');
    } finally {
      setIsUpdatingProfile(false);
    }
  };

  const handlePasswordSubmit = async (data: PasswordFormData) => {
    setIsChangingPassword(true);
    setPasswordSuccess(false);
    setError(null);

    try {
      await authApi.changePassword({
        current_password: data.current_password,
        new_password: data.new_password,
      });
      resetPassword();
      setPasswordSuccess(true);
      setTimeout(() => setPasswordSuccess(false), 3000);
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { message?: string } } };
      console.error('Error changing password:', err);
      setError(apiError.response?.data?.message || 'Failed to change password. Please try again.');
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleManageSubscription = async () => {
    try {
      const response = await subscriptionApi.getPortal();
      const portalUrl = response.data.data?.url || response.data.url;
      if (portalUrl) {
        window.open(portalUrl, '_blank');
      }
    } catch (err) {
      console.error('Error opening portal:', err);
      setError('Failed to open subscription portal.');
    }
  };

  const handleUpgrade = async (tierId: string) => {
    try {
      const response = await subscriptionApi.createCheckout(tierId);
      const checkoutUrl = response.data.data?.url || response.data.url;
      if (checkoutUrl) {
        window.location.href = checkoutUrl;
      }
    } catch (err) {
      console.error('Error creating checkout:', err);
      setError('Failed to start upgrade process.');
    }
  };

  const currentTier = subscriptionStatus?.tier || user?.subscription_tier || 'basic';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">Manage your account and preferences</p>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="profile" value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="profile">
            <User className="w-4 h-4 mr-2" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="security">
            <Lock className="w-4 h-4 mr-2" />
            Security
          </TabsTrigger>
          <TabsTrigger value="subscription">
            <CreditCard className="w-4 h-4 mr-2" />
            Subscription
          </TabsTrigger>
          <TabsTrigger value="help">
            <HelpCircle className="w-4 h-4 mr-2" />
            Help
          </TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile">
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Profile Information</h2>

            <form onSubmit={handleSubmitProfile(handleProfileSubmit)} className="space-y-4">
              {/* Name row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">First Name *</label>
                  <input
                    type="text"
                    {...registerProfile('first_name')}
                    className={`input ${profileErrors.first_name ? 'input-error' : ''}`}
                  />
                  {profileErrors.first_name && (
                    <p className="error-text mt-1">{profileErrors.first_name.message}</p>
                  )}
                </div>
                <div>
                  <label className="label">Last Name *</label>
                  <input
                    type="text"
                    {...registerProfile('last_name')}
                    className={`input ${profileErrors.last_name ? 'input-error' : ''}`}
                  />
                  {profileErrors.last_name && (
                    <p className="error-text mt-1">{profileErrors.last_name.message}</p>
                  )}
                </div>
              </div>

              {/* Email (read-only) */}
              <div>
                <label className="label">Email</label>
                <input
                  type="email"
                  value={user?.email || ''}
                  disabled
                  className="input bg-gray-50 text-gray-500"
                />
                <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
              </div>

              {/* Contact info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">Phone</label>
                  <input
                    type="tel"
                    {...registerProfile('phone')}
                    placeholder="+1 (555) 123-4567"
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">Location</label>
                  <input
                    type="text"
                    {...registerProfile('location')}
                    placeholder="San Francisco, CA"
                    className="input"
                  />
                </div>
              </div>

              {/* LinkedIn */}
              <div>
                <label className="label">LinkedIn URL</label>
                <input
                  type="url"
                  {...registerProfile('linkedin_url')}
                  placeholder="https://linkedin.com/in/yourprofile"
                  className={`input ${profileErrors.linkedin_url ? 'input-error' : ''}`}
                />
                {profileErrors.linkedin_url && (
                  <p className="error-text mt-1">{profileErrors.linkedin_url.message}</p>
                )}
              </div>

              {/* Career info */}
              <div className="border-t border-gray-200 pt-4 mt-4">
                <h3 className="font-medium text-gray-900 mb-3">Career Information</h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="label">Current Role</label>
                    <input
                      type="text"
                      {...registerProfile('current_role')}
                      placeholder="Software Engineer"
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="label">Years of Experience</label>
                    <input
                      type="number"
                      {...registerProfile('years_experience')}
                      min="0"
                      max="50"
                      className="input"
                    />
                  </div>
                </div>

                <div className="mt-4">
                  <label className="label">Career Stage</label>
                  <select {...registerProfile('career_stage')} className="input">
                    {CAREER_STAGES.map((stage) => (
                      <option key={stage.value} value={stage.value}>
                        {stage.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Skills Section */}
              <div className="border-t border-gray-200 pt-4 mt-4">
                <h3 className="font-medium text-gray-900 mb-1">Skills</h3>
                <p className="text-xs text-gray-500 mb-3">
                  Add skills from 120 O*NET dimensions across 3 categories
                </p>
                <SkillsAutocomplete
                  selectedSkills={skills}
                  onChange={setSkills}
                  showMatchPreview={skills.length >= 5}
                />
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  {error}
                </div>
              )}

              {profileSuccess && (
                <div className="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-lg flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Profile updated successfully!
                </div>
              )}

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={isUpdatingProfile}
                  className="btn btn-primary flex items-center gap-2"
                >
                  {isUpdatingProfile ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Save className="w-4 h-4" />
                  )}
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security">
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Change Password</h2>

            <form onSubmit={handleSubmitPassword(handlePasswordSubmit)} className="space-y-4 max-w-md">
              <div>
                <label className="label">Current Password</label>
                <div className="relative">
                  <input
                    type={showCurrentPassword ? 'text' : 'password'}
                    {...registerPassword('current_password')}
                    className={`input pr-10 ${passwordErrors.current_password ? 'input-error' : ''}`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showCurrentPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {passwordErrors.current_password && (
                  <p className="error-text mt-1">{passwordErrors.current_password.message}</p>
                )}
              </div>

              <div>
                <label className="label">New Password</label>
                <div className="relative">
                  <input
                    type={showNewPassword ? 'text' : 'password'}
                    {...registerPassword('new_password')}
                    className={`input pr-10 ${passwordErrors.new_password ? 'input-error' : ''}`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {passwordErrors.new_password && (
                  <p className="error-text mt-1">{passwordErrors.new_password.message}</p>
                )}
              </div>

              <div>
                <label className="label">Confirm New Password</label>
                <input
                  type="password"
                  {...registerPassword('confirm_password')}
                  className={`input ${passwordErrors.confirm_password ? 'input-error' : ''}`}
                />
                {passwordErrors.confirm_password && (
                  <p className="error-text mt-1">{passwordErrors.confirm_password.message}</p>
                )}
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  {error}
                </div>
              )}

              {passwordSuccess && (
                <div className="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-lg flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Password changed successfully!
                </div>
              )}

              <button
                type="submit"
                disabled={isChangingPassword}
                className="btn btn-primary flex items-center gap-2"
              >
                {isChangingPassword ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Lock className="w-4 h-4" />
                )}
                Change Password
              </button>
            </form>
          </div>
        </TabsContent>

        {/* Subscription Tab */}
        <TabsContent value="subscription">
          <div className="space-y-6">
            {/* Current subscription */}
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Current Plan</h2>
                {subscriptionStatus?.status === 'active' && currentTier !== 'basic' && (
                  <button
                    onClick={handleManageSubscription}
                    className="btn btn-outline btn-sm flex items-center gap-1"
                  >
                    Manage Subscription
                    <ExternalLink className="w-3 h-3" />
                  </button>
                )}
              </div>

              {isLoadingSubscription ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 text-primary-600 animate-spin" />
                </div>
              ) : (
                <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    SUBSCRIPTION_TIERS.find(t => t.id === currentTier)?.color || 'bg-gray-100'
                  }`}>
                    {SUBSCRIPTION_TIERS.find(t => t.id === currentTier)?.icon || <User className="w-6 h-6" />}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-gray-900">
                        {SUBSCRIPTION_TIERS.find(t => t.id === currentTier)?.name || 'Basic'}
                      </h3>
                      <Badge variant={currentTier === 'basic' ? 'default' : 'primary'} size="sm">
                        {subscriptionStatus?.status || 'Active'}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600">
                      {SUBSCRIPTION_TIERS.find(t => t.id === currentTier)?.description}
                    </p>
                    {subscriptionStatus?.current_period_end && (
                      <p className="text-xs text-gray-500 mt-1">
                        Renews on {new Date(subscriptionStatus.current_period_end).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Usage meters */}
            {usageData && (
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Usage This Month</h2>
                <div className="space-y-4">
                  {[
                    { label: 'Recruiters', data: usageData.recruiters },
                    { label: 'Messages', data: usageData.messages },
                    { label: 'Resumes', data: usageData.resumes },
                  ].map(({ label, data }) => {
                    if (!data || !data.limit) return null;
                    const pct = data.limit > 0 ? Math.min(100, ((data.used ?? 0) / data.limit) * 100) : 0;
                    const barColor = pct > 80 ? 'bg-red-500' : pct > 50 ? 'bg-yellow-500' : 'bg-green-500';
                    return (
                      <div key={label}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-gray-700">{label}</span>
                          <span className="text-sm font-medium text-gray-900">
                            {data.used}/{data.limit === 999999 ? '∞' : data.limit}
                          </span>
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${barColor} rounded-full transition-all`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        {pct > 80 && data.limit !== 999999 && (
                          <p className="text-xs text-red-600 mt-1">
                            Approaching limit — upgrade for more capacity
                          </p>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Plan comparison */}
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                {currentTier === 'expert' ? 'Your Plan Features' : 'Upgrade Your Plan'}
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {SUBSCRIPTION_TIERS.map((tier) => (
                  <div
                    key={tier.id}
                    className={`relative rounded-xl border-2 p-4 ${
                      tier.id === currentTier
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {tier.popular && tier.id !== currentTier && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                        <Badge variant="primary" size="sm">
                          <Sparkles className="w-3 h-3 mr-1" />
                          Popular
                        </Badge>
                      </div>
                    )}

                    {tier.id === currentTier && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                        <Badge variant="success" size="sm">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Current Plan
                        </Badge>
                      </div>
                    )}

                    <div className="text-center mb-4 pt-2">
                      <div className={`w-10 h-10 rounded-lg mx-auto flex items-center justify-center ${tier.color}`}>
                        {tier.icon}
                      </div>
                      <h3 className="font-semibold text-gray-900 mt-2">{tier.name}</h3>
                      <div className="mt-1">
                        <span className="text-2xl font-bold text-gray-900">${tier.price}</span>
                        {tier.price > 0 && <span className="text-gray-500">/mo</span>}
                      </div>
                    </div>

                    <ul className="space-y-2 mb-4">
                      {tier.features.map((feature, index) => (
                        <li key={index} className="flex items-center gap-2 text-sm text-gray-600">
                          <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                          {feature}
                        </li>
                      ))}
                    </ul>

                    {tier.id !== currentTier && tier.price > (SUBSCRIPTION_TIERS.find(t => t.id === currentTier)?.price || 0) && (
                      <button
                        onClick={() => handleUpgrade(tier.id)}
                        className="btn btn-primary w-full"
                      >
                        Upgrade to {tier.name}
                      </button>
                    )}

                    {tier.id === currentTier && (
                      <button disabled className="btn btn-outline w-full opacity-50 cursor-not-allowed">
                        Current Plan
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </TabsContent>

        {/* Help Tab */}
        <TabsContent value="help">
          <div className="space-y-6">
            {/* Getting Started */}
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Getting Started</h2>
              <p className="text-gray-600 mb-6">
                Learn how to use Jobezie to supercharge your job search with our interactive tour and features guide.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-lg border border-gray-200 hover:border-primary-300 transition-colors">
                  <div className="flex items-center mb-3">
                    <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center mr-3">
                      <Compass className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">Platform Tour</h3>
                      <p className="text-xs text-gray-500">
                        {hasCompletedTour('main') ? 'Completed' : '2 min walkthrough'}
                      </p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-4">
                    Take an interactive tour of Jobezie's key features and learn how to navigate the platform.
                  </p>
                  <button
                    onClick={() => startTour('main')}
                    className="btn btn-primary w-full flex items-center justify-center gap-2"
                  >
                    <Compass className="w-4 h-4" />
                    {hasCompletedTour('main') ? 'Retake Tour' : 'Start Tour'}
                  </button>
                </div>

                <Link
                  to="/learn"
                  className="p-4 rounded-lg border border-gray-200 hover:border-primary-300 transition-colors block"
                >
                  <div className="flex items-center mb-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center mr-3">
                      <BookOpen className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">Features Guide</h3>
                      <p className="text-xs text-gray-500">Documentation</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-4">
                    Browse detailed documentation for all Jobezie features with tips and best practices.
                  </p>
                  <div className="btn btn-outline w-full flex items-center justify-center gap-2">
                    <BookOpen className="w-4 h-4" />
                    View Features Guide
                  </div>
                </Link>
              </div>
            </div>

            {/* Quick Tours */}
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Feature Tours</h2>
              <p className="text-gray-600 mb-4">
                Take quick tours of specific features to learn how they work.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {[
                  { id: 'dashboard', name: 'Dashboard', description: 'Career readiness and pipeline' },
                  { id: 'resumes', name: 'Resumes', description: 'ATS scoring and optimization' },
                  { id: 'recruiters', name: 'Recruiters', description: 'CRM and pipeline stages' },
                  { id: 'messages', name: 'Messages', description: 'AI-powered messaging' },
                  { id: 'activity', name: 'Activity', description: 'Timeline and Kanban' },
                  { id: 'ai-coach', name: 'AI Coach', description: 'Career coaching chat' },
                ].map((tour) => (
                  <button
                    key={tour.id}
                    onClick={() => startTour(tour.id)}
                    className="p-3 text-left rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-gray-900">{tour.name}</span>
                      {hasCompletedTour(tour.id) && (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{tour.description}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Support */}
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Need More Help?</h2>
              <p className="text-gray-600">
                Can't find what you're looking for?{' '}
                <a
                  href="mailto:support@jobezie.com"
                  className="text-primary-600 hover:text-primary-700 font-medium"
                >
                  Contact our support team
                </a>
                {' '}and we'll be happy to assist you.
              </p>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
