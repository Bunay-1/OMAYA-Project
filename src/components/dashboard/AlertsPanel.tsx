import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  AlertTriangle, 
  AlertCircle, 
  Info, 
  XCircle, 
  ChevronDown, 
  ChevronUp,
  Bell,
  CheckCircle,
  ExternalLink,
  Clock
} from 'lucide-react';
import type { Alert } from '@/types/omaya';
import { cn } from '@/lib/utils';

interface AlertsPanelProps {
  alerts: Alert[];
  onAlertClick?: (alert: Alert) => void;
  compact?: boolean;
  newAlertIds?: Set<string>;
  onEscalate?: (alert: Alert) => void;
}

const severityConfig = {
  critical: {
    icon: XCircle,
    color: 'text-[#ff3366]',
    bg: 'bg-[#ff3366]/10',
    border: 'border-[#ff3366]/30',
    glow: 'shadow-[0_0_15px_rgba(255,51,102,0.3)]'
  },
  error: {
    icon: AlertCircle,
    color: 'text-[#ff3366]',
    bg: 'bg-[#ff3366]/10',
    border: 'border-[#ff3366]/30',
    glow: ''
  },
  warning: {
    icon: AlertTriangle,
    color: 'text-[#ffaa00]',
    bg: 'bg-[#ffaa00]/10',
    border: 'border-[#ffaa00]/30',
    glow: ''
  },
  info: {
    icon: Info,
    color: 'text-[#00d9ff]',
    bg: 'bg-[#00d9ff]/10',
    border: 'border-[#00d9ff]/30',
    glow: ''
  }
};

