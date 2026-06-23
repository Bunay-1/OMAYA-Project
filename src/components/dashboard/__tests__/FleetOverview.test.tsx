import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { FleetOverview } from '../FleetOverview';

// Mock machines
const mockMachines = [
  { id: 'OMAYA-001', name: 'Mill 001', zone: 'Zone A', status: 'operational', temperature: 60, vibration: 1.2, spindleSpeed: 10000, toolWear: 20, uptime: 98 },
  { id: 'OMAYA-002', name: 'Mill 002', zone: 'Zone B', status: 'warning', temperature: 75, vibration: 2.5, spindleSpeed: 9000, toolWear: 85, uptime: 92 },
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
    render(<FleetOverview machines={mockMachines} onMachineClick={() => {}} />);
    expect(screen.getAllByText(/OMAYA-001/)).toBeDefined();
    expect(screen.getAllByText(/OMAYA-002/)).toBeDefined();
  });

  it('renders zone info', () => {
    render(<FleetOverview machines={mockMachines} onMachineClick={() => {}} />);
    // Zones appear in the dropdown and in the machine cards (mocked hover/hidden)
    expect(screen.getAllByText('Zone A')).toBeDefined();
    expect(screen.getAllByText('Zone B')).toBeDefined();
  });
});
