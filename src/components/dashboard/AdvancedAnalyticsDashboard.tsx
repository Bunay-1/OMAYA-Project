import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus, Save, Download, TrendingUp, Filter, 
  BarChart3, LineChart, PieChart, Activity,
  Grid3x3, Layout, Settings, Trash2, Copy
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CustomKPIBuilder } from './analytics/CustomKPIBuilder';
import { CorrelationMatrix } from './analytics/CorrelationMatrix';
import { WidgetCanvas } from './analytics/WidgetCanvas';
import { WidgetLibrary } from './analytics/WidgetLibrary';
import type { AnalyticsWidget, CustomKPI } from '@/lib/analytics-engine';

export function AdvancedAnalyticsDashboard() {
  const [activeTab, setActiveTab] = useState('canvas');
  const [widgets, setWidgets] = useState<AnalyticsWidget[]>([]);
  const [customKPIs, setCustomKPIs] = useState<CustomKPI[]>([]);
  const [isLibraryOpen, setIsLibraryOpen] = useState(false);
  const [selectedWidget, setSelectedWidget] = useState<string | null>(null);

  const handleAddWidget = useCallback((widget: AnalyticsWidget) => {
    setWidgets(prev => [...prev, widget]);
    setIsLibraryOpen(false);
  }, []);

  const handleUpdateWidget = useCallback((id: string, updates: Partial<AnalyticsWidget>) => {
    setWidgets(prev => prev.map(w => w.id === id ? { ...w, ...updates } : w));
  }, []);

  const handleDeleteWidget = useCallback((id: string) => {
    setWidgets(prev => prev.filter(w => w.id !== id));
    if (selectedWidget === id) setSelectedWidget(null);
  }, [selectedWidget]);

  const handleDuplicateWidget = useCallback((id: string) => {
    const widget = widgets.find(w => w.id === id);
    if (widget) {
      const duplicate: AnalyticsWidget = {
        ...widget,
        id: `widget-${Date.now()}`,
        title: `${widget.title} (Copy)`,
        position: { x: widget.position.x + 20, y: widget.position.y + 20 }
      };
      setWidgets(prev => [...prev, duplicate]);
    }
  }, [widgets]);

  const handleSaveDashboard = () => {
    const dashboard = { widgets, customKPIs };
    localStorage.setItem('analytics-dashboard', JSON.stringify(dashboard));
    // Show toast notification
    console.log('Dashboard saved!');
  };

  const handleExportDashboard = () => {
    const dashboard = { widgets, customKPIs };
    const blob = new Blob([JSON.stringify(dashboard, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics-dashboard-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleAddKPI = useCallback((kpi: CustomKPI) => {
    setCustomKPIs(prev => [...prev, kpi]);
  }, []);

  return (
    <div className="flex flex-col h-full bg-slate-950">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-900/50 backdrop-blur">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500/20 to-pink-500/20">
            <TrendingUp className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">Advanced Analytics</h2>
            <p className="text-xs text-slate-400">Drag-and-drop reports & custom KPIs</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs">
            {widgets.length} Widgets
          </Badge>
          <Badge variant="outline" className="text-xs">
            {customKPIs.length} Custom KPIs
          </Badge>
          
          <div className="h-6 w-px bg-slate-700 mx-2" />

          <Button
            variant="ghost"
            size="sm"
            onClick={handleSaveDashboard}
            className="text-slate-300 hover:text-white"
          >
            <Save className="w-4 h-4 mr-2" />
            Save
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleExportDashboard}
            className="text-slate-300 hover:text-white"
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>

          <Button
            size="sm"
            onClick={() => setIsLibraryOpen(true)}
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Widget
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <div className="px-4 pt-2 border-b border-slate-800">
          <TabsList className="bg-slate-900/50">
            <TabsTrigger value="canvas" className="gap-2">
              <Layout className="w-4 h-4" />
              Canvas
            </TabsTrigger>
            <TabsTrigger value="kpi-builder" className="gap-2">
              <Activity className="w-4 h-4" />
              KPI Builder
            </TabsTrigger>
            <TabsTrigger value="correlation" className="gap-2">
              <Grid3x3 className="w-4 h-4" />
              Correlation
            </TabsTrigger>
          </TabsList>
        </div>

        <div className="flex-1 overflow-auto">
          <TabsContent value="canvas" className="h-full m-0 p-0">
            <WidgetCanvas
              widgets={widgets}
              selectedWidget={selectedWidget}
              onSelectWidget={setSelectedWidget}
              onUpdateWidget={handleUpdateWidget}
              onDeleteWidget={handleDeleteWidget}
              onDuplicateWidget={handleDuplicateWidget}
            />
          </TabsContent>

          <TabsContent value="kpi-builder" className="h-full m-0">
            <CustomKPIBuilder
              customKPIs={customKPIs}
              onAddKPI={handleAddKPI}
              onDeleteKPI={(id) => setCustomKPIs(prev => prev.filter(k => k.id !== id))}
            />
          </TabsContent>

          <TabsContent value="correlation" className="h-full m-0">
            <CorrelationMatrix />
          </TabsContent>
        </div>
      </Tabs>

      {/* Widget Library Modal */}
      <AnimatePresence>
        {isLibraryOpen && (
          <WidgetLibrary
            onClose={() => setIsLibraryOpen(false)}
            onAddWidget={handleAddWidget}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
