import { useState, useEffect, useCallback, useRef } from 'react';
import type { OMAYAMachine, Alert, TelemetryEvent, KPIData } from '@/types/omaya';
import {
  generateMachines,
  generateAlerts,
  generateKPIs,
  generateTelemetryEvents,
} from '@/data/mockData';

interface RealTimeDataState {
  machines: OMAYAMachine[];
  alerts: Alert[];
  kpis: KPIData;
  telemetryEvents: TelemetryEvent[];
  lastUpdate: Date;
  isLive: boolean;
}

interface UseRealTimeDataOptions {
  refreshInterval?: number; // milliseconds
  enabled?: boolean;
}

export function useRealTimeData(options: UseRealTimeDataOptions = {}) {
  const { refreshInterval = 3000, enabled = true } = options;
  const useMock = import.meta.env.VITE_USE_MOCK === 'true';
  
  const [data, setData] = useState<RealTimeDataState>(() => {
    const machines = generateMachines(120);
    return {
      machines,
      alerts: generateAlerts(machines),
      kpis: generateKPIs(),
      telemetryEvents: generateTelemetryEvents(machines),
      lastUpdate: new Date(),
      isLive: enabled,
    };
  });

  const [newAlertIds, setNewAlertIds] = useState<Set<string>>(new Set());
  const [updatedMachineIds, setUpdatedMachineIds] = useState<Set<string>>(new Set());
  const previousAlertsRef = useRef<string[]>([]);

  const refreshData = useCallback(() => {
    if (!useMock) {
      // In a real application, this would fetch from the FastAPI backend
      // fetch('/api/machines').then(res => res.json()).then(data => ...)
      console.log('Fetching real data from API...');
    }

    setData(prev => {
      const machines = generateMachines(120);
      const newAlerts = generateAlerts(machines);
      
      // Track new alerts
      const prevAlertIds = new Set(previousAlertsRef.current);
      const newIds = newAlerts
        .filter(a => !prevAlertIds.has(a.id))
        .map(a => a.id);
      
      if (newIds.length > 0) {
        setNewAlertIds(new Set(newIds));
        setTimeout(() => setNewAlertIds(new Set()), 3000);
      }
      
      previousAlertsRef.current = newAlerts.map(a => a.id);

      // Track updated machines (random subset for visual effect)
      const updatedIds = machines
        .filter(() => Math.random() < 0.1)
        .map(m => m.id);
      setUpdatedMachineIds(new Set(updatedIds));
      setTimeout(() => setUpdatedMachineIds(new Set()), 1000);

      return {
        machines,
        alerts: newAlerts,
        kpis: generateKPIs(),
        telemetryEvents: generateTelemetryEvents(machines),
        lastUpdate: new Date(),
        isLive: prev.isLive,
      };
    });
  }, []);

  const toggleLive = useCallback(() => {
    setData(prev => ({ ...prev, isLive: !prev.isLive }));
  }, []);

  useEffect(() => {
    if (!enabled || !data.isLive) return;

    const interval = setInterval(refreshData, refreshInterval);
    return () => clearInterval(interval);
  }, [enabled, data.isLive, refreshInterval, refreshData]);

  // Add new telemetry event periodically
  useEffect(() => {
    if (!enabled || !data.isLive) return;

    const interval = setInterval(() => {
      setData(prev => {
        const machine = prev.machines[Math.floor(Math.random() * prev.machines.length)];
        const messages = [
          'Spindle speed adjusted to optimal range',
          'Temperature normalized after cooling cycle',
          'Tool change completed successfully',
          'Vibration levels within acceptable range',
          'Production cycle completed',
          'Calibration check passed',
          'Lubrication cycle initiated',
          'Quality check passed',
          'Batch processing started',
          'Sensor data synchronized',
        ];
        
        const newEvent: TelemetryEvent = {
          id: `telem-${Date.now()}`,
          machineId: machine.id,
          machineName: machine.name,
          timestamp: new Date().toISOString(),
          type: ['status_change', 'alert', 'metric', 'maintenance'][Math.floor(Math.random() * 4)] as TelemetryEvent['type'],
          severity: machine.status === 'critical' ? 'critical' : machine.status === 'warning' ? 'warning' : 'info',
          message: messages[Math.floor(Math.random() * messages.length)],
        };

        return {
          ...prev,
          telemetryEvents: [newEvent, ...prev.telemetryEvents.slice(0, 49)],
        };
      });
    }, 1500);

    return () => clearInterval(interval);
  }, [enabled, data.isLive]);

  return {
    ...data,
    newAlertIds,
    updatedMachineIds,
    refreshData,
    toggleLive,
  };
}

// Hook for animated number transitions
export function useAnimatedValue(value: number, duration: number = 500) {
  const [displayValue, setDisplayValue] = useState(value);
  const [isAnimating, setIsAnimating] = useState(false);
  const previousValue = useRef(value);

  useEffect(() => {
    if (previousValue.current === value) return;

    setIsAnimating(true);
    const startValue = previousValue.current;
    const endValue = value;
    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      
      const currentValue = startValue + (endValue - startValue) * easeOutQuart;
      setDisplayValue(currentValue);

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setIsAnimating(false);
        previousValue.current = value;
      }
    };

    requestAnimationFrame(animate);
  }, [value, duration]);

  return { displayValue, isAnimating };
}
