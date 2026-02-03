import { MessageSquare } from 'lucide-react';

export function Messages() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Messages</h1>
        <p className="text-gray-600 mt-1">Compose and manage your outreach messages</p>
      </div>

      <div className="card text-center py-12">
        <MessageSquare className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Message Center</h3>
        <p className="text-gray-500">Full message builder coming soon...</p>
      </div>
    </div>
  );
}
