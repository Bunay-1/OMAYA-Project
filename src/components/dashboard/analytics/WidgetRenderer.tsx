import { useMemo } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, AreaChart, Area, ScatterChart, Scatter, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { useRealTimeData } from '@/hooks/useRealTimeData';
import { AnalyticsEngine } from '@/lib/analytics-engine';
import type { AnalyticsWidget } from '@/lib/analytics-engine';

interface WidgetRendererProps {
  widget: AnalyticsWidget;
}

const COLORS = ['#8b5cf6', '#ec4899', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'];

export function WidgetRenderer({ widget }: WidgetRendererProps) {
  const { machines } = useRealTimeData();

  const data = useMemo(() => {
    return AnalyticsEngine.generateWidgetData(widget, machines);
  }, [widget, machines]);

  switch (widget.type) {
    case 'line':
      return <LineChartWidget data={data} />;
    case 'bar':
      return <BarChartWidget data={data} />;
    case 'area':
      return <AreaChartWidget data={data} />;
    case 'pie':
      return <PieChartWidget data={data} />;
    case 'scatter':
      return <ScatterChartWidget data={data} />;
    case 'gauge':
      return <GaugeWidget value={data} />;
    case 'heatmap':
      return <HeatmapWidget data={data} />;
    default:
      return <div className="text-slate-400 text-sm">Unsupported chart type</div>;
  }
}

function LineChartWidget({ data }: { data: any }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data[0]?.data || []}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis 
          dataKey="x" 
          stroke="#64748b"
          tick={{ fontSize: 11 }}
          tickFormatter={(value) => new Date(value).toLocaleTimeString('en-US', { hour: '2-digit' })}
        />
        <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '8px',
            fontSize: '12px'
          }}
        />
        <Legend wrapperStyle={{ fontSize: '12px' }} />
        {data.map((series: any, i: number) => (
          <Line
            key={i}
            type="monotone"
            dataKey="y"
            data={series.data}
            stroke={COLORS[i % COLORS.length]}
            strokeWidth={2}
            dot={false}
            name={series.name}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

function BarChartWidget({ data }: { data: any }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data[0]?.data || []}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis 
          dataKey="x" 
          stroke="#64748b"
          tick={{ fontSize: 11 }}
        />
        <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '8px',
            fontSize: '12px'
          }}
        />
        <Legend wrapperStyle={{ fontSize: '12px' }} />
        {data.map((series: any, i: number) => (
          <Bar
            key={i}
            dataKey="y"
            data={series.data}
            fill={COLORS[i % COLORS.length]}
            name={series.name}
            radius={[4, 4, 0, 0]}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}

function AreaChartWidget({ data }: { data: any }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data[0]?.data || []}>
        <defs>
          {data.map((series: any, i: number) => (
            <linearGradient key={i} id={`gradient${i}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={COLORS[i % COLORS.length]} stopOpacity={0.8} />
              <stop offset="95%" stopColor={COLORS[i % COLORS.length]} stopOpacity={0} />
            </linearGradient>
          ))}
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis 
          dataKey="x" 
          stroke="#64748b"
          tick={{ fontSize: 11 }}
        />
        <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '8px',
            fontSize: '12px'
          }}
        />
        <Legend wrapperStyle={{ fontSize: '12px' }} />
        {data.map((series: any, i: number) => (
          <Area
            key={i}
            type="monotone"
            dataKey="y"
            data={series.data}
            stroke={COLORS[i % COLORS.length]}
            fill={`url(#gradient${i})`}
            name={series.name}
          />
        ))}
      </AreaChart>
    </ResponsiveContainer>
  );
}

function PieChartWidget({ data }: { data: any }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
          outerRadius="70%"
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry: any, index: number) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '8px',
            fontSize: '12px'
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}

function ScatterChartWidget({ data }: { data: any }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <ScatterChart>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis type="number" dataKey="x" stroke="#64748b" tick={{ fontSize: 11 }} />
        <YAxis type="number" dataKey="y" stroke="#64748b" tick={{ fontSize: 11 }} />
        <Tooltip
          cursor={{ strokeDasharray: '3 3' }}
          contentStyle={{
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '8px',
            fontSize: '12px'
          }}
        />
        <Scatter name="Data Points" data={data} fill={COLORS[0]} />
      </ScatterChart>
    </ResponsiveContainer>
  );
}

function GaugeWidget({ value }: { value: number }) {
  const percentage = Math.min(100, Math.max(0, value));
  const isHigh = percentage > 75;
  const isMedium = percentage > 50;

  return (
    <div className="flex flex-col items-center justify-center h-full">
      <div className="relative w-40 h-40">
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="80"
            cy="80"
            r="70"
            stroke="#1e293b"
            strokeWidth="12"
            fill="none"
          />
          <circle
            cx="80"
            cy="80"
            r="70"
            stroke={isHigh ? '#10b981' : isMedium ? '#f59e0b' : '#ef4444'}
            strokeWidth="12"
            fill="none"
            strokeDasharray={`${(percentage / 100) * 440} 440`}
            strokeLinecap="round"
            className="transition-all duration-1000"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="text-3xl font-bold text-white">{percentage.toFixed(1)}%</div>
          <div className="text-xs text-slate-400 mt-1">Current Value</div>
        </div>
      </div>
      <div className="mt-4 flex items-center gap-2">
        {isHigh ? (
          <TrendingUp className="w-4 h-4 text-green-400" />
        ) : (
          <TrendingDown className="w-4 h-4 text-red-400" />
        )}
        <span className="text-sm text-slate-400">
          {isHigh ? 'Above Target' : 'Below Target'}
        </span>
      </div>
    </div>
  );
}

function HeatmapWidget({ data }: { data: any }) {
  return (
    <div className="grid grid-cols-10 gap-1 h-full">
      {data.map((cell: any, i: number) => (
        <div
          key={i}
          className="rounded-sm"
          style={{
            backgroundColor: `rgba(139, 92, 246, ${cell.y / 100})`,
          }}
          title={`${cell.x}: ${cell.y}`}
        />
      ))}
    </div>
  );
}
