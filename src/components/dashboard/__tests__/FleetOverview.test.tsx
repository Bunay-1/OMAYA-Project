import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { FleetOverview } from '../FleetOverview';

import type { OmayaMachine } from '@/types/omaya';

// Mock machines
const mockMachines: OmayaMachine[] = [
  {
    id: 'OMAYA-001',
    name: 'Mill 001',
    zone: 'Zone A',
    status: 'operational',
    temperature: 60,
    vibration: 1.2,
    spindleSpeed: 10000,
    toolWear: 20,
    uptime: 98,
    cycleTime: 120,
    lastMaintenance: '2024-01-01',
    nextMaintenance: '2024-02-01',
    errorLogs: [],
    predictions: {
      failureProbability: 0.1,
      estimatedTimeToFailure: 100,
      recommendedAction: 'None',
      confidence: 0.9,
      contributingFactors: []
    }
  },
  {
    id: 'OMAYA-002',
    name: 'Mill 002',
    zone: 'Zone B',
    status: 'warning',
    temperature: 75,
    vibration: 2.5,
    spindleSpeed: 9000,
    toolWear: 85,
    uptime: 92,
    cycleTime: 150,
    lastMaintenance: '2024-01-15',
    nextMaintenance: '2024-02-15',
    errorLogs: [],
    predictions: {
      failureProbability: 0.4,
      estimatedTimeToFailure: 50,
      recommendedAction: 'Inspect spindle',
      confidence: 0.85,
      contributingFactors: ['Vibration']
    }
  },
];

vi.mock('lucide-react', () => {
  const Icon = () => <div />;
  return {
    Search: Icon,
    Filter: Icon,
    LayoutGrid: Icon,
    List: Icon,
    Cpu: Icon,
    AlertTriangle: Icon,
    Activity: Icon,
    Settings: Icon,
    ChevronRight: Icon,
    Clock: Icon,
    Thermometer: Icon,
    Zap: Icon,
    ArrowUpRight: Icon,
    ArrowDownRight: Icon,
    CheckCircle: Icon,
    XCircle: Icon,
    MapPin: Icon,
    Grid3X3: Icon,
  };
});

describe('FleetOverview Component', () => {
  it('renders list of machines', () => {
    render(<FleetOverview machines={mockMachines} onMachineSelect={() => {}} updatedMachineIds={new Set()} isLive={true} onToggleLive={() => {}} />);
    expect(screen.getAllByText(/OMAYA-001/)).toBeDefined();
    expect(screen.getAllByText(/OMAYA-002/)).toBeDefined();
  });

  it('renders zone info', () => {
    render(<FleetOverview machines={mockMachines} onMachineSelect={() => {}} updatedMachineIds={new Set()} isLive={true} onToggleLive={() => {}} />);
    // Zones appear in the dropdown and in the machine cards (mocked hover/hidden)
    expect(screen.getAllByText('Zone A')).toBeDefined();
    expect(screen.getAllByText('Zone B')).toBeDefined();
  });
});
