import { useState } from 'react';
import {
  MessageSquare,
  Loader2,
  Sparkles,
  Briefcase,
  Target,
  ChevronRight,
  AlertCircle,
  Lightbulb,
  Star,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Play,
  Pause,
} from 'lucide-react';
import { aiApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

type PrepMode = 'practice' | 'review' | 'tips';

interface QuestionResponse {
  question: string;
  question_type: string;
  sample_answer: string;
  key_points: string[];
  follow_up_questions: string[];
  difficulty: 'easy' | 'medium' | 'hard';
}

interface InterviewTips {
  category: string;
  tips: Array<{
    title: string;
    description: string;
    example?: string;
  }>;
}

const QUESTION_TYPES = [
  { value: 'behavioral', label: 'Behavioral', description: 'STAR method questions about past experiences' },
  { value: 'technical', label: 'Technical', description: 'Role-specific knowledge and skills' },
  { value: 'situational', label: 'Situational', description: 'Hypothetical scenarios and problem-solving' },
  { value: 'leadership', label: 'Leadership', description: 'Management and team leadership' },
  { value: 'culture', label: 'Culture Fit', description: 'Values and workplace alignment' },
];

const DIFFICULTY_COLORS = {
  easy: 'bg-green-100 text-green-700',
  medium: 'bg-yellow-100 text-yellow-700',
  hard: 'bg-red-100 text-red-700',
};

export function InterviewPrep() {
  const { user } = useAuth();
  const [activeMode, setActiveMode] = useState<PrepMode>('practice');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Practice Mode State
  const [practiceForm, setPracticeForm] = useState({
    target_role: user?.target_roles?.[0] || '',
    company: '',
    question_type: 'behavioral',
    difficulty: 'medium',
  });
  const [currentQuestion, setCurrentQuestion] = useState<QuestionResponse | null>(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [showSampleAnswer, setShowSampleAnswer] = useState(false);
  const [feedback, setFeedback] = useState<{ score: number; feedback: string } | null>(null);

  // Tips State
  const [tips, setTips] = useState<InterviewTips[]>([]);

  const handleGenerateQuestion = async () => {
    setIsLoading(true);
    setError(null);
    setShowSampleAnswer(false);
    setUserAnswer('');
    setFeedback(null);

    try {
      const response = await aiApi.interviewPrep({
        action: 'generate_question',
        target_role: practiceForm.target_role,
        company: practiceForm.company || undefined,
        question_type: practiceForm.question_type,
        difficulty: practiceForm.difficulty,
        user_context: {
          current_role: user?.current_role,
          years_experience: user?.years_experience,
          skills: user?.technical_skills,
        },
      });
      setCurrentQuestion(response.data.data);
    } catch (err) {
      console.error('Error generating question:', err);
      setError('Failed to generate question. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEvaluateAnswer = async () => {
    if (!currentQuestion || !userAnswer.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await aiApi.interviewPrep({
        action: 'evaluate_answer',
        question: currentQuestion.question,
        question_type: currentQuestion.question_type,
        user_answer: userAnswer,
        target_role: practiceForm.target_role,
      });
      setFeedback(response.data.data);
    } catch (err) {
      console.error('Error evaluating answer:', err);
      setError('Failed to evaluate answer. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetTips = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await aiApi.interviewPrep({
        action: 'get_tips',
        target_role: practiceForm.target_role || user?.target_roles?.[0],
        question_type: practiceForm.question_type,
      });
      setTips(response.data.data?.tips || []);
    } catch (err) {
      console.error('Error fetching tips:', err);
      setError('Failed to fetch tips. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const modes = [
    { id: 'practice' as const, label: 'Practice Questions', icon: Play },
    { id: 'tips' as const, label: 'Interview Tips', icon: Lightbulb },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <MessageSquare className="w-6 h-6 text-primary-600" />
          Interview Preparation
        </h1>
        <p className="text-gray-600 mt-1">
          Practice interview questions and get AI-powered feedback to improve your answers
        </p>
      </div>

      {/* Mode Tabs */}
      <div className="flex gap-2" data-tour="interview-modes">
        {modes.map((mode) => (
          <button
            key={mode.id}
            onClick={() => setActiveMode(mode.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
              activeMode === mode.id
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <mode.icon className="w-4 h-4" />
            {mode.label}
          </button>
        ))}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Practice Mode */}
      {activeMode === 'practice' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Settings Panel */}
          <div className="card lg:col-span-1" data-tour="interview-settings">
            <h2 className="text-lg font-semibold mb-4">Practice Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="label">Target Role</label>
                <div className="relative">
                  <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    className="input pl-10"
                    placeholder="e.g., Software Engineer"
                    value={practiceForm.target_role}
                    onChange={(e) => setPracticeForm({ ...practiceForm, target_role: e.target.value })}
                  />
                </div>
              </div>
              <div>
                <label className="label">Company (Optional)</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., Google, Amazon"
                  value={practiceForm.company}
                  onChange={(e) => setPracticeForm({ ...practiceForm, company: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Question Type</label>
                <select
                  className="input"
                  value={practiceForm.question_type}
                  onChange={(e) => setPracticeForm({ ...practiceForm, question_type: e.target.value })}
                >
                  {QUESTION_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  {QUESTION_TYPES.find((t) => t.value === practiceForm.question_type)?.description}
                </p>
              </div>
              <div>
                <label className="label">Difficulty</label>
                <select
                  className="input"
                  value={practiceForm.difficulty}
                  onChange={(e) => setPracticeForm({ ...practiceForm, difficulty: e.target.value })}
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
              <button
                onClick={handleGenerateQuestion}
                disabled={!practiceForm.target_role || isLoading}
                className="btn btn-primary w-full"
                data-tour="interview-generate"
              >
                {isLoading && !currentQuestion ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate Question
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Question & Answer Panel */}
          <div className="lg:col-span-2 space-y-4">
            {currentQuestion ? (
              <>
                {/* Question Card */}
                <div className="card">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${DIFFICULTY_COLORS[currentQuestion.difficulty]}`}>
                        {currentQuestion.difficulty}
                      </span>
                      <span className="text-sm text-gray-500">{currentQuestion.question_type}</span>
                    </div>
                    <button
                      onClick={handleGenerateQuestion}
                      disabled={isLoading}
                      className="text-gray-400 hover:text-gray-600"
                      title="New question"
                    >
                      <RotateCcw className="w-5 h-5" />
                    </button>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">{currentQuestion.question}</h3>

                  {/* Key Points */}
                  <div className="flex flex-wrap gap-2">
                    {currentQuestion.key_points?.map((point, i) => (
                      <span key={i} className="px-2 py-1 bg-primary-50 text-primary-700 text-xs rounded-full">
                        {point}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Answer Input */}
                <div className="card" data-tour="interview-answer">
                  <h3 className="font-semibold mb-3">Your Answer</h3>
                  <textarea
                    className="input min-h-[150px]"
                    placeholder="Type your answer here... Use the STAR method (Situation, Task, Action, Result) for behavioral questions."
                    value={userAnswer}
                    onChange={(e) => setUserAnswer(e.target.value)}
                  />
                  <div className="flex gap-3 mt-4">
                    <button
                      onClick={handleEvaluateAnswer}
                      disabled={!userAnswer.trim() || isLoading}
                      className="btn btn-primary flex-1"
                    >
                      {isLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <>
                          <Target className="w-4 h-4" />
                          Get Feedback
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => setShowSampleAnswer(!showSampleAnswer)}
                      className="btn btn-outline"
                    >
                      {showSampleAnswer ? 'Hide' : 'Show'} Sample Answer
                    </button>
                  </div>
                </div>

                {/* Sample Answer */}
                {showSampleAnswer && (
                  <div className="card bg-blue-50 border-blue-200">
                    <h3 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
                      <Lightbulb className="w-5 h-5" />
                      Sample Answer
                    </h3>
                    <p className="text-blue-800 whitespace-pre-wrap">{currentQuestion.sample_answer}</p>
                  </div>
                )}

                {/* Feedback */}
                {feedback && (
                  <div className="card bg-green-50 border-green-200">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-green-900 flex items-center gap-2">
                        <Star className="w-5 h-5" />
                        AI Feedback
                      </h3>
                      <div className="flex items-center gap-2">
                        <span className="text-2xl font-bold text-green-700">{feedback.score}/10</span>
                      </div>
                    </div>
                    <p className="text-green-800 whitespace-pre-wrap">{feedback.feedback}</p>
                  </div>
                )}

                {/* Follow-up Questions */}
                {currentQuestion.follow_up_questions?.length > 0 && (
                  <div className="card">
                    <h3 className="font-semibold mb-3">Potential Follow-up Questions</h3>
                    <ul className="space-y-2">
                      {currentQuestion.follow_up_questions.map((q, i) => (
                        <li key={i} className="flex items-start gap-2 text-gray-700">
                          <ChevronRight className="w-4 h-4 mt-1 text-gray-400 flex-shrink-0" />
                          {q}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            ) : (
              <div className="card">
                <div className="text-center py-12 text-gray-500">
                  <MessageSquare className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Practice?</h3>
                  <p className="max-w-md mx-auto">
                    Select your target role and question type, then click "Generate Question" to start practicing.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tips Mode */}
      {activeMode === 'tips' && (
        <div className="space-y-6">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Interview Tips</h2>
              <button
                onClick={handleGetTips}
                disabled={isLoading}
                className="btn btn-primary btn-sm"
              >
                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Get Personalized Tips'}
              </button>
            </div>

            {tips.length > 0 ? (
              <div className="space-y-6">
                {tips.map((category, idx) => (
                  <div key={idx}>
                    <h3 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                      <Lightbulb className="w-4 h-4 text-yellow-500" />
                      {category.category}
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {category.tips.map((tip, i) => (
                        <div key={i} className="p-4 bg-gray-50 rounded-lg">
                          <h4 className="font-medium text-gray-900 mb-2">{tip.title}</h4>
                          <p className="text-sm text-gray-600 mb-2">{tip.description}</p>
                          {tip.example && (
                            <div className="mt-2 p-2 bg-white rounded border-l-2 border-primary-500">
                              <p className="text-xs text-gray-500 mb-1">Example:</p>
                              <p className="text-sm text-gray-700 italic">{tip.example}</p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Lightbulb className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Click "Get Personalized Tips" to receive interview advice tailored to your target role</p>
              </div>
            )}
          </div>

          {/* Quick Tips */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="card bg-blue-50 border-blue-200">
              <h3 className="font-semibold text-blue-900 mb-2">STAR Method</h3>
              <p className="text-sm text-blue-700">
                <strong>S</strong>ituation - <strong>T</strong>ask - <strong>A</strong>ction - <strong>R</strong>esult.
                Structure behavioral answers with this framework.
              </p>
            </div>
            <div className="card bg-green-50 border-green-200">
              <h3 className="font-semibold text-green-900 mb-2">Research the Company</h3>
              <p className="text-sm text-green-700">
                Know the company's mission, recent news, and culture. Reference these in your answers.
              </p>
            </div>
            <div className="card bg-purple-50 border-purple-200">
              <h3 className="font-semibold text-purple-900 mb-2">Prepare Questions</h3>
              <p className="text-sm text-purple-700">
                Have 3-5 thoughtful questions ready about the role, team, and growth opportunities.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
