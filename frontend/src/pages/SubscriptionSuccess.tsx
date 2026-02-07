import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CheckCircle, ArrowRight, Settings } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export function SubscriptionSuccess() {
  const { refreshUser } = useAuth();
  const navigate = useNavigate();
  const [countdown, setCountdown] = useState(5);

  useEffect(() => {
    refreshUser();
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          navigate('/settings');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full text-center">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <CheckCircle className="w-10 h-10 text-green-600" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Payment Successful!</h1>
        <p className="text-gray-600 mb-8">
          Your subscription has been upgraded. You now have access to all your new features.
        </p>

        <div className="space-y-3">
          <Link to="/dashboard" className="btn btn-primary w-full flex items-center justify-center gap-2">
            Go to Dashboard
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link to="/settings" className="btn btn-outline w-full flex items-center justify-center gap-2">
            <Settings className="w-4 h-4" />
            View Subscription
          </Link>
        </div>

        <p className="text-xs text-gray-400 mt-6">
          Redirecting to settings in {countdown}s...
        </p>
      </div>
    </div>
  );
}
