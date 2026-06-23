/**
 * GraphQL Client Configuration
 * Connects to backend GraphQL endpoint
 */

const GRAPHQL_ENDPOINT = import.meta.env.VITE_GRAPHQL_URL || 'http://localhost:8000/graphql';

interface GraphQLResponse<T> {
  data?: T;
  errors?: Array<{
    message: string;
    locations?: Array<{ line: number; column: number }>;
    path?: string[];
  }>;
}

/**
 * Execute GraphQL query or mutation
 */
export async function graphqlRequest<T>(
  query: string,
  variables?: Record<string, any>
): Promise<T> {
  try {
    const response = await fetch(GRAPHQL_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        variables,
      }),
    });

    const result: GraphQLResponse<T> = await response.json();

    if (result.errors) {
      throw new Error(result.errors[0].message);
    }

    if (!result.data) {
      throw new Error('No data returned from GraphQL');
    }

    return result.data;
  } catch (error) {
    console.error('GraphQL request error:', error);
    throw error;
  }
}

/**
 * GraphQL Queries
 */

export const GET_MACHINES = `
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

export const GET_MACHINE = `
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

export const GET_ALERTS = `
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

export const GET_PREDICTION = `
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

export const GET_KPIS = `
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

export const GET_DRIFT_STATUS = `
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

/**
 * GraphQL Mutations
 */

export const ACKNOWLEDGE_ALERT = `
  mutation AcknowledgeAlert($alertId: String!) {
    acknowledgeAlert(alertId: $alertId) {
      id
      acknowledged
      timestamp
    }
  }
`;

export const SCHEDULE_MAINTENANCE = `
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

export const REQUEST_PREDICTION = `
  mutation RequestPrediction($input: PredictionInput!) {
    requestPrediction(input: $input) {
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

/**
 * Subscription (WebSocket)
 */
export function subscribeTelemetry(
  machineId: string,
  onData: (data: any) => void
): () => void {
  // WebSocket GraphQL subscription
  const wsUrl = GRAPHQL_ENDPOINT.replace('http', 'ws');
  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    ws.send(JSON.stringify({
      type: 'subscribe',
      query: `
        subscription TelemetryStream($machineId: String!) {
          telemetryStream(machineId: $machineId) {
            machineId
            temperature
            vibration
            spindleSpeed
            timestamp
          }
        }
      `,
      variables: { machineId }
    }));
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'data') {
      onData(data.payload);
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  // Return cleanup function
  return () => {
    ws.close();
  };
}

/**
 * Helper functions
 */

export async function fetchMachines(limit = 100, offset = 0) {
  const result = await graphqlRequest<{ machines: any[] }>(
    GET_MACHINES,
    { limit, offset }
  );
  return result.machines;
}

export async function fetchMachine(id: string) {
  const result = await graphqlRequest<{ machine: any }>(
    GET_MACHINE,
    { id }
  );
  return result.machine;
}

export async function fetchAlerts(limit = 50, offset = 0) {
  const result = await graphqlRequest<{ alerts: any[] }>(
    GET_ALERTS,
    { limit, offset }
  );
  return result.alerts;
}

export async function fetchKPIs() {
  const result = await graphqlRequest<{ kpis: any }>(GET_KPIS);
  return result.kpis;
}

export async function fetchDriftStatus() {
  const result = await graphqlRequest<{ driftStatus: any }>(GET_DRIFT_STATUS);
  return result.driftStatus;
}

export async function acknowledgeAlert(alertId: string) {
  const result = await graphqlRequest<{ acknowledgeAlert: any }>(
    ACKNOWLEDGE_ALERT,
    { alertId }
  );
  return result.acknowledgeAlert;
}

export async function scheduleMaintenance(
  machineId: string,
  scheduledDate: string,
  maintenanceType: string
) {
  const result = await graphqlRequest<{ scheduleMaintenance: any }>(
    SCHEDULE_MAINTENANCE,
    { machineId, scheduledDate, maintenanceType }
  );
  return result.scheduleMaintenance;
}
