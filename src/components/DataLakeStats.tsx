/**
 * Data Lake Statistics Component
 * Displays storage metrics and usage
 */
import { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Database, HardDrive, FileText, AlertCircle } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

interface DataLakeStats {
  connected: boolean;
  buckets: Record<string, {
    object_count: number;
    total_size_mb: number;
  }>;
}

export default function DataLakeStats() {
  const [stats, setStats] = useState<DataLakeStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/data-lake/stats');
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch data lake stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5 text-cyan-500 animate-pulse" />
            Data Lake Storage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Loading storage stats...</p>
        </CardContent>
      </Card>
    );
  }

  if (!stats || !stats.connected) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5 text-cyan-500" />
            Data Lake Storage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <AlertCircle className="h-4 w-4" />
            Data Lake not connected
          </div>
        </CardContent>
      </Card>
    );
  }

  const totalObjects = Object.values(stats.buckets).reduce(
    (sum, bucket) => sum + bucket.object_count,
    0
  );
  const totalSizeMB = Object.values(stats.buckets).reduce(
    (sum, bucket) => sum + bucket.total_size_mb,
    0
  );

  const bucketIcons: Record<string, any> = {
    'omaya-telemetry': HardDrive,
    'omaya-predictions': AlertCircle,
    'omaya-alerts': AlertCircle,
    'omaya-models': Database,
    'omaya-reports': FileText,
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5 text-cyan-500" />
            Data Lake Storage
          </CardTitle>
          <Badge variant="default" className="flex items-center gap-1">
            Connected
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Total statistics */}
        <div className="grid grid-cols-2 gap-4">
          <div className="rounded-lg border border-border bg-muted/50 p-4">
            <p className="text-sm font-medium text-muted-foreground">Total Objects</p>
            <p className="text-2xl font-bold">{totalObjects.toLocaleString()}</p>
          </div>
          <div className="rounded-lg border border-border bg-muted/50 p-4">
            <p className="text-sm font-medium text-muted-foreground">Total Size</p>
            <p className="text-2xl font-bold">{totalSizeMB.toFixed(1)} MB</p>
          </div>
        </div>

        {/* Bucket breakdown */}
        <div className="space-y-3">
          <h4 className="text-sm font-semibold">Storage by Bucket</h4>
          {Object.entries(stats.buckets).map(([bucketName, bucketData]) => {
            const Icon = bucketIcons[bucketName] || Database;
            const percentage = (bucketData.total_size_mb / totalSizeMB) * 100;

            return (
              <div key={bucketName} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Icon className="h-4 w-4 text-cyan-500" />
                    <span className="text-sm font-medium">
                      {bucketName.replace('omaya-', '').replace('-', ' ').toUpperCase()}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground">
                      {bucketData.object_count} objects
                    </span>
                    <Badge variant="secondary" className="text-xs">
                      {bucketData.total_size_mb.toFixed(2)} MB
                    </Badge>
                  </div>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full bg-cyan-500 transition-all"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* Storage usage info */}
        <div className="rounded-lg border border-border bg-card p-3">
          <p className="text-xs text-muted-foreground leading-relaxed">
            Data Lake provides long-term storage for telemetry, predictions, alerts, and trained models.
            Automatic archival ensures compliance and audit trail availability.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
