import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ChevronLeft, Loader2, Sparkles } from 'lucide-react';
import { recruiterApi, authApi } from '../../lib/api';
import type { Recruiter } from '../../types';

const recruiterSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  company: z.string().min(1, 'Company is required'),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  title: z.string().optional(),
  linkedin_url: z.string().url('Invalid URL').optional().or(z.literal('')),
});

type RecruiterFormData = z.infer<typeof recruiterSchema>;

interface FirstRecruiterStepProps {
  onNext: (recruiter: Recruiter) => void;
  onBack: () => void;
  onSkip: () => void;
}

export function FirstRecruiterStep({ onNext, onBack, onSkip }: FirstRecruiterStepProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RecruiterFormData>({
    resolver: zodResolver(recruiterSchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      company: '',
      email: '',
      title: '',
      linkedin_url: '',
    },
  });

  const onSubmit = async (data: RecruiterFormData) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await recruiterApi.create({
        first_name: data.first_name,
        last_name: data.last_name,
        company: data.company,
        email: data.email || undefined,
        title: data.title || undefined,
        linkedin_url: data.linkedin_url || undefined,
        source: 'onboarding',
      });

      // Handle both response formats (data.recruiter or data.data.recruiter)
      const recruiter = response.data.recruiter || response.data.data?.recruiter;

      // Update onboarding step
      await authApi.updateProfile({ onboarding_step: 5 });

      onNext(recruiter);
    } catch (err) {
      console.error('Error creating recruiter:', err);
      setError('Failed to add recruiter. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSkip = async () => {
    try {
      await authApi.updateProfile({ onboarding_step: 5 });
      onSkip();
    } catch (err) {
      console.error('Error updating onboarding step:', err);
      onSkip();
    }
  };

  return (
    <div>
      <button
        onClick={onBack}
        className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
      >
        <ChevronLeft className="w-5 h-5 mr-1" />
        Back
      </button>

      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        Add your first recruiter
      </h2>
      <p className="text-gray-600 mb-8">
        Track your conversations and we'll help you craft the perfect outreach message
      </p>

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="label">First Name *</label>
            <input
              type="text"
              {...register('first_name')}
              placeholder="Sarah"
              className={`input ${errors.first_name ? 'input-error' : ''}`}
            />
            {errors.first_name && (
              <p className="error-text mt-1">{errors.first_name.message}</p>
            )}
          </div>
          <div>
            <label className="label">Last Name *</label>
            <input
              type="text"
              {...register('last_name')}
              placeholder="Chen"
              className={`input ${errors.last_name ? 'input-error' : ''}`}
            />
            {errors.last_name && (
              <p className="error-text mt-1">{errors.last_name.message}</p>
            )}
          </div>
        </div>

        <div className="mb-4">
          <label className="label">Company *</label>
          <input
            type="text"
            {...register('company')}
            placeholder="Google"
            className={`input ${errors.company ? 'input-error' : ''}`}
          />
          {errors.company && (
            <p className="error-text mt-1">{errors.company.message}</p>
          )}
        </div>

        <div className="mb-4">
          <label className="label">Title (optional)</label>
          <input
            type="text"
            {...register('title')}
            placeholder="Senior Technical Recruiter"
            className="input"
          />
        </div>

        <div className="mb-4">
          <label className="label">Email (optional)</label>
          <input
            type="email"
            {...register('email')}
            placeholder="sarah.chen@google.com"
            className={`input ${errors.email ? 'input-error' : ''}`}
          />
          {errors.email && (
            <p className="error-text mt-1">{errors.email.message}</p>
          )}
        </div>

        <div className="mb-6">
          <label className="label">LinkedIn URL (optional)</label>
          <input
            type="url"
            {...register('linkedin_url')}
            placeholder="https://linkedin.com/in/sarahchen"
            className={`input ${errors.linkedin_url ? 'input-error' : ''}`}
          />
          {errors.linkedin_url && (
            <p className="error-text mt-1">{errors.linkedin_url.message}</p>
          )}
        </div>

        {/* AI Research hint */}
        <div className="flex items-start gap-3 bg-primary-50 border border-primary-200 rounded-lg p-4 mb-6">
          <Sparkles className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
          <p className="text-primary-800 text-sm">
            After adding, we can use AI to research this recruiter and personalize
            your outreach message for better response rates.
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <div className="flex gap-4">
          <button
            type="button"
            onClick={handleSkip}
            disabled={isSubmitting}
            className="btn btn-outline flex-1"
          >
            Skip for now
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn btn-primary flex-1 flex items-center justify-center gap-2"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Adding...
              </>
            ) : (
              'Add Recruiter'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
