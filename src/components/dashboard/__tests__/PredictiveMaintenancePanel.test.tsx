import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { PredictiveMaintenancePanel } from '../PredictiveMaintenancePanel';

const mockMachines = [
  {
    id: 'OMAYA-001',
    name: 'Mill 001',
    predictions: {
      failureProbability: 0.85,
      estimatedTimeToFailure: 24,
      confidence: 0.95,
      recommendedAction: 'Schedule immediate maintenance',
      contributingFactors: ['High temp', 'Vibration']
    }
  },
  {
    id: 'OMAYA-002',
    name: 'Mill 002',
    predictions: {
      failureProbability: 0.45,
      estimatedTimeToFailure: 120,
      confidence: 0.88,
      recommendedAction: 'Plan maintenance',
      contributingFactors: ['Tool wear']
    }
  }
];

vi.mock('lucide-react', () => {
  const Icon = () => <div />;
  return {
    Brain: Icon,
    Activity: Icon,
    Clock: Icon,
    AlertTriangle: Icon,
    TrendingUp: Icon,
    ArrowUpRight: Icon,
    ArrowDownRight: Icon,
    Info: Icon,
    BarChart3: Icon,
    Zap: Icon,
    Shield: Icon,
    ChevronRight: Icon,
    ExternalLink: Icon,
  };
});

// Mock UI components
vi.mock('@/components/ui/progress', () => ({
  Progress: () => <div role="progressbar" />
}));

describe('PredictiveMaintenancePanel Component', () => {
  it('renders high risk machines', () => {
    render(<PredictiveMaintenancePanel machines={mockMachines as any} onMachineSelect={() => {}} />);
    expect(screen.getByText('OMAYA-001')).toBeDefined();
    expect(screen.getByText(/85%/)).toBeDefined();
  });

  it('renders contributing factors', () => {
    render(<PredictiveMaintenancePanel machines={mockMachines as any} onMachineSelect={() => {}} />);
    expect(screen.getByText('High temp')).toBeDefined();
    expect(screen.getByText('Vibration')).toBeDefined();
  });
});
