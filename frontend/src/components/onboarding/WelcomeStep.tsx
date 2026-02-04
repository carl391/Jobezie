import { Sparkles } from 'lucide-react';

interface WelcomeStepProps {
  onNext: () => void;
  userName: string;
}

export function WelcomeStep({ onNext, userName }: WelcomeStepProps) {
  return (
    <div className="text-center">
      <div className="mb-8">
        <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <Sparkles className="w-10 h-10 text-primary-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-3">
          Welcome to Jobezie{userName ? `, ${userName}` : ''}!
        </h1>
        <p className="text-lg text-gray-600 max-w-md mx-auto">
          Your AI Career Assistant is ready to help you land your dream job.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8 max-w-md mx-auto">
        <h2 className="font-semibold text-gray-900 mb-4">
          Here's what we'll set up together:
        </h2>
        <ul className="text-left space-y-3">
          <li className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
              1
            </span>
            <span className="text-gray-600">Your career profile and goals</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
              2
            </span>
            <span className="text-gray-600">
              Resume upload with instant ATS scoring
            </span>
          </li>
          <li className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
              3
            </span>
            <span className="text-gray-600">
              Your first recruiter contact
            </span>
          </li>
        </ul>
      </div>

      <p className="text-sm text-gray-500 mb-6">
        This takes about 2-3 minutes
      </p>

      <button onClick={onNext} className="btn btn-primary px-8 py-3 text-lg">
        Let's Get Started
      </button>
    </div>
  );
}
