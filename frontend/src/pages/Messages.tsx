import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import {
  MessageSquare,
  Plus,
  Search,
  Filter,
  Inbox,
  Send,
  Clock,
  CheckCircle,
} from 'lucide-react';
import { messageApi, recruiterApi } from '../lib/api';
import { ComposeMessageModal } from '../components/messages/ComposeMessageModal';
import { MessageCard } from '../components/messages/MessageCard';
import { PillTabs } from '../components/ui/Tabs';
import { AIDisclosureBanner } from '../components/ui/AIDisclosureBanner';
import type { Message, Recruiter } from '../types';

const STATUS_FILTERS = [
  { value: 'all', label: 'All Messages' },
  { value: 'draft', label: 'Drafts', count: 0 },
  { value: 'ready', label: 'Ready to Send', count: 0 },
  { value: 'sent', label: 'Sent', count: 0 },
  { value: 'responded', label: 'Responses', count: 0 },
];

export function Messages() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [recruiters, setRecruiters] = useState<Recruiter[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showComposeModal, setShowComposeModal] = useState(false);
  const [editMessage, setEditMessage] = useState<Message | null>(null);
  const [stats, setStats] = useState({
    total: 0,
    drafts: 0,
    ready: 0,
    sent: 0,
    responded: 0,
  });

  const fetchMessages = useCallback(async () => {
    try {
      const params: { status?: string } = {};
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      const response = await messageApi.list(params);
      setMessages(response.data.messages || response.data.data?.messages || []);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    } finally {
      setIsLoading(false);
    }
  }, [statusFilter]);

  const fetchRecruiters = useCallback(async () => {
    try {
      const response = await recruiterApi.list({ limit: 100 });
      setRecruiters(response.data.recruiters || response.data.data?.recruiters || []);
    } catch (error) {
      console.error('Failed to fetch recruiters:', error);
    }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      const response = await messageApi.getStats();
      const statsData = response.data.data?.stats || response.data.stats || {};
      setStats({
        total: statsData.total || 0,
        drafts: statsData.by_status?.draft || 0,
        ready: statsData.by_status?.ready || 0,
        sent: statsData.by_status?.sent || 0,
        responded: statsData.by_status?.responded || 0,
      });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  }, []);

  useEffect(() => {
    fetchMessages();
    fetchRecruiters();
    fetchStats();
  }, [fetchMessages, fetchRecruiters, fetchStats]);

  const handleMessageCreated = (message: Message) => {
    setMessages((prev) => [message, ...prev]);
    fetchStats();
  };

  const handleMessageUpdated = (message: Message) => {
    setMessages((prev) =>
      prev.map((m) => (m.id === message.id ? message : m))
    );
    setEditMessage(null);
    fetchStats();
  };

  const handleDelete = async (messageId: string) => {
    if (!confirm('Are you sure you want to delete this message?')) return;

    try {
      await messageApi.delete(messageId);
      setMessages((prev) => prev.filter((m) => m.id !== messageId));
      fetchStats();
      toast.success('Message deleted');
    } catch (error) {
      toast.error('Failed to delete message');
      console.error('Failed to delete message:', error);
    }
  };

  const handleMarkSent = async (messageId: string) => {
    try {
      const response = await messageApi.markSent(messageId);
      const updatedMessage = response.data.data?.message || response.data.message;
      setMessages((prev) =>
        prev.map((m) => (m.id === messageId ? updatedMessage : m))
      );
      fetchStats();
      toast.success('Message marked as sent');
    } catch (error) {
      toast.error('Failed to mark message as sent');
      console.error('Failed to mark message as sent:', error);
    }
  };

  const getRecruiterById = (recruiterId: string) => {
    return recruiters.find((r) => r.id === recruiterId);
  };

  const filteredMessages = messages.filter((m) => {
    const recruiter = getRecruiterById(m.recruiter_id);
    const searchLower = searchQuery.toLowerCase();
    return (
      m.body.toLowerCase().includes(searchLower) ||
      m.subject?.toLowerCase().includes(searchLower) ||
      recruiter?.full_name?.toLowerCase().includes(searchLower) ||
      recruiter?.company?.toLowerCase().includes(searchLower)
    );
  });

  const statusFiltersWithCounts = STATUS_FILTERS.map((filter) => ({
    ...filter,
    count: filter.value === 'all' ? stats.total :
           filter.value === 'draft' ? stats.drafts :
           filter.value === 'ready' ? stats.ready :
           filter.value === 'sent' ? stats.sent :
           filter.value === 'responded' ? stats.responded : 0,
  }));

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <AIDisclosureBanner featureKey="message_generation" />
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Messages</h1>
          <p className="text-gray-600 mt-1">Compose and manage your outreach messages</p>
        </div>
        <button
          onClick={() => setShowComposeModal(true)}
          className="btn btn-primary flex items-center"
          data-tour="message-compose"
        >
          <Plus className="w-4 h-4 mr-2" />
          Compose
        </button>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4" data-tour="message-quality">
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
              <Inbox className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              <p className="text-xs text-gray-500">Total Messages</p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.drafts}</p>
              <p className="text-xs text-gray-500">Drafts</p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <Send className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.sent}</p>
              <p className="text-xs text-gray-500">Sent</p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.responded}</p>
              <p className="text-xs text-gray-500">Responses</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 z-10 pointer-events-none" />
          <input
            type="text"
            placeholder="Search messages..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input pl-10"
          />
        </div>
        <PillTabs
          tabs={statusFiltersWithCounts}
          activeTab={statusFilter}
          onChange={setStatusFilter}
        />
      </div>

      {/* Message list */}
      {filteredMessages.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {filteredMessages.map((message) => (
            <MessageCard
              key={message.id}
              message={message}
              recruiter={getRecruiterById(message.recruiter_id)}
              onEdit={(m) => {
                setEditMessage(m);
                setShowComposeModal(true);
              }}
              onDelete={handleDelete}
              onMarkSent={handleMarkSent}
            />
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <MessageSquare className="w-16 h-16 mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {searchQuery || statusFilter !== 'all'
              ? 'No messages found'
              : 'No messages yet'}
          </h3>
          <p className="text-gray-500 mb-4">
            {searchQuery || statusFilter !== 'all'
              ? 'Try adjusting your filters'
              : 'Start by composing your first outreach message'}
          </p>
          {!searchQuery && statusFilter === 'all' && (
            <button
              onClick={() => setShowComposeModal(true)}
              className="btn btn-primary"
            >
              Compose Message
            </button>
          )}
        </div>
      )}

      {/* Compose Modal */}
      <ComposeMessageModal
        isOpen={showComposeModal}
        onClose={() => {
          setShowComposeModal(false);
          setEditMessage(null);
        }}
        onSuccess={editMessage ? handleMessageUpdated : handleMessageCreated}
        editMessage={editMessage}
      />
    </div>
  );
}
