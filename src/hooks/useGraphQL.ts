/**
 * React Hook for GraphQL Queries
 * Provides easy data fetching with loading and error states
 */
import { useState, useEffect, useCallback } from 'react';
import { graphqlRequest } from '@/lib/graphql-client';

interface UseGraphQLResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

/**
 * Generic hook for GraphQL queries
 */
export function useGraphQL<T>(
  query: string,
  variables?: Record<string, any>,
  skip = false
): UseGraphQLResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(!skip);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    if (skip) return;

    try {
      setLoading(true);
      setError(null);
      const result = await graphqlRequest<T>(query, variables);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setLoading(false);
    }
  }, [query, JSON.stringify(variables), skip]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
  };
}

/**
 * Hook for machine data
 */
export function useMachines(limit = 100, offset = 0) {
  const query = `
    query GetMachines($limit: Int, $offset: Int) {
      machines(limit: $limit, offset: $offset) {
        id
        name
        status
        zone
        temperature
        vibration
        spindleSpeed
        toolWear
        operatingHours
        lastUpdated
      }
    }
  `;

  return useGraphQL<{ machines: any[] }>(query, { limit, offset });
}

/**
 * Hook for single machine
 */
export function useMachine(id: string, skip = false) {
  const query = `
    query GetMachine($id: String!) {
      machine(id: $id) {
        id
        name
        status
        zone
        temperature
        vibration
        spindleSpeed
        toolWear
        operatingHours
        lastUpdated
      }
    }
  `;

  return useGraphQL<{ machine: any }>(query, { id }, skip);
}

/**
 * Hook for alerts
 */
export function useAlerts(limit = 50, offset = 0) {
  const query = `
    query GetAlerts($limit: Int, $offset: Int) {
      alerts(limit: $limit, offset: $offset) {
        id
        machineId
        severity
        title
        message
        timestamp
        acknowledged
      }
    }
  `;

  return useGraphQL<{ alerts: any[] }>(query, { limit, offset });
}

/**
 * Hook for KPIs
 */
export function useKPIs() {
  const query = `
    query GetKPIs {
      kpis {
        oee
        uptime
        defectRate
        machinesRunning
        machinesIdle
        machinesError
      }
    }
  `;

  return useGraphQL<{ kpis: any }>(query);
}

/**
 * Hook for drift status
 */
export function useDriftStatus() {
  const query = `
    query GetDriftStatus {
      driftStatus {
        hasDrift
        accuracyDrift
        featureDrift
        currentAccuracy
        recommendation
      }
    }
  `;

  return useGraphQL<{ driftStatus: any }>(query);
}

/**
 * Hook for predictions
 */
export function usePrediction(machineId: string, skip = false) {
  const query = `
    query GetPrediction($machineId: String!) {
      prediction(machineId: $machineId) {
        machineId
        failureProbability
        rulHours
        rulDays
        confidence
        modelVersion
        factors
      }
    }
  `;

  return useGraphQL<{ prediction: any }>(query, { machineId }, skip);
}

/**
 * Hook for GraphQL mutations
 */
export function useGraphQLMutation<TData, TVariables = Record<string, any>>() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const mutate = async (
    query: string,
    variables: TVariables
  ): Promise<TData | null> => {
    try {
      setLoading(true);
      setError(null);
      const result = await graphqlRequest<TData>(query, variables);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    mutate,
    loading,
    error,
  };
}

/**
 * Hook for acknowledging alerts
 */
export function useAcknowledgeAlert() {
  const { mutate, loading, error } = useGraphQLMutation<{ acknowledgeAlert: any }>();

  const acknowledge = async (alertId: string) => {
    const query = `
      mutation AcknowledgeAlert($alertId: String!) {
        acknowledgeAlert(alertId: $alertId) {
          id
          acknowledged
          timestamp
        }
      }
    `;

    return mutate(query, { alertId });
  };

  return {
    acknowledge,
    loading,
    error,
  };
}

/**
 * Hook for scheduling maintenance
 */
export function useScheduleMaintenance() {
  const { mutate, loading, error } = useGraphQLMutation<{ scheduleMaintenance: any }>();

  const schedule = async (
    machineId: string,
    scheduledDate: string,
    maintenanceType: string
  ) => {
    const query = `
      mutation ScheduleMaintenance(
        $machineId: String!
        $scheduledDate: String!
        $maintenanceType: String!
      ) {
        scheduleMaintenance(
          machineId: $machineId
          scheduledDate: $scheduledDate
          maintenanceType: $maintenanceType
        ) {
          id
          machineId
          scheduledDate
          maintenanceType
          status
        }
      }
    `;

    return mutate(query, { machineId, scheduledDate, maintenanceType });
  };

  return {
    schedule,
    loading,
    error,
  };
}
