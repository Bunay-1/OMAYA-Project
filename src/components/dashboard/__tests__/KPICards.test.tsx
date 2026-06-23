import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { KPICards } from '../KPICards';

// Mock KPIData
const mockData = {
  oee: 88.5,
  uptime: 94.2,
  productionActual: 1250,
  productionTarget: 1500,
  defectRate: 1.8,
  mtbf: 240,
  mttr: 4.5,
  energyEfficiency: 92.1,
  throughput: 45
};

// Mock Framer Motion to avoid animation issues in tests
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    span: ({ children, ...props }: any) => <span {...props}>{children}</span>,
  },
}));

describe('KPICards Component', () => {
  it('renders OEE card correctly', () => {
    render(<KPICards data={mockData} />);
    expect(screen.getByText('Overall Equipment Effectiveness')).toBeDefined();
    // Use a more flexible matcher for values that might be formatted
    expect(screen.getByText(/88/)).toBeDefined();
  });

  it('renders Uptime card correctly', () => {
    render(<KPICards data={mockData} />);
    expect(screen.getByText('Fleet Uptime')).toBeDefined();
    expect(screen.getByText(/94/)).toBeDefined();
  });

  it('calculates production percentage correctly', () => {
    render(<KPICards data={mockData} />);
    // 1250/1500 * 100 = 83.333%
    expect(screen.getByText(/83.3%/)).toBeDefined();
  });

  it('renders Defect Rate card correctly', () => {
    render(<KPICards data={mockData} />);
    expect(screen.getByText('Defect Rate')).toBeDefined();
    expect(screen.getByText(/1.80/)).toBeDefined();
  });
});
