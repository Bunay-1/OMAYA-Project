// Advanced Analytics Engine for OMAYA Fleet
import type { OmayaMachine, Alert, KPIData } from '@/types/omaya';

export type AggregationType = 'sum' | 'avg' | 'min' | 'max' | 'count' | 'median' | 'stddev';
export type TimeGranularity = '1h' | '6h' | '12h' | '24h' | '7d' | '30d';
export type ChartType = 'line' | 'bar' | 'area' | 'pie' | 'scatter' | 'heatmap' | 'gauge';

export interface CustomKPI {
  id: string;
  name: string;
  formula: string;
  metric: string;
  aggregation: AggregationType;
  filters: KPIFilter[];
  target?: number;
  unit?: string;
  color?: string;
}

export interface KPIFilter {
  field: string;
  operator: 'eq' | 'gt' | 'lt' | 'gte' | 'lte' | 'contains';
  value: string | number;
}

export interface AnalyticsWidget {
  id: string;
  type: ChartType;
  title: string;
  dataSource: string;
  metrics: string[];
  dimensions: string[];
  aggregation: AggregationType;
  timeRange: TimeGranularity;
  filters: KPIFilter[];
  position: { x: number; y: number };
  size: { w: number; h: number };
}

export interface CorrelationAnalysis {
  variable1: string;
  variable2: string;
  coefficient: number;
  pValue: number;
  strength: 'weak' | 'moderate' | 'strong';
}

export class AnalyticsEngine {
  // Calculate custom KPI
  static calculateKPI(kpi: CustomKPI, data: OmayaMachine[]): number {
    let filtered = this.applyFilters(data, kpi.filters);
    
    const values = filtered.map(m => {
      // Extract metric value using dot notation
      return this.extractValue(m, kpi.metric);
    }).filter(v => v !== null && v !== undefined) as number[];

    return this.aggregate(values, kpi.aggregation);
  }

  // Apply filters to dataset
  static applyFilters(data: OmayaMachine[], filters: KPIFilter[]): OmayaMachine[] {
    return data.filter(item => {
      return filters.every(filter => {
        const value = this.extractValue(item, filter.field);
        return this.evaluateFilter(value, filter.operator, filter.value);
      });
    });
  }

  // Extract nested value using dot notation (e.g., "telemetry.temperature")
  static extractValue(obj: any, path: string): any {
    return path.split('.').reduce((acc, part) => acc?.[part], obj);
  }

  // Evaluate filter condition
  static evaluateFilter(value: any, operator: string, filterValue: any): boolean {
    switch (operator) {
      case 'eq': return value === filterValue;
      case 'gt': return value > filterValue;
      case 'lt': return value < filterValue;
      case 'gte': return value >= filterValue;
      case 'lte': return value <= filterValue;
      case 'contains': return String(value).includes(String(filterValue));
      default: return true;
    }
  }

  // Aggregate values
  static aggregate(values: number[], type: AggregationType): number {
    if (values.length === 0) return 0;

    switch (type) {
      case 'sum':
        return values.reduce((a, b) => a + b, 0);
      case 'avg':
        return values.reduce((a, b) => a + b, 0) / values.length;
      case 'min':
        return Math.min(...values);
      case 'max':
        return Math.max(...values);
      case 'count':
        return values.length;
      case 'median':
        const sorted = [...values].sort((a, b) => a - b);
        const mid = Math.floor(sorted.length / 2);
        return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
      case 'stddev':
        const avg = values.reduce((a, b) => a + b, 0) / values.length;
        const squareDiffs = values.map(v => Math.pow(v - avg, 2));
        return Math.sqrt(squareDiffs.reduce((a, b) => a + b, 0) / values.length);
      default:
        return 0;
    }
  }

