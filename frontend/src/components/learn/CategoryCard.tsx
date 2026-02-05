import { ChevronDown, ChevronRight } from 'lucide-react';
import { FeatureCard } from './FeatureCard';
import type { FeatureCategory } from '../../config/tours';
import clsx from 'clsx';

interface CategoryCardProps {
  category: FeatureCategory;
  icon: React.ElementType;
  isExpanded: boolean;
  onToggle: () => void;
}

export function CategoryCard({ category, icon: Icon, isExpanded, onToggle }: CategoryCardProps) {
  return (
    <div className="card p-0 overflow-hidden">
      {/* Category header */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center">
          <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center mr-4">
            <Icon className="w-5 h-5 text-primary-600" />
          </div>
          <div className="text-left">
            <h3 className="font-semibold text-gray-900">{category.name}</h3>
            <p className="text-sm text-gray-500">{category.description}</p>
          </div>
        </div>
        <div className="flex items-center">
          <span className="text-xs text-gray-400 mr-2">
            {category.features.length} feature{category.features.length !== 1 ? 's' : ''}
          </span>
          {isExpanded ? (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronRight className="w-5 h-5 text-gray-400" />
          )}
        </div>
      </button>

      {/* Features list */}
      <div
        className={clsx(
          'transition-all duration-300 ease-in-out overflow-hidden',
          isExpanded ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0'
        )}
      >
        <div className="border-t border-gray-100 p-4 space-y-3">
          {category.features.map((feature) => (
            <FeatureCard key={feature.id} feature={feature} />
          ))}
        </div>
      </div>
    </div>
  );
}
