import {
  MessageSquare,
  Mail,
  MailOpen,
  CheckCircle,
  Clock,
  Edit2,
  Trash2,
  Send,
  MoreVertical,
} from 'lucide-react';
import { useState } from 'react';
import { StatusBadge } from '../ui/Badge';
import { ScoreCircle } from '../ui/ScoreCircle';
import type { Message, Recruiter } from '../../types';

interface MessageCardProps {
  message: Message;
  recruiter?: Recruiter;
  onEdit: (message: Message) => void;
  onDelete: (messageId: string) => void;
  onMarkSent: (messageId: string) => void;
}

const MESSAGE_TYPE_LABELS: Record<string, string> = {
  initial_outreach: 'Initial Outreach',
  follow_up: 'Follow Up',
  thank_you: 'Thank You',
  check_in: 'Check In',
};

const STATUS_ICONS: Record<string, React.ReactNode> = {
  draft: <Clock className="w-4 h-4" />,
  ready: <Mail className="w-4 h-4" />,
  sent: <Send className="w-4 h-4" />,
  opened: <MailOpen className="w-4 h-4" />,
  responded: <CheckCircle className="w-4 h-4" />,
};

export function MessageCard({
  message,
  recruiter,
  onEdit,
  onDelete,
  onMarkSent,
}: MessageCardProps) {
  const [showMenu, setShowMenu] = useState(false);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  };

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  };

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
            message.status === 'responded' ? 'bg-green-100' :
            message.status === 'opened' ? 'bg-blue-100' :
            message.status === 'sent' ? 'bg-primary-100' :
            'bg-gray-100'
          }`}>
            {STATUS_ICONS[message.status] || <MessageSquare className="w-5 h-5 text-gray-600" />}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-medium text-gray-900 truncate">
                {recruiter?.name || 'Unknown Recruiter'}
              </h3>
              <StatusBadge status={message.status} size="sm" />
            </div>
            {recruiter?.company_name && (
              <p className="text-sm text-gray-500">{recruiter.company_name}</p>
            )}
            <span className="inline-block text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded mt-1">
              {MESSAGE_TYPE_LABELS[message.message_type] || message.message_type}
            </span>
          </div>
        </div>

        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-1 text-gray-400 hover:text-gray-600 rounded"
          >
            <MoreVertical className="w-4 h-4" />
          </button>

          {showMenu && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowMenu(false)}
              />
              <div className="absolute right-0 mt-1 w-36 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
                <button
                  onClick={() => {
                    onEdit(message);
                    setShowMenu(false);
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                >
                  <Edit2 className="w-4 h-4" />
                  Edit
                </button>
                {(message.status === 'draft' || message.status === 'ready') && (
                  <button
                    onClick={() => {
                      onMarkSent(message.id);
                      setShowMenu(false);
                    }}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                  >
                    <Send className="w-4 h-4" />
                    Mark as Sent
                  </button>
                )}
                <button
                  onClick={() => {
                    onDelete(message.id);
                    setShowMenu(false);
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Subject */}
      {message.subject && (
        <p className="mt-3 text-sm font-medium text-gray-800">
          {message.subject}
        </p>
      )}

      {/* Body preview */}
      <p className="mt-2 text-sm text-gray-600 line-clamp-2">
        {truncateText(message.body, 150)}
      </p>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between">
        <span className="text-xs text-gray-500">
          {formatDate(message.updated_at || message.created_at)}
        </span>

        <div className="flex items-center gap-3">
          {message.quality_score !== undefined && message.quality_score !== null && (
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-gray-500">Quality:</span>
              <ScoreCircle score={message.quality_score} size="sm" />
            </div>
          )}

          <button
            onClick={() => onEdit(message)}
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            View / Edit
          </button>
        </div>
      </div>
    </div>
  );
}
