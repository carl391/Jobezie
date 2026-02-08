import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Loader2,
  Sparkles,
  Send,
  Save,
  RefreshCw,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';
import { Modal, ModalFooter } from '../ui/Modal';
import { ScoreCircle } from '../ui/ScoreCircle';
import { messageApi, recruiterApi, aiApi, isHandledApiError } from '../../lib/api';
import type { Message, Recruiter, MessageQualityScore } from '../../types';

const messageSchema = z.object({
  recruiter_id: z.string().min(1, 'Please select a recruiter'),
  message_type: z.enum(['initial_outreach', 'follow_up', 'thank_you', 'check_in']),
  subject: z.string().optional(),
  body: z.string().min(10, 'Message must be at least 10 characters'),
});

type MessageFormData = z.infer<typeof messageSchema>;

interface ComposeMessageModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (message: Message) => void;
  editMessage?: Message | null;
  preselectedRecruiterId?: string;
}

const MESSAGE_TYPES = [
  { value: 'initial_outreach', label: 'Initial Outreach', description: 'First contact with a recruiter' },
  { value: 'follow_up', label: 'Follow Up', description: 'Following up on a previous conversation' },
  { value: 'thank_you', label: 'Thank You', description: 'Thank you after an interview or call' },
  { value: 'check_in', label: 'Check In', description: 'Periodic check-in to maintain relationship' },
];

