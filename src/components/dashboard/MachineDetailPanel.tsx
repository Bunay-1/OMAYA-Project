import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  Thermometer, 
  Activity, 
  Gauge, 
  Clock, 
  Wrench, 
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Brain,
  Calendar
} from 'lucide-react';
import type { OMAYAMachine, MachineStatus } from '@/types/omaya';
import { cn } from '@/lib/utils';
import { Progress } from '@/components/ui/progress';
import { useState } from 'react';
import ExplainableAI from '@/components/ExplainableAI';

interface MachineDetailPanelProps {
  machine: OMAYAMachine | null;
  onClose: () => void;
}

const statusConfig: Record<MachineStatus, { color: string; bg: string; label: string }> = {
  operational: { color: 'text-[#00ff88]', bg: 'bg-[#00ff88]/10', label: 'Operational' },
  warning: { color: 'text-[#ffaa00]', bg: 'bg-[#ffaa00]/10', label: 'Warning' },
  critical: { color: 'text-[#ff3366]', bg: 'bg-[#ff3366]/10', label: 'Critical' },
  offline: { color: 'text-gray-500', bg: 'bg-gray-500/10', label: 'Offline' },
  maintenance: { color: 'text-[#00d9ff]', bg: 'bg-[#00d9ff]/10', label: 'Maintenance' },
};

export function MachineDetailPanel({ machine, onClose }: MachineDetailPanelProps) {
  if (!machine) return null;
  
  const config = statusConfig[machine.status];
  
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, x: 300 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 300 }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        className="w-[400px] h-full glass-panel-solid overflow-hidden flex flex-col"
      >
        {/* Header */}
        <div className="p-6 border-b border-white/10">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className={cn(
                  "w-3 h-3 rounded-full",
                  config.color.replace('text-', 'bg-'),
                  machine.status === 'critical' && "animate-pulse"
                )} />
                <span className={cn("text-sm font-medium", config.color)}>{config.label}</span>
              </div>
              <h2 className="text-2xl font-display font-bold text-white">{machine.id}</h2>
              <p className="text-sm text-gray-400 mt-1">{machine.name}</p>
              <p className="text-xs text-gray-500">{machine.zone}</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto scrollbar-thin p-6 space-y-6">
          {/* Live Metrics */}
          <section>
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-4">Live Metrics</h3>
            <div className="grid grid-cols-2 gap-4">
              <MetricCard
                icon={Gauge}
                label="Spindle Speed"
                value={machine.spindleSpeed.toLocaleString()}
                unit="RPM"
                status={machine.spindleSpeed > 10000 ? 'good' : machine.spindleSpeed > 6000 ? 'warning' : 'critical'}
              />
              <MetricCard
                icon={Thermometer}
                label="Temperature"
                value={machine.temperature}
                unit="°C"
                status={machine.temperature < 50 ? 'good' : machine.temperature < 70 ? 'warning' : 'critical'}
              />
              <MetricCard
                icon={Activity}
                label="Vibration"
                value={machine.vibration.toFixed(2)}
                unit="mm/s"
                status={machine.vibration < 2 ? 'good' : machine.vibration < 5 ? 'warning' : 'critical'}
              />
              <MetricCard
                icon={Clock}
                label="Cycle Time"
                value={machine.cycleTime}
                unit="sec"
                status="neutral"
              />
            </div>
          </section>

          {/* Tool Wear */}
          <section>
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-4">Tool Wear</h3>
            <div className="glass-panel p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Wrench className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-white">Current Tool</span>
                </div>
                <span className={cn(
                  "text-lg font-mono font-bold",
                  machine.toolWear > 80 ? "text-[#ff3366]" : machine.toolWear > 60 ? "text-[#ffaa00]" : "text-[#00ff88]"
                )}>
                  {machine.toolWear}%
                </span>
              </div>
              <Progress 
                value={machine.toolWear} 
                className="h-2 bg-white/10"
              />
              <p className="text-xs text-gray-500 mt-2">
                {machine.toolWear > 80 
                  ? "⚠️ Replacement recommended soon" 
                  : machine.toolWear > 60 
                    ? "Tool wear approaching threshold"
                    : "Tool in good condition"}
              </p>
            </div>
          </section>

          {/* Uptime */}
          <section>
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-4">Uptime</h3>
            <div className="glass-panel p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm text-white">Machine Uptime</span>
                <span className={cn(
                  "text-lg font-mono font-bold",
                  machine.uptime > 90 ? "text-[#00ff88]" : machine.uptime > 75 ? "text-[#ffaa00]" : "text-[#ff3366]"
                )}>
                  {machine.uptime.toFixed(1)}%
                </span>
              </div>
              <Progress 
                value={machine.uptime} 
                className="h-2 bg-white/10"
              />
            </div>
          </section>

          {/* AI Predictions */}
          <section>
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-4 flex items-center gap-2">
              <Brain className="w-4 h-4 text-[#00d9ff]" />
              AI Predictions & Explanation
            </h3>
            <ExplainableAI prediction={machine.predictions} />
          </section>

          {/* Maintenance Schedule */}
          <section>
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-4 flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Maintenance
            </h3>
            <div className="space-y-3">
              <div className="glass-panel p-3 flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-400">Last Maintenance</p>
                  <p className="text-sm text-white font-mono">
                    {new Date(machine.lastMaintenance).toLocaleDateString()}
                  </p>
                </div>
                <TrendingDown className="w-4 h-4 text-gray-500" />
              </div>
              <div className="glass-panel p-3 flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-400">Next Scheduled</p>
                  <p className="text-sm text-white font-mono">
                    {new Date(machine.nextMaintenance).toLocaleDateString()}
                  </p>
                </div>
                <TrendingUp className="w-4 h-4 text-[#00ff88]" />
              </div>
            </div>
          </section>

          {/* Error Logs */}
          {machine.errorLogs.length > 0 && (
            <section>
              <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide mb-4 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-[#ff3366]" />
                Recent Errors
              </h3>
              <div className="space-y-2">
                {machine.errorLogs.map((log) => (
                  <div key={log.id} className="glass-panel p-3 border-l-2 border-[#ff3366]">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-mono text-[#ff3366]">{log.code}</span>
                      <span className="text-xs text-gray-500">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-sm text-white">{log.message}</p>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>

        {/* Actions */}
        <div className="p-4 border-t border-white/10 space-y-2">
          <button className="w-full py-2.5 rounded-lg bg-[#00ff88] text-[#0a0e1a] font-medium hover:bg-[#00ff88]/90 transition-all">
            Schedule Maintenance
          </button>
          <button className="w-full py-2.5 rounded-lg border border-white/20 text-white font-medium hover:bg-white/5 transition-all">
            View Full History
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

interface MetricCardProps {
  icon: React.ElementType;
  label: string;
  value: string | number;
  unit: string;
  status: 'good' | 'warning' | 'critical' | 'neutral';
}

function MetricCard({ icon: Icon, label, value, unit, status }: MetricCardProps) {
  const statusColors = {
    good: 'text-[#00ff88]',
    warning: 'text-[#ffaa00]',
    critical: 'text-[#ff3366]',
    neutral: 'text-white'
  };
  
  return (
    <div className="glass-panel p-3">
      <div className="flex items-center gap-2 mb-2">
        <Icon className="w-4 h-4 text-gray-400" />
        <span className="text-xs text-gray-400">{label}</span>
      </div>
      <div className="flex items-baseline gap-1">
        <span className={cn("text-xl font-mono font-bold", statusColors[status])}>
          {value}
        </span>
        <span className="text-xs text-gray-500">{unit}</span>
      </div>
    </div>
  );
}
