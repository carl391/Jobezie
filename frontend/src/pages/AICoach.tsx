import { Sparkles } from 'lucide-react';

export function AICoach() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">AI Career Coach</h1>
        <p className="text-gray-600 mt-1">Get personalized career advice powered by AI</p>
      </div>

      <div className="card text-center py-12">
        <Sparkles className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">AI Coaching</h3>
        <p className="text-gray-500">AI coaching interface coming soon...</p>
      </div>
    </div>
  );
}
