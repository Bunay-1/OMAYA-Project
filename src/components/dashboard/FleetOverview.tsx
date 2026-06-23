import { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Filter, Grid3X3, List, Maximize2, Search, RefreshCw, MapPin } from 'lucide-react';
import type { OMAYAMachine, MachineStatus } from '@/types/omaya';
import { cn } from '@/lib/utils';

interface FleetOverviewProps {
  machines: OMAYAMachine[];
  onMachineSelect: (machine: OMAYAMachine) => void;
  selectedMachineId?: string;
  updatedMachineIds?: Set<string>;
  isLive?: boolean;
  onToggleLive?: () => void;
}

const statusConfig: Record<MachineStatus, { color: string; bg: string; glow: string; label: string }> = {
  operational: { 
    color: 'bg-[#00ff88]', 
    bg: 'bg-[#00ff88]/10', 
    glow: 'shadow-[0_0_10px_rgba(0,255,136,0.5)]',
    label: 'Operational' 
  },
  warning: { 
    color: 'bg-[#ffaa00]', 
    bg: 'bg-[#ffaa00]/10', 
    glow: 'shadow-[0_0_10px_rgba(255,170,0,0.5)]',
    label: 'Warning' 
  },
  critical: { 
    color: 'bg-[#ff3366]', 
    bg: 'bg-[#ff3366]/10', 
    glow: 'shadow-[0_0_10px_rgba(255,51,102,0.5)]',
    label: 'Critical' 
  },
  offline: { 
    color: 'bg-gray-500', 
    bg: 'bg-gray-500/10', 
    glow: '',
    label: 'Offline' 
  },
  maintenance: { 
    color: 'bg-[#00d9ff]', 
    bg: 'bg-[#00d9ff]/10', 
    glow: 'shadow-[0_0_10px_rgba(0,217,255,0.5)]',
    label: 'Maintenance' 
  },
};

const zones = ['All Zones', 'Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E', 'Zone F'];

