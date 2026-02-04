import type { ReactNode } from 'react';
import type { LucideIcon } from 'lucide-react';
import { Inbox, FileText, Users, MessageSquare, Activity, Briefcase } from 'lucide-react';

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  action,
  className = '',
}: EmptyStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center py-12 px-4 text-center ${className}`}>
      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
        <Icon className="w-8 h-8 text-gray-400" />
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
      {description && (
        <p className="text-gray-500 max-w-sm mb-6">{description}</p>
      )}
      {action}
    </div>
  );
}

// Preset empty states for common pages
export function EmptyResumes({ onUpload }: { onUpload?: () => void }) {
  return (
    <EmptyState
      icon={FileText}
      title="No resumes yet"
      description="Upload your first resume to get started with ATS analysis and optimization."
      action={
        onUpload && (
          <button onClick={onUpload} className="btn btn-primary">
            Upload Resume
          </button>
        )
      }
    />
  );
}

export function EmptyRecruiters({ onAdd }: { onAdd?: () => void }) {
  return (
    <EmptyState
      icon={Users}
      title="No recruiters yet"
      description="Add recruiters to track your conversations and get personalized outreach messages."
      action={
        onAdd && (
          <button onClick={onAdd} className="btn btn-primary">
            Add Recruiter
          </button>
        )
      }
    />
  );
}

export function EmptyMessages({ onCreate }: { onCreate?: () => void }) {
  return (
    <EmptyState
      icon={MessageSquare}
      title="No messages yet"
      description="Create your first outreach message or generate one with AI."
      action={
        onCreate && (
          <button onClick={onCreate} className="btn btn-primary">
            Create Message
          </button>
        )
      }
    />
  );
}

export function EmptyActivities() {
  return (
    <EmptyState
      icon={Activity}
      title="No activities yet"
      description="Your activity feed will show here as you use Jobezie."
    />
  );
}

export function EmptySearchResults({ query }: { query?: string }) {
  return (
    <EmptyState
      icon={Briefcase}
      title="No results found"
      description={
        query
          ? `No results match "${query}". Try adjusting your search or filters.`
          : 'Try adjusting your search or filters to find what you\'re looking for.'
      }
    />
  );
}
