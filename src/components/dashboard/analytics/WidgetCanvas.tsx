import { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Trash2, Copy, Settings, Maximize2, GripVertical } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { WidgetRenderer } from './WidgetRenderer';
import type { AnalyticsWidget } from '@/lib/analytics-engine';

interface WidgetCanvasProps {
  widgets: AnalyticsWidget[];
  selectedWidget: string | null;
  onSelectWidget: (id: string | null) => void;
  onUpdateWidget: (id: string, updates: Partial<AnalyticsWidget>) => void;
  onDeleteWidget: (id: string) => void;
  onDuplicateWidget: (id: string) => void;
}

export function WidgetCanvas({
  widgets,
  selectedWidget,
  onSelectWidget,
  onUpdateWidget,
  onDeleteWidget,
  onDuplicateWidget
}: WidgetCanvasProps) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [dragging, setDragging] = useState<string | null>(null);
  const [resizing, setResizing] = useState<string | null>(null);

  const handleDragStart = (id: string) => {
    setDragging(id);
    onSelectWidget(id);
  };

  const handleDrag = (id: string, e: React.MouseEvent) => {
    if (dragging !== id) return;
    
    const widget = widgets.find(w => w.id === id);
    if (!widget) return;

    onUpdateWidget(id, {
      position: {
        x: widget.position.x + e.movementX,
        y: widget.position.y + e.movementY
      }
    });
  };

  const handleDragEnd = () => {
    setDragging(null);
  };

  if (widgets.length === 0) {
    return (
      <div className="h-full flex items-center justify-center bg-slate-950">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-800 mb-4">
            <motion.div
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <Maximize2 className="w-8 h-8 text-slate-400" />
            </motion.div>
          </div>
          <h3 className="text-lg font-medium text-slate-300 mb-2">
            Empty Canvas
          </h3>
          <p className="text-sm text-slate-500 mb-4">
            Click "Add Widget" to start building your dashboard
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={canvasRef}
      className="relative h-full bg-slate-950 overflow-auto"
      style={{
        backgroundImage: `
          linear-gradient(to right, rgba(51, 65, 85, 0.1) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(51, 65, 85, 0.1) 1px, transparent 1px)
        `,
        backgroundSize: '20px 20px'
      }}
      onClick={() => onSelectWidget(null)}
    >
      {widgets.map((widget) => {
        const isSelected = selectedWidget === widget.id;
        const isDragging = dragging === widget.id;

        return (
          <motion.div
            key={widget.id}
            className="absolute"
            style={{
              left: widget.position.x,
              top: widget.position.y,
              width: widget.size.w,
              height: widget.size.h,
              cursor: isDragging ? 'grabbing' : 'default',
              zIndex: isSelected ? 10 : 1
            }}
            animate={{
              scale: isDragging ? 1.02 : 1,
              opacity: isDragging ? 0.9 : 1
            }}
            onClick={(e) => {
              e.stopPropagation();
              onSelectWidget(widget.id);
            }}
          >
            <Card
              className={`h-full backdrop-blur-sm transition-all ${
                isSelected
                  ? 'ring-2 ring-purple-500 bg-slate-900/90 shadow-xl shadow-purple-500/20'
                  : 'bg-slate-900/70 hover:bg-slate-900/80'
              }`}
            >
              {/* Widget Header */}
              <div
                className={`flex items-center justify-between p-3 border-b cursor-grab active:cursor-grabbing ${
                  isSelected ? 'border-purple-500/30' : 'border-slate-800'
                }`}
                onMouseDown={() => handleDragStart(widget.id)}
                onMouseMove={(e) => handleDrag(widget.id, e)}
                onMouseUp={handleDragEnd}
                onMouseLeave={handleDragEnd}
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <GripVertical className="w-4 h-4 text-slate-500 flex-shrink-0" />
                  <h3 className="font-medium text-sm text-white truncate">
                    {widget.title}
                  </h3>
                </div>

                {isSelected && (
                  <div className="flex items-center gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 hover:bg-slate-800"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDuplicateWidget(widget.id);
                      }}
                    >
                      <Copy className="w-3.5 h-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 hover:bg-slate-800"
                      onClick={(e) => {
                        e.stopPropagation();
                        // Open settings modal
                      }}
                    >
                      <Settings className="w-3.5 h-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 hover:bg-red-900/50 hover:text-red-400"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteWidget(widget.id);
                      }}
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                )}
              </div>

              {/* Widget Content */}
              <div className="p-4 h-[calc(100%-60px)] overflow-auto">
                <WidgetRenderer widget={widget} />
              </div>

              {/* Resize Handle */}
              {isSelected && (
                <div
                  className="absolute bottom-0 right-0 w-4 h-4 cursor-nwse-resize bg-purple-500/50 hover:bg-purple-500"
                  style={{ clipPath: 'polygon(100% 0, 100% 100%, 0 100%)' }}
                  onMouseDown={(e) => {
                    e.stopPropagation();
                    setResizing(widget.id);
                  }}
                />
              )}
            </Card>
          </motion.div>
        );
      })}
    </div>
  );
}
