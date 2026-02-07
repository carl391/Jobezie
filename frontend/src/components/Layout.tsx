import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTour } from '../contexts/TourContext';
import { CommandPalette } from './ui/CommandPalette';
import { NotificationBell } from './ui/NotificationBell';
import { PageTransition } from './ui/PageTransition';
import {
  LayoutDashboard,
  FileText,
  Users,
  MessageSquare,
  Activity,
  Sparkles,
  Settings,
  LogOut,
  Menu,
  X,
  ChevronDown,
  Linkedin,
  BarChart3,
  MessageCircle,
  BookOpen,
  Compass,
  Zap,
  ArrowUpRight,
} from 'lucide-react';
import clsx from 'clsx';

interface LayoutProps {
  children: React.ReactNode;
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, tourId: 'nav-dashboard' },
  { name: 'Resumes', href: '/resumes', icon: FileText, tourId: 'nav-resumes' },
  { name: 'Recruiters', href: '/recruiters', icon: Users, tourId: 'nav-recruiters' },
  { name: 'Messages', href: '/messages', icon: MessageSquare, tourId: 'nav-messages' },
  { name: 'Activity', href: '/activity', icon: Activity, tourId: 'nav-activity' },
  { name: 'AI Coach', href: '/ai-coach', icon: Sparkles, tourId: 'nav-ai-coach' },
  { name: 'Interview Prep', href: '/interview-prep', icon: MessageCircle, tourId: 'nav-interview' },
  { name: 'LinkedIn', href: '/linkedin', icon: Linkedin, tourId: 'nav-linkedin' },
  { name: 'Labor Market', href: '/labor-market', icon: BarChart3, tourId: 'nav-labor-market' },
];

const TIER_BADGES: Record<string, { label: string; className: string }> = {
  basic: { label: 'Free', className: 'bg-gray-100 text-gray-600' },
  pro: { label: 'Pro', className: 'bg-blue-100 text-blue-700' },
  expert: { label: 'Expert', className: 'bg-purple-100 text-purple-700' },
  career_keeper: { label: 'Keeper', className: 'bg-emerald-100 text-emerald-700' },
};

export function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const { user, logout } = useAuth();
  const { startTour } = useTour();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleStartTour = () => {
    setUserMenuOpen(false);
    startTour('main');
  };

  const tier = user?.subscription_tier || 'basic';
  const tierBadge = TIER_BADGES[tier] || TIER_BADGES.basic;
  const isFreeTier = tier === 'basic';

  const SidebarContent = ({ onLinkClick }: { onLinkClick?: () => void }) => (
    <>
      {/* Brand header */}
      <div className="flex items-center h-16 px-5 bg-gradient-to-r from-primary-600 to-purple-600">
        <Link to="/dashboard" className="flex items-center gap-2.5" onClick={onLinkClick}>
          <svg width="32" height="32" viewBox="0 0 1024 1024" className="flex-shrink-0">
            <rect width="1024" height="1024" rx="228" fill="rgba(255,255,255,0.2)"/>
            <text x="512" y="712" textAnchor="middle" style={{ fontSize: 546, fontFamily: 'system-ui, -apple-system, sans-serif', fontWeight: 700, fill: '#FFFFFF' }}>J</text>
          </svg>
          <svg width="90" height="28" viewBox="0 0 320 100">
            <text x="160" y="65" textAnchor="middle" style={{ fontSize: 64, fontFamily: 'system-ui, -apple-system, sans-serif', fontWeight: 700, fill: '#FFFFFF', letterSpacing: '-0.03em' }}>Jobezie</text>
          </svg>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.name}
              to={item.href}
              data-tour={item.tourId}
              onClick={onLinkClick}
              className={clsx(
                'flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
                isActive
                  ? 'bg-gradient-to-r from-primary-50 to-purple-50 text-primary-700 shadow-sm border border-primary-100'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              )}
            >
              <item.icon className={clsx('w-[18px] h-[18px] mr-3', isActive && 'text-primary-600')} />
              {item.name}
              {isActive && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary-500" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Upgrade CTA for free users */}
      {isFreeTier && (
        <div className="px-3 pb-3">
          <Link
            to="/settings"
            onClick={onLinkClick}
            className="block p-3 rounded-xl bg-gradient-to-r from-primary-50 to-purple-50 border border-primary-100 hover:from-primary-100 hover:to-purple-100 transition-colors"
          >
            <div className="flex items-center gap-2 mb-1">
              <Zap className="w-4 h-4 text-primary-600" />
              <span className="text-xs font-semibold text-primary-700">Upgrade to Pro</span>
              <ArrowUpRight className="w-3 h-3 text-primary-500 ml-auto" />
            </div>
            <p className="text-[11px] text-gray-500">Unlock AI messages, advanced scoring & more</p>
          </Link>
        </div>
      )}

      {/* User section */}
      <div className="px-3 pb-4 border-t border-gray-100 pt-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center flex-shrink-0">
            <span className="text-sm font-semibold text-white">
              {user?.full_name?.charAt(0).toUpperCase() || 'U'}
            </span>
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-gray-900 truncate">{user?.full_name}</p>
            <span className={clsx('inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium', tierBadge.className)}>
              {tierBadge.label}
            </span>
          </div>
        </div>
      </div>
    </>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-900/50 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Mobile sidebar */}
      <div
        className={clsx(
          'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transform transition-transform duration-300 ease-in-out lg:hidden',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <button
          onClick={() => setSidebarOpen(false)}
          className="absolute top-4 right-4 p-1 rounded-lg hover:bg-white/20 z-10"
        >
          <X className="w-5 h-5 text-white" />
        </button>
        <div className="flex flex-col h-full">
          <SidebarContent onLinkClick={() => setSidebarOpen(false)} />
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-1 bg-white border-r border-gray-200">
          <SidebarContent />
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-gray-200">
          <div className="flex items-center justify-between h-16 px-4 lg:px-8">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-lg hover:bg-gray-100 lg:hidden"
            >
              <Menu className="w-5 h-5" />
            </button>

            <div className="flex-1" />

            {/* Notification bell */}
            <NotificationBell />

            {/* User menu */}
            <div className="relative ml-2">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center">
                  <span className="text-sm font-semibold text-white">
                    {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                  </span>
                </div>
                <span className="hidden md:block text-sm font-medium text-gray-700">
                  {user?.full_name}
                </span>
                <ChevronDown className="w-4 h-4 text-gray-500" />
              </button>

              {userMenuOpen && (
                <>
                  <div
                    className="fixed inset-0 z-40"
                    onClick={() => setUserMenuOpen(false)}
                  />
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-200 py-1 z-50">
                    <Link
                      to="/learn"
                      onClick={() => setUserMenuOpen(false)}
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      <BookOpen className="w-4 h-4 mr-2" />
                      Features Guide
                    </Link>
                    <button
                      onClick={handleStartTour}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      <Compass className="w-4 h-4 mr-2" />
                      Take Tour
                    </button>
                    <div className="border-t border-gray-100 my-1" />
                    <Link
                      to="/settings"
                      onClick={() => setUserMenuOpen(false)}
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      <Settings className="w-4 h-4 mr-2" />
                      Settings
                    </Link>
                    <button
                      onClick={() => {
                        setUserMenuOpen(false);
                        handleLogout();
                      }}
                      className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-gray-50"
                    >
                      <LogOut className="w-4 h-4 mr-2" />
                      Sign out
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 lg:p-8">
          <PageTransition>{children}</PageTransition>
        </main>
      </div>
      <CommandPalette />
    </div>
  );
}
