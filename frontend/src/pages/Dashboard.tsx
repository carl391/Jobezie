import { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { dashboardApi, activityApi, laborMarketApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { useTour } from '../contexts/TourContext';
import {
  TrendingUp,
  FileText,
  Users,
  MessageSquare,
  ArrowRight,
  Clock,
  AlertCircle,
  Zap,
  BarChart3,
} from 'lucide-react';
import type { DashboardData, Activity, SkillsMapData } from '../types';

interface HighDemandRole {
  role: string;
  growth_rate: number;
  shortage_score: number;
  demand_level: string;
}

export function Dashboard() {
  const { user } = useAuth();
  const { startTour, shouldShowTour, markTourSeen } = useTour();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [recentActivities, setRecentActivities] = useState<Activity[]>([]);
  const [skillsMap, setSkillsMap] = useState<SkillsMapData | null>(null);
  const [highDemandRoles, setHighDemandRoles] = useState<HighDemandRole[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const tourStarted = useRef(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dashboardRes, activitiesRes] = await Promise.all([
          dashboardApi.getDashboard(),
          activityApi.getRecent(5),
        ]);
        setDashboardData(dashboardRes.data.data || dashboardRes.data);
        setRecentActivities(activitiesRes.data.data?.activities || activitiesRes.data.activities || []);

        // Fetch skills coverage and high-demand roles (non-blocking)
        laborMarketApi.getSkillsMap()
          .then((res) => setSkillsMap(res.data.data || null))
          .catch(() => {});

        laborMarketApi.getHighDemandRoles()
          .then((res) => setHighDemandRoles((res.data.data || []).slice(0, 5)))
          .catch(() => {});
      } catch (err) {
        setError('Failed to load dashboard data');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  // Auto-start tour for new users after onboarding
  useEffect(() => {
    if (!isLoading && !tourStarted.current && user?.onboarding_completed && shouldShowTour()) {
      tourStarted.current = true;
      // Small delay to ensure all elements are rendered
      const timer = setTimeout(() => {
        startTour('main');
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [isLoading, user, shouldShowTour, startTour, markTourSeen]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card bg-red-50 border-red-200">
        <div className="flex items-center text-red-600">
          <AlertCircle className="w-5 h-5 mr-2" />
          {error}
        </div>
      </div>
    );
  }

  const readinessScore = dashboardData?.career_readiness?.overall_score || 0;
  const pipelineSummary = dashboardData?.pipeline_summary;

  return (
    <div className="space-y-6">
      {/* Welcome section */}
      <div className="flex items-center justify-between" data-tour="dashboard-header">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.full_name?.split(' ')[0]}!
          </h1>
          <p className="text-gray-600 mt-1">Here's what's happening with your job search</p>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div data-tour="career-readiness">
          <StatCard
            title="Career Readiness"
            value={`${Math.round(readinessScore)}%`}
            icon={TrendingUp}
            trend={readinessScore > 70 ? 'Good' : readinessScore > 50 ? 'Fair' : 'Needs work'}
            trendUp={readinessScore > 70}
            color="primary"
          />
        </div>
        <StatCard
          title="Active Recruiters"
          value={pipelineSummary?.total?.toString() || '0'}
          icon={Users}
          trend={`${pipelineSummary?.response_rate || 0}% response rate`}
          trendUp={(pipelineSummary?.response_rate || 0) > 20}
          color="green"
        />
        <StatCard
          title="Messages Sent"
          value={dashboardData?.usage_stats?.messages_sent_this_week?.toString() || '0'}
          icon={MessageSquare}
          trend="This week"
          color="blue"
        />
        <StatCard
          title="Resumes"
          value={dashboardData?.usage_stats?.resumes_tailored_this_month?.toString() || '0'}
          icon={FileText}
          trend="Tailored this month"
          color="purple"
        />
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pipeline summary */}
        <div className="lg:col-span-2 card" data-tour="pipeline-overview">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Pipeline Overview</h2>
            <Link
              to="/recruiters"
              className="text-sm text-primary-600 hover:text-primary-700 flex items-center"
            >
              View all <ArrowRight className="w-4 h-4 ml-1" />
            </Link>
          </div>

          {pipelineSummary?.by_stage && Object.keys(pipelineSummary.by_stage).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(pipelineSummary.by_stage).map(([stage, count]) => (
                <div key={stage} className="flex items-center">
                  <span className="w-32 text-sm text-gray-600 capitalize">
                    {stage.replace('_', ' ')}
                  </span>
                  <div className="flex-1 mx-4">
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-500 rounded-full"
                        style={{
                          width: `${Math.min(100, ((count as number) / (pipelineSummary.total || 1)) * 100)}%`,
                        }}
                      />
                    </div>
                  </div>
                  <span className="w-8 text-sm font-medium text-gray-900 text-right">
                    {count as number}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Users className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>No recruiters in your pipeline yet</p>
              <Link
                to="/recruiters"
                className="btn btn-primary mt-4 inline-flex items-center"
              >
                Add your first recruiter
              </Link>
            </div>
          )}
        </div>

        {/* Recent activity */}
        <div className="card" data-tour="recent-activity">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
            <Link
              to="/activity"
              className="text-sm text-primary-600 hover:text-primary-700 flex items-center"
            >
              View all <ArrowRight className="w-4 h-4 ml-1" />
            </Link>
          </div>

          {recentActivities.length > 0 ? (
            <div className="space-y-4">
              {recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-start">
                  <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
                    <Clock className="w-4 h-4 text-gray-500" />
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-gray-900">
                      {activity.description || activity.activity_type.replace('_', ' ')}
                    </p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {new Date(activity.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Clock className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>No recent activity</p>
            </div>
          )}
        </div>
      </div>

      {/* Skills Coverage + Hot Markets row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Skills Coverage Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-primary-600" />
              Skills Coverage
            </h2>
            <Link
              to="/settings"
              className="text-sm text-primary-600 hover:text-primary-700 flex items-center"
            >
              Improve <ArrowRight className="w-4 h-4 ml-1" />
            </Link>
          </div>
          {skillsMap ? (
            <div className="space-y-3">
              {Object.entries(skillsMap.coverage_by_category).map(([category, data]) => {
                const pct = data.pct;
                const barColor = pct >= 71 ? 'bg-green-500' : pct >= 41 ? 'bg-yellow-500' : 'bg-red-500';
                return (
                  <div key={category}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-700 capitalize">{category}</span>
                      <span className="text-xs text-gray-500">{data.matched}/{data.total}</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div className={`h-full ${barColor} rounded-full`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
              <div className="pt-2 border-t border-gray-100">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-900">Overall</span>
                  <span className="text-sm font-bold text-gray-900">
                    {skillsMap.total_matched} matched
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <BarChart3 className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>Add skills in Settings to see coverage</p>
            </div>
          )}
        </div>

        {/* Hot Job Markets */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-500" />
              Hot Job Markets
            </h2>
          </div>
          {highDemandRoles.length > 0 ? (
            <div className="space-y-3">
              {highDemandRoles.map((role) => {
                const scoreColor = role.shortage_score >= 71 ? 'text-green-600' : role.shortage_score >= 41 ? 'text-yellow-600' : 'text-red-600';
                const bgColor = role.shortage_score >= 71 ? 'bg-green-50' : role.shortage_score >= 41 ? 'bg-yellow-50' : 'bg-red-50';
                return (
                  <div key={role.role} className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
                    <div>
                      <p className="text-sm font-medium text-gray-900 capitalize">
                        {role.role.replace(/_/g, ' ')}
                      </p>
                      <p className="text-xs text-gray-500">
                        {role.growth_rate ?? 0}% projected growth
                      </p>
                    </div>
                    <div className="text-right">
                      <span className={`text-sm font-bold ${scoreColor} px-2 py-1 rounded ${bgColor}`}>
                        {role.shortage_score}
                      </span>
                      <p className="text-xs text-gray-500 mt-1">{role.demand_level}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Zap className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>Loading market data...</p>
            </div>
          )}
        </div>
      </div>

      {/* Follow-up recommendations */}
      <div className="card" data-tour="follow-ups">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Recommended Follow-ups
        </h2>
        {dashboardData?.follow_up_recommendations &&
          dashboardData.follow_up_recommendations.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {dashboardData.follow_up_recommendations.slice(0, 3).map((rec) => (
              <div
                key={rec.recruiter_id}
                className="p-4 rounded-lg border border-gray-200 hover:border-primary-300 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900">{rec.recruiter_name}</span>
                  <span
                    className={`text-xs px-2 py-1 rounded-full ${
                      rec.priority === 'high'
                        ? 'bg-red-100 text-red-700'
                        : rec.priority === 'medium'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {rec.priority}
                  </span>
                </div>
                <p className="text-sm text-gray-600">{rec.company}</p>
                <p className="text-sm text-gray-500 mt-2">{rec.reason}</p>
                <Link
                  to={`/messages?recruiter=${rec.recruiter_id}`}
                  className="text-sm text-primary-600 hover:text-primary-700 mt-3 inline-block"
                >
                  {rec.suggested_action}
                </Link>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Clock className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>No follow-ups recommended yet</p>
            <p className="text-sm mt-1">Add recruiters to your pipeline to get personalized recommendations</p>
          </div>
        )}
      </div>
    </div>
  );
}

interface StatCardProps {
  title: string;
  value: string;
  icon: React.ElementType;
  trend?: string;
  trendUp?: boolean;
  color: 'primary' | 'green' | 'blue' | 'purple';
}

function StatCard({ title, value, icon: Icon, trend, trendUp, color }: StatCardProps) {
  const colorClasses = {
    primary: 'bg-primary-50 text-primary-600',
    green: 'bg-green-50 text-green-600',
    blue: 'bg-blue-50 text-blue-600',
    purple: 'bg-purple-50 text-purple-600',
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="mt-4">
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-600 mt-1">{title}</p>
        {trend && (
          <p
            className={`text-xs mt-2 ${
              trendUp === undefined
                ? 'text-gray-500'
                : trendUp
                ? 'text-green-600'
                : 'text-yellow-600'
            }`}
          >
            {trend}
          </p>
        )}
      </div>
    </div>
  );
}
