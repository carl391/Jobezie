import { useState, useEffect, useCallback } from 'react';
import {
  Activity as ActivityIcon,
  Calendar,
  Clock,
  CheckCircle,
  MessageSquare,
  FileText,
  Users,
  TrendingUp,
  Filter,
  Columns,
  List,
  GripVertical,
  AlertTriangle,
} from 'lucide-react';
import { activityApi, recruiterApi } from '../lib/api';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/Tabs';
import { Badge } from '../components/ui/Badge';
import type { Activity, PipelineItem, Recruiter } from '../types';

const ACTIVITY_ICONS: Record<string, React.ReactNode> = {
  message_sent: <MessageSquare className="w-4 h-4" />,
  message_opened: <MessageSquare className="w-4 h-4" />,
  message_responded: <CheckCircle className="w-4 h-4" />,
  resume_uploaded: <FileText className="w-4 h-4" />,
  resume_scored: <TrendingUp className="w-4 h-4" />,
  recruiter_added: <Users className="w-4 h-4" />,
  recruiter_contacted: <MessageSquare className="w-4 h-4" />,
  stage_changed: <Columns className="w-4 h-4" />,
  interview_scheduled: <Calendar className="w-4 h-4" />,
  note_added: <FileText className="w-4 h-4" />,
};

const ACTIVITY_COLORS: Record<string, string> = {
  message_sent: 'bg-blue-100 text-blue-600',
  message_opened: 'bg-yellow-100 text-yellow-600',
  message_responded: 'bg-green-100 text-green-600',
  resume_uploaded: 'bg-purple-100 text-purple-600',
  resume_scored: 'bg-indigo-100 text-indigo-600',
  recruiter_added: 'bg-pink-100 text-pink-600',
  recruiter_contacted: 'bg-blue-100 text-blue-600',
  stage_changed: 'bg-orange-100 text-orange-600',
  interview_scheduled: 'bg-teal-100 text-teal-600',
  note_added: 'bg-gray-100 text-gray-600',
};

const PIPELINE_STAGES = [
  { id: 'new', label: 'New', color: 'bg-gray-100' },
  { id: 'researching', label: 'Researching', color: 'bg-blue-100' },
  { id: 'contacted', label: 'Contacted', color: 'bg-yellow-100' },
  { id: 'responded', label: 'Responded', color: 'bg-green-100' },
  { id: 'interviewing', label: 'Interviewing', color: 'bg-purple-100' },
  { id: 'offer', label: 'Offer', color: 'bg-orange-100' },
  { id: 'accepted', label: 'Accepted', color: 'bg-emerald-100' },
  { id: 'declined', label: 'Declined', color: 'bg-red-100' },
];

