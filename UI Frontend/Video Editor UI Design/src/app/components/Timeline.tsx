import { useState, useRef } from "react";
import { Button } from "./ui/button";
import { ZoomIn, ZoomOut } from "lucide-react";

export function Timeline() {
  const [zoom, setZoom] = useState(1);
  const [playheadPosition, setPlayheadPosition] = useState(0);
  const timelineRef = useRef<HTMLDivElement>(null);

  const pixelsPerSecond = 15 * zoom;
  const totalDuration = 120; // Total duration in seconds
  const timelineWidth = totalDuration * pixelsPerSecond;

  // Generate time markers every 5 seconds
  const markers = [];
  for (let i = 0; i <= totalDuration; i += 5) {
    markers.push(i);
  }

  const handleTimelineClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (timelineRef.current) {
      const rect = timelineRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left + timelineRef.current.scrollLeft;
      const time = x / pixelsPerSecond;
      setPlayheadPosition(Math.max(0, Math.min(time, totalDuration)));
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="h-32 flex flex-col bg-background border-t">
      {/* Timeline Header */}
      <div className="h-10 border-b px-4 flex items-center justify-between">
        <h3 className="font-semibold">Timeline</h3>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => setZoom(Math.max(0.5, zoom - 0.5))}
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="text-sm text-muted-foreground min-w-12 text-center">
            {Math.round(zoom * 100)}%
          </span>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => setZoom(Math.min(3, zoom + 0.5))}
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Scrollable Timeline */}
      <div className="flex-1 overflow-x-auto overflow-y-hidden" ref={timelineRef}>
        <div
          className="relative h-full bg-muted/30 cursor-pointer"
          style={{ width: timelineWidth }}
          onClick={handleTimelineClick}
        >
          {/* Time markers */}
          {markers.map((time) => (
            <div
              key={time}
              className="absolute top-0 bottom-0 flex flex-col items-center"
              style={{ left: time * pixelsPerSecond }}
            >
              <div className="w-px h-4 bg-border" />
              <span className="text-xs text-muted-foreground mt-1">
                {formatTime(time)}
              </span>
              {/* Vertical grid line */}
              <div className="absolute top-4 bottom-0 w-px bg-border/30" />
            </div>
          ))}

          {/* Playhead */}
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-red-500 pointer-events-none z-20"
            style={{ left: playheadPosition * pixelsPerSecond }}
          >
            <div
              className="absolute -top-1 -left-2 w-4 h-4 bg-red-500"
              style={{ clipPath: "polygon(50% 0%, 0% 100%, 100% 100%)" }}
            />
            <div className="absolute top-3 left-1/2 -translate-x-1/2 bg-red-500 px-1.5 py-0.5 rounded text-xs text-white font-mono whitespace-nowrap">
              {formatTime(playheadPosition)}
            </div>
          </div>

          {/* Example colored dots - these can be added dynamically */}
          <div
            className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-blue-500 border-2 border-background cursor-pointer hover:scale-125 transition-transform z-10"
            style={{ left: 10 * pixelsPerSecond }}
            title="Marker at 0:10"
          />
          <div
            className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-green-500 border-2 border-background cursor-pointer hover:scale-125 transition-transform z-10"
            style={{ left: 25 * pixelsPerSecond }}
            title="Marker at 0:25"
          />
          <div
            className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-yellow-500 border-2 border-background cursor-pointer hover:scale-125 transition-transform z-10"
            style={{ left: 50 * pixelsPerSecond }}
            title="Marker at 0:50"
          />
        </div>
      </div>
    </div>
  );
}
