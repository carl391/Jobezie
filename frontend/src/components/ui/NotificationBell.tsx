import { useState, useEffect, useRef, useCallback } from 'react';
import { Bell, Check, CheckCheck, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { notificationApi } from '../../lib/api';
import clsx from 'clsx';

interface NotificationItem {
  id: string;
  title: string;
  body: string | null;
  type: string;
  is_read: boolean;
  action_url: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

const TYPE_COLORS: Record<string, string> = {
  follow_up_reminder: 'bg-blue-100 text-blue-700',
  usage_warning: 'bg-yellow-100 text-yellow-700',
  tier_limit: 'bg-red-100 text-red-700',
  achievement: 'bg-green-100 text-green-700',
  market_alert: 'bg-purple-100 text-purple-700',
  system: 'bg-gray-100 text-gray-700',
};

const TYPE_LABELS: Record<string, string> = {
  follow_up_reminder: 'Follow-up',
  usage_warning: 'Usage',
  tier_limit: 'Limit',
  achievement: 'Achievement',
  market_alert: 'Market',
  system: 'System',
};

function timeAgo(dateString: string): string {
  const now = new Date();
  const date = new Date(dateString);
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return 'just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  return date.toLocaleDateString();
}

export function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const fetchUnreadCount = useCallback(async () => {
    try {
      const response = await notificationApi.getUnreadCount();
      const count = response.data.data?.count ?? response.data.count ?? 0;
      setUnreadCount(count);
    } catch {
      // Silently fail -- bell just won't show a badge
    }
  }, []);

  const fetchNotifications = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await notificationApi.list({ limit: 15 });
      const data = response.data.data || response.data;
      setNotifications(data.notifications || []);
    } catch {
      // Silently fail
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Poll unread count every 60 seconds
  useEffect(() => {
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 60000);
    return () => clearInterval(interval);
  }, [fetchUnreadCount]);

  // Generate notifications on mount (fires once)
  useEffect(() => {
    notificationApi.generate().catch(() => {});
  }, []);

  // Fetch full list when dropdown opens
  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen, fetchNotifications]);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  const handleMarkRead = async (id: string) => {
    try {
      await notificationApi.markRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch {
      // Silently fail
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationApi.markAllRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch {
      // Silently fail
    }
  };

  const handleNotificationClick = (notification: NotificationItem) => {
    if (!notification.is_read) {
      handleMarkRead(notification.id);
    }
    if (notification.action_url) {
      setIsOpen(false);
      navigate(notification.action_url);
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
        aria-label="Notifications"
      >
        <Bell className="w-5 h-5 text-gray-600" />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-bold text-white bg-red-500 rounded-full">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 max-h-[28rem] bg-white rounded-xl shadow-lg border border-gray-200 z-50 flex flex-col overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <h3 className="text-sm font-semibold text-gray-900">Notifications</h3>
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllRead}
                className="flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 font-medium"
              >
                <CheckCheck className="w-3.5 h-3.5" />
                Mark all read
              </button>
            )}
          </div>

          {/* Notification list */}
          <div className="flex-1 overflow-y-auto">
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-primary-600" />
              </div>
            ) : notifications.length === 0 ? (
              <div className="text-center py-8 px-4">
                <Bell className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                <p className="text-sm text-gray-500">No notifications yet</p>
                <p className="text-xs text-gray-400 mt-1">
                  You'll see follow-up reminders and usage alerts here
                </p>
              </div>
            ) : (
              <div>
                {notifications.map((notification) => (
                  <button
                    key={notification.id}
                    onClick={() => handleNotificationClick(notification)}
                    className={clsx(
                      'w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors border-b border-gray-50 last:border-0',
                      !notification.is_read && 'bg-primary-50/40'
                    )}
                  >
                    <div className="flex items-start gap-3">
                      {/* Unread dot */}
                      <div className="mt-1.5 flex-shrink-0">
                        {!notification.is_read ? (
                          <div className="w-2 h-2 rounded-full bg-primary-500" />
                        ) : (
                          <div className="w-2 h-2" />
                        )}
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-0.5">
                          <span
                            className={clsx(
                              'inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium',
                              TYPE_COLORS[notification.type] || TYPE_COLORS.system
                            )}
                          >
                            {TYPE_LABELS[notification.type] || 'System'}
                          </span>
                          <span className="text-[10px] text-gray-400">
                            {timeAgo(notification.created_at)}
                          </span>
                        </div>
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {notification.title}
                        </p>
                        {notification.body && (
                          <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">
                            {notification.body}
                          </p>
                        )}
                        {notification.action_url && (
                          <span className="inline-flex items-center gap-1 text-[11px] text-primary-600 mt-1">
                            <ExternalLink className="w-3 h-3" />
                            View
                          </span>
                        )}
                      </div>

                      {/* Mark read button */}
                      {!notification.is_read && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleMarkRead(notification.id);
                          }}
                          className="mt-1 p-1 rounded hover:bg-gray-200 transition-colors flex-shrink-0"
                          title="Mark as read"
                        >
                          <Check className="w-3.5 h-3.5 text-gray-400" />
                        </button>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
