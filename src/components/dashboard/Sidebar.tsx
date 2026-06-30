import { useState } from 'react';
import { 
  LayoutDashboard, 
  Activity, 
  Wrench,
  Camera,
  Database, 
  AlertTriangle, 
  Calendar, 
  BarChart3, 
  Settings, 
  Search,
  ChevronLeft,
  ChevronRight,
  Cpu,
  Shield,
  Globe,
  Lightbulb,
  TrendingUp
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const navItems = [
  { id: 'overview', label: 'Fleet Overview', icon: LayoutDashboard },
  { id: 'machines', label: 'Machines', icon: Cpu },
  { id: 'telemetry', label: 'Live Telemetry', icon: Activity },
  { id: 'predictive', label: 'Predictive AI', icon: BarChart3 },
  { id: 'visual-inspection', label: 'Visual Inspection', icon: Camera },
  { id: 'tools', label: 'Tool Wear', icon: Wrench },
  { id: 'alerts', label: 'Alerts', icon: AlertTriangle },
  { id: 'maintenance', label: 'Maintenance', icon: Calendar },
  { id: 'analytics', label: 'Advanced Analytics', icon: TrendingUp },
  { id: 'explainability', label: 'AI Explainability', icon: Lightbulb },
  { id: 'graphql', label: 'GraphQL Explorer', icon: Database },
  { id: 'audit', label: 'Audit Trail', icon: Shield },
  { id: 'multi-region', label: 'Multi-Region', icon: Globe },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <aside 
      className={cn(
        "h-screen glass-panel-solid flex flex-col transition-all duration-300 relative",
        collapsed ? "w-[72px]" : "w-[240px]"
      )}
    >
      {/* Logo */}
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#00ff88] to-[#00d9ff] flex items-center justify-center glow-green">
            <Cpu className="w-6 h-6 text-[#0a0e1a]" />
          </div>
          {!collapsed && (
            <div className="animate-slide-in">
              <h1 className="font-display font-extrabold text-lg tracking-wide text-white">OMAYA</h1>
              <p className="text-[10px] text-[#00d9ff] font-mono tracking-widest">COMMAND CENTER</p>
            </div>
          )}
        </div>
      </div>

      {/* Search */}
      {!collapsed && (
        <div className="p-4 border-b border-white/10">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Search machines..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#0a0e1a] border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder:text-gray-500 focus:outline-none focus:border-[#00ff88]/50 focus:ring-1 focus:ring-[#00ff88]/20 transition-all"
            />
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto scrollbar-thin">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group",
                isActive 
                  ? "bg-[#00ff88]/10 text-[#00ff88] border border-[#00ff88]/30" 
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              )}
            >
              <Icon className={cn(
                "w-5 h-5 flex-shrink-0 transition-all",
                isActive && "drop-shadow-[0_0_8px_rgba(0,255,136,0.6)]"
              )} />
              {!collapsed && (
                <span className="text-sm font-medium truncate">{item.label}</span>
              )}
              {isActive && !collapsed && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-[#00ff88] animate-pulse" />
              )}
            </button>
          );
        })}
      </nav>

      {/* Status Indicator */}
      {!collapsed && (
        <div className="p-4 border-t border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#00ff88] animate-pulse" />
            <span className="text-xs text-gray-400">System Online</span>
          </div>
          <p className="text-[10px] text-gray-500 mt-1 font-mono">Last sync: 2s ago</p>
        </div>
      )}

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-[#1a1f2e] border border-white/10 flex items-center justify-center text-gray-400 hover:text-white hover:border-[#00ff88]/50 transition-all z-10"
      >
        {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
      </button>
    </aside>
  );
}
