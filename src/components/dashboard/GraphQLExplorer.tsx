/**
 * GraphQL Explorer Component
 * Interactive GraphQL query builder and tester
 */
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Code, Play, Copy, Check, AlertCircle, Database } from 'lucide-react';
import { graphqlRequest } from '@/lib/graphql-client';

const exampleQueries = [
  {
    name: 'Get All Machines',
    query: `query GetMachines {
  machines(limit: 10) {
    id
    name
    status
    temperature
    vibration
  }
}`,
  },
  {
    name: 'Get Machine by ID',
    query: `query GetMachine {
  machine(id: "OMAYA-001") {
    id
    name
    status
    zone
    temperature
    vibration
    toolWear
  }
}`,
  },
  {
    name: 'Get KPIs',
    query: `query GetKPIs {
  kpis {
    oee
    uptime
    defectRate
    machinesRunning
    machinesIdle
    machinesError
  }
}`,
  },
  {
    name: 'Get Alerts',
    query: `query GetAlerts {
  alerts(limit: 5) {
    id
    machineId
    severity
    title
    message
    timestamp
  }
}`,
  },
  {
    name: 'Get Prediction',
    query: `query GetPrediction {
  prediction(machineId: "OMAYA-001") {
    machineId
    failureProbability
    rulHours
    confidence
    factors
  }
}`,
  },
  {
    name: 'Acknowledge Alert',
    query: `mutation AcknowledgeAlert {
  acknowledgeAlert(alertId: "ALERT-001") {
    id
    acknowledged
    timestamp
  }
}`,
  },
  {
    name: 'Schedule Maintenance',
    query: `mutation ScheduleMaintenance {
  scheduleMaintenance(
    machineId: "OMAYA-001"
    scheduledDate: "2024-02-01"
    maintenanceType: "Preventive"
  ) {
    id
    machineId
    scheduledDate
    status
  }
}`,
  },
];

export function GraphQLExplorer() {
  const [query, setQuery] = useState(exampleQueries[0].query);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const executeQuery = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await graphqlRequest(query);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(query);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Database className="w-8 h-8 text-[#00d9ff]" />
          <div>
            <h2 className="text-2xl font-bold text-white">GraphQL Explorer</h2>
            <p className="text-sm text-gray-400">
              Test GraphQL queries and mutations
            </p>
          </div>
        </div>
        <Badge variant="outline" className="text-[#00d9ff] border-[#00d9ff]">
          Interactive API
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Example Queries */}
        <Card className="glass-panel border-gray-800">
          <CardHeader>
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <Code className="w-5 h-5 text-[#00d9ff]" />
              Example Queries
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[500px]">
              <div className="space-y-2">
                {exampleQueries.map((example, index) => (
                  <Button
                    key={index}
                    variant="ghost"
                    className="w-full justify-start text-left hover:bg-[#00d9ff]/10"
                    onClick={() => setQuery(example.query)}
                  >
                    <span className="text-white">{example.name}</span>
                  </Button>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Query Editor */}
        <Card className="glass-panel border-gray-800 lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg text-white flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Code className="w-5 h-5 text-[#00d9ff]" />
                Query Editor
              </span>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={copyToClipboard}
                  className="border-gray-700 hover:bg-gray-800"
                >
                  {copied ? (
                    <Check className="w-4 h-4 text-green-400" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </Button>
                <Button
                  size="sm"
                  onClick={executeQuery}
                  disabled={loading}
                  className="bg-[#00d9ff] hover:bg-[#00d9ff]/90 text-black"
                >
                  <Play className="w-4 h-4 mr-2" />
                  {loading ? 'Running...' : 'Execute'}
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="font-mono text-sm min-h-[250px] bg-black/50 border-gray-700 text-gray-300"
              placeholder="Enter your GraphQL query..."
            />

            {/* Result */}
            <div className="mt-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-sm font-medium text-gray-400">Result:</span>
                {error && (
                  <Badge variant="destructive" className="flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" />
                    Error
                  </Badge>
                )}
                {result && !error && (
                  <Badge variant="outline" className="text-green-400 border-green-400">
                    Success
                  </Badge>
                )}
              </div>

              <ScrollArea className="h-[250px]">
                <pre className="bg-black/50 p-4 rounded-lg border border-gray-800 text-sm">
                  <code className="text-gray-300">
                    {error ? (
                      <span className="text-red-400">{error}</span>
                    ) : result ? (
                      JSON.stringify(result, null, 2)
                    ) : (
                      <span className="text-gray-500">No result yet. Run a query to see output.</span>
                    )}
                  </code>
                </pre>
              </ScrollArea>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Schema Info */}
      <Card className="glass-panel border-gray-800">
        <CardHeader>
          <CardTitle className="text-lg text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-[#00d9ff]" />
            GraphQL Schema
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-black/30 rounded-lg border border-gray-800">
              <div className="text-sm font-medium text-gray-400 mb-2">Queries</div>
              <div className="space-y-1 text-sm text-gray-300">
                <div>• machines</div>
                <div>• machine(id)</div>
                <div>• alerts</div>
                <div>• prediction(machineId)</div>
                <div>• kpis</div>
                <div>• driftStatus</div>
              </div>
            </div>

            <div className="p-4 bg-black/30 rounded-lg border border-gray-800">
              <div className="text-sm font-medium text-gray-400 mb-2">Mutations</div>
              <div className="space-y-1 text-sm text-gray-300">
                <div>• acknowledgeAlert</div>
                <div>• scheduleMaintenance</div>
                <div>• requestPrediction</div>
              </div>
            </div>

            <div className="p-4 bg-black/30 rounded-lg border border-gray-800">
              <div className="text-sm font-medium text-gray-400 mb-2">Subscriptions</div>
              <div className="space-y-1 text-sm text-gray-300">
                <div>• telemetryStream</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
