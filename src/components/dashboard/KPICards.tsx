import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, Activity, Clock, Target, Zap, AlertCircle, Gauge, RefreshCw } from 'lucide-react';
import type { KPIData } from '@/types/omaya';
import { cn } from '@/lib/utils';

interface KPICardsProps {
  data: KPIData;
  isLive?: boolean;
}

// Hook for animated number transitions
function useAnimatedValue(value: number, duration: number = 500) {
  const [displayValue, setDisplayValue] = useState(value);
  const [isAnimating, setIsAnimating] = useState(false);
  const previousValue = useRef(value);

  useEffect(() => {
    if (Math.abs(previousValue.current - value) < 0.01) return;

    setIsAnimating(true);
    const startValue = previousValue.current;
    const endValue = value;
    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      
      const currentValue = startValue + (endValue - startValue) * easeOutQuart;
      setDisplayValue(currentValue);

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setIsAnimating(false);
        previousValue.current = value;
      }
    };

    requestAnimationFrame(animate);
  }, [value, duration]);

  return { displayValue, isAnimating };
}

interface KPICardProps {
  title: string;
  value: number;
  unit?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon: React.ElementType;
  color: 'green' | 'cyan' | 'amber' | 'red';
  delay?: number;
  decimals?: number;
}

const colorClasses = {
  green: {
    text: 'text-[#00ff88]',
    glow: 'text-glow-green',
    bg: 'bg-[#00ff88]/10',
    border: 'border-[#00ff88]/30',
    shadow: 'shadow-[0_0_30px_rgba(0,255,136,0.2)]'
  },
  cyan: {
    text: 'text-[#00d9ff]',
    glow: 'text-glow-cyan',
    bg: 'bg-[#00d9ff]/10',
    border: 'border-[#00d9ff]/30',
    shadow: 'shadow-[0_0_30px_rgba(0,217,255,0.2)]'
  },
  amber: {
    text: 'text-[#ffaa00]',
    glow: '',
    bg: 'bg-[#ffaa00]/10',
    border: 'border-[#ffaa00]/30',
    shadow: 'shadow-[0_0_30px_rgba(255,170,0,0.2)]'
  },
  red: {
    text: 'text-[#ff3366]',
    glow: '',
    bg: 'bg-[#ff3366]/10',
    border: 'border-[#ff3366]/30',
    shadow: 'shadow-[0_0_30px_rgba(255,51,102,0.2)]'
  }
};

function KPICard({ title, value, unit, trend, trendValue, icon: Icon, color, delay = 0, decimals = 1 }: KPICardProps) {
  const colors = colorClasses[color];
  const { displayValue, isAnimating } = useAnimatedValue(value);
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className={cn(
        "glass-panel p-6 relative overflow-hidden group hover:-translate-y-1 transition-transform duration-300",
        colors.shadow
      )}
    >
      {/* Background Glow */}
      <div className={cn(
        "absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500",
        colors.bg
      )} />
      
      {/* Update Indicator */}
      {isAnimating && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0 }}
          className="absolute top-3 right-3"
        >
          <RefreshCw className={cn("w-4 h-4 animate-spin", colors.text)} />
        </motion.div>
      )}
      
      {/* Icon */}
      <div className={cn(
        "w-12 h-12 rounded-xl flex items-center justify-center mb-4",
        colors.bg,
        colors.border,
        "border"
      )}>
        <Icon className={cn("w-6 h-6", colors.text)} />
      </div>
      
      {/* Title */}
      <p className="text-sm text-gray-400 font-medium tracking-wide uppercase mb-2">{title}</p>
      
      {/* Value */}
      <div className="flex items-baseline gap-2">
        <motion.span 
          className={cn(
            "text-4xl font-display font-extrabold tracking-tight",
            colors.text,
            colors.glow
          )}
          animate={isAnimating ? { scale: [1, 1.05, 1] } : {}}
          transition={{ duration: 0.3 }}
        >
          {displayValue.toFixed(decimals)}
        </motion.span>
        {unit && <span className="text-lg text-gray-500 font-mono">{unit}</span>}
      </div>
      
      {/* Trend */}
      {trend && trendValue && (
        <div className="flex items-center gap-1.5 mt-3">
          {trend === 'up' && <TrendingUp className="w-4 h-4 text-[#00ff88]" />}
          {trend === 'down' && <TrendingDown className="w-4 h-4 text-[#ff3366]" />}
          {trend === 'neutral' && <Minus className="w-4 h-4 text-gray-500" />}
          <span className={cn(
            "text-sm font-mono",
            trend === 'up' && "text-[#00ff88]",
            trend === 'down' && "text-[#ff3366]",
            trend === 'neutral' && "text-gray-500"
          )}>
            {trendValue}
          </span>
          <span className="text-xs text-gray-500">vs last week</span>
        </div>
      )}
      
      {/* Decorative Corner */}
      <div className={cn(
        "absolute top-0 right-0 w-20 h-20 opacity-10",
        colors.bg
      )} style={{
        clipPath: 'polygon(100% 0, 0 0, 100% 100%)'
      }} />
    </motion.div>
  );
}

