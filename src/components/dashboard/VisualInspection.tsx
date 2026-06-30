import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, CheckCircle2, AlertCircle, Scan, History, BarChart3, Upload, RefreshCcw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Detection {
  class: string;
  confidence: number;
  bbox: number[];
}

interface InspectionResult {
  timestamp: string;
  status: 'PASS' | 'FAIL';
  quality_score: number;
  detections: Detection[];
  part_id: string;
  machine_id: string;
  inspection_time_ms: number;
}

export function VisualInspection() {
  const [isScanning, setIsScanning] = useState(false);
  const [lastResult, setLastResult] = useState<InspectionResult | null>(null);
  const [history, setHistory] = useState<InspectionResult[]>([]);
  const [stats, setStats] = useState({
    total: 0,
    passed: 0,
    failed: 0,
    passRate: 0
  });

  const runInspection = async () => {
    setIsScanning(true);
    try {
      // Simulate API call to backend
      const response = await fetch('/api/inspect/image', { method: 'POST' });
      const data = await response.json();

      // Artificial delay for effect
      await new Promise(resolve => setTimeout(resolve, 800));

      setLastResult(data);
      setHistory(prev => [data, ...prev].slice(0, 10));
      updateStats(data);
    } catch (error) {
      console.error('Inspection failed:', error);
    } finally {
      setIsScanning(false);
    }
  };

  const updateStats = (result: InspectionResult) => {
    setStats(prev => {
      const newTotal = prev.total + 1;
      const newPassed = result.status === 'PASS' ? prev.passed + 1 : prev.passed;
      const newFailed = result.status === 'FAIL' ? prev.failed + 1 : prev.failed;
      return {
        total: newTotal,
        passed: newPassed,
        failed: newFailed,
        passRate: (newPassed / newTotal) * 100
      };
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Visual Inspection</h1>
          <p className="text-gray-400 mt-1">AI-powered quality control using YOLO</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium flex items-center gap-2">
            <Scan className="w-3.5 h-3.5" />
            YOLOv8 Active
          </div>
          <button
            onClick={runInspection}
            disabled={isScanning}
            className="px-4 py-2 bg-[#00ff88] hover:bg-[#00e67a] disabled:opacity-50 text-[#0a0e1a] rounded-lg font-medium transition-all flex items-center gap-2 glow-green"
          >
            {isScanning ? <RefreshCcw className="w-4 h-4 animate-spin" /> : <Camera className="w-4 h-4" />}
            {isScanning ? 'Inspecting...' : 'Start Inspection'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Main Camera View */}
        <div className="col-span-8 space-y-6">
          <div className="glass-panel relative aspect-video bg-black/40 rounded-xl overflow-hidden border border-white/10 group">
            {/* Viewport Overlay */}
            <div className="absolute inset-0 pointer-events-none">
              <div className="absolute top-8 left-8 w-16 h-16 border-t-2 border-l-2 border-[#00ff88]/50" />
              <div className="absolute top-8 right-8 w-16 h-16 border-t-2 border-r-2 border-[#00ff88]/50" />
              <div className="absolute bottom-8 left-8 w-16 h-16 border-b-2 border-l-2 border-[#00ff88]/50" />
              <div className="absolute bottom-8 right-8 w-16 h-16 border-b-2 border-r-2 border-[#00ff88]/50" />

              {/* Scanning Line */}
              {isScanning && (
                <motion.div
                  initial={{ top: '10%' }}
                  animate={{ top: '90%' }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                  className="absolute left-8 right-8 h-0.5 bg-[#00ff88]/30 shadow-[0_0_15px_rgba(0,255,136,0.5)] z-10"
                />
              )}
            </div>

            {/* Mock Image Content */}
            <div className="absolute inset-0 flex items-center justify-center">
              {!lastResult && !isScanning ? (
                <div className="text-center space-y-4">
                  <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mx-auto">
                    <Camera className="w-8 h-8 text-gray-500" />
                  </div>
                  <p className="text-gray-400">Camera ready. Click start to begin inspection.</p>
                </div>
              ) : (
                <div className="w-full h-full relative">
                  {/* Placeholder for real camera/image */}
                  <div className="w-full h-full bg-gradient-to-br from-gray-800 to-gray-900 opacity-40" />

                  {/* Detections Overlay */}
                  {lastResult && !isScanning && lastResult.detections.map((det, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className={cn(
                        "absolute border-2 rounded-sm",
                        det.class === 'quality_ok' ? "border-[#00ff88] bg-[#00ff88]/10" : "border-red-500 bg-red-500/10"
                      )}
                      style={{
                        left: `${det.bbox[0] / 6}%`,
                        top: `${det.bbox[1] / 6}%`,
                        width: `${(det.bbox[2] - det.bbox[0]) / 6}%`,
                        height: `${(det.bbox[3] - det.bbox[1]) / 6}%`
                      }}
                    >
                      <div className={cn(
                        "absolute -top-6 left-0 px-2 py-0.5 text-[10px] font-bold text-white uppercase rounded-t-sm",
                        det.class === 'quality_ok' ? "bg-[#00ff88]" : "bg-red-500"
                      )}>
                        {det.class.replace('_', ' ')} ({(det.confidence * 100).toFixed(1)}%)
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>

            {/* Status Badge */}
            <AnimatePresence>
              {lastResult && !isScanning && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="absolute top-6 right-6 z-20"
                >
                  <div className={cn(
                    "px-4 py-2 rounded-lg flex items-center gap-3 backdrop-blur-md border",
                    lastResult.status === 'PASS'
                      ? "bg-green-500/20 border-green-500/30 text-green-400"
                      : "bg-red-500/20 border-red-500/30 text-red-400"
                  )}>
                    {lastResult.status === 'PASS' ? <CheckCircle2 className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                    <span className="font-bold tracking-wider">{lastResult.status}</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Detailed Results Card */}
          {lastResult && (
            <div className="grid grid-cols-3 gap-4">
              <div className="glass-panel p-4 rounded-xl space-y-1">
                <p className="text-xs text-gray-400 uppercase tracking-wider font-medium">Part ID</p>
                <p className="text-lg font-bold text-white font-mono">{lastResult.part_id}</p>
              </div>
              <div className="glass-panel p-4 rounded-xl space-y-1">
                <p className="text-xs text-gray-400 uppercase tracking-wider font-medium">Quality Score</p>
                <div className="flex items-center gap-3">
                  <p className="text-lg font-bold text-white">{(lastResult.quality_score * 100).toFixed(1)}%</p>
                  <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <div
                      className={cn(
                        "h-full transition-all duration-1000",
                        lastResult.quality_score > 0.85 ? "bg-[#00ff88]" : "bg-red-500"
                      )}
                      style={{ width: `${lastResult.quality_score * 100}%` }}
                    />
                  </div>
                </div>
              </div>
              <div className="glass-panel p-4 rounded-xl space-y-1">
                <p className="text-xs text-gray-400 uppercase tracking-wider font-medium">Inference Time</p>
                <p className="text-lg font-bold text-white">{lastResult.inspection_time_ms}ms</p>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar Stats & History */}
        <div className="col-span-4 space-y-6">
          {/* Quick Stats */}
          <div className="glass-panel p-5 rounded-xl space-y-4">
            <div className="flex items-center gap-3">
              <BarChart3 className="w-5 h-5 text-[#00ff88]" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Shift Statistics</h3>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-400">Total Inspected</span>
                <span className="text-white font-mono">{stats.total}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-green-400">Passed</span>
                <span className="text-white font-mono">{stats.passed}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-red-400">Failed</span>
                <span className="text-white font-mono">{stats.failed}</span>
              </div>
              <div className="pt-2 border-t border-white/10">
                <div className="flex justify-between items-center mb-1.5">
                  <span className="text-sm text-gray-400">Overall Yield</span>
                  <span className="text-sm font-bold text-[#00ff88]">{stats.passRate.toFixed(1)}%</span>
                </div>
                <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-[#00ff88]" style={{ width: `${stats.passRate}%` }} />
                </div>
              </div>
            </div>
          </div>

          {/* Recent History */}
          <div className="glass-panel p-5 rounded-xl space-y-4 flex flex-col h-[400px]">
            <div className="flex items-center gap-3">
              <History className="w-5 h-5 text-blue-400" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Recent History</h3>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-thin">
              {history.length === 0 ? (
                <p className="text-center text-gray-500 text-xs py-10">No recent inspections</p>
              ) : (
                history.map((item, idx) => (
                  <div key={idx} className="p-3 bg-white/5 rounded-lg border border-white/5 hover:border-white/10 transition-all group">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-[10px] font-mono text-gray-500 uppercase">{item.part_id}</span>
                      <span className={cn(
                        "text-[10px] font-bold px-1.5 py-0.5 rounded",
                        item.status === 'PASS' ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"
                      )}>
                        {item.status}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-400">{new Date(item.timestamp).toLocaleTimeString()}</span>
                      <span className="text-xs text-white font-medium">{(item.quality_score * 100).toFixed(0)}% Score</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <button className="w-full py-3 glass-panel hover:bg-white/5 rounded-xl text-gray-400 text-xs flex items-center justify-center gap-2 transition-all">
            <Upload className="w-4 h-4" />
            Upload Reference Images
          </button>
        </div>
      </div>
    </div>
  );
}
