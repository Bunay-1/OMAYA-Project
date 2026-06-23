import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { 
  Calendar, 
  ChevronLeft, 
  ChevronRight, 
  Clock, 
  User, 
  DollarSign,
  CheckCircle,
  AlertCircle,
  Loader2,
  CalendarDays
} from 'lucide-react';
import type { MaintenanceEvent } from '@/types/omaya';
import { cn } from '@/lib/utils';

interface MaintenanceCalendarProps {
  events: MaintenanceEvent[];
}

const statusConfig = {
  scheduled: { color: 'text-[#00d9ff]', bg: 'bg-[#00d9ff]/10', icon: CalendarDays },
  in_progress: { color: 'text-[#ffaa00]', bg: 'bg-[#ffaa00]/10', icon: Loader2 },
  completed: { color: 'text-[#00ff88]', bg: 'bg-[#00ff88]/10', icon: CheckCircle },
  overdue: { color: 'text-[#ff3366]', bg: 'bg-[#ff3366]/10', icon: AlertCircle }
};

const typeConfig = {
  preventive: { color: 'text-[#00d9ff]', label: 'Preventive' },
  corrective: { color: 'text-[#ff3366]', label: 'Corrective' },
  predictive: { color: 'text-[#00ff88]', label: 'Predictive' }
};

export function MaintenanceCalendar({ events }: MaintenanceCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<'calendar' | 'list'>('list');

  const currentMonth = currentDate.getMonth();
  const currentYear = currentDate.getFullYear();

  const monthEvents = useMemo(() => {
    return events.filter(event => {
      const eventDate = new Date(event.scheduledDate);
      return eventDate.getMonth() === currentMonth && eventDate.getFullYear() === currentYear;
    });
  }, [events, currentMonth, currentYear]);

  const upcomingEvents = useMemo(() => {
    const now = new Date();
    return events
      .filter(event => new Date(event.scheduledDate) >= now || event.status === 'in_progress')
      .sort((a, b) => new Date(a.scheduledDate).getTime() - new Date(b.scheduledDate).getTime())
      .slice(0, 10);
  }, [events]);

  const stats = useMemo(() => ({
    scheduled: events.filter(e => e.status === 'scheduled').length,
    inProgress: events.filter(e => e.status === 'in_progress').length,
    completed: events.filter(e => e.status === 'completed').length,
    overdue: events.filter(e => e.status === 'overdue').length
  }), [events]);

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      newDate.setMonth(prev.getMonth() + (direction === 'next' ? 1 : -1));
      return newDate;
    });
  };

  return (
    <div className="glass-panel p-6 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#00d9ff]/10 border border-[#00d9ff]/30 flex items-center justify-center">
            <Calendar className="w-5 h-5 text-[#00d9ff]" />
          </div>
          <div>
            <h3 className="text-lg font-display font-bold text-white">Maintenance Calendar</h3>
            <p className="text-xs text-gray-400">{events.length} scheduled events</p>
          </div>
        </div>
        <div className="flex gap-1">
          <button
            onClick={() => setView('list')}
            className={cn(
              "px-3 py-1.5 rounded-lg text-xs font-medium transition-all",
              view === 'list' ? "bg-white/10 text-white" : "text-gray-500 hover:text-white"
            )}
          >
            List
          </button>
          <button
            onClick={() => setView('calendar')}
            className={cn(
              "px-3 py-1.5 rounded-lg text-xs font-medium transition-all",
              view === 'calendar' ? "bg-white/10 text-white" : "text-gray-500 hover:text-white"
            )}
          >
            Calendar
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-3 mb-6">
        <div className="glass-panel p-3 text-center">
          <p className="text-xl font-display font-bold text-[#00d9ff]">{stats.scheduled}</p>
          <p className="text-[10px] text-gray-400">Scheduled</p>
        </div>
        <div className="glass-panel p-3 text-center">
          <p className="text-xl font-display font-bold text-[#ffaa00]">{stats.inProgress}</p>
          <p className="text-[10px] text-gray-400">In Progress</p>
        </div>
        <div className="glass-panel p-3 text-center">
          <p className="text-xl font-display font-bold text-[#00ff88]">{stats.completed}</p>
          <p className="text-[10px] text-gray-400">Completed</p>
        </div>
        <div className="glass-panel p-3 text-center">
          <p className="text-xl font-display font-bold text-[#ff3366]">{stats.overdue}</p>
          <p className="text-[10px] text-gray-400">Overdue</p>
        </div>
      </div>

      {view === 'calendar' ? (
        <>
          {/* Month Navigation */}
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => navigateMonth('prev')}
              className="p-2 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-all"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <h4 className="text-lg font-display font-bold text-white">
              {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </h4>
            <button
              onClick={() => navigateMonth('next')}
              className="p-2 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-all"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>

          {/* Calendar Grid */}
          <div className="flex-1 overflow-y-auto scrollbar-thin">
            <CalendarGrid 
              currentDate={currentDate} 
              events={monthEvents} 
            />
          </div>
        </>
      ) : (
        /* List View */
        <div className="flex-1 overflow-y-auto scrollbar-thin space-y-2">
          {upcomingEvents.map((event, index) => (
            <MaintenanceEventCard key={event.id} event={event} delay={index * 0.03} />
          ))}
        </div>
      )}
    </div>
  );
}

