import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Sidebar } from '../Sidebar';
import { BrowserRouter } from 'react-router-dom';

// Manual mock all icons used in Sidebar
vi.mock('lucide-react', () => {
  const Icon = () => <div />;
  return {
    LayoutDashboard: Icon,
    Cpu: Icon,
    Activity: Icon,
    BarChart3: Icon,
    Wrench: Icon,
    AlertTriangle: Icon,
    Calendar: Icon,
    TrendingUp: Icon,
    Lightbulb: Icon,
    Database: Icon,
    Globe: Icon,
    Shield: Icon,
    History: Icon,
    FileText: Icon,
    Settings: Icon,
    LogOut: Icon,
    User: Icon,
    ChevronRight: Icon,
    ChevronLeft: Icon,
    Search: Icon,
    Bell: Icon,
    Clock: Icon,
    Zap: Icon,
    Target: Icon,
    Gauge: Icon,
    RefreshCw: Icon,
    Menu: Icon,
    X: Icon,
  };
});

describe('Sidebar Component', () => {
  it('renders brand name', () => {
    render(
      <Sidebar activeTab="overview" onTabChange={() => {}} />
    );
    expect(screen.getByText('OMAYA')).toBeDefined();
  });

  it('renders navigation items', () => {
    render(
      <Sidebar activeTab="overview" onTabChange={() => {}} />
    );
    expect(screen.getByText('Fleet Overview')).toBeDefined();
    expect(screen.getByText('Alerts')).toBeDefined();
  });
});