export function KPICards({ data, isLive = true }: KPICardsProps) {
  const productionPercentage = ((data.productionActual / data.productionTarget) * 100).toFixed(1);
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <KPICard
        title="Overall Equipment Effectiveness"
        value={data.oee}
        unit="%"
        trend={data.oee > 85 ? 'up' : 'down'}
        trendValue={data.oee > 85 ? '+2.3%' : '-1.2%'}
        icon={Gauge}
        color="green"
        delay={0}
      />
      <KPICard
        title="Fleet Uptime"
        value={data.uptime}
        unit="%"
        trend={data.uptime > 90 ? 'up' : 'neutral'}
        trendValue={data.uptime > 90 ? '+1.5%' : '0%'}
        icon={Activity}
        color="cyan"
        delay={0.1}
      />
      <KPICard
        title="Production Output"
        value={data.productionActual}
        unit="units"
        trend={data.productionActual >= data.productionTarget ? 'up' : 'down'}
        trendValue={`${productionPercentage}% of target`}
        icon={Target}
        color={data.productionActual >= data.productionTarget ? 'green' : 'amber'}
        delay={0.2}
        decimals={0}
      />
      <KPICard
        title="Defect Rate"
        value={data.defectRate}
        unit="%"
        trend={data.defectRate < 2 ? 'up' : 'down'}
        trendValue={data.defectRate < 2 ? '-0.3%' : '+0.5%'}
        icon={AlertCircle}
        color={data.defectRate < 2 ? 'green' : 'red'}
        delay={0.3}
        decimals={2}
      />
    </div>
  );
}

export function SecondaryKPIs({ data }: KPICardsProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3, delay: 0.4 }}
        className="glass-panel p-4"
      >
        <div className="flex items-center gap-2 mb-2">
          <Clock className="w-4 h-4 text-[#00d9ff]" />
          <span className="text-xs text-gray-400 uppercase tracking-wide">MTBF</span>
        </div>
        <p className="text-2xl font-display font-bold text-white">{data.mtbf}<span className="text-sm text-gray-500 ml-1">hrs</span></p>
      </motion.div>
      
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3, delay: 0.5 }}
        className="glass-panel p-4"
      >
        <div className="flex items-center gap-2 mb-2">
          <Clock className="w-4 h-4 text-[#ffaa00]" />
          <span className="text-xs text-gray-400 uppercase tracking-wide">MTTR</span>
        </div>
        <p className="text-2xl font-display font-bold text-white">{data.mttr.toFixed(1)}<span className="text-sm text-gray-500 ml-1">hrs</span></p>
      </motion.div>
      
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3, delay: 0.6 }}
        className="glass-panel p-4"
      >
        <div className="flex items-center gap-2 mb-2">
          <Zap className="w-4 h-4 text-[#00ff88]" />
          <span className="text-xs text-gray-400 uppercase tracking-wide">Energy Eff.</span>
        </div>
        <p className="text-2xl font-display font-bold text-white">{data.energyEfficiency.toFixed(1)}<span className="text-sm text-gray-500 ml-1">%</span></p>
      </motion.div>
      
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3, delay: 0.7 }}
        className="glass-panel p-4"
      >
        <div className="flex items-center gap-2 mb-2">
          <Target className="w-4 h-4 text-[#00d9ff]" />
          <span className="text-xs text-gray-400 uppercase tracking-wide">Throughput</span>
        </div>
        <p className="text-2xl font-display font-bold text-white">{data.throughput}<span className="text-sm text-gray-500 ml-1">/hr</span></p>
      </motion.div>
    </div>
  );
}
