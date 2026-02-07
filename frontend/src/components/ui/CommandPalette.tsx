import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Command } from 'cmdk';
import {
  LayoutDashboard,
  FileText,
  Users,
  MessageSquare,
  Activity,
  Sparkles,
  MessageCircle,
  Linkedin,
  BarChart3,
  Settings,
  Search,
} from 'lucide-react';

interface NavigationItem {
  id: string;
  label: string;
  path: string;
  icon: React.ElementType;
  keywords?: string[];
}

const navigationItems: NavigationItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    path: '/dashboard',
    icon: LayoutDashboard,
    keywords: ['home', 'overview', 'stats'],
  },
  {
    id: 'resumes',
    label: 'Resumes',
    path: '/resumes',
    icon: FileText,
    keywords: ['cv', 'resume', 'ats', 'score'],
  },
  {
    id: 'recruiters',
    label: 'Recruiters',
    path: '/recruiters',
    icon: Users,
    keywords: ['crm', 'contacts', 'pipeline'],
  },
  {
    id: 'messages',
    label: 'Messages',
    path: '/messages',
    icon: MessageSquare,
    keywords: ['outreach', 'email', 'communication'],
  },
  {
    id: 'activity',
    label: 'Activity',
    path: '/activity',
    icon: Activity,
    keywords: ['timeline', 'kanban', 'tasks'],
  },
  {
    id: 'ai-coach',
    label: 'AI Coach',
    path: '/ai-coach',
    icon: Sparkles,
    keywords: ['assistant', 'help', 'career'],
  },
  {
    id: 'interview-prep',
    label: 'Interview Prep',
    path: '/interview-prep',
    icon: MessageCircle,
    keywords: ['interview', 'practice', 'questions'],
  },
  {
    id: 'linkedin',
    label: 'LinkedIn',
    path: '/linkedin',
    icon: Linkedin,
    keywords: ['profile', 'social', 'network'],
  },
  {
    id: 'labor-market',
    label: 'Labor Market',
    path: '/labor-market',
    icon: BarChart3,
    keywords: ['market', 'salary', 'trends', 'jobs'],
  },
  {
    id: 'settings',
    label: 'Settings',
    path: '/settings',
    icon: Settings,
    keywords: ['profile', 'account', 'preferences'],
  },
];

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  const handleSelect = (path: string) => {
    setOpen(false);
    navigate(path);
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
      onClick={() => setOpen(false)}
    >
      <div
        className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-lg"
        onClick={(e) => e.stopPropagation()}
      >
        <Command className="bg-white rounded-lg shadow-2xl border border-gray-200 overflow-hidden">
          <div className="flex items-center border-b border-gray-200 px-3">
            <Search className="w-4 h-4 text-gray-400 mr-2" />
            <Command.Input
              placeholder="Search navigation..."
              className="flex-1 py-3 outline-none text-sm text-gray-900 placeholder:text-gray-400"
            />
          </div>
          <Command.List className="max-h-[400px] overflow-y-auto p-2">
            <Command.Empty className="py-6 text-center text-sm text-gray-500">
              No results found.
            </Command.Empty>
            <Command.Group heading="Navigation" className="text-xs font-semibold text-gray-500 px-2 py-1.5">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Command.Item
                    key={item.id}
                    value={`${item.label} ${item.keywords?.join(' ')}`}
                    onSelect={() => handleSelect(item.path)}
                    className="flex items-center px-3 py-2.5 rounded-md cursor-pointer text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-900 data-[selected=true]:bg-indigo-50 data-[selected=true]:text-indigo-900 transition-colors"
                  >
                    <Icon className="w-4 h-4 mr-3 flex-shrink-0" />
                    <span>{item.label}</span>
                  </Command.Item>
                );
              })}
            </Command.Group>
          </Command.List>
          <div className="border-t border-gray-200 px-3 py-2 text-xs text-gray-500 flex items-center justify-between">
            <span>Press ESC to close</span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs font-mono">
                ↑↓
              </kbd>
              <span>to navigate</span>
              <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs font-mono ml-2">
                ↵
              </kbd>
              <span>to select</span>
            </span>
          </div>
        </Command>
      </div>
    </div>
  );
}