export function ComposeMessageModal({
  isOpen,
  onClose,
  onSuccess,
  editMessage,
  preselectedRecruiterId,
}: ComposeMessageModalProps) {
  const [recruiters, setRecruiters] = useState<Recruiter[]>([]);
  const [isLoadingRecruiters, setIsLoadingRecruiters] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [qualityScore, setQualityScore] = useState<MessageQualityScore | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tips, setTips] = useState<string[]>([]);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors },
  } = useForm<MessageFormData>({
    resolver: zodResolver(messageSchema),
    defaultValues: {
      recruiter_id: editMessage?.recruiter_id || preselectedRecruiterId || '',
      message_type: editMessage?.message_type || 'initial_outreach',
      subject: editMessage?.subject || '',
      body: editMessage?.body || '',
    },
  });

  const watchBody = watch('body');
  const watchMessageType = watch('message_type');
  const watchRecruiterId = watch('recruiter_id');

  // Fetch recruiters
  useEffect(() => {
    if (isOpen) {
      fetchRecruiters();
    }
  }, [isOpen]);

  // Fetch tips when message type changes
  useEffect(() => {
    if (watchMessageType) {
      fetchTips(watchMessageType);
    }
  }, [watchMessageType]);

  // Reset form when modal opens/closes or edit message changes
  useEffect(() => {
    if (isOpen) {
      reset({
        recruiter_id: editMessage?.recruiter_id || preselectedRecruiterId || '',
        message_type: editMessage?.message_type || 'initial_outreach',
        subject: editMessage?.subject || '',
        body: editMessage?.body || '',
      });
      setQualityScore(null);
      setError(null);
    }
  }, [isOpen, editMessage, preselectedRecruiterId, reset]);

  const fetchRecruiters = async () => {
    setIsLoadingRecruiters(true);
    try {
      const response = await recruiterApi.list({ limit: 100 });
      setRecruiters(response.data.recruiters || response.data.data?.recruiters || []);
    } catch (err) {
      console.error('Error fetching recruiters:', err);
    } finally {
      setIsLoadingRecruiters(false);
    }
  };

  const fetchTips = async (messageType: string) => {
    try {
      const response = await messageApi.getTips(messageType);
      setTips(response.data.data?.tips || response.data.tips || []);
    } catch (err) {
      console.error('Error fetching tips:', err);
      setTips([]);
    }
  };

  const handleValidate = async () => {
    if (!watchBody || watchBody.length < 10) return;

    setIsValidating(true);
    try {
      const response = await messageApi.validate({
        body: watchBody,
        message_type: watchMessageType,
      });
      setQualityScore(response.data.data?.score || response.data.score);
    } catch (err) {
      console.error('Error validating message:', err);
    } finally {
      setIsValidating(false);
    }
  };

  const handleGenerate = async () => {
    if (!watchRecruiterId) {
      setError('Please select a recruiter first');
      return;
    }

    setIsGenerating(true);
    setError(null);
    try {
      const response = await aiApi.generateMessage({
        recruiter_id: watchRecruiterId,
        message_type: watchMessageType,
      });
      const generated = response.data.data?.message || response.data.message;
      if (generated) {
        setValue('subject', generated.subject || '');
        setValue('body', generated.body || '');
      }
    } catch (err: any) {
      console.error('Error generating message:', err);
      if (!isHandledApiError(err)) toast.error('Failed to generate message');
      setError(err?.response?.data?.message || 'Failed to generate message. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const onSubmit = async (data: MessageFormData, saveAsDraft: boolean = false) => {
    setIsSubmitting(true);
    setError(null);

    try {
      let response;
      const messageData = {
        ...data,
        status: saveAsDraft ? 'draft' : 'ready',
      };

      if (editMessage) {
        response = await messageApi.update(editMessage.id, messageData);
      } else {
        response = await messageApi.create(messageData);
      }

      const message = response.data.data?.message || response.data.message;
      reset();
      onSuccess(message);
      onClose();
      toast.success(editMessage ? 'Message updated' : 'Message created');
    } catch (err: any) {
      console.error('Error saving message:', err);
      if (!isHandledApiError(err)) toast.error('Failed to save message');
      setError(err?.response?.data?.message || 'Failed to save message. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    reset();
    setQualityScore(null);
    setError(null);
    onClose();
  };

  const selectedRecruiter = recruiters.find(r => r.id === watchRecruiterId);

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={editMessage ? 'Edit Message' : 'Compose Message'}
      size="xl"
    >
      <form onSubmit={handleSubmit((data) => onSubmit(data, false))}>
        <div className="grid grid-cols-3 gap-6">
          {/* Main form - 2 columns */}
          <div className="col-span-2 space-y-4">
            {/* Recruiter select */}
            <div>
              <label className="label">Recruiter *</label>
              {isLoadingRecruiters ? (
                <div className="input flex items-center justify-center">
                  <Loader2 className="w-4 h-4 animate-spin" />
                </div>
              ) : (
                <select
                  {...register('recruiter_id')}
                  className={`input ${errors.recruiter_id ? 'input-error' : ''}`}
                >
                  <option value="">Select a recruiter...</option>
                  {recruiters.map((recruiter) => (
                    <option key={recruiter.id} value={recruiter.id}>
                      {recruiter.full_name} {recruiter.company ? `- ${recruiter.company}` : ''}
                    </option>
                  ))}
                </select>
              )}
              {errors.recruiter_id && (
                <p className="error-text mt-1">{errors.recruiter_id.message}</p>
              )}
            </div>

            {/* Message type */}
            <div>
              <label className="label">Message Type</label>
              <div className="grid grid-cols-2 gap-2">
                {MESSAGE_TYPES.map((type) => (
                  <label
                    key={type.value}
                    className={`relative flex cursor-pointer rounded-lg border p-3 transition-all ${
                      watchMessageType === type.value
                        ? 'border-primary-500 bg-primary-50 ring-1 ring-primary-500'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      {...register('message_type')}
                      value={type.value}
                      className="sr-only"
                    />
                    <div>
                      <span className="block text-sm font-medium text-gray-900">
                        {type.label}
                      </span>
                      <span className="block text-xs text-gray-500 mt-0.5">
                        {type.description}
                      </span>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Subject */}
            <div>
              <label className="label">Subject</label>
              <input
                type="text"
                {...register('subject')}
                placeholder="Enter email subject..."
                className="input"
              />
            </div>

            {/* Body */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="label mb-0">Message *</label>
                <button
                  type="button"
                  onClick={handleGenerate}
                  disabled={isGenerating || !watchRecruiterId}
                  className="btn btn-outline btn-sm"
                  data-tour="message-ai"
                >
                  {isGenerating ? (
                    <Loader2 className="w-3 h-3 animate-spin mr-1" />
                  ) : (
                    <Sparkles className="w-3 h-3 mr-1" />
                  )}
                  AI Generate
                </button>
              </div>
              <textarea
                {...register('body')}
                rows={8}
                placeholder="Write your message here..."
                className={`input resize-none ${errors.body ? 'input-error' : ''}`}
              />
              {errors.body && (
                <p className="error-text mt-1">{errors.body.message}</p>
              )}
              <div className="flex items-center justify-between mt-2">
                <span className="text-xs text-gray-500">
                  {watchBody?.length || 0} characters
                </span>
                <button
                  type="button"
                  onClick={handleValidate}
                  disabled={isValidating || !watchBody || watchBody.length < 10}
                  className="text-xs text-primary-600 hover:text-primary-700 flex items-center gap-1"
                >
                  {isValidating ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : (
                    <RefreshCw className="w-3 h-3" />
                  )}
                  Check Quality
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                {error}
              </div>
            )}
          </div>

          {/* Sidebar - 1 column */}
          <div className="space-y-4">
            {/* Selected recruiter info */}
            {selectedRecruiter && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Selected Recruiter</h4>
                <p className="text-sm text-gray-700">{selectedRecruiter.name}</p>
                {selectedRecruiter.company_name && (
                  <p className="text-xs text-gray-500">{selectedRecruiter.company_name}</p>
                )}
                {selectedRecruiter.title && (
                  <p className="text-xs text-gray-500">{selectedRecruiter.title}</p>
                )}
              </div>
            )}

            {/* Quality score */}
            {qualityScore && (
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-medium text-gray-900">Quality Score</h4>
                  <ScoreCircle score={qualityScore.overall_score} size="sm" />
                </div>
                <div className="space-y-2">
                  {[
                    { label: 'Word Count', score: qualityScore.word_count_score },
                    { label: 'Personalization', score: qualityScore.personalization_score },
                    { label: 'Metrics', score: qualityScore.metrics_score },
                    { label: 'Call to Action', score: qualityScore.cta_score },
                    { label: 'Tone', score: qualityScore.tone_score },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center justify-between text-xs">
                      <span className="text-gray-600">{item.label}</span>
                      <span className={`font-medium ${
                        item.score >= 71 ? 'text-green-600' :
                        item.score >= 41 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {item.score ?? 0}%
                      </span>
                    </div>
                  ))}
                </div>
                {qualityScore.suggestions && qualityScore.suggestions.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs font-medium text-gray-700 mb-1">Suggestions:</p>
                    <ul className="space-y-1">
                      {qualityScore.suggestions.slice(0, 3).map((suggestion, idx) => (
                        <li key={idx} className="text-xs text-gray-600 flex items-start gap-1">
                          <span className="text-yellow-500">•</span>
                          {suggestion}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Tips */}
            {tips.length > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-blue-900 mb-2 flex items-center gap-1">
                  <Sparkles className="w-4 h-4" />
                  Tips for {MESSAGE_TYPES.find(t => t.value === watchMessageType)?.label}
                </h4>
                <ul className="space-y-1.5">
                  {tips.slice(0, 4).map((tip, idx) => (
                    <li key={idx} className="text-xs text-blue-800 flex items-start gap-1">
                      <CheckCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

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
            type="button"
            onClick={handleSubmit((data) => onSubmit(data, true))}
            disabled={isSubmitting}
            className="btn btn-outline flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            Save Draft
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn btn-primary flex items-center gap-2"
          >
            {isSubmitting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            {editMessage ? 'Update' : 'Save & Send Later'}
          </button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
