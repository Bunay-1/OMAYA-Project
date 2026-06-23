import type { 
  OmayaMachine, 
  Alert, 
  Tool, 
  MaintenanceEvent, 
  KPIData, 
  ProductionForecast, 
  TelemetryEvent,
  MachineStatus 
} from '@/types/omaya';

const zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E', 'Zone F'];
const machineTypes = ['OMAYA-5X', 'OMAYA-3X', 'OMAYA-Lathe', 'OMAYA-Mill', 'OMAYA-Router'];

function randomBetween(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomFloat(min: number, max: number, decimals: number = 2): number {
  return parseFloat((Math.random() * (max - min) + min).toFixed(decimals));
}

function randomStatus(): MachineStatus {
  const rand = Math.random();
  if (rand < 0.7) return 'operational';
  if (rand < 0.85) return 'warning';
  if (rand < 0.92) return 'critical';
  if (rand < 0.97) return 'maintenance';
  return 'offline';
}

function generateMachineId(index: number): string {
  return `OMAYA-${String(index + 1).padStart(3, '0')}`;
}

function randomDate(daysAgo: number, daysAhead: number = 0): string {
  const now = new Date();
  const offset = randomBetween(-daysAgo, daysAhead);
  now.setDate(now.getDate() + offset);
  return now.toISOString();
}

export function generateMachines(count: number = 120): OmayaMachine[] {
  return Array.from({ length: count }, (_, i) => {
    const status = randomStatus();
    const isHealthy = status === 'operational';
    
    return {
      id: generateMachineId(i),
      name: `${machineTypes[i % machineTypes.length]} #${i + 1}`,
      zone: zones[i % zones.length],
      status,
      spindleSpeed: isHealthy ? randomBetween(8000, 12000) : randomBetween(4000, 8000),
      temperature: isHealthy ? randomBetween(35, 55) : randomBetween(55, 85),
      vibration: isHealthy ? randomFloat(0.1, 2.5) : randomFloat(2.5, 8.0),
      toolWear: randomBetween(5, 95),
      cycleTime: randomBetween(45, 180),
      uptime: isHealthy ? randomFloat(85, 99) : randomFloat(50, 85),
      lastMaintenance: randomDate(30, 0),
      nextMaintenance: randomDate(0, 30),
      errorLogs: status !== 'operational' ? [
        {
          id: `err-${i}-1`,
          timestamp: randomDate(1, 0),
          severity: status === 'critical' ? 'critical' : 'warning',
          message: status === 'critical' ? 'Spindle overheating detected' : 'Vibration levels elevated',
          code: status === 'critical' ? 'E-001' : 'W-003'
        }
      ] : [],
      predictions: {
        failureProbability: isHealthy ? randomFloat(0.01, 0.15) : randomFloat(0.3, 0.85),
        estimatedTimeToFailure: isHealthy ? randomBetween(200, 1000) : randomBetween(10, 100),
        recommendedAction: isHealthy ? 'Continue monitoring' : 'Schedule preventive maintenance',
        confidence: randomFloat(0.75, 0.98),
        contributingFactors: isHealthy 
          ? ['Normal wear patterns'] 
          : ['High vibration', 'Elevated temperature', 'Tool wear approaching limit']
      }
    };
  });
}

export function generateAlerts(machines: OmayaMachine[]): Alert[] {
  const alertTypes: Alert['type'][] = ['overheating', 'vibration', 'tool_breakage', 'maintenance', 'performance', 'error'];
  const alerts: Alert[] = [];
  
  machines.forEach((machine, index) => {
    if (machine.status !== 'operational') {
      alerts.push({
        id: `alert-${index}`,
        machineId: machine.id,
        machineName: machine.name,
        timestamp: randomDate(0, 0),
        severity: machine.status === 'critical' ? 'critical' : machine.status === 'warning' ? 'warning' : 'info',
        type: alertTypes[randomBetween(0, alertTypes.length - 1)],
        title: machine.status === 'critical' 
          ? `Critical: ${machine.name} requires immediate attention`
          : `Warning: ${machine.name} showing anomalies`,
        message: machine.status === 'critical'
          ? 'Temperature exceeding safe limits. Immediate shutdown recommended.'
          : 'Vibration patterns indicate potential bearing wear.',
        acknowledged: Math.random() > 0.7,
        rootCause: 'Bearing degradation detected through vibration analysis',
        recommendedActions: [
          'Reduce spindle speed by 20%',
          'Schedule bearing replacement',
          'Increase lubrication frequency'
        ]
      });
    }
  });
  
  return alerts.sort((a, b) => {
    const severityOrder = { critical: 0, error: 1, warning: 2, info: 3 };
    return severityOrder[a.severity] - severityOrder[b.severity];
  });
}

export function generateTools(machines: OmayaMachine[]): Tool[] {
  const toolNames = ['End Mill 10mm', 'Drill Bit 8mm', 'Face Mill 50mm', 'Ball Nose 6mm', 'Thread Tap M8'];
  const tools: Tool[] = [];
  
  machines.slice(0, 50).forEach((machine, index) => {
    tools.push({
      id: `tool-${index}`,
      name: toolNames[index % toolNames.length],
      machineId: machine.id,
      machineName: machine.name,
      wearPercentage: machine.toolWear,
      estimatedLifeRemaining: randomBetween(5, 100),
      replacementCost: randomBetween(50, 500),
      downtimeImpact: randomBetween(15, 60),
      lastReplaced: randomDate(14, 0),
      scheduledReplacement: machine.toolWear > 80 ? randomDate(0, 3) : undefined
    });
  });
  
  return tools.sort((a, b) => b.wearPercentage - a.wearPercentage);
}

export function generateMaintenanceEvents(machines: OmayaMachine[]): MaintenanceEvent[] {
  const events: MaintenanceEvent[] = [];
  const types: MaintenanceEvent['type'][] = ['preventive', 'corrective', 'predictive'];
  const statuses: MaintenanceEvent['status'][] = ['scheduled', 'in_progress', 'completed', 'overdue'];
  
  machines.slice(0, 30).forEach((machine, index) => {
    events.push({
      id: `maint-${index}`,
      machineId: machine.id,
      machineName: machine.name,
      type: types[index % types.length],
      status: statuses[index % statuses.length],
      scheduledDate: randomDate(-5, 14),
      completedDate: index % 4 === 2 ? randomDate(5, 0) : undefined,
      description: `${types[index % types.length]} maintenance - ${machine.name}`,
      technician: `Tech-${randomBetween(1, 10)}`,
      duration: randomBetween(30, 240),
      cost: randomBetween(100, 2000)
    });
  });
  
  return events;
}

export function generateKPIs(): KPIData {
  return {
    oee: randomFloat(78, 92),
    uptime: randomFloat(88, 97),
    defectRate: randomFloat(0.5, 3.5),
    throughput: randomBetween(850, 1200),
    mtbf: randomBetween(150, 400),
    mttr: randomFloat(1.5, 4.5),
    energyEfficiency: randomFloat(82, 95),
    productionTarget: 1000,
    productionActual: randomBetween(850, 1050)
  };
}

export function generateProductionForecast(): ProductionForecast[] {
  const forecasts: ProductionForecast[] = [];
  const now = new Date();
  
  for (let i = 0; i < 14; i++) {
    const date = new Date(now);
    date.setDate(date.getDate() + i);
    const planned = 1000;
    const predicted = randomBetween(850, 1050);
    
    forecasts.push({
      date: date.toISOString().split('T')[0],
      planned,
      predicted,
      predictedDowntime: randomBetween(0, 120),
      confidence: randomFloat(0.75, 0.95)
    });
  }
  
  return forecasts;
}

export function generateTelemetryEvents(machines: OmayaMachine[]): TelemetryEvent[] {
  const events: TelemetryEvent[] = [];
  const eventTypes: TelemetryEvent['type'][] = ['status_change', 'alert', 'metric', 'maintenance'];
  const messages = [
    'Spindle speed adjusted to optimal range',
    'Temperature normalized after cooling cycle',
    'Tool change completed successfully',
    'Vibration levels within acceptable range',
    'Production cycle completed',
    'Preventive maintenance reminder',
    'Calibration check passed',
    'Lubrication cycle initiated'
  ];
  
  for (let i = 0; i < 50; i++) {
    const machine = machines[randomBetween(0, machines.length - 1)];
    const now = new Date();
    now.setMinutes(now.getMinutes() - randomBetween(0, 120));
    
    events.push({
      id: `telem-${i}`,
      machineId: machine.id,
      machineName: machine.name,
      timestamp: now.toISOString(),
      type: eventTypes[randomBetween(0, eventTypes.length - 1)],
      severity: machine.status === 'critical' ? 'critical' : machine.status === 'warning' ? 'warning' : 'info',
      message: messages[randomBetween(0, messages.length - 1)]
    });
  }
  
  return events.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
}

// Initialize mock data
export const mockMachines = generateMachines(120);
export const mockAlerts = generateAlerts(mockMachines);
export const mockTools = generateTools(mockMachines);
export const mockMaintenanceEvents = generateMaintenanceEvents(mockMachines);
export const mockKPIs = generateKPIs();
export const mockProductionForecast = generateProductionForecast();
export const mockTelemetryEvents = generateTelemetryEvents(mockMachines);
