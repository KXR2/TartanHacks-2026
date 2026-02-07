import { useState } from "react";
import { Button } from "./ui/button";
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Maximize2,
} from "lucide-react";

export function PlaybackControls() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const totalDuration = 45; // Video duration in seconds

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const frames = Math.floor((seconds % 1) * 30);
    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}:${frames.toString().padStart(2, "0")}`;
  };

  return (
    <div className="h-16 border-t bg-background px-4 flex items-center gap-4">
      {/* Playback Controls */}
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon">
          <SkipBack className="h-4 w-4" />
        </Button>
        <Button
          variant="default"
          size="icon"
          onClick={() => setIsPlaying(!isPlaying)}
        >
          {isPlaying ? (
            <Pause className="h-4 w-4" />
          ) : (
            <Play className="h-4 w-4 ml-0.5" />
          )}
        </Button>
        <Button variant="ghost" size="icon">
          <SkipForward className="h-4 w-4" />
        </Button>
      </div>

      {/* Timecode */}
      <div className="flex items-center gap-2">
        <span className="font-mono text-sm">{formatTime(currentTime)}</span>
        <span className="text-muted-foreground text-sm">/</span>
        <span className="font-mono text-sm text-muted-foreground">
          {formatTime(totalDuration)}
        </span>
      </div>

      {/* Fullscreen */}
      <Button variant="ghost" size="icon" className="ml-auto">
        <Maximize2 className="h-4 w-4" />
      </Button>
    </div>
  );
}