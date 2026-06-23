import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ToolWearTracker } from '../ToolWearTracker';

const mockTools = [
  { id: 'T1', name: 'Drill 1', machineName: 'M1', wearPercentage: 85, estimatedLifeRemaining: 10, replacementCost: 200, downtimeImpact: 30 },
  { id: 'T2', name: 'Mill 2', machineName: 'M2', wearPercentage: 20, estimatedLifeRemaining: 150, replacementCost: 500, downtimeImpact: 45 },
];

vi.mock('lucide-react', () => {
  const Icon = () => <div />;
  return {
    Wrench: Icon,
    AlertTriangle: Icon,
    TrendingUp: Icon,
    Clock: Icon,
    CheckCircle: Icon,
    DollarSign: Icon,
    Calendar: Icon,
    ChevronRight: Icon,
    Filter: Icon,
  };
});

// Mock UI components
vi.mock('@/components/ui/progress', () => ({
  Progress: () => <div role="progressbar" />
}));

describe('ToolWearTracker Component', () => {
  it('renders critical wear tools', () => {
    render(<ToolWearTracker tools={mockTools as any} />);
    expect(screen.getByText('Drill 1')).toBeDefined();
    expect(screen.getByText(/85%/)).toBeDefined();
  });

  it('renders normal wear tools', () => {
    render(<ToolWearTracker tools={mockTools as any} />);
    expect(screen.getByText('Mill 2')).toBeDefined();
    expect(screen.getByText(/20%/)).toBeDefined();
  });
});
