import { useState, useEffect } from 'react';
import {
  Loader2,
  FileText,
  Calendar,
  HardDrive,
  Star,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';
import { Modal } from '../ui/Modal';
import { Badge } from '../ui/Badge';
import { resumeApi } from '../../lib/api';
import type { Resume } from '../../types';

interface ViewResumeModalProps {
  isOpen: boolean;
  onClose: () => void;
  resumeId: string;
}

interface ResumeDetails extends Resume {
  parsed_content?: {
    contact?: {
      name?: string;
      email?: string;
      phone?: string;
      location?: string;
      linkedin?: string;
    };
    summary?: string;
    skills?: string[];
    experience?: {
      title: string;
      company: string;
      duration: string;
      description: string;
    }[];
    education?: {
      degree: string;
      institution: string;
      year: string;
    }[];
  };
  suggestions?: string[];
}

export function ViewResumeModal({ isOpen, onClose, resumeId }: ViewResumeModalProps) {
  const [resume, setResume] = useState<ResumeDetails | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && resumeId) {
      fetchResume();
    }
  }, [isOpen, resumeId]);

  const fetchResume = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [resumeRes, suggestionsRes] = await Promise.all([
        resumeApi.get(resumeId),
        resumeApi.getSuggestions(resumeId).catch(() => ({ data: { suggestions: [] } })),
      ]);

      const resumeData = resumeRes.data.data?.resume || resumeRes.data.resume;
      const suggestions = suggestionsRes.data.data?.suggestions || suggestionsRes.data.suggestions || [];

      setResume({ ...resumeData, suggestions });
    } catch (err) {
      console.error('Error fetching resume:', err);
      setError('Failed to load resume details');
    } finally {
      setIsLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (isLoading) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="Resume Details" size="xl">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
        </div>
      </Modal>
    );
  }

  if (error || !resume) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="Resume Details" size="xl">
        <div className="text-center py-12">
          <AlertCircle className="w-12 h-12 mx-auto text-red-400 mb-4" />
          <p className="text-red-600">{error || 'Resume not found'}</p>
          <button onClick={onClose} className="btn btn-primary mt-4">
            Close
          </button>
        </div>
      </Modal>
    );
  }

  const parsed = resume.parsed_content;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="" size="xl" showCloseButton>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-primary-50 rounded-xl flex items-center justify-center">
              <FileText className="w-7 h-7 text-primary-600" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-gray-900">{resume.name}</h2>
                {resume.is_master && (
                  <Badge variant="warning" size="sm">
                    <Star className="w-3 h-3 mr-1" /> Master
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <HardDrive className="w-3.5 h-3.5" />
                  {formatFileSize(resume.file_size)}
                </span>
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" />
                  {new Date(resume.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
          <Badge
            variant={resume.parse_status === 'parsed' ? 'success' : 'warning'}
            size="sm"
          >
            {resume.parse_status === 'parsed' ? (
              <><CheckCircle className="w-3 h-3 mr-1" /> Parsed</>
            ) : (
              resume.parse_status
            )}
          </Badge>
        </div>

        {/* ATS Score summary if available */}
        {resume.ats_score && (
          <div className="bg-gradient-to-r from-primary-50 to-blue-50 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">ATS Compatibility Score</p>
                <p className="text-3xl font-bold text-primary-700">
                  {resume.ats_score.overall_score}%
                </p>
              </div>
              <div className="w-16 h-16 relative">
                <svg className="w-full h-full -rotate-90">
                  <circle
                    cx="32"
                    cy="32"
                    r="28"
                    fill="none"
                    stroke="#e2e8f0"
                    strokeWidth="6"
                  />
                  <circle
                    cx="32"
                    cy="32"
                    r="28"
                    fill="none"
                    stroke={resume.ats_score.overall_score >= 80 ? '#22c55e' : resume.ats_score.overall_score >= 60 ? '#eab308' : '#ef4444'}
                    strokeWidth="6"
                    strokeDasharray={`${(resume.ats_score.overall_score / 100) * 176} 176`}
                    strokeLinecap="round"
                  />
                </svg>
              </div>
            </div>
          </div>
        )}

        {/* Parsed content sections */}
        {parsed && (
          <div className="space-y-6">
            {/* Contact Info */}
            {parsed.contact && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
                  Contact Information
                </h3>
                <div className="bg-gray-50 rounded-lg p-4 grid grid-cols-2 gap-3 text-sm">
                  {parsed.contact.name && (
                    <div>
                      <span className="text-gray-500">Name:</span>{' '}
                      <span className="font-medium">{parsed.contact.name}</span>
                    </div>
                  )}
                  {parsed.contact.email && (
                    <div>
                      <span className="text-gray-500">Email:</span>{' '}
                      <span className="font-medium">{parsed.contact.email}</span>
                    </div>
                  )}
                  {parsed.contact.phone && (
                    <div>
                      <span className="text-gray-500">Phone:</span>{' '}
                      <span className="font-medium">{parsed.contact.phone}</span>
                    </div>
                  )}
                  {parsed.contact.location && (
                    <div>
                      <span className="text-gray-500">Location:</span>{' '}
                      <span className="font-medium">{parsed.contact.location}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Summary */}
            {parsed.summary && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
                  Professional Summary
                </h3>
                <p className="text-gray-700 bg-gray-50 rounded-lg p-4">
                  {parsed.summary}
                </p>
              </div>
            )}

            {/* Skills */}
            {parsed.skills && parsed.skills.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
                  Skills
                </h3>
                <div className="flex flex-wrap gap-2">
                  {parsed.skills.map((skill, index) => (
                    <Badge key={index} variant="primary" size="sm">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Experience */}
            {parsed.experience && parsed.experience.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
                  Experience
                </h3>
                <div className="space-y-4">
                  {parsed.experience.map((exp, index) => (
                    <div key={index} className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-medium text-gray-900">{exp.title}</p>
                          <p className="text-sm text-gray-600">{exp.company}</p>
                        </div>
                        <span className="text-sm text-gray-500">{exp.duration}</span>
                      </div>
                      {exp.description && (
                        <p className="mt-2 text-sm text-gray-700">{exp.description}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Education */}
            {parsed.education && parsed.education.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
                  Education
                </h3>
                <div className="space-y-3">
                  {parsed.education.map((edu, index) => (
                    <div key={index} className="bg-gray-50 rounded-lg p-4 flex justify-between items-center">
                      <div>
                        <p className="font-medium text-gray-900">{edu.degree}</p>
                        <p className="text-sm text-gray-600">{edu.institution}</p>
                      </div>
                      <span className="text-sm text-gray-500">{edu.year}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Suggestions */}
        {resume.suggestions && resume.suggestions.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Improvement Suggestions
            </h3>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <ul className="space-y-2">
                {resume.suggestions.map((suggestion, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-yellow-800">
                    <span className="text-yellow-600 mt-0.5">•</span>
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
          <button onClick={onClose} className="btn btn-outline">
            Close
          </button>
        </div>
      </div>
    </Modal>
  );
}