export function FleetOverview({ machines, onMachineSelect, selectedMachineId, updatedMachineIds = new Set(), isLive = true, onToggleLive }: FleetOverviewProps) {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedZone, setSelectedZone] = useState('All Zones');
  const [selectedStatus, setSelectedStatus] = useState<MachineStatus | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredMachines = useMemo(() => {
    return machines.filter(machine => {
      const zoneMatch = selectedZone === 'All Zones' || machine.zone === selectedZone;
      const statusMatch = selectedStatus === 'all' || machine.status === selectedStatus;
      const searchMatch = searchQuery === '' || 
        machine.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        machine.name.toLowerCase().includes(searchQuery.toLowerCase());
      return zoneMatch && statusMatch && searchMatch;
    });
  }, [machines, selectedZone, selectedStatus, searchQuery]);

  const statusCounts = useMemo(() => {
    const counts: Record<MachineStatus, number> = {
      operational: 0,
      warning: 0,
      critical: 0,
      offline: 0,
      maintenance: 0
    };
    machines.forEach(m => counts[m.status]++);
    return counts;
  }, [machines]);

  return (
    <div className="glass-panel p-6 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <MapPin className="w-5 h-5 text-[#00d9ff]" />
            {isLive && (
              <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-[#00ff88] animate-pulse" />
            )}
          </div>
          <div>
            <h2 className="text-xl font-display font-bold text-white">Fleet Overview</h2>
            <p className="text-sm text-gray-400 mt-1">{machines.length} machines monitored</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {/* Live Toggle */}
          <button
            onClick={onToggleLive}
            className={cn(
              "flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all",
              isLive 
                ? "bg-[#00ff88]/20 text-[#00ff88] border border-[#00ff88]/30" 
                : "bg-white/5 text-gray-400 border border-white/10"
            )}
          >
            <span className={cn("w-2 h-2 rounded-full", isLive ? "bg-[#00ff88] animate-pulse" : "bg-gray-500")} />
            {isLive ? 'Live' : 'Paused'}
          </button>
          <button
            onClick={() => setViewMode('grid')}
            className={cn(
              "p-2 rounded-lg transition-all",
              viewMode === 'grid' ? "bg-[#00ff88]/20 text-[#00ff88]" : "text-gray-400 hover:text-white"
            )}
          >
            <Grid3X3 className="w-5 h-5" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={cn(
              "p-2 rounded-lg transition-all",
              viewMode === 'list' ? "bg-[#00ff88]/20 text-[#00ff88]" : "text-gray-400 hover:text-white"
            )}
          >
            <List className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
        <input
          type="text"
          placeholder="Search machines by ID or name..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-[#0a0e1a] border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#00ff88]/50 transition-colors"
        />
      </div>

      {/* Status Summary */}
      <div className="flex flex-wrap gap-2 mb-4">
        {(Object.entries(statusCounts) as [MachineStatus, number][]).map(([status, count]) => (
          <button
            key={status}
            onClick={() => setSelectedStatus(selectedStatus === status ? 'all' : status)}
            className={cn(
              "flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all",
              selectedStatus === status 
                ? `${statusConfig[status].bg} ${statusConfig[status].color.replace('bg-', 'text-')} border border-current`
                : "bg-white/5 text-gray-400 hover:bg-white/10"
            )}
          >
            <span className={cn("w-2 h-2 rounded-full", statusConfig[status].color)} />
            <span>{statusConfig[status].label}</span>
            <span className="font-mono">{count}</span>
          </button>
        ))}
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 mb-4">
        <Filter className="w-4 h-4 text-gray-500" />
        <select
          value={selectedZone}
          onChange={(e) => setSelectedZone(e.target.value)}
          className="bg-[#0a0e1a] border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-[#00ff88]/50"
        >
          {zones.map(zone => (
            <option key={zone} value={zone}>{zone}</option>
          ))}
        </select>
      </div>

      {/* Machine Grid */}
      <div className="flex-1 overflow-auto scrollbar-thin">
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-8 md:grid-cols-10 lg:grid-cols-12 gap-2">
            <AnimatePresence mode="popLayout">
              {filteredMachines.map((machine, index) => (
                <MachineCell
                  key={machine.id}
                  machine={machine}
                  isSelected={machine.id === selectedMachineId}
                  isUpdated={updatedMachineIds.has(machine.id)}
                  onClick={() => onMachineSelect(machine)}
                  delay={index * 0.01}
                />
              ))}
            </AnimatePresence>
          </div>
        ) : (
          <div className="space-y-2">
            <AnimatePresence mode="popLayout">
              {filteredMachines.map((machine, index) => (
                <MachineRow
                  key={machine.id}
                  machine={machine}
                  isSelected={machine.id === selectedMachineId}
                  isUpdated={updatedMachineIds.has(machine.id)}
                  onClick={() => onMachineSelect(machine)}
                  delay={index * 0.02}
                />
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
}

interface MachineCellProps {
  machine: OMAYAMachine;
  isSelected: boolean;
  isUpdated?: boolean;
  onClick: () => void;
  delay: number;
}

function MachineCell({ machine, isSelected, isUpdated = false, onClick, delay }: MachineCellProps) {
  const config = statusConfig[machine.status];
  
  return (
    <motion.button
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ 
        opacity: 1, 
        scale: isUpdated ? [1, 1.15, 1] : 1,
        transition: { duration: isUpdated ? 0.3 : 0.2, delay: isUpdated ? 0 : delay }
      }}
      exit={{ opacity: 0, scale: 0.8 }}
      whileHover={{ scale: 1.1, y: -4 }}
      onClick={onClick}
      className={cn(
        "aspect-square rounded-lg flex flex-col items-center justify-center p-1 transition-all relative group",
        config.bg,
        isSelected && "ring-2 ring-[#00ff88]",
        isUpdated && "ring-2 ring-[#00d9ff] ring-opacity-50",
        machine.status === 'critical' && "animate-pulse"
      )}
    >
      <motion.div 
        className={cn(
          "w-3 h-3 rounded-full mb-1",
          config.color,
          config.glow
        )}
        animate={isUpdated ? { scale: [1, 1.5, 1] } : {}}
        transition={{ duration: 0.3 }}
      />
      <span className="text-[8px] font-mono text-gray-400 truncate w-full text-center">
        {machine.id.replace('OMAYA-', '')}
      </span>
      
      {/* Tooltip */}
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
        <div className="glass-panel-solid px-3 py-2 rounded-lg text-left whitespace-nowrap">
          <p className="text-xs font-medium text-white">{machine.id}</p>
          <p className="text-[10px] text-gray-400">{machine.zone}</p>
          <p className={cn("text-[10px] font-medium", config.color.replace('bg-', 'text-'))}>
            {config.label}
          </p>
          <div className="mt-1 pt-1 border-t border-white/10">
            <p className="text-[10px] text-gray-400">
              Temp: <span className="text-white">{machine.temperature}°C</span>
            </p>
            <p className="text-[10px] text-gray-400">
              Vibration: <span className="text-white">{machine.vibration.toFixed(1)} mm/s</span>
            </p>
          </div>
        </div>
      </div>
    </motion.button>
  );
}

function MachineRow({ machine, isSelected, isUpdated = false, onClick, delay }: MachineCellProps) {
  const config = statusConfig[machine.status];
  
  return (
    <motion.button
      initial={{ opacity: 0, x: -20 }}
      animate={{ 
        opacity: 1, 
        x: 0,
        backgroundColor: isUpdated ? 'rgba(0, 217, 255, 0.1)' : undefined
      }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.2, delay }}
      onClick={onClick}
      className={cn(
        "w-full flex items-center gap-4 p-3 rounded-lg transition-all",
        config.bg,
        isSelected && "ring-2 ring-[#00ff88]",
        "hover:bg-white/10"
      )}
    >
      <motion.div 
        className={cn(
          "w-3 h-3 rounded-full flex-shrink-0",
          config.color,
          config.glow
        )}
        animate={isUpdated ? { scale: [1, 1.5, 1] } : {}}
        transition={{ duration: 0.3 }}
      />
      <div className="flex-1 text-left">
        <p className="text-sm font-medium text-white">{machine.id}</p>
        <p className="text-xs text-gray-400">{machine.name}</p>
      </div>
      <div className="text-right">
        <p className="text-xs text-gray-400">{machine.zone}</p>
        <p className={cn("text-xs font-medium", config.color.replace('bg-', 'text-'))}>
          {config.label}
        </p>
      </div>
      <div className="text-right">
        <p className="text-xs text-gray-400">Temp</p>
        <p className={cn(
          "text-sm font-mono font-medium",
          machine.temperature > 70 ? "text-[#ff3366]" : machine.temperature > 55 ? "text-[#ffaa00]" : "text-[#00ff88]"
        )}>
          {machine.temperature}°C
        </p>
      </div>
      <div className="text-right">
        <p className="text-xs text-gray-400">Tool Wear</p>
        <p className={cn(
          "text-sm font-mono font-medium",
          machine.toolWear > 80 ? "text-[#ff3366]" : machine.toolWear > 60 ? "text-[#ffaa00]" : "text-[#00ff88]"
        )}>
          {machine.toolWear}%
        </p>
      </div>
      <Maximize2 className="w-4 h-4 text-gray-500" />
    </motion.button>
  );
}
