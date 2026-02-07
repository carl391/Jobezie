import { useState } from 'react';
import { toast } from 'sonner';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Loader2, Sparkles } from 'lucide-react';
import { Modal, ModalFooter } from '../ui/Modal';
import { recruiterApi } from '../../lib/api';
import type { Recruiter } from '../../types';

const recruiterSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  company: z.string().min(1, 'Company is required'),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  phone: z.string().optional(),
  title: z.string().optional(),
  linkedin_url: z.string().url('Invalid URL').optional().or(z.literal('')),
  specialty: z.string().optional(),
  source: z.string().optional(),
  notes: z.string().optional(),
});

type RecruiterFormData = z.infer<typeof recruiterSchema>;

interface AddRecruiterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (recruiter: Recruiter) => void;
}

const SOURCE_OPTIONS = [
  { value: '', label: 'Select source...' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'referral', label: 'Referral' },
  { value: 'job_board', label: 'Job Board' },
  { value: 'company_website', label: 'Company Website' },
  { value: 'networking_event', label: 'Networking Event' },
  { value: 'cold_outreach', label: 'Cold Outreach' },
  { value: 'other', label: 'Other' },
];

const SPECIALTY_OPTIONS = [
  { value: '', label: 'Select specialty...' },
  { value: 'technology', label: 'Technology' },
  { value: 'finance', label: 'Finance' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'marketing', label: 'Marketing' },
  { value: 'sales', label: 'Sales' },
  { value: 'executive', label: 'Executive Search' },
  { value: 'engineering', label: 'Engineering' },
  { value: 'product', label: 'Product' },
  { value: 'design', label: 'Design' },
  { value: 'general', label: 'General' },
];

export function AddRecruiterModal({ isOpen, onClose, onSuccess }: AddRecruiterModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<RecruiterFormData>({
    resolver: zodResolver(recruiterSchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      company: '',
      email: '',
      phone: '',
      title: '',
      linkedin_url: '',
      specialty: '',
      source: '',
      notes: '',
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
        phone: data.phone || undefined,
        title: data.title || undefined,
        linkedin_url: data.linkedin_url || undefined,
        specialty: data.specialty || undefined,
        source: data.source || undefined,
        notes: data.notes || undefined,
      });

      const recruiter = response.data.data?.recruiter || response.data.recruiter;
      reset();
      onSuccess(recruiter);
      onClose();
      toast.success('Recruiter added successfully');
    } catch (err) {
      console.error('Error creating recruiter:', err);
      toast.error('Failed to add recruiter');
      setError('Failed to add recruiter. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    reset();
    setError(null);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Add Recruiter" size="lg">
      <form onSubmit={handleSubmit(onSubmit)}>
        {/* Name row */}
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

        {/* Company */}
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

        {/* Title */}
        <div className="mb-4">
          <label className="label">Title</label>
          <input
            type="text"
            {...register('title')}
            placeholder="Senior Technical Recruiter"
            className="input"
          />
        </div>

        {/* Contact row */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="label">Email</label>
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
          <div>
            <label className="label">Phone</label>
            <input
              type="tel"
              {...register('phone')}
              placeholder="+1 (555) 123-4567"
              className="input"
            />
          </div>
        </div>

        {/* LinkedIn */}
        <div className="mb-4">
          <label className="label">LinkedIn URL</label>
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

        {/* Specialty and Source row */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="label">Specialty</label>
            <select {...register('specialty')} className="input">
              {SPECIALTY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Source</label>
            <select {...register('source')} className="input">
              {SOURCE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Notes */}
        <div className="mb-4">
          <label className="label">Notes</label>
          <textarea
            {...register('notes')}
            rows={3}
            placeholder="Any initial notes about this recruiter..."
            className="input resize-none"
          />
        </div>

        {/* AI Research hint */}
        <div className="flex items-start gap-3 bg-primary-50 border border-primary-200 rounded-lg p-4 mb-4">
          <Sparkles className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
          <p className="text-primary-800 text-sm">
            After adding, we can use AI to research this recruiter and personalize
            your outreach messages for better response rates.
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        <ModalFooter>
          <button
            type="button"
            onClick={handleClose}
            disabled={isSubmitting}
            className="btn btn-outline"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn btn-primary flex items-center gap-2"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Adding...
              </>
            ) : (
              'Add Recruiter'
            )}
          </button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
