import { motion } from 'framer-motion';
import { TrendingUp, Target, Clock, AlertTriangle } from 'lucide-react';
import type { ProductionForecast } from '@/types/omaya';
import { cn } from '@/lib/utils';

interface ProductionForecastChartProps {
  forecasts: ProductionForecast[];
}

export function ProductionForecastChart({ forecasts }: ProductionForecastChartProps) {
  const maxValue = Math.max(...forecasts.flatMap(f => [f.planned, f.predicted]));
  
  const totalPlanned = forecasts.reduce((sum, f) => sum + f.planned, 0);
  const totalPredicted = forecasts.reduce((sum, f) => sum + f.predicted, 0);
  const totalDowntime = forecasts.reduce((sum, f) => sum + f.predictedDowntime, 0);
  const avgConfidence = forecasts.reduce((sum, f) => sum + f.confidence, 0) / forecasts.length;
  
  const variance = ((totalPredicted - totalPlanned) / totalPlanned * 100).toFixed(1);
  const isPositive = totalPredicted >= totalPlanned;

  return (
    <div className="glass-panel p-6 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#00ff88]/10 border border-[#00ff88]/30 flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-[#00ff88]" />
          </div>
          <div>
            <h3 className="text-lg font-display font-bold text-white">Production Forecast</h3>
            <p className="text-xs text-gray-400">14-day AI prediction</p>
          </div>
        </div>
        <div className={cn(
          "px-3 py-1.5 rounded-full text-xs font-medium",
          isPositive ? "bg-[#00ff88]/10 text-[#00ff88]" : "bg-[#ff3366]/10 text-[#ff3366]"
        )}>
          {isPositive ? '+' : ''}{variance}% vs target
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="glass-panel p-3">
          <div className="flex items-center gap-2 mb-1">
            <Target className="w-3 h-3 text-gray-500" />
            <span className="text-[10px] text-gray-400 uppercase">Planned</span>
          </div>
          <p className="text-xl font-display font-bold text-white">{totalPlanned.toLocaleString()}</p>
        </div>
        <div className="glass-panel p-3">
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="w-3 h-3 text-[#00d9ff]" />
            <span className="text-[10px] text-gray-400 uppercase">Predicted</span>
          </div>
          <p className={cn(
            "text-xl font-display font-bold",
            isPositive ? "text-[#00ff88]" : "text-[#ff3366]"
          )}>
            {totalPredicted.toLocaleString()}
          </p>
        </div>
        <div className="glass-panel p-3">
          <div className="flex items-center gap-2 mb-1">
            <Clock className="w-3 h-3 text-[#ffaa00]" />
            <span className="text-[10px] text-gray-400 uppercase">Downtime</span>
          </div>
          <p className="text-xl font-display font-bold text-[#ffaa00]">{totalDowntime}m</p>
        </div>
        <div className="glass-panel p-3">
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="w-3 h-3 text-[#00d9ff]" />
            <span className="text-[10px] text-gray-400 uppercase">Confidence</span>
          </div>
          <p className="text-xl font-display font-bold text-[#00d9ff]">{(avgConfidence * 100).toFixed(0)}%</p>
        </div>
      </div>

      {/* Chart */}
      <div className="flex-1 flex flex-col">
        {/* Legend */}
        <div className="flex items-center gap-6 mb-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#00d9ff]" />
            <span className="text-xs text-gray-400">Planned</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#00ff88]" />
            <span className="text-xs text-gray-400">Predicted</span>
          </div>
        </div>

        {/* Bar Chart */}
        <div className="flex-1 flex items-end gap-2">
          {forecasts.map((forecast, index) => {
            const plannedHeight = (forecast.planned / maxValue) * 100;
            const predictedHeight = (forecast.predicted / maxValue) * 100;
            const date = new Date(forecast.date);
            const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
            const dayNum = date.getDate();
            
            return (
              <motion.div
                key={forecast.date}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className="flex-1 flex flex-col items-center group"
              >
                {/* Bars */}
                <div className="w-full flex gap-1 items-end h-32 mb-2">
                  <div 
                    className="flex-1 bg-[#00d9ff]/30 rounded-t-sm transition-all group-hover:bg-[#00d9ff]/50"
                    style={{ height: `${plannedHeight}%` }}
                  />
                  <div 
                    className={cn(
                      "flex-1 rounded-t-sm transition-all",
                      forecast.predicted >= forecast.planned 
                        ? "bg-[#00ff88]/50 group-hover:bg-[#00ff88]/70" 
                        : "bg-[#ff3366]/50 group-hover:bg-[#ff3366]/70"
                    )}
                    style={{ height: `${predictedHeight}%` }}
                  />
                </div>
                
                {/* Label */}
                <div className="text-center">
                  <p className="text-[10px] text-gray-500">{dayName}</p>
                  <p className="text-xs text-gray-400 font-mono">{dayNum}</p>
                </div>
                
                {/* Tooltip */}
                <div className="absolute bottom-full mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                  <div className="glass-panel-solid px-3 py-2 rounded-lg text-left whitespace-nowrap">
                    <p className="text-xs text-white font-medium mb-1">{date.toLocaleDateString()}</p>
                    <div className="space-y-1">
                      <p className="text-[10px] text-gray-400">
                        Planned: <span className="text-[#00d9ff] font-mono">{forecast.planned}</span>
                      </p>
                      <p className="text-[10px] text-gray-400">
                        Predicted: <span className={cn(
                          "font-mono",
                          forecast.predicted >= forecast.planned ? "text-[#00ff88]" : "text-[#ff3366]"
                        )}>{forecast.predicted}</span>
                      </p>
                      <p className="text-[10px] text-gray-400">
                        Downtime: <span className="text-[#ffaa00] font-mono">{forecast.predictedDowntime}m</span>
                      </p>
                      <p className="text-[10px] text-gray-400">
                        Confidence: <span className="text-[#00d9ff] font-mono">{(forecast.confidence * 100).toFixed(0)}%</span>
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
