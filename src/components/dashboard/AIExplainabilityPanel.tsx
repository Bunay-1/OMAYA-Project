import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Lightbulb, TrendingUp, TrendingDown, AlertCircle, Info } from 'lucide-react';

interface Feature {
  value: number;
  shap_value: number;
  impact: string;
  importance: number;
}

interface ExplainabilityData {
  machineId: string;
  features: Record<string, number>;
  shap: {
    method: string;
    base_value: number;
    contributions: Record<string, Feature>;
    top_factors: string[];
    explanation: string;
  };
  lime: {
    method: string;
    prediction_probability: number;
    contributions: Record<string, any>;
    top_factors: string[];
    explanation: string;
  };
  featureImportance: Record<string, number>;
}

interface Props {
  machineId: string;
}

export function AIExplainabilityPanel({ machineId }: Props) {
  const [data, setData] = useState<ExplainabilityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('shap');

  useEffect(() => {
    if (machineId) {
      fetchExplanation();
    }
  }, [machineId]);

  const fetchExplanation = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/explainability/${machineId}`);
      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error('Failed to fetch AI explanation:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className="p-6 bg-gray-900/50 border-gray-800">
        <div className="text-center py-8 text-gray-400">Loading AI explanation...</div>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card className="p-6 bg-gray-900/50 border-gray-800">
        <div className="text-center py-8 text-gray-400">No explanation data available</div>
      </Card>
    );
  }

  const renderShapExplanation = () => {
    const contributions = Object.entries(data.shap.contributions)
      .sort(([, a], [, b]) => b.importance - a.importance);

    return (
      <div className="space-y-4">
        {/* Summary */}
        <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-400 mt-0.5" />
            <div>
              <div className="text-sm font-medium text-blue-400 mb-1">SHAP Explanation</div>
              <div className="text-sm text-gray-300">{data.shap.explanation}</div>
            </div>
          </div>
        </div>

        {/* Base Value */}
        <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
          <span className="text-sm text-gray-400">Base Prediction Value</span>
          <span className="text-lg font-bold text-white">{data.shap.base_value.toFixed(3)}</span>
        </div>

        {/* Feature Contributions */}
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-gray-400 mb-3">Feature Contributions</h4>
          {contributions.map(([feature, contrib], index) => {
            const isPositive = contrib.impact === 'positive';
            const absValue = Math.abs(contrib.shap_value);
            const maxValue = Math.max(...contributions.map(([, c]) => Math.abs(c.shap_value)));
            const widthPercent = (absValue / maxValue) * 100;

            return (
              <motion.div
                key={feature}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="space-y-2"
              >
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    {isPositive ? (
                      <TrendingUp className="w-4 h-4 text-red-400" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-green-400" />
                    )}
                    <span className="text-white font-medium capitalize">
                      {feature.replace(/([A-Z])/g, ' $1').trim()}
                    </span>
                    <Badge variant="outline" className="text-xs">
                      {contrib.value.toFixed(2)}
                    </Badge>
                  </div>
                  <span className={`font-mono text-xs ${isPositive ? 'text-red-400' : 'text-green-400'}`}>
                    {isPositive ? '+' : ''}{contrib.shap_value.toFixed(3)}
                  </span>
                </div>
                
                <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${isPositive ? 'bg-gradient-to-r from-red-500 to-red-600' : 'bg-gradient-to-r from-green-500 to-green-600'}`}
                    style={{ width: `${widthPercent}%` }}
                  />
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderLimeExplanation = () => {
    const contributions = Object.entries(data.lime.contributions)
      .sort(([, a], [, b]) => (b as any).importance - (a as any).importance);

    return (
      <div className="space-y-4">
        {/* Summary */}
        <div className="p-4 bg-purple-500/10 border border-purple-500/20 rounded-lg">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-purple-400 mt-0.5" />
            <div>
              <div className="text-sm font-medium text-purple-400 mb-1">LIME Explanation</div>
              <div className="text-sm text-gray-300">{data.lime.explanation}</div>
            </div>
          </div>
        </div>

        {/* Prediction Probability */}
        <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
          <span className="text-sm text-gray-400">Failure Probability</span>
          <span className="text-lg font-bold text-white">
            {(data.lime.prediction_probability * 100).toFixed(1)}%
          </span>
        </div>

        {/* Conditions */}
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-gray-400 mb-3">Contributing Conditions</h4>
          {contributions.map(([feature, contrib]: [string, any], index) => {
            const isPositive = contrib.impact === 'positive';
            const absWeight = Math.abs(contrib.weight);
            const maxWeight = Math.max(...contributions.map(([, c]: [string, any]) => Math.abs(c.weight)));
            const widthPercent = (absWeight / maxWeight) * 100;

            return (
              <motion.div
                key={feature}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="space-y-2"
              >
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    {isPositive ? (
                      <TrendingUp className="w-4 h-4 text-red-400" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-green-400" />
                    )}
                    <span className="text-white font-medium capitalize">
                      {feature.replace(/([A-Z])/g, ' $1').trim()}
                    </span>
                  </div>
                  <span className={`font-mono text-xs ${isPositive ? 'text-red-400' : 'text-green-400'}`}>
                    {isPositive ? '+' : ''}{contrib.weight.toFixed(3)}
                  </span>
                </div>
                
                <div className="text-xs text-gray-400 mb-1 font-mono">
                  {contrib.condition}
                </div>
                
                <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${isPositive ? 'bg-gradient-to-r from-red-500 to-red-600' : 'bg-gradient-to-r from-green-500 to-green-600'}`}
                    style={{ width: `${widthPercent}%` }}
                  />
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderFeatureImportance = () => {
    const features = Object.entries(data.featureImportance)
      .sort(([, a], [, b]) => b - a);

    return (
      <div className="space-y-3">
        <div className="p-4 bg-cyan-500/10 border border-cyan-500/20 rounded-lg">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-cyan-400 mt-0.5" />
            <div>
              <div className="text-sm font-medium text-cyan-400 mb-1">Global Feature Importance</div>
              <div className="text-sm text-gray-300">
                Overall importance of each feature across all predictions
              </div>
            </div>
          </div>
        </div>

        {features.map(([feature, importance], index) => (
          <motion.div
            key={feature}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="space-y-2"
          >
            <div className="flex items-center justify-between text-sm">
              <span className="text-white font-medium capitalize">
                {feature.replace(/([A-Z])/g, ' $1').trim()}
              </span>
              <span className="text-cyan-400 font-mono text-xs">
                {(importance * 100).toFixed(1)}%
              </span>
            </div>
            
            <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-blue-500"
                style={{ width: `${importance * 100}%` }}
              />
            </div>
          </motion.div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-yellow-500/20 border border-yellow-500/30">
            <Lightbulb className="w-6 h-6 text-yellow-400" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">AI Explainability</h3>
            <p className="text-sm text-gray-400">Understanding prediction factors</p>
          </div>
        </div>
        
        <Button onClick={fetchExplanation} variant="outline" size="sm">
          Refresh
        </Button>
      </div>

      {/* Tabs */}
      <Card className="bg-gray-900/50 border-gray-800">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <div className="border-b border-gray-800 px-6 pt-4">
            <TabsList className="bg-gray-800/50">
              <TabsTrigger value="shap">SHAP Analysis</TabsTrigger>
              <TabsTrigger value="lime">LIME Explanation</TabsTrigger>
              <TabsTrigger value="importance">Feature Importance</TabsTrigger>
            </TabsList>
          </div>

          <ScrollArea className="h-[600px]">
            <div className="p-6">
              <TabsContent value="shap" className="mt-0">
                {renderShapExplanation()}
              </TabsContent>
              
              <TabsContent value="lime" className="mt-0">
                {renderLimeExplanation()}
              </TabsContent>
              
              <TabsContent value="importance" className="mt-0">
                {renderFeatureImportance()}
              </TabsContent>
            </div>
          </ScrollArea>
        </Tabs>
      </Card>
    </div>
  );
}
