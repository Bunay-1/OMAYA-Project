/**
 * Model Drift Monitor Component
 * Displays drift detection status and alerts
 */
import { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Activity, AlertTriangle, CheckCircle2, TrendingUp } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

interface DriftStatus {
  hasDrift: boolean;
  accuracyDrift: boolean;
  featureDrift: boolean;
  currentAccuracy: number;
  baselineAccuracy: number;
  accuracyDrop: number;
  featureDriftScores: Record<string, number>;
  maxPSI: number;
  samplesAnalyzed: number;
  recommendation: string;
}

export default function ModelDriftMonitor() {
  const [driftStatus, setDriftStatus] = useState<DriftStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDriftStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/drift/status');
        const data = await response.json();
        setDriftStatus(data);
      } catch (error) {
        console.error('Failed to fetch drift status:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDriftStatus();
    const interval = setInterval(fetchDriftStatus, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-blue-500 animate-pulse" />
            Model Drift Monitor
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Loading drift status...</p>
        </CardContent>
      </Card>
    );
  }

  if (!driftStatus) {
    return null;
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-blue-500" />
            Model Drift Monitor
          </CardTitle>
          <Badge
            variant={driftStatus.hasDrift ? 'destructive' : 'default'}
            className="flex items-center gap-1"
          >
            {driftStatus.hasDrift ? (
              <>
                <AlertTriangle className="h-3 w-3" />
                Drift Detected
              </>
            ) : (
              <>
                <CheckCircle2 className="h-3 w-3" />
                No Drift
              </>
            )}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Recommendation Alert */}
        {driftStatus.hasDrift && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{driftStatus.recommendation}</AlertDescription>
          </Alert>
        )}

        {/* Accuracy Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">Current Accuracy</p>
              <Badge variant={driftStatus.accuracyDrift ? 'destructive' : 'secondary'}>
                {(driftStatus.currentAccuracy * 100).toFixed(1)}%
              </Badge>
            </div>
            <Progress 
              value={driftStatus.currentAccuracy * 100} 
              className="h-2"
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">Baseline Accuracy</p>
              <Badge variant="secondary">
                {(driftStatus.baselineAccuracy * 100).toFixed(1)}%
              </Badge>
            </div>
            <Progress 
              value={driftStatus.baselineAccuracy * 100} 
              className="h-2"
            />
          </div>
        </div>

        {/* Accuracy Drop */}
        {driftStatus.accuracyDrop > 0 && (
          <div className="flex items-center justify-between rounded-lg border border-red-200 bg-red-50 p-3 dark:border-red-900 dark:bg-red-950">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 rotate-180 text-red-500" />
              <span className="text-sm font-medium text-red-900 dark:text-red-100">
                Accuracy Drop
              </span>
            </div>
            <span className="text-sm font-bold text-red-600 dark:text-red-400">
              -{(driftStatus.accuracyDrop * 100).toFixed(1)}%
            </span>
          </div>
        )}

        {/* Feature Drift Scores */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold">Feature Drift (PSI Scores)</h4>
            <Badge variant={driftStatus.featureDrift ? 'destructive' : 'secondary'}>
              Max PSI: {driftStatus.maxPSI.toFixed(3)}
            </Badge>
          </div>

          <div className="space-y-2">
            {Object.entries(driftStatus.featureDriftScores).map(([feature, psi]) => {
              const isDrifted = psi > 0.2;
              const percentage = Math.min((psi / 0.5) * 100, 100);

              return (
                <div key={feature} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="capitalize">
                      {feature.replace(/([A-Z])/g, ' $1').trim()}
                    </span>
                    <Badge
                      variant={isDrifted ? 'destructive' : 'secondary'}
                      className="text-xs"
                    >
                      {psi.toFixed(3)}
                    </Badge>
                  </div>
                  <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                    <div
                      className={`h-full transition-all ${
                        isDrifted ? 'bg-red-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <p className="text-xs text-muted-foreground">
            PSI {'>'} 0.2 indicates significant drift
          </p>
        </div>

        {/* Statistics */}
        <div className="flex items-center justify-between rounded-lg border border-border bg-muted/50 p-3">
          <div>
            <p className="text-sm font-medium">Samples Analyzed</p>
            <p className="text-xs text-muted-foreground">
              Used for drift detection
            </p>
          </div>
          <p className="text-2xl font-bold">{driftStatus.samplesAnalyzed}</p>
        </div>
      </CardContent>
    </Card>
  );
}
