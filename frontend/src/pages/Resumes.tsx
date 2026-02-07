import { useState, useEffect, useCallback } from 'react';
import { resumeApi } from '../lib/api';
import { FileText, Upload, Star, Trash2, Eye, BarChart2, Lightbulb, Target } from 'lucide-react';
import { ViewResumeModal } from '../components/resumes/ViewResumeModal';
import { ATSScoreModal } from '../components/resumes/ATSScoreModal';
import { ResumeAnalysisModal } from '../components/resumes/ResumeAnalysisModal';
import { ResumeTailorModal } from '../components/resumes/ResumeTailorModal';
import type { Resume } from '../types';

export function Resumes() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [viewResumeId, setViewResumeId] = useState<string | null>(null);
  const [scoreResumeId, setScoreResumeId] = useState<string | null>(null);
  const [analysisResumeId, setAnalysisResumeId] = useState<string | null>(null);
  const [tailorResumeId, setTailorResumeId] = useState<string | null>(null);

  const fetchResumes = useCallback(async () => {
    try {
      const response = await resumeApi.list();
      setResumes(response.data.data?.resumes || response.data.resumes || []);
    } catch (error) {
      console.error('Failed to fetch resumes:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchResumes();
  }, [fetchResumes]);

  const handleUpload = async (files: FileList) => {
    setUploadError(null);
    const file = files[0];

    if (!file) return;

    const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!validTypes.includes(file.type)) {
      setUploadError('Please upload a PDF or Word document');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      await resumeApi.upload(formData);
      fetchResumes();
    } catch (error) {
      setUploadError('Failed to upload resume');
      console.error(error);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files) {
      handleUpload(e.dataTransfer.files);
    }
  };

  const handleSetMaster = async (id: string) => {
    try {
      await resumeApi.setMaster(id);
      fetchResumes();
    } catch (error) {
      console.error('Failed to set master resume:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this resume?')) return;

    try {
      await resumeApi.delete(id);
      fetchResumes();
    } catch (error) {
      console.error('Failed to delete resume:', error);
    }
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
          <h1 className="text-2xl font-bold text-gray-900">Resumes</h1>
          <p className="text-gray-600 mt-1">Manage and optimize your resumes</p>
        </div>
      </div>

      {/* Upload area */}
      <div
        data-tour="resume-upload"
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`card border-2 border-dashed transition-colors ${
          isDragging ? 'border-primary-500 bg-primary-50' : 'border-gray-300'
        }`}
      >
        <div className="text-center py-8">
          <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-600 mb-2">Drag and drop your resume here, or</p>
          <label className="btn btn-primary cursor-pointer">
            Browse files
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              className="hidden"
              onChange={(e) => e.target.files && handleUpload(e.target.files)}
            />
          </label>
          <p className="text-sm text-gray-500 mt-2">PDF or Word documents up to 5MB</p>
          {uploadError && (
            <p className="text-sm text-red-600 mt-2">{uploadError}</p>
          )}
        </div>
      </div>

      {/* Resume list */}
      {resumes.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {resumes.map((resume, index) => (
            <div key={resume.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-primary-600" />
                  </div>
                  <div className="ml-3">
                    <h3 className="font-medium text-gray-900">{resume.title}</h3>
                    <p className="text-sm text-gray-500">
                      {resume.file_size ? `${(resume.file_size / 1024).toFixed(1)} KB` : 'N/A'}
                    </p>
                  </div>
                </div>
                {resume.is_master && (
                  <span className="flex items-center text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full">
                    <Star className="w-3 h-3 mr-1" /> Master
                  </span>
                )}
              </div>

              <div
                className="mt-4 p-3 bg-gray-50 rounded-lg"
                data-tour={index === 0 ? "resume-ats" : undefined}
              >
                {resume.ats_total_score !== undefined ? (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">ATS Score</span>
                      <span className={`text-lg font-bold ${
                        resume.ats_total_score >= 80 ? 'text-green-600' :
                        resume.ats_total_score >= 60 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {resume.ats_total_score}%
                      </span>
                    </div>
                    <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          resume.ats_total_score >= 80 ? 'bg-green-500' :
                          resume.ats_total_score >= 60 ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}
                        style={{ width: `${resume.ats_total_score}%` }}
                      />
                    </div>
                  </>
                ) : (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">ATS Score</span>
                    <span className="text-sm text-gray-400">Click to analyze</span>
                  </div>
                )}
              </div>

              <div className="mt-4 flex items-center justify-between">
                <div className="flex space-x-1">
                  <button
                    onClick={() => setViewResumeId(resume.id)}
                    className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
                    title="View"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setScoreResumeId(resume.id)}
                    className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
                    title="ATS Score"
                  >
                    <BarChart2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setAnalysisResumeId(resume.id)}
                    className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
                    title="Analysis & Suggestions"
                  >
                    <Lightbulb className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setTailorResumeId(resume.id)}
                    className="p-2 text-gray-500 hover:text-orange-600 hover:bg-orange-50 rounded-lg"
                    title="Tailor for Job"
                    data-tour={index === 0 ? "resume-optimize" : undefined}
                  >
                    <Target className="w-4 h-4" />
                  </button>
                  {!resume.is_master && (
                    <button
                      onClick={() => handleSetMaster(resume.id)}
                      className="p-2 text-gray-500 hover:text-yellow-600 hover:bg-yellow-50 rounded-lg"
                      title="Set as master"
                    >
                      <Star className="w-4 h-4" />
                    </button>
                  )}
                </div>
                <button
                  onClick={() => handleDelete(resume.id)}
                  className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center py-12" data-tour="resume-ats">
          <FileText className="w-16 h-16 mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No resumes yet</h3>
          <p className="text-gray-500 mb-4" data-tour="resume-optimize">Upload your first resume to get started</p>
        </div>
      )}

      {/* View Resume Modal */}
      {viewResumeId && (
        <ViewResumeModal
          isOpen={!!viewResumeId}
          onClose={() => setViewResumeId(null)}
          resumeId={viewResumeId}
        />
      )}

      {/* ATS Score Modal */}
      {scoreResumeId && (
        <ATSScoreModal
          isOpen={!!scoreResumeId}
          onClose={() => setScoreResumeId(null)}
          resumeId={scoreResumeId}
          resumeName={resumes.find(r => r.id === scoreResumeId)?.title || 'Resume'}
          initialScore={resumes.find(r => r.id === scoreResumeId)?.ats_total_score}
          onScoreUpdated={(newScore: number) => {
            setResumes(prev => prev.map(r =>
              r.id === scoreResumeId ? { ...r, ats_total_score: newScore } : r
            ));
          }}
        />
      )}

      {/* Analysis Modal */}
      {analysisResumeId && (
        <ResumeAnalysisModal
          isOpen={!!analysisResumeId}
          onClose={() => setAnalysisResumeId(null)}
          resumeId={analysisResumeId}
          resumeName={resumes.find(r => r.id === analysisResumeId)?.title || 'Resume'}
        />
      )}

      {/* Tailor Modal */}
      {tailorResumeId && (
        <ResumeTailorModal
          isOpen={!!tailorResumeId}
          onClose={() => setTailorResumeId(null)}
          resumeId={tailorResumeId}
          resumeName={resumes.find(r => r.id === tailorResumeId)?.title || 'Resume'}
          onTailored={fetchResumes}
        />
      )}
    </div>
  );
}
