import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Loader2,
  Mail,
  Phone,
  Linkedin,
  Building,
  Briefcase,
  Calendar,
  MessageSquare,
  Send,
  Plus,
  Trash2,
} from 'lucide-react';
import { Modal } from '../ui/Modal';
import { Badge, StageBadge } from '../ui/Badge';
import { ScoreCircle, ScoreBar } from '../ui/ScoreCircle';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/Tabs';
import { recruiterApi, activityApi } from '../../lib/api';
import type { Recruiter, RecruiterNote, Activity } from '../../types';

interface RecruiterDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  recruiterId: string;
  onUpdate?: (recruiter: Recruiter) => void;
}

const PIPELINE_STAGES = [
  { id: 'new', label: 'New' },
  { id: 'researching', label: 'Researching' },
  { id: 'contacted', label: 'Contacted' },
  { id: 'responded', label: 'Responded' },
  { id: 'interviewing', label: 'Interviewing' },
  { id: 'offer', label: 'Offer' },
  { id: 'accepted', label: 'Accepted' },
  { id: 'declined', label: 'Declined' },
];

export function RecruiterDetailsModal({
  isOpen,
  onClose,
  recruiterId,
  onUpdate,
}: RecruiterDetailsModalProps) {
  const navigate = useNavigate();
  const [recruiter, setRecruiter] = useState<Recruiter | null>(null);
  const [notes, setNotes] = useState<RecruiterNote[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newNote, setNewNote] = useState('');
  const [isAddingNote, setIsAddingNote] = useState(false);
  const [isChangingStage, setIsChangingStage] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && recruiterId) {
      fetchData();
    }
  }, [isOpen, recruiterId]);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [recruiterRes, notesRes, activitiesRes] = await Promise.all([
        recruiterApi.get(recruiterId),
        recruiterApi.getNotes(recruiterId),
        activityApi.list({ recruiter_id: recruiterId, limit: 10 }),
      ]);

      setRecruiter(recruiterRes.data.data?.recruiter || recruiterRes.data.recruiter);
      setNotes(notesRes.data.data?.notes || notesRes.data.notes || []);
      setActivities(activitiesRes.data.data?.activities || activitiesRes.data.activities || []);
    } catch (err) {
      console.error('Error fetching recruiter details:', err);
      setError('Failed to load recruiter details');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddNote = async () => {
    if (!newNote.trim()) return;

    setIsAddingNote(true);
    try {
      const response = await recruiterApi.addNote(recruiterId, newNote.trim());
      const note = response.data.data?.note || response.data.note;
      setNotes([note, ...notes]);
      setNewNote('');
    } catch (err) {
      console.error('Error adding note:', err);
    } finally {
      setIsAddingNote(false);
    }
  };

  const handleStageChange = async (newStage: string) => {
    if (!recruiter || recruiter.status === newStage) return;

    setIsChangingStage(true);
    try {
      const response = await recruiterApi.updateStage(recruiterId, newStage);
      const updated = response.data.data?.recruiter || response.data.recruiter;
      setRecruiter(updated);
      onUpdate?.(updated);
    } catch (err) {
      console.error('Error updating stage:', err);
    } finally {
      setIsChangingStage(false);
    }
  };

  // Use response score from backend (formerly "engagement score")
  const getResponseScore = () => {
    return recruiter?.engagement_score || 0;
  };

  // Use fit score from backend
  const getFitScore = () => {
    return recruiter?.fit_score || 0;
  };

  const handleCreateMessage = () => {
    onClose();
    navigate(`/messages?recruiterId=${recruiterId}`);
  };

  if (isLoading) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="Recruiter Details" size="xl">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
        </div>
      </Modal>
    );
  }

  if (error || !recruiter) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="Recruiter Details" size="xl">
        <div className="text-center py-12">
          <p className="text-red-600">{error || 'Recruiter not found'}</p>
          <button onClick={onClose} className="btn btn-primary mt-4">
            Close
          </button>
        </div>
      </Modal>
    );
  }

  const responseScore = getResponseScore();
  const fitScore = getFitScore();

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="" size="xl" showCloseButton>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{recruiter.full_name}</h2>
            {recruiter.title && recruiter.company && (
              <p className="text-gray-600 mt-1">
                {recruiter.title} at {recruiter.company}
              </p>
            )}
          </div>
          <StageBadge stage={recruiter.status} size="md" />
        </div>

        {/* Contact info */}
        <div className="flex flex-wrap gap-4">
          {recruiter.email && (
            <a
              href={`mailto:${recruiter.email}`}
              className="flex items-center gap-2 text-gray-600 hover:text-primary-600"
            >
              <Mail className="w-4 h-4" />
              {recruiter.email}
            </a>
          )}
          {recruiter.phone && (
            <a
              href={`tel:${recruiter.phone}`}
              className="flex items-center gap-2 text-gray-600 hover:text-primary-600"
            >
              <Phone className="w-4 h-4" />
              {recruiter.phone}
            </a>
          )}
          {recruiter.linkedin_url && (
            <a
              href={recruiter.linkedin_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-gray-600 hover:text-primary-600"
            >
              <Linkedin className="w-4 h-4" />
              LinkedIn Profile
            </a>
          )}
        </div>

        {/* Scores */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="card p-4 text-center">
            <ScoreCircle score={responseScore} size="md" />
            <p className="text-sm text-gray-600 mt-2">Response Score</p>
          </div>
          <div className="card p-4 text-center">
            <ScoreCircle score={fitScore} size="md" />
            <p className="text-sm text-gray-600 mt-2">Fit Score</p>
          </div>
          <div className="card p-4 text-center">
            <div className="text-3xl font-bold text-gray-900">{recruiter.messages_sent}</div>
            <p className="text-sm text-gray-600 mt-1">Messages Sent</p>
          </div>
          <div className="card p-4 text-center">
            <div className="text-3xl font-bold text-gray-900">{recruiter.responses_received}</div>
            <p className="text-sm text-gray-600 mt-1">Responses</p>
          </div>
        </div>

        {/* Stage selector */}
        <div>
          <label className="label">Pipeline Stage</label>
          <div className="flex flex-wrap gap-2">
            {PIPELINE_STAGES.map((stage) => (
              <button
                key={stage.id}
                onClick={() => handleStageChange(stage.id)}
                disabled={isChangingStage}
                className={`px-3 py-1.5 text-sm rounded-full transition-all ${
                  recruiter.status === stage.id
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {stage.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="notes">
          <TabsList>
            <TabsTrigger value="notes">Notes ({notes.length})</TabsTrigger>
            <TabsTrigger value="activity">Activity ({activities.length})</TabsTrigger>
            <TabsTrigger value="details">Details</TabsTrigger>
          </TabsList>

          <TabsContent value="notes" className="mt-4">
            {/* Add note form */}
            <div className="mb-4">
              <div className="flex gap-2">
                <textarea
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  placeholder="Add a note..."
                  rows={2}
                  className="input flex-1 resize-none"
                />
                <button
                  onClick={handleAddNote}
                  disabled={isAddingNote || !newNote.trim()}
                  className="btn btn-primary self-end"
                >
                  {isAddingNote ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Plus className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Notes list */}
            {notes.length > 0 ? (
              <div className="space-y-3">
                {notes.map((note) => (
                  <div key={note.id} className="bg-gray-50 rounded-lg p-4">
                    <p className="text-gray-800">{note.content}</p>
                    <p className="text-xs text-gray-500 mt-2">
                      {new Date(note.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No notes yet</p>
            )}
          </TabsContent>

          <TabsContent value="activity" className="mt-4">
            {activities.length > 0 ? (
              <div className="space-y-3">
                {activities.map((activity) => (
                  <div key={activity.id} className="flex items-start gap-3 py-3 border-b border-gray-100 last:border-0">
                    <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                      <MessageSquare className="w-4 h-4 text-gray-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-gray-800">{activity.description || activity.activity_type}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(activity.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No activity yet</p>
            )}
          </TabsContent>

          <TabsContent value="details" className="mt-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Building className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">Company:</span>
                  <span className="text-sm font-medium">{recruiter.company || 'Not specified'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Briefcase className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">Title:</span>
                  <span className="text-sm font-medium">{recruiter.title || 'Not specified'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">Added:</span>
                  <span className="text-sm font-medium">
                    {new Date(recruiter.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Send className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">Messages Opened:</span>
                  <span className="text-sm font-medium">{recruiter.messages_opened || 0}</span>
                </div>
                {recruiter.last_contact_date && (
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-600">Last Contact:</span>
                    <span className="text-sm font-medium">
                      {new Date(recruiter.last_contact_date).toLocaleDateString()}
                    </span>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">Priority Score:</span>
                  <span className="text-sm font-medium">{recruiter.priority_score}</span>
                </div>
              </div>
            </div>

            {recruiter.next_action && (
              <div className="mt-4 p-4 bg-yellow-50 rounded-lg">
                <p className="text-sm font-medium text-yellow-800">Next Action:</p>
                <p className="text-yellow-700">{recruiter.next_action}</p>
                {recruiter.next_action_date && (
                  <p className="text-xs text-yellow-600 mt-1">
                    Due: {new Date(recruiter.next_action_date).toLocaleDateString()}
                  </p>
                )}
              </div>
            )}
          </TabsContent>
        </Tabs>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
          <button onClick={onClose} className="btn btn-outline">
            Close
          </button>
          <button onClick={handleCreateMessage} className="btn btn-primary">
            <MessageSquare className="w-4 h-4 mr-2" />
            Create Message
          </button>
        </div>
      </div>
    </Modal>
  );
}
