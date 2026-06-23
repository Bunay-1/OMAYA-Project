import { motion } from 'framer-motion';
import { X, LineChart, BarChart3, PieChart, Activity, Dot, Gauge } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type { AnalyticsWidget, ChartType } from '@/lib/analytics-engine';

interface WidgetLibraryProps {
  onClose: () => void;
  onAddWidget: (widget: AnalyticsWidget) => void;
}

const widgetTemplates: Array<{
  type: ChartType;
  icon: any;
  name: string;
  description: string;
  color: string;
}> = [
  {
    type: 'line',
    icon: LineChart,
    name: 'Time Series',
    description: 'Track metrics over time with line charts',
    color: 'from-blue-500 to-cyan-500'
  },
  {
    type: 'bar',
    icon: BarChart3,
    name: 'Bar Chart',
    description: 'Compare values across categories',
    color: 'from-purple-500 to-pink-500'
  },
  {
    type: 'area',
    icon: Activity,
    name: 'Area Chart',
    description: 'Visualize trends with filled areas',
    color: 'from-green-500 to-emerald-500'
  },
  {
    type: 'pie',
    icon: PieChart,
    name: 'Pie Chart',
    description: 'Show proportions and distributions',
    color: 'from-orange-500 to-red-500'
  },
  {
    type: 'scatter',
    icon: Dot,
    name: 'Scatter Plot',
    description: 'Analyze relationships between variables',
    color: 'from-teal-500 to-cyan-500'
  },
  {
    type: 'gauge',
    icon: Gauge,
    name: 'Gauge',
    description: 'Display single KPI with progress',
    color: 'from-indigo-500 to-purple-500'
  }
];

export function WidgetLibrary({ onClose, onAddWidget }: WidgetLibraryProps) {
  const handleAddWidget = (type: ChartType) => {
    const widget: AnalyticsWidget = {
      id: `widget-${Date.now()}`,
      type,
      title: `New ${type.charAt(0).toUpperCase() + type.slice(1)} Chart`,
      dataSource: 'machines',
      metrics: ['telemetry.temperature'],
      dimensions: ['status'],
      aggregation: 'avg',
      timeRange: '24h',
      filters: [],
      position: { x: 50, y: 50 },
      size: { w: 400, h: 300 }
    };
    onAddWidget(widget);
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="w-full max-w-4xl"
        onClick={(e) => e.stopPropagation()}
      >
        <Card className="bg-slate-900 border-slate-800 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-slate-800">
            <div>
              <h2 className="text-xl font-semibold text-white">Widget Library</h2>
              <p className="text-sm text-slate-400 mt-1">
                Choose a visualization type to add to your dashboard
              </p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="hover:bg-slate-800"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>

          {/* Widget Grid */}
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {widgetTemplates.map((template, index) => {
              const Icon = template.icon;
              return (
                <motion.div
                  key={template.type}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Card
                    className="bg-slate-800/50 border-slate-700 hover:border-purple-500/50 transition-all cursor-pointer group"
                    onClick={() => handleAddWidget(template.type)}
                  >
                    <div className="p-4">
                      <div className={`inline-flex p-3 rounded-lg bg-gradient-to-br ${template.color} mb-3 group-hover:scale-110 transition-transform`}>
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                      <h3 className="font-medium text-white mb-1">{template.name}</h3>
                      <p className="text-sm text-slate-400">{template.description}</p>
                    </div>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </Card>
      </motion.div>
    </motion.div>
  );
}
