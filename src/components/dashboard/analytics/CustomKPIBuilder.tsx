import { useState } from 'react';
import { motion } from 'framer-motion';
import { Plus, Trash2, TrendingUp, Calculator, Filter } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useRealTimeData } from '@/hooks/useRealTimeData';
import { AnalyticsEngine } from '@/lib/analytics-engine';
import type { CustomKPI, AggregationType } from '@/lib/analytics-engine';

interface CustomKPIBuilderProps {
  customKPIs: CustomKPI[];
  onAddKPI: (kpi: CustomKPI) => void;
  onDeleteKPI: (id: string) => void;
}

export function CustomKPIBuilder({ customKPIs, onAddKPI, onDeleteKPI }: CustomKPIBuilderProps) {
  const { machines } = useRealTimeData();
  const [isBuilding, setIsBuilding] = useState(false);
  const [name, setName] = useState('');
  const [metric, setMetric] = useState('telemetry.temperature');
  const [aggregation, setAggregation] = useState<AggregationType>('avg');

  const handleCreate = () => {
    if (!name) return;

    const kpi: CustomKPI = {
      id: `kpi-${Date.now()}`,
      name,
      formula: `${aggregation}(${metric})`,
      metric,
      aggregation,
      filters: [],
      unit: metric.includes('temperature') ? '°C' : undefined,
      color: '#8b5cf6'
    };

    onAddKPI(kpi);
    setIsBuilding(false);
    setName('');
  };

  return (
    <div className="h-full overflow-auto p-6 bg-slate-950">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white">Custom KPI Builder</h2>
            <p className="text-slate-400 mt-1">Create custom metrics for your business needs</p>
          </div>
          <Button
            onClick={() => setIsBuilding(!isBuilding)}
            className="bg-gradient-to-r from-purple-600 to-pink-600"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create KPI
          </Button>
        </div>

        {/* KPI Builder Form */}
        {isBuilding && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card className="bg-slate-900 border-slate-800 p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Calculator className="w-5 h-5 text-purple-400" />
                New Custom KPI
              </h3>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-slate-300">KPI Name</Label>
                  <Input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g., Average Machine Temperature"
                    className="bg-slate-800 border-slate-700"
                  />
                </div>

                <div className="space-y-2">
                  <Label className="text-slate-300">Metric</Label>
                  <Select value={metric} onValueChange={setMetric}>
                    <SelectTrigger className="bg-slate-800 border-slate-700">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="telemetry.temperature">Temperature</SelectItem>
                      <SelectItem value="telemetry.vibration">Vibration</SelectItem>
                      <SelectItem value="telemetry.spindleSpeed">Spindle Speed</SelectItem>
                      <SelectItem value="oee">OEE</SelectItem>
                      <SelectItem value="uptime">Uptime</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label className="text-slate-300">Aggregation</Label>
                  <Select value={aggregation} onValueChange={(v) => setAggregation(v as AggregationType)}>
                    <SelectTrigger className="bg-slate-800 border-slate-700">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="avg">Average</SelectItem>
                      <SelectItem value="sum">Sum</SelectItem>
                      <SelectItem value="min">Minimum</SelectItem>
                      <SelectItem value="max">Maximum</SelectItem>
                      <SelectItem value="count">Count</SelectItem>
                      <SelectItem value="median">Median</SelectItem>
                      <SelectItem value="stddev">Standard Deviation</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2 flex items-end">
                  <div className="flex gap-2 w-full">
                    <Button
                      onClick={handleCreate}
                      disabled={!name}
                      className="flex-1 bg-purple-600 hover:bg-purple-700"
                    >
                      Create
                    </Button>
                    <Button
                      onClick={() => setIsBuilding(false)}
                      variant="outline"
                      className="flex-1"
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>
        )}

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {customKPIs.map((kpi, index) => {
            const value = AnalyticsEngine.calculateKPI(kpi, machines);
            
            return (
              <motion.div
                key={kpi.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card className="bg-slate-900 border-slate-800 p-5 hover:border-purple-500/50 transition-all group">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="p-2 rounded-lg bg-purple-500/20">
                        <TrendingUp className="w-4 h-4 text-purple-400" />
                      </div>
                      <div>
                        <h3 className="font-medium text-white text-sm">{kpi.name}</h3>
                        <p className="text-xs text-slate-400">{kpi.formula}</p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={() => onDeleteKPI(kpi.id)}
                    >
                      <Trash2 className="w-3.5 h-3.5 text-red-400" />
                    </Button>
                  </div>

                  <div className="flex items-end justify-between">
                    <div>
                      <div className="text-3xl font-bold text-white">
                        {value.toFixed(1)}
                        {kpi.unit && <span className="text-xl text-slate-400 ml-1">{kpi.unit}</span>}
                      </div>
                      {kpi.target && (
                        <div className="text-xs text-slate-400 mt-1">
                          Target: {kpi.target}{kpi.unit}
                        </div>
                      )}
                    </div>

                    {kpi.filters.length > 0 && (
                      <Badge variant="outline" className="text-xs">
                        <Filter className="w-3 h-3 mr-1" />
                        {kpi.filters.length}
                      </Badge>
                    )}
                  </div>

                  {kpi.target && (
                    <div className="mt-3 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-purple-600 to-pink-600"
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(100, (value / kpi.target) * 100)}%` }}
                        transition={{ duration: 1, ease: 'easeOut' }}
                      />
                    </div>
                  )}
                </Card>
              </motion.div>
            );
          })}
        </div>

        {customKPIs.length === 0 && !isBuilding && (
          <div className="text-center py-12">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-800 mb-4">
              <Calculator className="w-8 h-8 text-slate-400" />
            </div>
            <h3 className="text-lg font-medium text-slate-300 mb-2">No Custom KPIs Yet</h3>
            <p className="text-sm text-slate-500">Click "Create KPI" to build your first metric</p>
          </div>
        )}
      </div>
    </div>
  );
}
