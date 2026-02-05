import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge } from './Badge';

describe('Badge', () => {
  it('renders with default variant', () => {
    render(<Badge>Default Badge</Badge>);
    expect(screen.getByText('Default Badge')).toBeInTheDocument();
  });

  it('renders with success variant', () => {
    render(<Badge variant="success">Success</Badge>);
    const badge = screen.getByText('Success');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('bg-green-100');
  });

  it('renders with warning variant', () => {
    render(<Badge variant="warning">Warning</Badge>);
    const badge = screen.getByText('Warning');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('bg-yellow-100');
  });

  it('renders with error variant', () => {
    render(<Badge variant="error">Error</Badge>);
    const badge = screen.getByText('Error');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('bg-red-100');
  });

  it('applies custom className', () => {
    render(<Badge className="custom-class">Custom</Badge>);
    const badge = screen.getByText('Custom');
    expect(badge).toHaveClass('custom-class');
  });
});
