import { useState } from 'react';
import {
  Download,
  Trash2,
  AlertTriangle,
  Loader2,
  CheckCircle,
  X,
  Shield,
  FileArchive,
} from 'lucide-react';
import { api } from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';

/**
 * DataPrivacySettings - Settings panel for account deletion + data export.
 *
 * Mount inside your Settings page:
 *   <DataPrivacySettings />
 *
 * Endpoints used:
 *   DELETE /api/profile/account
 *   POST   /api/profile/account/cancel-deletion
 *   POST   /api/profile/export
 *   GET    /api/profile/export/status
 */
export function DataPrivacySettings() {
  const { user, logout } = useAuth();

  // -- Deletion State --
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [deleteConfirmation, setDeleteConfirmation] = useState('');
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState('');
  const [deleteSuccess, setDeleteSuccess] = useState(false);

  // -- Export State --
  const [exportLoading, setExportLoading] = useState(false);
  const [exportStatus, setExportStatus] = useState<
    'idle' | 'processing' | 'completed' | 'failed'
  >('idle');
  const [exportError, setExportError] = useState('');
  const [exportToken, setExportToken] = useState<string | null>(null);
  const [exportSize, setExportSize] = useState<number | null>(null);

  // -------------------------------------------
  // Account Deletion
  // -------------------------------------------

  const handleDeleteAccount = async () => {
    if (deleteConfirmation !== 'DELETE') {
      setDeleteError('Please type DELETE to confirm');
      return;
    }
    if (!deletePassword) {
      setDeleteError('Password is required');
      return;
    }

    setDeleteLoading(true);
    setDeleteError('');

    try {
      await api.delete('/profile/account', {
        data: {
          password: deletePassword,
          confirmation: deleteConfirmation,
        },
      });

      setDeleteSuccess(true);
      setTimeout(() => logout(), 3000);
    } catch (err) {
      const error = err as { response?: { data?: { data?: { error?: string } } } };
      setDeleteError(
        error.response?.data?.data?.error || 'Failed to delete account'
      );
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleCancelDeletion = async () => {
    try {
      await api.post('/profile/account/cancel-deletion');
      window.location.reload();
    } catch {
      window.location.reload();
    }
  };

  const resetDeleteModal = () => {
    setShowDeleteModal(false);
    setDeleteError('');
    setDeletePassword('');
    setDeleteConfirmation('');
  };

  // -------------------------------------------
  // Data Export
  // -------------------------------------------

  const handleExportData = async () => {
    setExportLoading(true);
    setExportError('');
    setExportStatus('processing');

    try {
      const res = await api.post('/profile/export');
      const data = res.data?.data || res.data;

      setExportStatus('completed');
      setExportToken(data.download_token);
      setExportSize(data.file_size_bytes);
    } catch (err) {
      const error = err as { response?: { data?: { data?: { error?: string } } } };
      setExportError(
        error.response?.data?.data?.error || 'Export failed'
      );
      setExportStatus('failed');
    } finally {
      setExportLoading(false);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // -------------------------------------------
  // Render
  // -------------------------------------------

  return (
    <div className="space-y-8">
      {/* Section Header */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Shield className="h-5 w-5 text-blue-600" />
          Data & Privacy
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          Manage your data, download a copy, or delete your account.
        </p>
      </div>

      {/* -- Pending Deletion Banner -- */}
      {user?.deletion_requested_at && !deleteSuccess && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-medium text-amber-900">
                Account scheduled for deletion
              </p>
              <p className="mt-1 text-sm text-amber-700">
                Your account and all data will be permanently deleted on{' '}
                <strong>
                  {user.deletion_scheduled_for
                    ? new Date(user.deletion_scheduled_for).toLocaleDateString(
                        'en-US',
                        { year: 'numeric', month: 'long', day: 'numeric' }
                      )
                    : '(date pending)'}
                </strong>
                . You can cancel at any time before then.
              </p>
              <button
                onClick={handleCancelDeletion}
                className="mt-2 text-sm font-medium text-amber-800 underline hover:text-amber-950 transition-colors"
              >
                Cancel deletion - keep my account
              </button>
            </div>
          </div>
        </div>
      )}

      {/* -- Data Export Card -- */}
      <div className="rounded-lg border border-gray-200 p-5">
        <h3 className="text-sm font-medium text-gray-900 flex items-center gap-2">
          <Download className="h-4 w-4 text-gray-600" />
          Export Your Data
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          Download a ZIP file containing your profile, resumes, recruiter contacts,
          messages, activity history, AI Coach conversations, and score history.
          The download link is valid for 7 days.
        </p>

        {/* Export error */}
        {exportError && (
          <p className="mt-3 text-sm text-red-600">{exportError}</p>
        )}

        {/* Export success */}
        {exportStatus === 'completed' && exportToken && (
          <div className="mt-3 rounded-md bg-green-50 border border-green-200 p-3">
            <div className="flex items-center gap-2">
              <FileArchive className="h-4 w-4 text-green-600" />
              <div className="text-sm text-green-800">
                <span className="font-medium">Export ready</span>
                {exportSize && (
                  <span className="text-green-600">
                    {' '}({formatBytes(exportSize)})
                  </span>
                )}
                {' - '}
                <a
                  href={`/api/profile/export/download/${exportToken}`}
                  className="font-medium underline hover:text-green-900"
                  download
                >
                  Download ZIP
                </a>
              </div>
            </div>
          </div>
        )}

        <button
          onClick={handleExportData}
          disabled={exportLoading}
          className="mt-4 inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 transition-colors"
        >
          {exportLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Generating export...
            </>
          ) : (
            <>
              <Download className="h-4 w-4" />
              Export my data
            </>
          )}
        </button>
      </div>

      {/* -- Delete Account Card -- */}
      <div className="rounded-lg border border-red-200 bg-red-50/30 p-5">
        <h3 className="text-sm font-medium text-red-700 flex items-center gap-2">
          <Trash2 className="h-4 w-4" />
          Delete Account
        </h3>
        <p className="mt-1 text-sm text-gray-600">
          Permanently delete your Jobezie account and all associated data.
          Your account enters a 30-day grace period before permanent deletion.
          You can cancel during this window.
        </p>
        <p className="mt-2 text-xs text-gray-500">
          We recommend exporting your data before deleting your account.
        </p>

        <button
          onClick={() => setShowDeleteModal(true)}
          disabled={!!user?.deletion_requested_at}
          className="mt-4 inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Trash2 className="h-4 w-4" />
          {user?.deletion_requested_at ? 'Deletion pending...' : 'Delete my account'}
        </button>
      </div>

      {/* -------------------------------------------
          Delete Confirmation Modal
          ------------------------------------------- */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-xl bg-white shadow-2xl">
            <div className="p-6">
              {deleteSuccess ? (
                /* -- Success State -- */
                <div className="text-center py-4">
                  <CheckCircle className="mx-auto h-12 w-12 text-green-500" />
                  <h3 className="mt-3 text-lg font-semibold text-gray-900">
                    Deletion scheduled
                  </h3>
                  <p className="mt-2 text-sm text-gray-500">
                    Your account will be permanently deleted in 30 days.
                    Check your email for confirmation details.
                  </p>
                  <p className="mt-1 text-sm text-gray-400">Logging out...</p>
                </div>
              ) : (
                /* -- Confirmation Form -- */
                <>
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-gray-900">
                      Delete Account
                    </h3>
                    <button
                      onClick={resetDeleteModal}
                      className="rounded-md p-1 text-gray-400 hover:bg-gray-100 transition-colors"
                    >
                      <X className="h-5 w-5" />
                    </button>
                  </div>

                  {/* Warning box */}
                  <div className="mt-4 rounded-lg bg-red-50 border border-red-200 p-3">
                    <p className="text-sm font-medium text-red-800">
                      This will permanently delete:
                    </p>
                    <ul className="mt-2 space-y-1 text-sm text-red-700">
                      <li>- Your profile and all personal data</li>
                      <li>- All resumes and generated content</li>
                      <li>- Recruiter contacts and message history</li>
                      <li>- AI Coach conversation history</li>
                      <li>- Your subscription (cancelled, no refund for current period)</li>
                    </ul>
                  </div>

                  {/* Form fields */}
                  <div className="mt-4 space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Enter your password
                      </label>
                      <input
                        type="password"
                        value={deletePassword}
                        onChange={(e) => {
                          setDeletePassword(e.target.value);
                          setDeleteError('');
                        }}
                        className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-red-500 focus:ring-1 focus:ring-red-500 outline-none"
                        placeholder="Password"
                        autoComplete="current-password"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Type{' '}
                        <span className="font-mono font-bold text-red-600">
                          DELETE
                        </span>{' '}
                        to confirm
                      </label>
                      <input
                        type="text"
                        value={deleteConfirmation}
                        onChange={(e) => {
                          setDeleteConfirmation(e.target.value.toUpperCase());
                          setDeleteError('');
                        }}
                        className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm font-mono text-gray-900 placeholder-gray-400 focus:border-red-500 focus:ring-1 focus:ring-red-500 outline-none"
                        placeholder="DELETE"
                        autoComplete="off"
                        spellCheck={false}
                      />
                    </div>
                  </div>

                  {/* Error message */}
                  {deleteError && (
                    <p className="mt-3 text-sm text-red-600">
                      {deleteError}
                    </p>
                  )}

                  {/* Action buttons */}
                  <div className="mt-5 flex gap-3">
                    <button
                      onClick={resetDeleteModal}
                      className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleDeleteAccount}
                      disabled={
                        deleteLoading ||
                        deleteConfirmation !== 'DELETE' ||
                        !deletePassword
                      }
                      className="flex-1 inline-flex items-center justify-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {deleteLoading ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Deleting...
                        </>
                      ) : (
                        'Delete permanently'
                      )}
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
