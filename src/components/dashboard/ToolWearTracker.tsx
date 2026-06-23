import { useState } from 'react';
import { motion } from 'framer-motion';
import { Wrench, Clock, DollarSign, AlertTriangle, Calendar, ChevronRight, Filter } from 'lucide-react';
import type { Tool } from '@/types/omaya';
import { cn } from '@/lib/utils';
import { Progress } from '@/components/ui/progress';

interface ToolWearTrackerProps {
  tools: Tool[];
}

export function ToolWearTracker({ tools }: ToolWearTrackerProps) {
  const [filter, setFilter] = useState<'all' | 'critical' | 'warning' | 'good'>('all');
  const [sortBy, setSortBy] = useState<'wear' | 'life' | 'cost'>('wear');

  const filteredTools = tools
    .filter(tool => {
      if (filter === 'all') return true;
      if (filter === 'critical') return tool.wearPercentage > 80;
      if (filter === 'warning') return tool.wearPercentage > 60 && tool.wearPercentage <= 80;
      return tool.wearPercentage <= 60;
    })
    .sort((a, b) => {
      if (sortBy === 'wear') return b.wearPercentage - a.wearPercentage;
      if (sortBy === 'life') return a.estimatedLifeRemaining - b.estimatedLifeRemaining;
      return b.replacementCost - a.replacementCost;
    });

  const criticalCount = tools.filter(t => t.wearPercentage > 80).length;
  const warningCount = tools.filter(t => t.wearPercentage > 60 && t.wearPercentage <= 80).length;
  const totalReplacementCost = tools.filter(t => t.wearPercentage > 80).reduce((sum, t) => sum + t.replacementCost, 0);

  return (
    <div className="glass-panel p-6 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#ffaa00]/10 border border-[#ffaa00]/30 flex items-center justify-center">
            <Wrench className="w-5 h-5 text-[#ffaa00]" />
          </div>
          <div>
            <h3 className="text-lg font-display font-bold text-white">Tool Wear Tracker</h3>
            <p className="text-xs text-gray-400">{tools.length} tools monitored</p>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="glass-panel p-3 text-center">
          <p className="text-2xl font-display font-bold text-[#ff3366]">{criticalCount}</p>
          <p className="text-[10px] text-gray-400 uppercase tracking-wide">Critical</p>
        </div>
        <div className="glass-panel p-3 text-center">
          <p className="text-2xl font-display font-bold text-[#ffaa00]">{warningCount}</p>
          <p className="text-[10px] text-gray-400 uppercase tracking-wide">Warning</p>
        </div>
        <div className="glass-panel p-3 text-center">
          <p className="text-lg font-display font-bold text-white">${totalReplacementCost.toLocaleString()}</p>
          <p className="text-[10px] text-gray-400 uppercase tracking-wide">Est. Cost</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex gap-1">
          {(['all', 'critical', 'warning', 'good'] as const).map((f) => (
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
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as 'wear' | 'life' | 'cost')}
          className="bg-[#0a0e1a] border border-white/10 rounded-lg px-2 py-1 text-xs text-white focus:outline-none"
        >
          <option value="wear">Sort by Wear</option>
          <option value="life">Sort by Life</option>
          <option value="cost">Sort by Cost</option>
        </select>
      </div>

      {/* Tools List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin space-y-2">
        {filteredTools.map((tool, index) => (
          <ToolCard key={tool.id} tool={tool} delay={index * 0.03} />
        ))}
      </div>
    </div>
  );
}

interface ToolCardProps {
  tool: Tool;
  delay: number;
}

function ToolCard({ tool, delay }: ToolCardProps) {
  const [expanded, setExpanded] = useState(false);
  
  const wearLevel = tool.wearPercentage > 80 ? 'critical' : tool.wearPercentage > 60 ? 'warning' : 'good';
  const wearConfig = {
    critical: { color: 'text-[#ff3366]', bg: 'bg-[#ff3366]', border: 'border-[#ff3366]/30' },
    warning: { color: 'text-[#ffaa00]', bg: 'bg-[#ffaa00]', border: 'border-[#ffaa00]/30' },
    good: { color: 'text-[#00ff88]', bg: 'bg-[#00ff88]', border: 'border-[#00ff88]/30' }
  };
  
  const config = wearConfig[wearLevel];
  
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2, delay }}
      className={cn(
        "rounded-lg bg-white/5 border overflow-hidden transition-all",
        config.border
      )}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-3 flex items-center gap-3 text-left hover:bg-white/5 transition-all"
      >
        <div className={cn(
          "w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0",
          wearLevel === 'critical' ? 'bg-[#ff3366]/20' : wearLevel === 'warning' ? 'bg-[#ffaa00]/20' : 'bg-[#00ff88]/20'
        )}>
          <Wrench className={cn("w-4 h-4", config.color)} />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <p className="text-sm font-medium text-white truncate">{tool.name}</p>
            {wearLevel === 'critical' && (
              <AlertTriangle className="w-3 h-3 text-[#ff3366]" />
            )}
          </div>
          <p className="text-xs text-gray-400">{tool.machineName}</p>
        </div>
        
        <div className="text-right flex-shrink-0">
          <p className={cn("text-lg font-mono font-bold", config.color)}>
            {tool.wearPercentage}%
          </p>
          <p className="text-[10px] text-gray-500">wear</p>
        </div>
        
        <ChevronRight className={cn(
          "w-4 h-4 text-gray-500 transition-transform",
          expanded && "rotate-90"
        )} />
      </button>
      
      {expanded && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="px-3 pb-3 border-t border-white/10"
        >
          <div className="pt-3 space-y-3">
            {/* Wear Progress */}
            <div>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-gray-400">Wear Level</span>
                <span className={config.color}>{tool.wearPercentage}%</span>
              </div>
              <Progress value={tool.wearPercentage} className="h-1.5 bg-white/10" />
            </div>
            
            {/* Stats */}
            <div className="grid grid-cols-2 gap-3">
              <div className="flex items-center gap-2">
                <Clock className="w-3 h-3 text-gray-500" />
                <div>
                  <p className="text-[10px] text-gray-500">Life Remaining</p>
                  <p className="text-sm text-white font-mono">{tool.estimatedLifeRemaining}h</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <DollarSign className="w-3 h-3 text-gray-500" />
                <div>
                  <p className="text-[10px] text-gray-500">Replacement</p>
                  <p className="text-sm text-white font-mono">${tool.replacementCost}</p>
                </div>
              </div>
            </div>
            
            {/* Downtime Impact */}
            <div className="flex items-center justify-between p-2 rounded-lg bg-white/5">
              <span className="text-xs text-gray-400">Downtime Impact</span>
              <span className="text-sm text-[#ffaa00] font-mono">{tool.downtimeImpact} min</span>
            </div>
            
            {/* Scheduled Replacement */}
            {tool.scheduledReplacement && (
              <div className="flex items-center gap-2 p-2 rounded-lg bg-[#00d9ff]/10 border border-[#00d9ff]/20">
                <Calendar className="w-4 h-4 text-[#00d9ff]" />
                <div>
                  <p className="text-[10px] text-gray-400">Scheduled Replacement</p>
                  <p className="text-xs text-[#00d9ff] font-mono">
                    {new Date(tool.scheduledReplacement).toLocaleDateString()}
                  </p>
                </div>
              </div>
            )}
            
            {/* Action Button */}
            <button className="w-full py-2 rounded-lg bg-[#00ff88] text-[#0a0e1a] text-sm font-medium hover:bg-[#00ff88]/90 transition-all">
              Schedule Replacement
            </button>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
