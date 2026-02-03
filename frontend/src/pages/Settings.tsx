import { Settings as SettingsIcon } from 'lucide-react';

export function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">Manage your account and preferences</p>
      </div>

      <div className="card text-center py-12">
        <SettingsIcon className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Account Settings</h3>
        <p className="text-gray-500">Settings page coming soon...</p>
      </div>
    </div>
  );
}
