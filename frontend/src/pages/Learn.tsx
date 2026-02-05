import { useState } from 'react';
import { Search, Rocket, FileText, Users, MessageSquare, Activity, Sparkles } from 'lucide-react';
import { FEATURE_CATEGORIES } from '../config/tours';
import { CategoryCard } from '../components/learn/CategoryCard';

// Icon mapping for categories
const iconMap: Record<string, React.ElementType> = {
  Rocket,
  FileText,
  Users,
  MessageSquare,
  Activity,
  Sparkles,
};

export function Learn() {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);

  // Filter categories and features based on search
  const filteredCategories = FEATURE_CATEGORIES.map((category) => {
    const filteredFeatures = category.features.filter(
      (feature) =>
        feature.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        feature.description.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return {
      ...category,
      features: filteredFeatures,
    };
  }).filter(
    (category) =>
      category.features.length > 0 ||
      category.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      category.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleToggleCategory = (categoryId: string) => {
    setExpandedCategory(expandedCategory === categoryId ? null : categoryId);
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Features Guide</h1>
        <p className="text-gray-600 mt-1">
          Learn how to use Jobezie to supercharge your job search
        </p>
      </div>

      {/* Search */}
      <div className="relative mb-8">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search features..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="input pl-10"
        />
      </div>

      {/* Categories */}
      <div className="space-y-4">
        {filteredCategories.length > 0 ? (
          filteredCategories.map((category) => (
            <CategoryCard
              key={category.id}
              category={category}
              icon={iconMap[category.icon] || Sparkles}
              isExpanded={expandedCategory === category.id || searchQuery.length > 0}
              onToggle={() => handleToggleCategory(category.id)}
            />
          ))
        ) : (
          <div className="text-center py-12 text-gray-500">
            <Search className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>No features found matching "{searchQuery}"</p>
            <button
              onClick={() => setSearchQuery('')}
              className="text-primary-600 hover:text-primary-700 mt-2"
            >
              Clear search
            </button>
          </div>
        )}
      </div>

      {/* Help footer */}
      <div className="mt-12 p-6 bg-gray-50 rounded-xl text-center">
        <p className="text-gray-600">
          Need more help?{' '}
          <a
            href="mailto:support@jobezie.com"
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            Contact Support
          </a>
        </p>
      </div>
    </div>
  );
}
