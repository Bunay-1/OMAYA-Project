import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useRealTimeData } from '@/hooks/useRealTimeData';
import { AnalyticsEngine } from '@/lib/analytics-engine';
import type { CorrelationAnalysis } from '@/lib/analytics-engine';

const variables = [
  { key: 'telemetry.temperature', label: 'Temperature' },
  { key: 'telemetry.vibration', label: 'Vibration' },
  { key: 'telemetry.spindleSpeed', label: 'Spindle Speed' },
  { key: 'oee', label: 'OEE' },
  { key: 'uptime', label: 'Uptime' }
];

export function CorrelationMatrix() {
  const { machines } = useRealTimeData();

  const correlations = useMemo(() => {
    const results: CorrelationAnalysis[] = [];
    
    for (let i = 0; i < variables.length; i++) {
      for (let j = i + 1; j < variables.length; j++) {
        const corr = AnalyticsEngine.correlate(
          machines,
          variables[i].key,
          variables[j].key
        );
        results.push(corr);
      }
    }

    return results.sort((a, b) => Math.abs(b.coefficient) - Math.abs(a.coefficient));
  }, [machines]);

  const getCorrelationColor = (coefficient: number) => {
    const abs = Math.abs(coefficient);
    if (abs > 0.7) return 'from-red-500 to-orange-500';
    if (abs > 0.4) return 'from-yellow-500 to-amber-500';
    return 'from-green-500 to-emerald-500';
  };

  const getStrengthIcon = (strength: string) => {
    switch (strength) {
      case 'strong':
        return <AlertTriangle className="w-4 h-4 text-red-400" />;
      case 'moderate':
        return <TrendingUp className="w-4 h-4 text-yellow-400" />;
      case 'weak':
        return <CheckCircle2 className="w-4 h-4 text-green-400" />;
    }
  };

  return (
    <div className="h-full overflow-auto p-6 bg-slate-950">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-bold text-white">Correlation Analysis</h2>
          <p className="text-slate-400 mt-1">
            Discover relationships between machine metrics
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-3 gap-4">
          <Card className="bg-slate-900 border-slate-800 p-4">
            <div className="text-sm text-slate-400 mb-1">Strong Correlations</div>
            <div className="text-2xl font-bold text-white">
              {correlations.filter(c => c.strength === 'strong').length}
            </div>
          </Card>
          <Card className="bg-slate-900 border-slate-800 p-4">
            <div className="text-sm text-slate-400 mb-1">Moderate Correlations</div>
            <div className="text-2xl font-bold text-white">
              {correlations.filter(c => c.strength === 'moderate').length}
            </div>
          </Card>
          <Card className="bg-slate-900 border-slate-800 p-4">
            <div className="text-sm text-slate-400 mb-1">Weak Correlations</div>
            <div className="text-2xl font-bold text-white">
              {correlations.filter(c => c.strength === 'weak').length}
            </div>
          </Card>
        </div>

        {/* Correlation List */}
        <div className="space-y-3">
          {correlations.map((corr, index) => {
            const var1Label = variables.find(v => v.key === corr.variable1)?.label || corr.variable1;
            const var2Label = variables.find(v => v.key === corr.variable2)?.label || corr.variable2;
            const isPositive = corr.coefficient > 0;

            return (
              <motion.div
                key={`${corr.variable1}-${corr.variable2}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card className="bg-slate-900 border-slate-800 p-5 hover:border-purple-500/50 transition-all">
                  <div className="flex items-center gap-4">
                    {/* Strength Indicator */}
                    <div className="flex-shrink-0">
                      {getStrengthIcon(corr.strength)}
                    </div>

                    {/* Variables */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-white">{var1Label}</span>
                        <span className="text-slate-600">↔</span>
                        <span className="font-medium text-white">{var2Label}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge 
                          variant="outline" 
                          className={`text-xs capitalize ${
                            corr.strength === 'strong' ? 'border-red-500/50 text-red-400' :
                            corr.strength === 'moderate' ? 'border-yellow-500/50 text-yellow-400' :
                            'border-green-500/50 text-green-400'
                          }`}
                        >
                          {corr.strength}
                        </Badge>
                        <span className="text-xs text-slate-500">
                          {isPositive ? 'Positive' : 'Negative'} correlation
                        </span>
                      </div>
                    </div>

                    {/* Coefficient */}
                    <div className="text-right flex-shrink-0">
                      <div className="text-2xl font-bold text-white">
                        {corr.coefficient.toFixed(3)}
                      </div>
                      <div className="text-xs text-slate-500">
                        p = {corr.pValue.toFixed(3)}
                      </div>
                    </div>

                    {/* Visual Bar */}
                    <div className="w-32 h-2 bg-slate-800 rounded-full overflow-hidden flex-shrink-0">
                      <motion.div
                        className={`h-full bg-gradient-to-r ${getCorrelationColor(corr.coefficient)}`}
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.abs(corr.coefficient) * 100}%` }}
                        transition={{ duration: 0.8, delay: index * 0.05 }}
                      />
                    </div>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>

        {/* Insights */}
        <Card className="bg-gradient-to-br from-purple-900/20 to-pink-900/20 border-purple-500/30 p-6">
          <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-purple-400" />
            Key Insights
          </h3>
          <ul className="space-y-2 text-sm text-slate-300">
            <li className="flex items-start gap-2">
              <span className="text-purple-400 mt-0.5">•</span>
              <span>Strong correlations indicate variables that move together - monitor these for cascading effects</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-purple-400 mt-0.5">•</span>
              <span>Negative correlations suggest inverse relationships - useful for anomaly detection</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-purple-400 mt-0.5">•</span>
              <span>P-values below 0.05 indicate statistically significant relationships</span>
            </li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
