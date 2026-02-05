import { Compass, Lightbulb, CheckCircle } from 'lucide-react';
import { useTour } from '../../contexts/TourContext';
import type { Feature } from '../../config/tours';

interface FeatureCardProps {
  feature: Feature;
}

export function FeatureCard({ feature }: FeatureCardProps) {
  const { startTour } = useTour();

  const handleLaunchTour = () => {
    if (feature.tourId) {
      startTour(feature.tourId);
    }
  };

  return (
    <div className="p-4 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h4 className="font-medium text-gray-900">{feature.name}</h4>
          <p className="text-sm text-gray-600 mt-1">{feature.description}</p>

          {/* Tips section */}
          {feature.tips && feature.tips.length > 0 && (
            <div className="mt-3">
              <div className="flex items-center text-xs font-medium text-gray-500 mb-2">
                <Lightbulb className="w-3.5 h-3.5 mr-1" />
                Tips
              </div>
              <ul className="space-y-1.5">
                {feature.tips.map((tip, index) => (
                  <li key={index} className="flex items-start text-sm text-gray-600">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Launch tour button */}
        {feature.tourId && (
          <button
            onClick={handleLaunchTour}
            className="ml-4 flex items-center px-3 py-1.5 text-sm font-medium text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors"
          >
            <Compass className="w-4 h-4 mr-1.5" />
            Tour
          </button>
        )}
      </div>
    </div>
  );
}
