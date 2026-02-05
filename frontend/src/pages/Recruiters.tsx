import { useState, useEffect, useCallback } from 'react';
import { recruiterApi } from '../lib/api';
import { Users, Plus, Search, Filter } from 'lucide-react';
import { AddRecruiterModal } from '../components/recruiters/AddRecruiterModal';
import { RecruiterDetailsModal } from '../components/recruiters/RecruiterDetailsModal';
import type { Recruiter } from '../types';

const PIPELINE_STAGES = [
  { id: 'new', label: 'New', color: 'bg-gray-100 text-gray-700' },
  { id: 'researching', label: 'Researching', color: 'bg-blue-100 text-blue-700' },
  { id: 'contacted', label: 'Contacted', color: 'bg-yellow-100 text-yellow-700' },
  { id: 'responded', label: 'Responded', color: 'bg-green-100 text-green-700' },
  { id: 'interviewing', label: 'Interviewing', color: 'bg-purple-100 text-purple-700' },
  { id: 'offer', label: 'Offer', color: 'bg-emerald-100 text-emerald-700' },
  { id: 'accepted', label: 'Accepted', color: 'bg-green-100 text-green-700' },
  { id: 'declined', label: 'Declined', color: 'bg-red-100 text-red-700' },
];

export function Recruiters() {
  const [recruiters, setRecruiters] = useState<Recruiter[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStage, setSelectedStage] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedRecruiterId, setSelectedRecruiterId] = useState<string | null>(null);

  const fetchRecruiters = useCallback(async () => {
    try {
      const response = await recruiterApi.list({ status: selectedStage || undefined });
      setRecruiters(response.data.recruiters || response.data.data?.recruiters || []);
    } catch (error) {
      console.error('Failed to fetch recruiters:', error);
    } finally {
      setIsLoading(false);
    }
  }, [selectedStage]);

  useEffect(() => {
    fetchRecruiters();
  }, [fetchRecruiters]);

  const handleRecruiterAdded = (newRecruiter: Recruiter) => {
    setRecruiters((prev) => [newRecruiter, ...prev]);
  };

  const handleRecruiterUpdated = (updatedRecruiter: Recruiter) => {
    setRecruiters((prev) =>
      prev.map((r) => (r.id === updatedRecruiter.id ? updatedRecruiter : r))
    );
  };

  const filteredRecruiters = recruiters.filter((r) =>
    r.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.company?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStageColor = (status: string) => {
    return PIPELINE_STAGES.find((s) => s.id === status)?.color || 'bg-gray-100 text-gray-700';
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Recruiter CRM</h1>
          <p className="text-gray-600 mt-1">Track and manage your recruiter relationships</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn btn-primary flex items-center"
          data-tour="recruiter-add"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Recruiter
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name or company..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input pl-10"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-400" />
          <select
            value={selectedStage || ''}
            onChange={(e) => setSelectedStage(e.target.value || null)}
            className="input w-auto"
          >
            <option value="">All stages</option>
            {PIPELINE_STAGES.map((stage) => (
              <option key={stage.id} value={stage.id}>
                {stage.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Pipeline stages overview */}
      <div className="flex gap-2 overflow-x-auto pb-2" data-tour="recruiter-pipeline">
        {PIPELINE_STAGES.map((stage) => {
          const count = recruiters.filter((r) => r.status === stage.id).length;
          return (
            <button
              key={stage.id}
              onClick={() => setSelectedStage(selectedStage === stage.id ? null : stage.id)}
              className={`flex-shrink-0 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedStage === stage.id
                  ? 'ring-2 ring-primary-500 ' + stage.color
                  : stage.color + ' hover:ring-2 hover:ring-gray-300'
              }`}
            >
              {stage.label} ({count})
            </button>
          );
        })}
      </div>

      {/* Recruiter list */}
      {filteredRecruiters.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRecruiters.map((recruiter, index) => (
            <div key={recruiter.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">{recruiter.full_name}</h3>
                  {recruiter.title && recruiter.company && (
                    <p className="text-sm text-gray-500">
                      {recruiter.title} at {recruiter.company}
                    </p>
                  )}
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${getStageColor(recruiter.status)}`}>
                  {PIPELINE_STAGES.find((s) => s.id === recruiter.status)?.label || recruiter.status}
                </span>
              </div>

              <div
                className="mt-4 grid grid-cols-3 gap-2 text-center"
                data-tour={index === 0 ? "recruiter-engagement" : undefined}
              >
                <div>
                  <p className="text-lg font-semibold text-gray-900">{recruiter.messages_sent}</p>
                  <p className="text-xs text-gray-500">Sent</p>
                </div>
                <div>
                  <p className="text-lg font-semibold text-gray-900">{recruiter.messages_opened || 0}</p>
                  <p className="text-xs text-gray-500">Opened</p>
                </div>
                <div>
                  <p className="text-lg font-semibold text-gray-900">{recruiter.responses_received}</p>
                  <p className="text-xs text-gray-500">Replies</p>
                </div>
              </div>

              {recruiter.next_action && (
                <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
                  <p className="text-sm text-yellow-800">
                    <span className="font-medium">Next:</span> {recruiter.next_action}
                  </p>
                  {recruiter.next_action_date && (
                    <p className="text-xs text-yellow-600 mt-1">
                      Due: {new Date(recruiter.next_action_date).toLocaleDateString()}
                    </p>
                  )}
                </div>
              )}

              <div className="mt-4 flex justify-end">
                <button
                  onClick={() => setSelectedRecruiterId(recruiter.id)}
                  className="btn btn-outline text-sm"
                >
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center py-12" data-tour="recruiter-engagement">
          <Users className="w-16 h-16 mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No recruiters found</h3>
          <p className="text-gray-500 mb-4">
            {searchQuery || selectedStage
              ? 'Try adjusting your filters'
              : 'Add your first recruiter to start tracking'}
          </p>
          {!searchQuery && !selectedStage && (
            <button
              onClick={() => setShowAddModal(true)}
              className="btn btn-primary"
            >
              Add Recruiter
            </button>
          )}
        </div>
      )}

      {/* Add Recruiter Modal */}
      <AddRecruiterModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSuccess={handleRecruiterAdded}
      />

      {/* Recruiter Details Modal */}
      {selectedRecruiterId && (
        <RecruiterDetailsModal
          isOpen={!!selectedRecruiterId}
          onClose={() => setSelectedRecruiterId(null)}
          recruiterId={selectedRecruiterId}
          onUpdate={handleRecruiterUpdated}
        />
      )}
    </div>
  );
}
