import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Sidebar } from './Sidebar';
import { KPICards, SecondaryKPIs } from './KPICards';
import { FleetOverview } from './FleetOverview';
import { MachineDetailPanel } from './MachineDetailPanel';
import { AlertsPanel } from './AlertsPanel';
import { TelemetryFeed } from './TelemetryFeed';
import { PredictiveMaintenancePanel } from './PredictiveMaintenancePanel';
import { ToolWearTracker } from './ToolWearTracker';
import { GraphQLExplorer } from './GraphQLExplorer';
import { AdvancedAnalyticsDashboard } from './AdvancedAnalyticsDashboard';
import { MaintenanceCalendar } from './MaintenanceCalendar';
import { ProductionForecastChart } from './ProductionForecastChart';
import { VisualInspection } from './VisualInspection';
import RAGDashboard from './RAGDashboard';
import { AuditTrailPanel } from './AuditTrailPanel';
import { MultiRegionDashboard } from './MultiRegionDashboard';
import { AIExplainabilityPanel } from './AIExplainabilityPanel';
import ModelDriftMonitor from '@/components/ModelDriftMonitor';
import DataLakeStats from '@/components/DataLakeStats';
import ExplainableAI from '@/components/ExplainableAI';
import { useRealTimeData } from '@/hooks/useRealTimeData';
import type { OmayaMachine } from '@/types/omaya';

// Lazy load mock data constants
let mockDataConstants: any = {
  mockTools: [],
  mockMaintenanceEvents: [],
  mockProductionForecast: [],
};

const loadMockConstants = async () => {
  const mock = await import('@/data/mockData');
  mockDataConstants = {
    mockTools: mock.mockTools,
    mockMaintenanceEvents: mock.mockMaintenanceEvents,
    mockProductionForecast: mock.mockProductionForecast,
  };
};

export function Dashboard() {
  useEffect(() => {
    // Environment guard: Never use mock data in production
    const isProd = import.meta.env.PROD;
    const useMock = import.meta.env.VITE_USE_MOCK === 'true' && !isProd;

    if (useMock) {
      console.warn('⚠️ Using mock data in development mode');
      loadMockConstants().then(() => setIsLoaded(true));
    } else {
      if (import.meta.env.VITE_USE_MOCK === 'true' && isProd) {
        console.error('❌ CRITICAL: Mock data requested in production! Guard activated.');
      }
      setIsLoaded(true);
    }
  }, []);

  const [activeTab, setActiveTab] = useState('overview');
  const [selectedMachine, setSelectedMachine] = useState<OmayaMachine | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  // Real-time data hook with 3 second refresh
  const {
    machines,
    alerts,
    kpis,
    telemetryEvents,
    isLive,
    newAlertIds,
    updatedMachineIds,
    toggleLive,
  } = useRealTimeData({ refreshInterval: 3000 });

  const handleMachineSelect = (machine: OmayaMachine) => {
    setSelectedMachine(machine);
  };

  const handleCloseDetail = () => {
    setSelectedMachine(null);
  };

  return (
    <div className="flex h-screen bg-[#0a0e1a] overflow-hidden">
      {/* Background Grid */}
      <div className="fixed inset-0 grid-bg pointer-events-none" />
      
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        <div className="flex-1 overflow-y-auto scrollbar-thin p-6">
          {activeTab === 'overview' && (
            <OverviewTab
              isLoaded={isLoaded}
              onMachineSelect={handleMachineSelect}
              selectedMachineId={selectedMachine?.id}
              machines={machines}
              alerts={alerts}
              kpis={kpis}
              telemetryEvents={telemetryEvents}
              isLive={isLive}
              onToggleLive={toggleLive}
              newAlertIds={newAlertIds}
              updatedMachineIds={updatedMachineIds}
            />
          )}
          
          {activeTab === 'machines' && (
            <MachinesTab
              isLoaded={isLoaded}
              onMachineSelect={handleMachineSelect}
              selectedMachineId={selectedMachine?.id}
              machines={machines}
              isLive={isLive}
              onToggleLive={toggleLive}
              updatedMachineIds={updatedMachineIds}
            />
          )}
          
          {activeTab === 'telemetry' && (
            <TelemetryTab 
              isLoaded={isLoaded} 
              telemetryEvents={telemetryEvents}
              isLive={isLive}
              onToggleLive={toggleLive}
            />
          )}
          
          {activeTab === 'predictive' && (
            <PredictiveTab
              isLoaded={isLoaded}
              onMachineSelect={handleMachineSelect}
              machines={machines}
            />
          )}

          {activeTab === 'visual-inspection' && (
            <VisualInspectionTab isLoaded={isLoaded} />
          )}
          
          {activeTab === 'tools' && (
            <ToolsTab isLoaded={isLoaded} />
          )}
          
          {activeTab === 'alerts' && (
            <AlertsTab 
              isLoaded={isLoaded} 
              alerts={alerts}
              newAlertIds={newAlertIds}
            />
          )}
          
          {activeTab === 'maintenance' && (
            <MaintenanceTab isLoaded={isLoaded} />
          )}
          
          {activeTab === 'explainability' && (
            <ExplainabilityTab 
              isLoaded={isLoaded}
              selectedMachine={selectedMachine}
            />
          )}

          {activeTab === 'rag' && (
            <RAGTab isLoaded={isLoaded} />
          )}
          
          {activeTab === 'graphql' && (
            <GraphQLTab isLoaded={isLoaded} />
          )}
          
          {activeTab === 'analytics' && (
            <AnalyticsTab isLoaded={isLoaded} />
          )}
          
          {activeTab === 'audit' && (
            <AuditTab isLoaded={isLoaded} />
          )}
          
          {activeTab === 'multi-region' && (
            <MultiRegionTab isLoaded={isLoaded} />
          )}
          
          {activeTab === 'settings' && (
            <SettingsTab />
          )}
        </div>

        {/* Machine Detail Panel */}
        {selectedMachine && (
          <MachineDetailPanel
            machine={selectedMachine}
            onClose={handleCloseDetail}
          />
        )}
      </main>
    </div>
  );
}