  // Correlation analysis between two variables
  static correlate(data: OmayaMachine[], var1: string, var2: string): CorrelationAnalysis {
    const pairs = data.map(m => ({
      x: this.extractValue(m, var1),
      y: this.extractValue(m, var2)
    })).filter(p => p.x !== null && p.y !== null && !isNaN(p.x) && !isNaN(p.y));

    if (pairs.length < 2) {
      return {
        variable1: var1,
        variable2: var2,
        coefficient: 0,
        pValue: 1,
        strength: 'weak'
      };
    }

    const n = pairs.length;
    const sumX = pairs.reduce((s, p) => s + p.x, 0);
    const sumY = pairs.reduce((s, p) => s + p.y, 0);
    const sumXY = pairs.reduce((s, p) => s + p.x * p.y, 0);
    const sumX2 = pairs.reduce((s, p) => s + p.x * p.x, 0);
    const sumY2 = pairs.reduce((s, p) => s + p.y * p.y, 0);

    const numerator = n * sumXY - sumX * sumY;
    const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));

    const coefficient = denominator === 0 ? 0 : numerator / denominator;

    // Simplified p-value approximation
    const t = coefficient * Math.sqrt((n - 2) / (1 - coefficient * coefficient));
    const pValue = Math.abs(t) > 2 ? 0.05 : 0.1; // Simplified

    const absCoeff = Math.abs(coefficient);
    const strength = absCoeff > 0.7 ? 'strong' : absCoeff > 0.4 ? 'moderate' : 'weak';

    return { variable1: var1, variable2: var2, coefficient, pValue, strength };
  }

  // Time series aggregation
  static aggregateTimeSeries(
    data: any[],
    timeField: string,
    valueField: string,
    granularity: TimeGranularity,
    aggregation: AggregationType
  ): Array<{ time: string; value: number }> {
    const grouped = new Map<string, number[]>();

    data.forEach(item => {
      const time = this.extractValue(item, timeField);
      const value = this.extractValue(item, valueField);
      
      if (!time || value === null || value === undefined) return;

      const bucket = this.getTimeBucket(new Date(time), granularity);
      
      if (!grouped.has(bucket)) {
        grouped.set(bucket, []);
      }
      grouped.get(bucket)!.push(value);
    });

    return Array.from(grouped.entries())
      .map(([time, values]) => ({
        time,
        value: this.aggregate(values, aggregation)
      }))
      .sort((a, b) => a.time.localeCompare(b.time));
  }

  // Get time bucket based on granularity
  static getTimeBucket(date: Date, granularity: TimeGranularity): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hour = String(date.getHours()).padStart(2, '0');

    switch (granularity) {
      case '1h':
        return `${year}-${month}-${day}T${hour}:00`;
      case '6h':
        const hour6 = Math.floor(date.getHours() / 6) * 6;
        return `${year}-${month}-${day}T${String(hour6).padStart(2, '0')}:00`;
      case '12h':
        const hour12 = Math.floor(date.getHours() / 12) * 12;
        return `${year}-${month}-${day}T${String(hour12).padStart(2, '0')}:00`;
      case '24h':
        return `${year}-${month}-${day}`;
      case '7d':
        const week = Math.floor((date.getTime() - new Date(year, 0, 1).getTime()) / (7 * 24 * 60 * 60 * 1000));
        return `${year}-W${String(week).padStart(2, '0')}`;
      case '30d':
        return `${year}-${month}`;
      default:
        return date.toISOString();
    }
  }

  // Generate widget data
  static generateWidgetData(widget: AnalyticsWidget, data: OmayaMachine[]): any {
    const filtered = this.applyFilters(data, widget.filters);

    switch (widget.type) {
      case 'line':
      case 'area':
      case 'bar':
        return this.generateTimeSeriesData(widget, filtered);
      case 'pie':
        return this.generatePieData(widget, filtered);
      case 'scatter':
        return this.generateScatterData(widget, filtered);
      case 'heatmap':
        return this.generateHeatmapData(widget, filtered);
      case 'gauge':
        return this.generateGaugeData(widget, filtered);
      default:
        return [];
    }
  }

  private static generateTimeSeriesData(widget: AnalyticsWidget, data: OmayaMachine[]): any {
    // Mock implementation - in real scenario, query time-series data
    return widget.metrics.map(metric => ({
      name: metric,
      data: Array.from({ length: 24 }, (_, i) => ({
        x: new Date(Date.now() - (23 - i) * 3600000).toISOString(),
        y: Math.random() * 100
      }))
    }));
  }

  private static generatePieData(widget: AnalyticsWidget, data: OmayaMachine[]): any {
    const dimension = widget.dimensions[0];
    const grouped = new Map<string, number>();

    data.forEach(item => {
      const key = String(this.extractValue(item, dimension));
      grouped.set(key, (grouped.get(key) || 0) + 1);
    });

    return Array.from(grouped.entries()).map(([name, value]) => ({ name, value }));
  }

  private static generateScatterData(widget: AnalyticsWidget, data: OmayaMachine[]): any {
    return data.map(item => ({
      x: this.extractValue(item, widget.metrics[0]),
      y: this.extractValue(item, widget.metrics[1]),
      name: item.id
    }));
  }

  private static generateHeatmapData(widget: AnalyticsWidget, data: OmayaMachine[]): any {
    // Simplified heatmap
    return data.slice(0, 10).map(item => ({
      x: this.extractValue(item, widget.dimensions[0]),
      y: this.extractValue(item, widget.metrics[0])
    }));
  }

  private static generateGaugeData(widget: AnalyticsWidget, data: OmayaMachine[]): any {
    const values = data.map(m => this.extractValue(m, widget.metrics[0])).filter(v => v !== null);
    return this.aggregate(values, widget.aggregation);
  }
}
