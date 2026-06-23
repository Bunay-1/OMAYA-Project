/**
 * Explainable AI Component
 * Displays SHAP/LIME explanations for predictions
 */
import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Brain, TrendingUp, TrendingDown, Info } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface ExplanationProps {
  prediction: {
    failureProbability: number;
    explanation?: {
      method: string;
      contributions: Record<string, {
        value: number;
        shap_value?: number;
        weight?: number;
        impact: string;
        importance: number;
      }>;
      top_factors: string[];
      explanation: string;
    };
  };
}

export default function ExplainableAI({ prediction }: ExplanationProps) {
  const [selectedMethod, setSelectedMethod] = useState<'shap' | 'lime'>('shap');
  const explanation = prediction.explanation;

  if (!explanation) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-purple-500" />
            Model Explanation
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No explanation available for this prediction
          </p>
        </CardContent>
      </Card>
    );
  }

  const contributions = Object.entries(explanation.contributions);
  const maxImportance = Math.max(...contributions.map(([_, data]) => data.importance));

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-purple-500" />
            Model Explanation
            <Badge variant="outline" className="ml-2">
              {explanation.method}
            </Badge>
          </CardTitle>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Info className="h-4 w-4 text-muted-foreground" />
              </TooltipTrigger>
              <TooltipContent>
                <p className="max-w-xs text-xs">
                  {explanation.method === 'SHAP' 
                    ? 'SHAP (SHapley Additive exPlanations) shows how each feature contributes to the prediction'
                    : 'LIME (Local Interpretable Model-agnostic Explanations) provides local feature importance'}
                </p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Explanation summary */}
        <div className="rounded-lg bg-muted/50 p-4">
          <p className="text-sm leading-relaxed">{explanation.explanation}</p>
        </div>

        {/* Feature contributions */}
        <div className="space-y-3">
          <h4 className="text-sm font-semibold">Feature Contributions</h4>
          {contributions.map(([feature, data]) => {
            const percentage = (data.importance / maxImportance) * 100;
            const isPositive = data.impact === 'positive';

            return (
              <div key={feature} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    {isPositive ? (
                      <TrendingUp className="h-4 w-4 text-red-500" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-green-500" />
                    )}
                    <span className="font-medium capitalize">
                      {feature.replace(/([A-Z])/g, ' $1').trim()}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">
                      Value: {data.value.toFixed(2)}
                    </span>
                    <Badge
                      variant={isPositive ? 'destructive' : 'default'}
                      className="text-xs"
                    >
                      {isPositive ? '+' : '-'}
                      {Math.abs(data.shap_value || data.weight || 0).toFixed(3)}
                    </Badge>
                  </div>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                  <div
                    className={`h-full transition-all ${
                      isPositive ? 'bg-red-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* Top factors summary */}
        <div className="space-y-2">
          <h4 className="text-sm font-semibold">Top Contributing Factors</h4>
          <div className="flex flex-wrap gap-2">
            {explanation.top_factors.map((factor, index) => (
              <Badge key={factor} variant="secondary">
                {index + 1}. {factor.replace(/([A-Z])/g, ' $1').trim()}
              </Badge>
            ))}
          </div>
        </div>

        {/* Model confidence */}
        <div className="rounded-lg border border-border bg-card p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Prediction Confidence</p>
              <p className="text-xs text-muted-foreground">
                Based on feature analysis
              </p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold">
                {(prediction.failureProbability * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-muted-foreground">Failure Risk</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