interface TabProps {
  isLoaded: boolean;
  onMachineSelect?: (machine: OmayaMachine) => void;
  selectedMachineId?: string;
  machines?: OmayaMachine[];
  alerts?: import('@/types/omaya').Alert[];
  kpis?: import('@/types/omaya').KPIData;
  telemetryEvents?: import('@/types/omaya').TelemetryEvent[];
  isLive?: boolean;
  onToggleLive?: () => void;
  newAlertIds?: Set<string>;
  updatedMachineIds?: Set<string>;
}

function OverviewTab({ 
  isLoaded, 
  onMachineSelect, 
  selectedMachineId, 
  machines = [], 
  alerts = [], 
  kpis,
  telemetryEvents = [],
  isLive = true,
  onToggleLive,
  newAlertIds = new Set(),
  updatedMachineIds = new Set()
}: TabProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isLoaded ? 1 : 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-display font-extrabold text-white tracking-tight">
              OMAYA Platform
            </h1>
            <p className="text-gray-400 mt-2">
              Real-time monitoring of {machines.length} machines across 6 zones
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${isLive ? 'bg-[#00ff88] animate-pulse' : 'bg-gray-500'}`} />
            <span className="text-sm text-gray-400">{isLive ? 'Live Updates' : 'Paused'}</span>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      {kpis && <KPICards data={kpis} isLive={isLive} />}
      
      {/* Secondary KPIs */}
      {kpis && <SecondaryKPIs data={kpis} />}

      {/* Main Grid */}
      <div className="grid grid-cols-12 gap-6">
        {/* Fleet Overview - Large */}
        <div className="col-span-8 h-[500px]">
          <FleetOverview
            machines={machines}
            onMachineSelect={onMachineSelect!}
            selectedMachineId={selectedMachineId}
            updatedMachineIds={updatedMachineIds}
            isLive={isLive}
            onToggleLive={onToggleLive}
          />
        </div>

        {/* Alerts Panel */}
        <div className="col-span-4 h-[500px]">
          <AlertsPanel 
            alerts={alerts} 
            compact 
            newAlertIds={newAlertIds}
            onEscalate={(alert) => {
              console.log('Escalating alert:', alert);
            }}
          />
        </div>

        {/* Production Forecast */}
        <div className="col-span-8 h-[400px]">
          <ProductionForecastChart forecasts={mockDataConstants.mockProductionForecast} />
        </div>

        {/* Telemetry Feed */}
        <div className="col-span-4 h-[400px]">
          <TelemetryFeed 
            events={telemetryEvents} 
            maxItems={15} 
            isLive={isLive}
            onToggleLive={onToggleLive}
          />
        </div>
      </div>
    </motion.div>
  );
}

function RAGTab({ isLoaded }: { isLoaded: boolean }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isLoaded ? 1 : 0 }}
      transition={{ duration: 0.5 }}
      className="h-full"
    >
      <RAGDashboard />
    </motion.div>
  );
}

function VisualInspectionTab({ isLoaded }: { isLoaded: boolean }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isLoaded ? 1 : 0 }}
      transition={{ duration: 0.5 }}
      className="h-full"
    >
      <VisualInspection />
    </motion.div>
  );
}

function MachinesTab({ isLoaded, onMachineSelect, selectedMachineId, machines = [], isLive, onToggleLive, updatedMachineIds = new Set() }: TabProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isLoaded ? 1 : 0 }}
      transition={{ duration: 0.5 }}
      className="h-full"
    >
      <div className="mb-6">
        <h1 className="text-2xl font-display font-bold text-white">Machine Fleet</h1>
        <p className="text-gray-400 mt-1">Detailed view of all OMAYA machines</p>
      </div>
      <div className="h-[calc(100%-80px)]">
        <FleetOverview
          machines={machines}
          onMachineSelect={onMachineSelect!}
          selectedMachineId={selectedMachineId}
          updatedMachineIds={updatedMachineIds}
          isLive={isLive}
          onToggleLive={onToggleLive}
        />
      </div>
    </motion.div>
  );
}

function TelemetryTab({ isLoaded, telemetryEvents = [], isLive, onToggleLive }: TabProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isLoaded ? 1 : 0 }}
      transition={{ duration: 0.5 }}
      className="h-full"
    >
      <div className="mb-6">
        <h1 className="text-2xl font-display font-bold text-white">Live Telemetry</h1>
        <p className="text-gray-400 mt-1">Real-time event stream from all machines</p>
      </div>
      <div className="h-[calc(100%-80px)]">
        <TelemetryFeed 
          events={telemetryEvents} 
          maxItems={50} 
          isLive={isLive}
          onToggleLive={onToggleLive}
        />
      </div>
    </motion.div>
  );
}

function PredictiveTab({ isLoaded, onMachineSelect, machines = [] }: TabProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isLoaded ? 1 : 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <div className="mb-6">
        <h1 className="text-2xl font-display font-bold text-white">Predictive Analytics</h1>
        <p className="text-gray-400 mt-1">AI-powered failure predictions and maintenance recommendations</p>
      </div>
      
      <div className="grid grid-cols-2 gap-6">
        <div className="h-[600px]">
          <PredictiveMaintenancePanel
            machines={machines}
            onMachineSelect={onMachineSelect!}
          />
        </div>
        <div className="h-[600px]">
          <ProductionForecastChart forecasts={mockDataConstants.mockProductionForecast} />
        </div>
      </div>
    </motion.div>
  );
}

function ToolsTab({ isLoaded }: { isLoaded: boolean }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isLoaded ? 1 : 0 }}
      transition={{ duration: 0.5 }}
      className="h-full"
    >
      <div className="mb-6">
        <h1 className="text-2xl font-display font-bold text-white">Tool Wear Tracking</h1>
        <p className="text-gray-400 mt-1">Monitor tool condition and schedule replacements</p>
      </div>
      <div className="h-[calc(100%-80px)]">
        <ToolWearTracker tools={mockDataConstants.mockTools} />
      </div>
    </motion.div>
  );
}

function AlertsTab({ isLoaded, alerts = [], newAlertIds = new Set() }: TabProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isLoaded ? 1 : 0 }}
      transition={{ duration: 0.5 }}
      className="h-full"
    >
      <div className="mb-6">
        <h1 className="text-2xl font-display font-bold text-white">Alert Center</h1>
        <p className="text-gray-400 mt-1">All active alerts and notifications</p>
      </div>
      <div className="h-[calc(100%-80px)]">
        <AlertsPanel alerts={alerts} newAlertIds={newAlertIds} />
      </div>
    </motion.div>
  );
}

function MaintenanceTab({ isLoaded }: { isLoaded: boolean }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isLoaded ? 1 : 0 }}
      transition={{ duration: 0.5 }}
      className="h-full"
    >
      <div className="mb-6">
        <h1 className="text-2xl font-display font-bold text-white">Maintenance Schedule</h1>
        <p className="text-gray-400 mt-1">Preventive and corrective maintenance calendar</p>
      </div>
      <div className="h-[calc(100%-80px)]">
        <MaintenanceCalendar events={mockDataConstants.mockMaintenanceEvents} />
      </div>
    </motion.div>
  );
}

function SettingsTab() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <div className="mb-6">
        <h1 className="text-2xl font-display font-bold text-white">System Monitoring & Settings</h1>
        <p className="text-gray-400 mt-1">Advanced system monitoring and configuration</p>
      </div>
      
      {/* Enterprise Monitoring */}
      <div className="grid grid-cols-2 gap-6">
        <ModelDriftMonitor />
        <DataLakeStats />
      </div>
      
      <div className="glass-panel p-6 max-w-2xl">
        <h3 className="text-lg font-medium text-white mb-4">Dashboard Settings</h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between py-3 border-b border-white/10">
            <div>
              <p className="text-sm text-white">Auto-refresh interval</p>
              <p className="text-xs text-gray-400">How often to refresh machine data</p>
            </div>
            <select className="bg-[#0a0e1a] border border-white/10 rounded-lg px-3 py-2 text-sm text-white">
              <option>2 seconds</option>
              <option>5 seconds</option>
              <option>10 seconds</option>
              <option>30 seconds</option>
            </select>
          </div>
          
          <div className="flex items-center justify-between py-3 border-b border-white/10">
            <div>
              <p className="text-sm text-white">Alert notifications</p>
              <p className="text-xs text-gray-400">Show desktop notifications for critical alerts</p>
            </div>
            <button className="w-12 h-6 rounded-full bg-[#00ff88] relative">
              <span className="absolute right-1 top-1 w-4 h-4 rounded-full bg-white" />
            </button>
          </div>
          
          <div className="flex items-center justify-between py-3 border-b border-white/10">
            <div>
              <p className="text-sm text-white">Sound alerts</p>
              <p className="text-xs text-gray-400">Play sound for critical machine alerts</p>
            </div>
            <button className="w-12 h-6 rounded-full bg-white/20 relative">
              <span className="absolute left-1 top-1 w-4 h-4 rounded-full bg-white" />
            </button>
          </div>
          
          <div className="flex items-center justify-between py-3">
            <div>
              <p className="text-sm text-white">Default view</p>
              <p className="text-xs text-gray-400">Starting tab when opening dashboard</p>
            </div>
            <select className="bg-[#0a0e1a] border border-white/10 rounded-lg px-3 py-2 text-sm text-white">
              <option>Overview</option>
              <option>Machines</option>
              <option>Alerts</option>
              <option>Predictive</option>
            </select>
          </div>
        </div>
      </div>
      
      <div className="glass-panel p-6 max-w-2xl">
        <h3 className="text-lg font-medium text-white mb-4">System Information</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-400">Platform Version</span>
            <span className="text-white font-mono">v3.1.5</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Connected Machines</span>
            <span className="text-[#00ff88] font-mono">120</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">Data Retention</span>
            <span className="text-white font-mono">90 days</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-400">AI Model Version</span>
            <span className="text-[#00d9ff] font-mono">PredictiveML v3.2</span>
          </div>
        </div>
      </div>
      
      {/* Enterprise Modules Status */}
      <div className="glass-panel p-6 max-w-2xl">
        <h3 className="text-lg font-medium text-white mb-4">Enterprise Features</h3>
        
        <div className="space-y-3">
          <div className="flex justify-between items-center p-3 bg-purple-500/10 border border-purple-500/20 rounded-lg">
            <div>
              <div className="text-sm font-medium text-white">AI Explainability</div>
              <div className="text-xs text-gray-400">SHAP/LIME analysis</div>
            </div>
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          </div>
          
          <div className="flex justify-between items-center p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
            <div>
              <div className="text-sm font-medium text-white">Multi-Region</div>
              <div className="text-xs text-gray-400">4 regions operational</div>
            </div>
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          </div>
          
          <div className="flex justify-between items-center p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
            <div>
              <div className="text-sm font-medium text-white">Audit Trail</div>
              <div className="text-xs text-gray-400">Compliance logging</div>
            </div>
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          </div>
          
          <div className="flex justify-between items-center p-3 bg-cyan-500/10 border border-cyan-500/20 rounded-lg">
            <div>
              <div className="text-sm font-medium text-white">Data Lake</div>
              <div className="text-xs text-gray-400">MinIO storage</div>
            </div>
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// New enterprise tabs

function ExplainabilityTab({ isLoaded, selectedMachine }: TabProps & { selectedMachine?: OmayaMachine | null }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isLoaded ? 1 : 0 }}
      className="space-y-6"
    >
      {selectedMachine ? (
        <AIExplainabilityPanel machineId={selectedMachine.id} />
      ) : (
        <div className="text-center py-20">
          <p className="text-gray-400 mb-2">Select a machine to view AI explanation</p>
          <p className="text-sm text-gray-500">Go to Fleet Overview and click on a machine</p>
        </div>
      )}
    </motion.div>
  );
}

function AuditTab({ isLoaded }: TabProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isLoaded ? 1 : 0 }}
      className="space-y-6"
    >
      <AuditTrailPanel />
    </motion.div>
  );
}

function MultiRegionTab({ isLoaded }: TabProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isLoaded ? 1 : 0 }}
      className="space-y-6"
    >
      <MultiRegionDashboard />
    </motion.div>
  );
}

function GraphQLTab({ isLoaded }: TabProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isLoaded ? 1 : 0 }}
      className="space-y-6"
    >
      <GraphQLExplorer />
    </motion.div>
  );
}

function AnalyticsTab({ isLoaded }: TabProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: isLoaded ? 1 : 0 }}
      className="h-full"
    >
      <AdvancedAnalyticsDashboard />
    </motion.div>
  );
}
