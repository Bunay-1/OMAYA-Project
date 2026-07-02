import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MachineDetailPanel } from '../MachineDetailPanel';

const mockMachine = {
  id: 'OMAYA-001',
  name: 'Mill 001',
  zone: 'Zone A',
  status: 'operational',
  temperature: 62.5,
  vibration: 1.2,
  spindleSpeed: 10000,
  toolWear: 35,
  uptime: 98.5,
  lastMaintenance: '2024-01-15T10:30:00Z',
  errorLogs: [], // Added missing required property
  predictions: { failureProbability: 0.1, estimatedTimeToFailure: 48, recommendedAction: 'None' }
};

vi.mock('lucide-react', () => {
  const Icon = () => <div />;
  return {
    X: Icon,
    Cpu: Icon,
    Activity: Icon,
    Thermometer: Icon,
    Zap: Icon,
    Clock: Icon,
    Calendar: Icon,
    Shield: Icon,
    AlertTriangle: Icon,
    CheckCircle: Icon,
    Settings: Icon,
    Tool: Icon,
    Gauge: Icon,
    ChevronRight: Icon,
    BarChart3: Icon,
    ArrowUpRight: Icon,
    ArrowDownRight: Icon,
    History: Icon,
    Wrench: Icon,
    Power: Icon,
    Play: Icon,
    Pause: Icon,
    RotateCcw: Icon,
    Brain: Icon,
    Info: Icon,
    AlertCircle: Icon,
    XCircle: Icon,
    TrendingUp: Icon,
    TrendingDown: Icon,
    Minus: Icon,
    Maximize2: Icon,
    ExternalLink: Icon,
    ActivitySquare: Icon,
  };
});

// Mock Recharts to avoid drawing issues in tests
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div style={{width: '100%', height: '100%'}}>{children}</div>,
  LineChart: ({ children }: any) => <div>{children}</div>,
  Line: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
  AreaChart: ({ children }: any) => <div>{children}</div>,
  Area: () => <div />,
}));

describe('MachineDetailPanel Component', () => {
  it('renders machine basic details', () => {
    render(<MachineDetailPanel machine={mockMachine as any} onClose={() => {}} />);
    expect(screen.getByText('OMAYA-001')).toBeDefined();
    expect(screen.getByText('Mill 001')).toBeDefined();
    expect(screen.getByText('Zone A')).toBeDefined();
  });

  it('renders telemetry values', () => {
    render(<MachineDetailPanel machine={mockMachine as any} onClose={() => {}} />);
    expect(screen.getByText(/62.5/)).toBeDefined();
    expect(screen.getAllByText(/1.2/).length).toBeGreaterThan(0);
  });
});
