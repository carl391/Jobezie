import { useState, useRef, useEffect } from 'react';
import {
  Sparkles,
  Send,
  Loader2,
  MessageCircle,
  Lightbulb,
  Target,
  FileText,
  Users,
  RefreshCw,
  ChevronRight,
  User,
  Bot,
} from 'lucide-react';
import { aiApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const QUICK_PROMPTS = [
  {
    icon: <Target className="w-5 h-5" />,
    title: 'Career Strategy',
    prompt: "What's the best strategy for transitioning into a senior role in my field?",
    color: 'bg-blue-100 text-blue-700 hover:bg-blue-200',
  },
  {
    icon: <FileText className="w-5 h-5" />,
    title: 'Resume Tips',
    prompt: 'How can I make my resume stand out to recruiters and ATS systems?',
    color: 'bg-green-100 text-green-700 hover:bg-green-200',
  },
  {
    icon: <MessageCircle className="w-5 h-5" />,
    title: 'Interview Prep',
    prompt: 'What are the most common behavioral interview questions and how should I answer them?',
    color: 'bg-purple-100 text-purple-700 hover:bg-purple-200',
  },
  {
    icon: <Users className="w-5 h-5" />,
    title: 'Networking',
    prompt: 'How can I effectively network with recruiters on LinkedIn?',
    color: 'bg-orange-100 text-orange-700 hover:bg-orange-200',
  },
];

const FOLLOW_UP_SUGGESTIONS = [
  'Can you give me specific examples?',
  'How should I tailor this to my industry?',
  'What are common mistakes to avoid?',
  'Can you help me practice this?',
];

export function AICoach() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (messageText?: string) => {
    const text = messageText || inputValue.trim();
    if (!text || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await aiApi.careerCoach({
        question: text,
        context: {
          user_name: user?.first_name || user?.full_name,
          career_stage: user?.career_stage,
          current_role: user?.current_role,
          target_roles: user?.target_roles,
          years_experience: user?.years_experience,
          conversation_history: messages.slice(-6).map((m) => ({
            role: m.role,
            content: m.content,
          })),
        },
      });

      const aiResponse = response.data.data?.response || response.data.response;

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: aiResponse || "I'm sorry, I couldn't generate a response. Please try again.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Error getting AI response:', err);
      setError('Failed to get a response. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setError(null);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-primary-600" />
            AI Career Coach
          </h1>
          <p className="text-gray-600 mt-1">Get personalized career advice powered by AI</p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={handleClearChat}
            className="btn btn-outline btn-sm flex items-center gap-1"
          >
            <RefreshCw className="w-4 h-4" />
            New Chat
          </button>
        )}
      </div>

      {/* Chat container */}
      <div className="flex-1 flex flex-col bg-white rounded-xl border border-gray-200 overflow-hidden">
        {/* Messages area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            // Empty state with quick prompts
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mb-4">
                <Sparkles className="w-8 h-8 text-primary-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Hi{user?.first_name ? `, ${user.first_name}` : ''}! How can I help you today?
              </h2>
              <p className="text-gray-500 max-w-md mb-6">
                I'm your AI career coach. Ask me anything about job searching, resume writing,
                interview preparation, or career strategy.
              </p>

              {/* Quick prompts */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
                {QUICK_PROMPTS.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => handleSendMessage(prompt.prompt)}
                    className={`flex items-center gap-3 p-4 rounded-xl text-left transition-all ${prompt.color}`}
                  >
                    {prompt.icon}
                    <div>
                      <p className="font-medium">{prompt.title}</p>
                      <p className="text-xs opacity-80 line-clamp-1">{prompt.prompt}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            // Chat messages
            <>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4 text-primary-600" />
                    </div>
                  )}

                  <div
                    className={`max-w-[70%] ${
                      message.role === 'user'
                        ? 'bg-primary-600 text-white rounded-2xl rounded-tr-md'
                        : 'bg-gray-100 text-gray-900 rounded-2xl rounded-tl-md'
                    } px-4 py-3`}
                  >
                    <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                    <p
                      className={`text-xs mt-1 ${
                        message.role === 'user' ? 'text-primary-200' : 'text-gray-400'
                      }`}
                    >
                      {formatTime(message.timestamp)}
                    </p>
                  </div>

                  {message.role === 'user' && (
                    <div className="w-8 h-8 bg-gray-200 rounded-lg flex items-center justify-center flex-shrink-0">
                      <User className="w-4 h-4 text-gray-600" />
                    </div>
                  )}
                </div>
              ))}

              {/* Loading indicator */}
              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-primary-600" />
                  </div>
                  <div className="bg-gray-100 rounded-2xl rounded-tl-md px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin text-primary-600" />
                      <span className="text-sm text-gray-500">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Error message */}
              {error && (
                <div className="flex justify-center">
                  <div className="bg-red-50 text-red-600 px-4 py-2 rounded-lg text-sm">
                    {error}
                  </div>
                </div>
              )}

              {/* Follow-up suggestions */}
              {messages.length > 0 && messages[messages.length - 1].role === 'assistant' && !isLoading && (
                <div className="flex flex-wrap gap-2 mt-2 ml-11">
                  {FOLLOW_UP_SUGGESTIONS.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSendMessage(suggestion)}
                      className="text-xs px-3 py-1.5 bg-gray-50 text-gray-600 rounded-full hover:bg-gray-100 transition-colors flex items-center gap-1"
                    >
                      {suggestion}
                      <ChevronRight className="w-3 h-3" />
                    </button>
                  ))}
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input area */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-end gap-3">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask me anything about your career..."
                rows={1}
                className="input pr-12 resize-none min-h-[44px] max-h-32"
                style={{
                  height: 'auto',
                  minHeight: '44px',
                }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = 'auto';
                  target.style.height = `${Math.min(target.scrollHeight, 128)}px`;
                }}
              />
              <div className="absolute right-2 bottom-2 text-xs text-gray-400">
                Press Enter to send
              </div>
            </div>
            <button
              onClick={() => handleSendMessage()}
              disabled={!inputValue.trim() || isLoading}
              className="btn btn-primary h-[44px] px-4"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>

          {/* Context indicator */}
          {user && (user.current_role || user.career_stage) && (
            <div className="mt-2 flex items-center gap-2 text-xs text-gray-400">
              <Lightbulb className="w-3 h-3" />
              <span>
                AI is personalized for
                {user.current_role && ` ${user.current_role}`}
                {user.career_stage && ` (${user.career_stage})`}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
