export type MachineStatus = 'operational' | 'warning' | 'critical' | 'offline' | 'maintenance';

export interface OmayaMachine {
  id: string;
  name: string;
  zone: string;
  status: MachineStatus;
  spindleSpeed: number;
  temperature: number;
  vibration: number;
  toolWear: number;
  cycleTime: number;
  uptime: number;
  lastMaintenance: string;
  nextMaintenance: string;
  errorLogs: ErrorLog[];
  predictions: MachinePrediction;
}

export interface ErrorLog {
  id: string;
  timestamp: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  code: string;
}

export interface MachinePrediction {
  failureProbability: number;
  estimatedTimeToFailure: number; // hours
  recommendedAction: string;
  confidence: number;
  contributingFactors: string[];
}

export interface Alert {
  id: string;
  machineId: string;
  machineName: string;
  timestamp: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  type: 'overheating' | 'vibration' | 'tool_breakage' | 'maintenance' | 'performance' | 'error';
  title: string;
  message: string;
  acknowledged: boolean;
  rootCause?: string;
  recommendedActions?: string[];
}

export interface Tool {
  id: string;
  name: string;
  machineId: string;
  machineName: string;
  wearPercentage: number;
  estimatedLifeRemaining: number; // hours
  replacementCost: number;
  downtimeImpact: number; // minutes
  lastReplaced: string;
  scheduledReplacement?: string;
}

export interface MaintenanceEvent {
  id: string;
  machineId: string;
  machineName: string;
  type: 'preventive' | 'corrective' | 'predictive';
  status: 'scheduled' | 'in_progress' | 'completed' | 'overdue';
  scheduledDate: string;
  completedDate?: string;
  description: string;
  technician?: string;
  duration?: number; // minutes
  cost?: number;
}

export interface KPIData {
  oee: number;
  uptime: number;
  defectRate: number;
  throughput: number;
  mtbf: number; // Mean Time Between Failures (hours)
  mttr: number; // Mean Time To Repair (hours)
  energyEfficiency: number;
  productionTarget: number;
  productionActual: number;
}

export interface ProductionForecast {
  date: string;
  planned: number;
  predicted: number;
  predictedDowntime: number;
  confidence: number;
}

export interface TelemetryEvent {
  id: string;
  machineId: string;
  machineName: string;
  timestamp: string;
  type: 'status_change' | 'alert' | 'metric' | 'maintenance';
  severity: 'info' | 'warning' | 'error' | 'critical';
  message: string;
}
