interface ScoreCircleProps {
  score: number;
  maxScore?: number;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showLabel?: boolean;
  label?: string;
  className?: string;
}

const sizeConfig = {
  sm: { size: 48, stroke: 4, fontSize: 'text-sm', labelSize: 'text-xs' },
  md: { size: 64, stroke: 5, fontSize: 'text-lg', labelSize: 'text-xs' },
  lg: { size: 96, stroke: 6, fontSize: 'text-2xl', labelSize: 'text-sm' },
  xl: { size: 128, stroke: 8, fontSize: 'text-4xl', labelSize: 'text-sm' },
};

export function ScoreCircle({
  score,
  maxScore = 100,
  size = 'md',
  showLabel = false,
  label,
  className = '',
}: ScoreCircleProps) {
  const config = sizeConfig[size];
  const percentage = Math.min((score / maxScore) * 100, 100);
  const radius = (config.size - config.stroke) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const getColor = (pct: number): string => {
    if (pct >= 80) return 'text-green-500';
    if (pct >= 60) return 'text-blue-500';
    if (pct >= 40) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getTrackColor = (pct: number): string => {
    if (pct >= 80) return 'text-green-100';
    if (pct >= 60) return 'text-blue-100';
    if (pct >= 40) return 'text-yellow-100';
    return 'text-red-100';
  };

  return (
    <div className={`inline-flex flex-col items-center ${className}`}>
      <div className="relative" style={{ width: config.size, height: config.size }}>
        {/* Background circle */}
        <svg
          className="absolute inset-0"
          width={config.size}
          height={config.size}
        >
          <circle
            className={getTrackColor(percentage)}
            strokeWidth={config.stroke}
            stroke="currentColor"
            fill="transparent"
            r={radius}
            cx={config.size / 2}
            cy={config.size / 2}
          />
        </svg>

        {/* Progress circle */}
        <svg
          className="absolute inset-0 -rotate-90"
          width={config.size}
          height={config.size}
        >
          <circle
            className={`${getColor(percentage)} transition-all duration-500 ease-out`}
            strokeWidth={config.stroke}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            stroke="currentColor"
            fill="transparent"
            r={radius}
            cx={config.size / 2}
            cy={config.size / 2}
          />
        </svg>

        {/* Score text */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`font-bold ${getColor(percentage)} ${config.fontSize}`}>
            {Math.round(score)}
          </span>
        </div>
      </div>

      {showLabel && label && (
        <span className={`mt-2 text-gray-600 ${config.labelSize}`}>{label}</span>
      )}
    </div>
  );
}

// Progress bar variant
interface ScoreBarProps {
  score: number;
  maxScore?: number;
  showValue?: boolean;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const barSizeClasses = {
  sm: 'h-1.5',
  md: 'h-2',
  lg: 'h-3',
};

export function ScoreBar({
  score,
  maxScore = 100,
  showValue = true,
  label,
  size = 'md',
  className = '',
}: ScoreBarProps) {
  const percentage = Math.min((score / maxScore) * 100, 100);

  const getBarColor = (pct: number): string => {
    if (pct >= 80) return 'bg-green-500';
    if (pct >= 60) return 'bg-blue-500';
    if (pct >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getBgColor = (pct: number): string => {
    if (pct >= 80) return 'bg-green-100';
    if (pct >= 60) return 'bg-blue-100';
    if (pct >= 40) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className={className}>
      {(label || showValue) && (
        <div className="flex items-center justify-between mb-1.5">
          {label && <span className="text-sm text-gray-600">{label}</span>}
          {showValue && (
            <span className="text-sm font-medium text-gray-900">
              {Math.round(score)}/{maxScore}
            </span>
          )}
        </div>
      )}
      <div
        className={`${getBgColor(percentage)} ${barSizeClasses[size]} rounded-full overflow-hidden`}
      >
        <div
          className={`${getBarColor(percentage)} ${barSizeClasses[size]} rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
