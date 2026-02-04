import type { ReactNode } from 'react';

type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'error' | 'info';
type BadgeSize = 'sm' | 'md' | 'lg';

interface BadgeProps {
  children: ReactNode;
  variant?: BadgeVariant;
  size?: BadgeSize;
  dot?: boolean;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'bg-gray-100 text-gray-700',
  primary: 'bg-primary-100 text-primary-700',
  success: 'bg-green-100 text-green-700',
  warning: 'bg-yellow-100 text-yellow-700',
  error: 'bg-red-100 text-red-700',
  info: 'bg-blue-100 text-blue-700',
};

const dotColors: Record<BadgeVariant, string> = {
  default: 'bg-gray-500',
  primary: 'bg-primary-500',
  success: 'bg-green-500',
  warning: 'bg-yellow-500',
  error: 'bg-red-500',
  info: 'bg-blue-500',
};

const sizeClasses: Record<BadgeSize, string> = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-sm',
};

export function Badge({
  children,
  variant = 'default',
  size = 'md',
  dot = false,
  className = '',
}: BadgeProps) {
  return (
    <span
      className={`
        inline-flex items-center gap-1.5 font-medium rounded-full
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
      `}
    >
      {dot && (
        <span
          className={`w-1.5 h-1.5 rounded-full ${dotColors[variant]}`}
        />
      )}
      {children}
    </span>
  );
}

// Pipeline stage badge with predefined colors
interface StageBadgeProps {
  stage: string;
  size?: BadgeSize;
}

const stageVariants: Record<string, BadgeVariant> = {
  new: 'default',
  researching: 'info',
  contacted: 'primary',
  responded: 'success',
  interviewing: 'warning',
  offer: 'success',
  accepted: 'success',
  declined: 'error',
};

export function StageBadge({ stage, size = 'sm' }: StageBadgeProps) {
  const variant = stageVariants[stage.toLowerCase()] || 'default';
  const displayName = stage.charAt(0).toUpperCase() + stage.slice(1).replace('_', ' ');

  return (
    <Badge variant={variant} size={size} dot>
      {displayName}
    </Badge>
  );
}

// Message status badge
interface StatusBadgeProps {
  status: string;
  size?: BadgeSize;
}

const statusVariants: Record<string, BadgeVariant> = {
  draft: 'default',
  ready: 'info',
  sent: 'primary',
  opened: 'warning',
  responded: 'success',
};

export function StatusBadge({ status, size = 'sm' }: StatusBadgeProps) {
  const variant = statusVariants[status.toLowerCase()] || 'default';
  const displayName = status.charAt(0).toUpperCase() + status.slice(1);

  return (
    <Badge variant={variant} size={size}>
      {displayName}
    </Badge>
  );
}
