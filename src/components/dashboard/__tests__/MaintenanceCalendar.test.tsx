import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MaintenanceCalendar } from '../MaintenanceCalendar';

vi.mock('lucide-react', () => {
  const Icon = () => <div />;
  return {
    Calendar: Icon,
    ChevronLeft: Icon,
    ChevronRight: Icon,
    Plus: Icon,
    Clock: Icon,
    Tool: Icon,
    AlertTriangle: Icon,
    CheckCircle: Icon,
    Filter: Icon,
    Wrench: Icon,
    CalendarDays: Icon,
    Search: Icon,
    Loader2: Icon,
    AlertCircle: Icon,
    User: Icon,
    DollarSign: Icon,
  };
});

describe('MaintenanceCalendar Component', () => {
  it('renders calendar title', () => {
    render(<MaintenanceCalendar events={[]} />);
    expect(screen.getByText('Maintenance Calendar')).toBeDefined();
  });

  it('renders stats area', () => {
    render(<MaintenanceCalendar events={[]} />);
    expect(screen.getByText('In Progress')).toBeDefined();
    expect(screen.getByText('Completed')).toBeDefined();
    expect(screen.getByText('Overdue')).toBeDefined();
  });
});
