import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Shield, FileText, Download, AlertCircle, CheckCircle2, User, Clock } from 'lucide-react';

interface AuditEvent {
  event_id: string;
  timestamp: string;
  event_type: string;
  user_id: string;
  resource_type: string;
  resource_id?: string;
  status: string;
  action_details?: any;
}

export function AuditTrailPanel() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState<any>(null);

  useEffect(() => {
    fetchAuditEvents();
  }, []);

  const fetchAuditEvents = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/audit/recent?limit=50');
      const data = await response.json();
      setEvents(data.events || []);
    } catch (error) {
      console.error('Failed to fetch audit events:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateComplianceReport = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/audit/report?days=7');
      const data = await response.json();
      setReport(data);
    } catch (error) {
      console.error('Failed to generate report:', error);
    }
  };

  const getEventTypeIcon = (eventType: string) => {
    if (eventType.includes('LOGIN')) return User;
    if (eventType.includes('ALERT')) return AlertCircle;
    if (eventType.includes('DATA')) return FileText;
    return Shield;
  };

  const getEventTypeBadge = (eventType: string) => {
    const colors: Record<string, string> = {
      LOGIN: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      DATA_READ: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
      DATA_CREATE: 'bg-green-500/20 text-green-400 border-green-500/30',
      DATA_UPDATE: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      ALERT_CREATED: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      PREDICTION_REQUESTED: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    };
    
    const color = Object.keys(colors).find(key => eventType.includes(key)) || 'default';
    return colors[color] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-purple-500/20 border border-purple-500/30">
            <Shield className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Audit Trail</h2>
            <p className="text-sm text-gray-400">Compliance & Security Logging</p>
          </div>
        </div>
        
        <Button
          onClick={generateComplianceReport}
          className="bg-purple-600 hover:bg-purple-700"
        >
          <FileText className="w-4 h-4 mr-2" />
          Generate Report
        </Button>
      </div>

      {/* Statistics */}
      {report && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-4 gap-4"
        >
          <Card className="p-4 bg-gray-900/50 border-gray-800">
            <div className="text-sm text-gray-400 mb-1">Total Events</div>
            <div className="text-2xl font-bold text-white">{report.statistics?.total_events || 0}</div>
          </Card>
          <Card className="p-4 bg-gray-900/50 border-gray-800">
            <div className="text-sm text-gray-400 mb-1">Success Rate</div>
            <div className="text-2xl font-bold text-green-400">
              {report.statistics?.by_status?.SUCCESS 
                ? Math.round((report.statistics.by_status.SUCCESS / report.statistics.total_events) * 100)
                : 0}%
            </div>
          </Card>
          <Card className="p-4 bg-gray-900/50 border-gray-800">
            <div className="text-sm text-gray-400 mb-1">Security Events</div>
            <div className="text-2xl font-bold text-orange-400">
              {report.statistics?.security_events?.length || 0}
            </div>
          </Card>
          <Card className="p-4 bg-gray-900/50 border-gray-800">
            <div className="text-sm text-gray-400 mb-1">Failed Events</div>
            <div className="text-2xl font-bold text-red-400">
              {report.statistics?.failed_events?.length || 0}
            </div>
          </Card>
        </motion.div>
      )}

      {/* Events List */}
      <Card className="bg-gray-900/50 border-gray-800">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Recent Events</h3>
          
          {loading ? (
            <div className="text-center py-8 text-gray-400">Loading events...</div>
          ) : events.length === 0 ? (
            <div className="text-center py-8 text-gray-400">No audit events found</div>
          ) : (
            <ScrollArea className="h-[500px] pr-4">
              <div className="space-y-3">
                {events.map((event, index) => {
                  const IconComponent = getEventTypeIcon(event.event_type);
                  
                  return (
                    <motion.div
                      key={event.event_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50 hover:border-purple-500/30 transition-colors"
                    >
                      <div className="flex items-start gap-4">
                        <div className="p-2 rounded-lg bg-purple-500/10 border border-purple-500/20">
                          <IconComponent className="w-4 h-4 text-purple-400" />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge className={getEventTypeBadge(event.event_type)}>
                              {event.event_type.replace(/_/g, ' ')}
                            </Badge>
                            
                            {event.status === 'SUCCESS' ? (
                              <CheckCircle2 className="w-4 h-4 text-green-400" />
                            ) : (
                              <AlertCircle className="w-4 h-4 text-red-400" />
                            )}
                          </div>
                          
                          <div className="text-sm text-gray-300 mb-2">
                            <span className="text-white font-medium">{event.user_id}</span>
                            {' • '}
                            <span className="text-gray-400">{event.resource_type}</span>
                            {event.resource_id && (
                              <>
                                {' • '}
                                <span className="text-purple-400">{event.resource_id}</span>
                              </>
                            )}
                          </div>
                          
                          <div className="flex items-center gap-2 text-xs text-gray-500">
                            <Clock className="w-3 h-3" />
                            {new Date(event.timestamp).toLocaleString()}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </ScrollArea>
          )}
        </div>
      </Card>
    </div>
  );
}
