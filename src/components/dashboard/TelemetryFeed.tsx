import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, AlertTriangle, Info, Settings, Wrench, Pause, Play, Filter } from 'lucide-react';
import type { TelemetryEvent } from '@/types/omaya';
import { cn } from '@/lib/utils';

interface TelemetryFeedProps {
  events: TelemetryEvent[];
  maxItems?: number;
  isLive?: boolean;
  onToggleLive?: () => void;
}

const typeConfig = {
  status_change: { icon: Activity, color: 'text-[#00d9ff]' },
  alert: { icon: AlertTriangle, color: 'text-[#ffaa00]' },
  metric: { icon: Settings, color: 'text-gray-400' },
  maintenance: { icon: Wrench, color: 'text-[#00ff88]' }
};

const severityColors = {
  info: 'border-l-[#00d9ff]',
  warning: 'border-l-[#ffaa00]',
  error: 'border-l-[#ff3366]',
  critical: 'border-l-[#ff3366]'
};

export function TelemetryFeed({ events, maxItems = 20, isLive = true, onToggleLive }: TelemetryFeedProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [filter, setFilter] = useState<TelemetryEvent['type'] | 'all'>('all');
  const [autoScroll, setAutoScroll] = useState(true);
  
  const filteredEvents = events
    .filter(e => filter === 'all' || e.type === filter)
    .slice(0, maxItems);

  // Auto-scroll to top when new events arrive
  useEffect(() => {
    if (autoScroll && scrollRef.current && isLive) {
      scrollRef.current.scrollTop = 0;
    }
  }, [events, autoScroll, isLive]);

  return (
    <div className="glass-panel p-6 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Activity className="w-5 h-5 text-[#00d9ff]" />
            {isLive && (
              <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-[#00ff88] animate-pulse" />
            )}
          </div>
          <div>
            <h3 className="text-lg font-display font-bold text-white">Live Telemetry</h3>
            <p className="text-xs text-gray-400">Real-time event stream</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {/* Filter Dropdown */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as TelemetryEvent['type'] | 'all')}
            className="bg-[#0a0e1a] border border-white/10 rounded-lg px-2 py-1 text-xs text-white focus:outline-none focus:border-[#00ff88]/50"
          >
            <option value="all">All Events</option>
            <option value="status_change">Status</option>
            <option value="alert">Alerts</option>
            <option value="metric">Metrics</option>
            <option value="maintenance">Maintenance</option>
          </select>
          
          {/* Live Toggle */}
          <button
            onClick={onToggleLive}
            className={cn(
              "flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs font-medium transition-all",
              isLive 
                ? "bg-[#00ff88]/20 text-[#00ff88]" 
                : "bg-white/5 text-gray-400"
            )}
          >
            {isLive ? (
              <>
                <span className="w-1.5 h-1.5 rounded-full bg-[#00ff88] animate-pulse" />
                Live
              </>
            ) : (
              <>
                <Pause className="w-3 h-3" />
                Paused
              </>
            )}
          </button>
        </div>
      </div>

      {/* Event Count */}
      <div className="flex items-center justify-between mb-3 px-1">
        <span className="text-xs text-gray-500">
          Showing <span className="text-white font-mono">{filteredEvents.length}</span> events
        </span>
        <span className="text-xs text-gray-500 font-mono">
          {new Date().toLocaleTimeString()}
        </span>
      </div>

      {/* Event Stream */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto scrollbar-thin space-y-2"
        onScroll={(e) => {
          const target = e.target as HTMLDivElement;
          setAutoScroll(target.scrollTop < 10);
        }}
      >
        <AnimatePresence mode="popLayout">
          {filteredEvents.map((event, index) => (
            <TelemetryEventCard 
              key={event.id} 
              event={event} 
              delay={index * 0.02}
              isNew={index === 0 && isLive}
            />
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

interface TelemetryEventCardProps {
  event: TelemetryEvent;
  delay: number;
  isNew?: boolean;
}

function TelemetryEventCard({ event, delay, isNew = false }: TelemetryEventCardProps) {
  const config = typeConfig[event.type];
  const Icon = config.icon;
  const time = new Date(event.timestamp);
  
  return (
    <motion.div
      initial={{ opacity: 0, x: isNew ? -30 : -20, scale: isNew ? 0.95 : 1 }}
      animate={{ 
        opacity: 1, 
        x: 0, 
        scale: 1,
        backgroundColor: isNew ? 'rgba(0, 217, 255, 0.1)' : undefined
      }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ 
        duration: isNew ? 0.3 : 0.2, 
        delay: isNew ? 0 : delay,
        type: isNew ? 'spring' : 'tween'
      }}
      className={cn(
        "p-3 rounded-lg bg-white/5 border-l-2 hover:bg-white/10 transition-all cursor-pointer",
        severityColors[event.severity],
        isNew && "ring-1 ring-[#00d9ff]/30"
      )}
    >
      <div className="flex items-start gap-3">
        <motion.div
          animate={isNew ? { scale: [1, 1.2, 1] } : {}}
          transition={{ duration: 0.3 }}
        >
          <Icon className={cn("w-4 h-4 mt-0.5 flex-shrink-0", config.color)} />
        </motion.div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono text-[#00d9ff]">{event.machineId}</span>
            <span className="text-[10px] text-gray-600">•</span>
            <span className="text-[10px] text-gray-500">{event.machineName}</span>
            {isNew && (
              <span className="px-1 py-0.5 rounded text-[8px] font-bold bg-[#00d9ff]/20 text-[#00d9ff]">
                NEW
              </span>
            )}
          </div>
          <p className="text-sm text-white line-clamp-1">{event.message}</p>
        </div>
        <span className="text-[10px] text-gray-500 font-mono flex-shrink-0">
          {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
        </span>
      </div>
    </motion.div>
  );
}