export function Activity() {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [pipelineItems, setPipelineItems] = useState<PipelineItem[]>([]);
  const [recruiters, setRecruiters] = useState<Recruiter[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeView, setActiveView] = useState<'timeline' | 'kanban'>('timeline');
  const [activityFilter, setActivityFilter] = useState('all');
  const [timelineData, setTimelineData] = useState<{ date: string; count: number }[]>([]);
  const [stats, setStats] = useState({
    total_activities: 0,
    messages_sent: 0,
    responses: 0,
    interviews: 0,
  });

  // Drag-and-drop state
  const [draggedItemId, setDraggedItemId] = useState<string | null>(null);
  const [dragOverStage, setDragOverStage] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [activitiesRes, pipelineRes, recruitersRes, timelineRes, statsRes] = await Promise.all([
        activityApi.list({ limit: 50 }),
        activityApi.getPipeline(),
        recruiterApi.list({ limit: 100 }),
        activityApi.getTimeline(30).catch(() => ({ data: { timeline: [] } })),
        activityApi.getCounts().catch(() => ({ data: { counts: {} } })),
      ]);

      setActivities(activitiesRes.data.activities || activitiesRes.data.data?.activities || []);
      setPipelineItems(pipelineRes.data.pipeline || pipelineRes.data.data?.pipeline || []);
      setRecruiters(recruitersRes.data.recruiters || recruitersRes.data.data?.recruiters || []);
      setTimelineData(timelineRes.data.timeline || timelineRes.data.data?.timeline || []);

      const countsData = statsRes.data.counts || statsRes.data.data?.counts || {};
      setStats({
        total_activities: countsData.total || 0,
        messages_sent: countsData.messages_sent || 0,
        responses: countsData.responses || 0,
        interviews: countsData.interviews || 0,
      });
    } catch (error) {
      console.error('Failed to fetch activity data:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleMoveItem = async (itemId: string, newStage: string) => {
    try {
      await activityApi.movePipelineItem(itemId, newStage);
      setPipelineItems((prev) =>
        prev.map((item) =>
          item.id === itemId ? { ...item, stage: newStage } : item
        )
      );
    } catch (error) {
      console.error('Failed to move pipeline item:', error);
    }
  };

  // Drag-and-drop handlers
  const handleDragStart = (e: React.DragEvent, itemId: string) => {
    setDraggedItemId(itemId);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', itemId);
    // Add a slight delay before adding the dragging class
    const target = e.target as HTMLElement;
    setTimeout(() => {
      target.style.opacity = '0.5';
    }, 0);
  };

  const handleDragEnd = (e: React.DragEvent) => {
    setDraggedItemId(null);
    setDragOverStage(null);
    const target = e.target as HTMLElement;
    target.style.opacity = '1';
  };

  const handleDragOver = (e: React.DragEvent, stageId: string) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverStage(stageId);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    // Only clear if we're leaving the column, not entering a child element
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const x = e.clientX;
    const y = e.clientY;
    if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
      setDragOverStage(null);
    }
  };

  const handleDrop = async (e: React.DragEvent, targetStage: string) => {
    e.preventDefault();
    setDragOverStage(null);

    const itemId = e.dataTransfer.getData('text/plain');
    if (!itemId) return;

    const item = pipelineItems.find((i) => i.id === itemId);
    if (!item || item.stage === targetStage) return;

    await handleMoveItem(itemId, targetStage);
  };

  const getRecruiterById = (recruiterId?: string) => {
    if (!recruiterId) return null;
    return recruiters.find((r) => r.id === recruiterId);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  };

  const groupActivitiesByDate = (activities: Activity[]) => {
    const groups: { [key: string]: Activity[] } = {};

    activities.forEach((activity) => {
      const date = new Date(activity.created_at).toLocaleDateString();
      if (!groups[date]) {
        groups[date] = [];
      }
      groups[date].push(activity);
    });

    return groups;
  };

  const filteredActivities = activities.filter((a) => {
    if (activityFilter === 'all') return true;
    return a.activity_type.includes(activityFilter);
  });

  const groupedActivities = groupActivitiesByDate(filteredActivities);

  const getItemsForStage = (stageId: string) => {
    return pipelineItems.filter((item) => item.stage === stageId);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Activity</h1>
          <p className="text-gray-600 mt-1">Track your job search activities and pipeline</p>
        </div>
        <div className="flex items-center gap-2 bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveView('timeline')}
            data-tour="activity-timeline"
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${
              activeView === 'timeline'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <List className="w-4 h-4 inline mr-1" />
            Timeline
          </button>
          <button
            onClick={() => setActiveView('kanban')}
            data-tour="activity-kanban"
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${
              activeView === 'kanban'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Columns className="w-4 h-4 inline mr-1" />
            Kanban
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <ActivityIcon className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.total_activities}</p>
              <p className="text-xs text-gray-500">Total Activities</p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.messages_sent}</p>
              <p className="text-xs text-gray-500">Messages Sent</p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.responses}</p>
              <p className="text-xs text-gray-500">Responses</p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.interviews}</p>
              <p className="text-xs text-gray-500">Interviews</p>
            </div>
          </div>
        </div>
      </div>

      {/* Timeline View */}
      {activeView === 'timeline' && (
        <div className="space-y-4">
          {/* Activity filter */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            <Filter className="w-4 h-4 text-gray-400 flex-shrink-0" />
            {[
              { value: 'all', label: 'All' },
              { value: 'message', label: 'Messages' },
              { value: 'resume', label: 'Resumes' },
              { value: 'recruiter', label: 'Recruiters' },
              { value: 'interview', label: 'Interviews' },
            ].map((filter) => (
              <button
                key={filter.value}
                onClick={() => setActivityFilter(filter.value)}
                className={`px-3 py-1.5 text-sm rounded-full whitespace-nowrap transition-all ${
                  activityFilter === filter.value
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {filter.label}
              </button>
            ))}
          </div>

          {/* Activity timeline */}
          {Object.keys(groupedActivities).length > 0 ? (
            <div className="space-y-6">
              {Object.entries(groupedActivities).map(([date, dateActivities]) => (
                <div key={date}>
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                      <Calendar className="w-4 h-4 text-gray-500" />
                    </div>
                    <h3 className="font-medium text-gray-900">{date}</h3>
                    <span className="text-sm text-gray-500">
                      {dateActivities.length} {dateActivities.length === 1 ? 'activity' : 'activities'}
                    </span>
                  </div>

                  <div className="ml-4 border-l-2 border-gray-200 pl-6 space-y-4">
                    {dateActivities.map((activity) => {
                      const recruiter = getRecruiterById(activity.recruiter_id);
                      return (
                        <div
                          key={activity.id}
                          className="flex items-start gap-3 bg-white rounded-lg p-4 border border-gray-100 hover:shadow-sm transition-shadow"
                        >
                          <div
                            className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                              ACTIVITY_COLORS[activity.activity_type] || 'bg-gray-100 text-gray-600'
                            }`}
                          >
                            {ACTIVITY_ICONS[activity.activity_type] || (
                              <ActivityIcon className="w-4 h-4" />
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-gray-900">
                              {activity.description || activity.activity_type.replace(/_/g, ' ')}
                            </p>
                            {recruiter && (
                              <p className="text-sm text-gray-500 mt-0.5">
                                {recruiter.full_name || recruiter.name || 'Unknown'}
                                {(recruiter.company || recruiter.company_name) && ` at ${recruiter.company || recruiter.company_name}`}
                              </p>
                            )}
                          </div>
                          <span className="text-xs text-gray-400 whitespace-nowrap">
                            {formatDate(activity.created_at)}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="card text-center py-12">
              <ActivityIcon className="w-16 h-16 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No activities yet</h3>
              <p className="text-gray-500">
                Your job search activities will appear here as you use the platform
              </p>
            </div>
          )}
        </div>
      )}

      {/* Kanban View */}
      {activeView === 'kanban' && (
        <div className="overflow-x-auto pb-4">
          <p className="text-sm text-gray-500 mb-3">
            Drag and drop cards between columns to update their status
          </p>
          <div className="flex gap-4 min-w-max">
            {PIPELINE_STAGES.map((stage) => {
              const items = getItemsForStage(stage.id);
              const isDropTarget = dragOverStage === stage.id && draggedItemId !== null;
              const draggedItem = pipelineItems.find((i) => i.id === draggedItemId);
              const canDrop = draggedItem && draggedItem.stage !== stage.id;

              return (
                <div
                  key={stage.id}
                  className={`w-72 flex-shrink-0 rounded-xl ${stage.color} p-3 transition-all ${
                    isDropTarget && canDrop ? 'ring-2 ring-primary-500 ring-offset-2' : ''
                  }`}
                  onDragOver={(e) => handleDragOver(e, stage.id)}
                  onDragLeave={handleDragLeave}
                  onDrop={(e) => handleDrop(e, stage.id)}
                >
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-medium text-gray-900">{stage.label}</h3>
                    <span className="text-sm text-gray-500 bg-white/50 px-2 py-0.5 rounded-full">
                      {items.length}
                    </span>
                  </div>

                  <div className="space-y-2 min-h-[100px]">
                    {items.length > 0 ? (
                      items.map((item) => {
                        const recruiter = item.recruiter || getRecruiterById(item.recruiter?.id);
                        const isDragging = draggedItemId === item.id;
                        return (
                          <div
                            key={item.id}
                            draggable
                            onDragStart={(e) => handleDragStart(e, item.id)}
                            onDragEnd={handleDragEnd}
                            className={`bg-white rounded-lg p-3 shadow-sm hover:shadow-md transition-all cursor-grab active:cursor-grabbing ${
                              isDragging ? 'opacity-50 scale-95' : ''
                            }`}
                          >
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex items-center gap-2">
                                <GripVertical className="w-4 h-4 text-gray-300 flex-shrink-0" />
                                <div>
                                  <p className="font-medium text-gray-900 text-sm">
                                    {recruiter?.full_name || recruiter?.name || 'Unknown'}
                                  </p>
                                  {(recruiter?.company || recruiter?.company_name) && (
                                    <p className="text-xs text-gray-500">
                                      {recruiter.company || recruiter.company_name}
                                    </p>
                                  )}
                                </div>
                              </div>
                              {item.is_urgent && (
                                <AlertTriangle className="w-4 h-4 text-orange-500" />
                              )}
                            </div>

                            <div className="flex items-center justify-between text-xs">
                              <span className="text-gray-500">
                                {item.days_in_stage ?? 0} {item.days_in_stage === 1 ? 'day' : 'days'} in stage
                              </span>
                              {item.last_activity && (
                                <span className="text-gray-400">
                                  {formatDate(item.last_activity)}
                                </span>
                              )}
                            </div>
                          </div>
                        );
                      })
                    ) : (
                      <div className={`text-center py-8 text-gray-400 text-sm rounded-lg border-2 border-dashed ${
                        isDropTarget && canDrop ? 'border-primary-400 bg-primary-50' : 'border-transparent'
                      }`}>
                        {isDropTarget && canDrop ? 'Drop here' : 'No items in this stage'}
                      </div>
                    )}

                    {/* Drop zone indicator when dragging over a column with items */}
                    {isDropTarget && canDrop && items.length > 0 && (
                      <div className="h-16 rounded-lg border-2 border-dashed border-primary-400 bg-primary-50 flex items-center justify-center text-sm text-primary-600">
                        Drop here
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
