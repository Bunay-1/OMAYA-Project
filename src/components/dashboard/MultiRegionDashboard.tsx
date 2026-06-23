import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Globe, Activity, Zap, TrendingUp, AlertCircle, CheckCircle2 } from 'lucide-react';

interface Region {
  name: string;
  status: string;
  priority: number;
  latency_ms: number;
  capacity_percent: number;
  endpoint: string;
}

interface MultiRegionStatus {
  current_region: string;
  primary_region: string;
  should_failover: boolean;
  failover_target: string | null;
  regions: Record<string, Region>;
  traffic_routing: Record<string, any>;
  healthy_count: number;
  total_count: number;
}

export function MultiRegionDashboard() {
  const [status, setStatus] = useState<MultiRegionStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMultiRegionStatus();
    const interval = setInterval(fetchMultiRegionStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchMultiRegionStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/multi-region/status');
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Failed to fetch multi-region status:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (regionStatus: string) => {
    const colors: Record<string, string> = {
      healthy: 'text-green-400 bg-green-500/20 border-green-500/30',
      degraded: 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30',
      unhealthy: 'text-red-400 bg-red-500/20 border-red-500/30',
      maintenance: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    };
    return colors[regionStatus] || 'text-gray-400 bg-gray-500/20 border-gray-500/30';
  };

  const getStatusIcon = (regionStatus: string) => {
    if (regionStatus === 'healthy') return CheckCircle2;
    if (regionStatus === 'degraded') return AlertCircle;
    return Activity;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading multi-region status...</div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Failed to load multi-region data</div>
      </div>
    );
  }

  const regionEntries = Object.entries(status.regions);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-blue-500/20 border border-blue-500/30">
            <Globe className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Multi-Region Deployment</h2>
            <p className="text-sm text-gray-400">Global Infrastructure Status</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-sm text-gray-400">Active Region</div>
            <div className="text-lg font-bold text-white">{status.current_region}</div>
          </div>
          <Badge className={status.should_failover ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'}>
            {status.should_failover ? 'Failover Ready' : 'Normal Operations'}
          </Badge>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="p-4 bg-gray-900/50 border-gray-800">
          <div className="flex items-center gap-3">
            <Globe className="w-5 h-5 text-blue-400" />
            <div>
              <div className="text-sm text-gray-400">Total Regions</div>
              <div className="text-2xl font-bold text-white">{status.total_count}</div>
            </div>
          </div>
        </Card>
        
        <Card className="p-4 bg-gray-900/50 border-gray-800">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-green-400" />
            <div>
              <div className="text-sm text-gray-400">Healthy Regions</div>
              <div className="text-2xl font-bold text-green-400">{status.healthy_count}</div>
            </div>
          </div>
        </Card>
        
        <Card className="p-4 bg-gray-900/50 border-gray-800">
          <div className="flex items-center gap-3">
            <Zap className="w-5 h-5 text-purple-400" />
            <div>
              <div className="text-sm text-gray-400">Failover Target</div>
              <div className="text-lg font-bold text-purple-400">
                {status.failover_target || 'N/A'}
              </div>
            </div>
          </div>
        </Card>
        
        <Card className="p-4 bg-gray-900/50 border-gray-800">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-5 h-5 text-cyan-400" />
            <div>
              <div className="text-sm text-gray-400">Uptime</div>
              <div className="text-2xl font-bold text-cyan-400">99.9%</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Regions Grid */}
      <div className="grid grid-cols-2 gap-4">
        {regionEntries.map(([code, region], index) => {
          const StatusIcon = getStatusIcon(region.status);
          const isPrimary = code === status.primary_region;
          const isCurrent = code === status.current_region;
          
          return (
            <motion.div
              key={code}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className={`p-6 bg-gray-900/50 border-gray-800 hover:border-blue-500/30 transition-colors ${isCurrent ? 'ring-2 ring-blue-500/50' : ''}`}>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${getStatusColor(region.status)}`}>
                      <StatusIcon className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-bold text-white">{region.name}</h3>
                        {isPrimary && (
                          <Badge className="bg-purple-500/20 text-purple-400 text-xs">PRIMARY</Badge>
                        )}
                        {isCurrent && (
                          <Badge className="bg-blue-500/20 text-blue-400 text-xs">ACTIVE</Badge>
                        )}
                      </div>
                      <div className="text-sm text-gray-400">{code}</div>
                    </div>
                  </div>
                  
                  <Badge className={getStatusColor(region.status)}>
                    {region.status.toUpperCase()}
                  </Badge>
                </div>

                <div className="space-y-3">
                  {/* Latency */}
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-400">Latency</span>
                      <span className="text-white font-medium">{region.latency_ms}ms</span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min((region.latency_ms / 100) * 100, 100)}%` }}
                        className={`h-full ${region.latency_ms < 50 ? 'bg-green-500' : region.latency_ms < 100 ? 'bg-yellow-500' : 'bg-red-500'}`}
                      />
                    </div>
                  </div>

                  {/* Capacity */}
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-400">Capacity</span>
                      <span className="text-white font-medium">{region.capacity_percent}%</span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${region.capacity_percent}%` }}
                        className="h-full bg-blue-500"
                      />
                    </div>
                  </div>

                  {/* Traffic Weight */}
                  {status.traffic_routing[code] && (
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-400">Traffic Weight</span>
                        <span className="text-white font-medium">
                          {status.traffic_routing[code].weight}%
                        </span>
                      </div>
                      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${status.traffic_routing[code].weight}%` }}
                          className="h-full bg-purple-500"
                        />
                      </div>
                    </div>
                  )}

                  {/* Priority */}
                  <div className="flex items-center justify-between text-sm pt-2 border-t border-gray-800">
                    <span className="text-gray-400">Priority</span>
                    <span className="text-white font-medium">#{region.priority}</span>
                  </div>

                  {/* Endpoint */}
                  <div className="text-xs text-gray-500 truncate">
                    {region.endpoint}
                  </div>
                </div>
              </Card>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