export function AlertsPanel({ alerts, onAlertClick, compact = false, newAlertIds = new Set(), onEscalate }: AlertsPanelProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'critical' | 'warning' | 'info'>('all');

  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'all') return true;
    if (filter === 'critical') return alert.severity === 'critical' || alert.severity === 'error';
    return alert.severity === filter;
  });

  const criticalCount = alerts.filter(a => a.severity === 'critical' || a.severity === 'error').length;
  const warningCount = alerts.filter(a => a.severity === 'warning').length;

  return (
    <div className={cn("glass-panel flex flex-col", compact ? "p-4" : "p-6")}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Bell className="w-5 h-5 text-white" />
            {criticalCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-[#ff3366] text-[10px] font-bold flex items-center justify-center animate-pulse">
                {criticalCount}
              </span>
            )}
          </div>
          <div>
            <h3 className="text-lg font-display font-bold text-white">Alerts</h3>
            {!compact && (
              <p className="text-xs text-gray-400">{alerts.length} active alerts</p>
            )}
          </div>
        </div>
        
        {!compact && (
          <div className="flex gap-1">
            {(['all', 'critical', 'warning', 'info'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={cn(
                  "px-3 py-1 rounded-lg text-xs font-medium transition-all",
                  filter === f 
                    ? "bg-white/10 text-white" 
                    : "text-gray-500 hover:text-white"
                )}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Alert Stats */}
      {!compact && (
        <div className="flex gap-4 mb-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#ff3366]" />
            <span className="text-xs text-gray-400">Critical: <span className="text-white font-mono">{criticalCount}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#ffaa00]" />
            <span className="text-xs text-gray-400">Warning: <span className="text-white font-mono">{warningCount}</span></span>
          </div>
        </div>
      )}

      {/* Alerts List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin space-y-2">
        <AnimatePresence mode="popLayout">
          {filteredAlerts.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center py-8 text-gray-500"
            >
              <CheckCircle className="w-8 h-8 mb-2 text-[#00ff88]" />
              <p className="text-sm">No alerts to display</p>
            </motion.div>
          ) : (
            filteredAlerts.map((alert, index) => (
              <AlertCard
                key={alert.id}
                alert={alert}
                isExpanded={expandedId === alert.id}
                isNew={newAlertIds.has(alert.id)}
                onToggle={() => setExpandedId(expandedId === alert.id ? null : alert.id)}
                onClick={() => onAlertClick?.(alert)}
                onEscalate={() => onEscalate?.(alert)}
                delay={index * 0.05}
                compact={compact}
              />
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

interface AlertCardProps {
  alert: Alert;
  isExpanded: boolean;
  isNew?: boolean;
  onToggle: () => void;
  onClick?: () => void;
  onEscalate?: () => void;
  delay: number;
  compact: boolean;
}

function AlertCard({ alert, isExpanded, isNew = false, onToggle, onClick, onEscalate, delay, compact }: AlertCardProps) {
  const config = severityConfig[alert.severity];
  const Icon = config.icon;
  
  const timeAgo = getTimeAgo(new Date(alert.timestamp));
  
  return (
    <motion.div
      initial={{ opacity: 0, x: isNew ? 100 : 20, scale: isNew ? 0.9 : 1 }}
      animate={{ 
        opacity: 1, 
        x: 0, 
        scale: 1,
        boxShadow: isNew ? '0 0 20px rgba(0, 217, 255, 0.5)' : undefined
      }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ 
        duration: isNew ? 0.4 : 0.2, 
        delay: isNew ? 0 : delay,
        type: isNew ? 'spring' : 'tween',
        stiffness: 200
      }}
      className={cn(
        "rounded-lg border overflow-hidden transition-all",
        config.bg,
        config.border,
        alert.severity === 'critical' && config.glow,
        alert.severity === 'critical' && "animate-pulse-slow",
        isNew && "ring-2 ring-[#00d9ff] ring-opacity-50"
      )}
    >
      <button
        onClick={onToggle}
        className="w-full p-3 flex items-start gap-3 text-left"
      >
        <motion.div
          animate={isNew ? { rotate: [0, -10, 10, -10, 0] } : {}}
          transition={{ duration: 0.5 }}
        >
          <Icon className={cn("w-5 h-5 flex-shrink-0 mt-0.5", config.color)} />
        </motion.div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={cn("text-sm font-medium", config.color)}>{alert.title}</span>
            {isNew && (
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-[#00d9ff]/20 text-[#00d9ff] animate-pulse">
                NEW
              </span>
            )}
            {alert.acknowledged && (
              <CheckCircle className="w-3 h-3 text-[#00ff88]" />
            )}
          </div>
          {!compact && (
            <p className="text-xs text-gray-400 line-clamp-2">{alert.message}</p>
          )}
          <div className="flex items-center gap-2 mt-2">
            <Clock className="w-3 h-3 text-gray-500" />
            <span className="text-[10px] text-gray-500 font-mono">{timeAgo}</span>
            <span className="text-[10px] text-gray-600">•</span>
            <span className="text-[10px] text-gray-500">{alert.machineName}</span>
          </div>
        </div>
        {!compact && (
          isExpanded ? (
            <ChevronUp className="w-4 h-4 text-gray-500" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-500" />
          )
        )}
      </button>
      
      <AnimatePresence>
        {isExpanded && !compact && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="border-t border-white/10"
          >
            <div className="p-4 space-y-4">
              {alert.rootCause && (
                <div>
                  <p className="text-xs text-gray-400 mb-1">Root Cause Analysis</p>
                  <p className="text-sm text-white">{alert.rootCause}</p>
                </div>
              )}
              
              {alert.recommendedActions && alert.recommendedActions.length > 0 && (
                <div>
                  <p className="text-xs text-gray-400 mb-2">Recommended Actions</p>
                  <ul className="space-y-1">
                    {alert.recommendedActions.map((action, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-white">
                        <span className="text-[#00d9ff]">•</span>
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              <div className="flex gap-2 pt-2">
                <button 
                  onClick={onClick}
                  className="flex-1 py-2 rounded-lg bg-[#00ff88] text-[#0a0e1a] text-sm font-medium hover:bg-[#00ff88]/90 transition-all flex items-center justify-center gap-2"
                >
                  <ExternalLink className="w-4 h-4" />
                  View Machine
                </button>
                <button 
                  onClick={onEscalate}
                  className="px-4 py-2 rounded-lg border border-[#ff3366]/50 text-[#ff3366] text-sm font-medium hover:bg-[#ff3366]/10 transition-all"
                >
                  Escalate
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function getTimeAgo(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}
