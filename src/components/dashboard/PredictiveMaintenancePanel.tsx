import { motion } from 'framer-motion';
import { Brain, Clock, AlertTriangle, TrendingUp, ChevronRight, Zap } from 'lucide-react';
import type { OmayaMachine } from '@/types/omaya';
import { cn } from '@/lib/utils';
import { Progress } from '@/components/ui/progress';

interface PredictiveMaintenancePanelProps {
  machines: OmayaMachine[];
  onMachineSelect: (machine: OmayaMachine) => void;
}

export function PredictiveMaintenancePanel({ machines, onMachineSelect }: PredictiveMaintenancePanelProps) {
  // Sort by failure probability (highest first)
  const sortedMachines = [...machines]
    .filter(m => m.predictions.failureProbability > 0.1)
    .sort((a, b) => b.predictions.failureProbability - a.predictions.failureProbability)
    .slice(0, 10);

  const highRiskCount = sortedMachines.filter(m => m.predictions.failureProbability > 0.5).length;
  const mediumRiskCount = sortedMachines.filter(m => m.predictions.failureProbability > 0.25 && m.predictions.failureProbability <= 0.5).length;

  return (
    <div className="glass-panel p-6 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#00d9ff]/10 border border-[#00d9ff]/30 flex items-center justify-center">
            <Brain className="w-5 h-5 text-[#00d9ff]" />
          </div>
          <div>
            <h3 className="text-lg font-display font-bold text-white">Predictive Maintenance</h3>
            <p className="text-xs text-gray-400">AI-powered failure forecasts</p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#00d9ff]/10 border border-[#00d9ff]/30">
          <Zap className="w-3 h-3 text-[#00d9ff]" />
          <span className="text-xs text-[#00d9ff] font-medium">AI Active</span>
        </div>
      </div>

      {/* Risk Summary */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="glass-panel p-4 border border-[#ff3366]/20">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-[#ff3366]" />
            <span className="text-xs text-gray-400">High Risk</span>
          </div>
          <p className="text-3xl font-display font-bold text-[#ff3366]">{highRiskCount}</p>
          <p className="text-xs text-gray-500 mt-1">Machines need attention</p>
        </div>
        <div className="glass-panel p-4 border border-[#ffaa00]/20">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-4 h-4 text-[#ffaa00]" />
            <span className="text-xs text-gray-400">Medium Risk</span>
          </div>
          <p className="text-3xl font-display font-bold text-[#ffaa00]">{mediumRiskCount}</p>
          <p className="text-xs text-gray-500 mt-1">Monitor closely</p>
        </div>
      </div>

      {/* Predictions List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin space-y-3">
        {sortedMachines.map((machine, index) => (
          <PredictionCard
            key={machine.id}
            machine={machine}
            onClick={() => onMachineSelect(machine)}
            delay={index * 0.05}
          />
        ))}
        
        {sortedMachines.length === 0 && (
          <div className="flex flex-col items-center justify-center py-8 text-gray-500">
            <Brain className="w-8 h-8 mb-2 text-[#00d9ff]/50" />
            <p className="text-sm">No high-risk predictions</p>
            <p className="text-xs text-gray-600">All machines operating normally</p>
          </div>
        )}
      </div>
    </div>
  );
}

interface PredictionCardProps {
  machine: OmayaMachine;
  onClick: () => void;
  delay: number;
}

function PredictionCard({ machine, onClick, delay }: PredictionCardProps) {
  const { predictions } = machine;
  const riskLevel = predictions.failureProbability > 0.5 ? 'high' : predictions.failureProbability > 0.25 ? 'medium' : 'low';
  
  const riskConfig = {
    high: { color: 'text-[#ff3366]', bg: 'bg-[#ff3366]/10', border: 'border-[#ff3366]/30' },
    medium: { color: 'text-[#ffaa00]', bg: 'bg-[#ffaa00]/10', border: 'border-[#ffaa00]/30' },
    low: { color: 'text-[#00ff88]', bg: 'bg-[#00ff88]/10', border: 'border-[#00ff88]/30' }
  };
  
  const config = riskConfig[riskLevel];
  
  return (
    <motion.button
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay }}
      onClick={onClick}
      className={cn(
        "w-full p-4 rounded-xl text-left transition-all hover:-translate-y-1 group",
        config.bg,
        "border",
        config.border
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="text-sm font-medium text-white">{machine.id}</p>
          <p className="text-xs text-gray-400">{machine.name}</p>
        </div>
        <div className="text-right">
          <p className={cn("text-2xl font-mono font-bold", config.color)}>
            {(predictions.failureProbability * 100).toFixed(0)}%
          </p>
          <p className="text-[10px] text-gray-500">Failure Risk</p>
        </div>
      </div>
      
      <div className="mb-3">
        <Progress 
          value={predictions.failureProbability * 100} 
          className="h-1.5 bg-white/10"
        />
      </div>
      
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3 text-gray-500" />
            <span className="text-gray-400">TTF: <span className="text-white font-mono">{predictions.estimatedTimeToFailure}h</span></span>
          </div>
          <div className="flex items-center gap-1">
            <TrendingUp className="w-3 h-3 text-gray-500" />
            <span className="text-gray-400">Conf: <span className="text-[#00d9ff] font-mono">{(predictions.confidence * 100).toFixed(0)}%</span></span>
          </div>
        </div>
        <ChevronRight className="w-4 h-4 text-gray-500 group-hover:text-white transition-colors" />
      </div>
      
      {/* Contributing Factors */}
      <div className="mt-3 pt-3 border-t border-white/10">
        <div className="flex flex-wrap gap-1">
          {predictions.contributingFactors.slice(0, 3).map((factor, i) => (
            <span key={i} className="text-[10px] px-2 py-0.5 rounded-full bg-white/5 text-gray-400">
              {factor}
            </span>
          ))}
        </div>
      </div>
    </motion.button>
  );
}
