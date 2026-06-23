import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { AlertsPanel } from '../AlertsPanel';
import type { Alert } from '@/types/omaya';

const mockAlerts: Alert[] = [
  {
    id: '1',
    machineId: 'M1',
    machineName: 'Machine 1',
    severity: 'critical',
    type: 'failure',
    title: 'Critical Failure',
    message: 'Something went wrong',
    timestamp: new Date().toISOString(),
    acknowledged: false
  },
  {
    id: '2',
    machineId: 'M2',
    machineName: 'Machine 2',
    severity: 'warning',
    type: 'wear',
    title: 'High Wear',
    message: 'Tool wear is high',
    timestamp: new Date().toISOString(),
    acknowledged: false
  }
];

// Mock Framer Motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

describe('AlertsPanel Component', () => {
  it('renders all alerts by default', () => {
    render(<AlertsPanel alerts={mockAlerts} />);
    expect(screen.getByText('Critical Failure')).toBeDefined();
    expect(screen.getByText('High Wear')).toBeDefined();
  });

  it('filters alerts when filter button is clicked', () => {
    render(<AlertsPanel alerts={mockAlerts} />);

    const criticalFilter = screen.getByRole('button', { name: 'Critical' });
    fireEvent.click(criticalFilter);

    expect(screen.getByText('Critical Failure')).toBeDefined();
    expect(screen.queryByText('High Wear')).toBeNull();
  });

  it('displays "No alerts" message when empty', () => {
    render(<AlertsPanel alerts={[]} />);
    expect(screen.getByText('No alerts to display')).toBeDefined();
  });

  it('expands alert card on click to show details', () => {
    render(<AlertsPanel alerts={mockAlerts} />);

    const alertCard = screen.getByText('Critical Failure');
    fireEvent.click(alertCard);

    expect(screen.getByText('View Machine')).toBeDefined();
    expect(screen.getByText('Escalate')).toBeDefined();
  });
});