interface CalendarGridProps {
  currentDate: Date;
  events: MaintenanceEvent[];
}

function CalendarGrid({ currentDate, events }: CalendarGridProps) {
  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();
  
  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);
  const blanks = Array.from({ length: firstDayOfMonth }, (_, i) => i);
  
  const getEventsForDay = (day: number) => {
    return events.filter(event => {
      const eventDate = new Date(event.scheduledDate);
      return eventDate.getDate() === day;
    });
  };

  return (
    <div>
      {/* Day Headers */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
          <div key={day} className="text-center text-xs text-gray-500 py-2">
            {day}
          </div>
        ))}
      </div>
      
      {/* Calendar Days */}
      <div className="grid grid-cols-7 gap-1">
        {blanks.map(i => (
          <div key={`blank-${i}`} className="aspect-square" />
        ))}
        {days.map(day => {
          const dayEvents = getEventsForDay(day);
          const isToday = new Date().getDate() === day && 
                          new Date().getMonth() === currentDate.getMonth() &&
                          new Date().getFullYear() === currentDate.getFullYear();
          
          return (
            <div
              key={day}
              className={cn(
                "aspect-square rounded-lg p-1 text-center relative transition-all hover:bg-white/10 cursor-pointer",
                isToday && "ring-1 ring-[#00ff88]",
                dayEvents.length > 0 && "bg-white/5"
              )}
            >
              <span className={cn(
                "text-xs",
                isToday ? "text-[#00ff88] font-bold" : "text-gray-400"
              )}>
                {day}
              </span>
              {dayEvents.length > 0 && (
                <div className="absolute bottom-1 left-1/2 -translate-x-1/2 flex gap-0.5">
                  {dayEvents.slice(0, 3).map((event, i) => (
                    <div
                      key={i}
                      className={cn(
                        "w-1.5 h-1.5 rounded-full",
                        statusConfig[event.status].color.replace('text-', 'bg-')
                      )}
                    />
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

interface MaintenanceEventCardProps {
  event: MaintenanceEvent;
  delay: number;
}

function MaintenanceEventCard({ event, delay }: MaintenanceEventCardProps) {
  const status = statusConfig[event.status];
  const type = typeConfig[event.type];
  const StatusIcon = status.icon;
  const eventDate = new Date(event.scheduledDate);
  
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2, delay }}
      className={cn(
        "p-4 rounded-xl border transition-all hover:bg-white/5 cursor-pointer",
        status.bg,
        status.color.replace('text-', 'border-').replace(']', '/30]')
      )}
    >
      <div className="flex items-start gap-3">
        <div className={cn(
          "w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0",
          status.bg
        )}>
          <StatusIcon className={cn("w-5 h-5", status.color, event.status === 'in_progress' && "animate-spin")} />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <p className="text-sm font-medium text-white truncate">{event.machineName}</p>
            <span className={cn("text-[10px] px-2 py-0.5 rounded-full", type.color, type.color.replace('text-', 'bg-').replace(']', '/20]'))}>
              {type.label}
            </span>
          </div>
          <p className="text-xs text-gray-400 line-clamp-1">{event.description}</p>
          
          <div className="flex items-center gap-4 mt-2">
            <div className="flex items-center gap-1">
              <Calendar className="w-3 h-3 text-gray-500" />
              <span className="text-[10px] text-gray-400 font-mono">
                {eventDate.toLocaleDateString()}
              </span>
            </div>
            {event.technician && (
              <div className="flex items-center gap-1">
                <User className="w-3 h-3 text-gray-500" />
                <span className="text-[10px] text-gray-400">{event.technician}</span>
              </div>
            )}
            {event.duration && (
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3 text-gray-500" />
                <span className="text-[10px] text-gray-400">{event.duration}min</span>
              </div>
            )}
          </div>
        </div>
        
        <div className="text-right flex-shrink-0">
          <p className={cn("text-xs font-medium capitalize", status.color)}>
            {event.status.replace('_', ' ')}
          </p>
          {event.cost && (
            <p className="text-[10px] text-gray-500 mt-1">
              ${event.cost.toLocaleString()}
            </p>
          )}
        </div>
      </div>
    </motion.div>
  );
}
