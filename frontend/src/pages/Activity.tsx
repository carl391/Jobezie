import { Activity as ActivityIcon } from 'lucide-react';

export function Activity() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Activity</h1>
        <p className="text-gray-600 mt-1">Track your job search activities</p>
      </div>

      <div className="card text-center py-12">
        <ActivityIcon className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Activity Timeline</h3>
        <p className="text-gray-500">Activity feed coming soon...</p>
      </div>
    </div>
  );
}
