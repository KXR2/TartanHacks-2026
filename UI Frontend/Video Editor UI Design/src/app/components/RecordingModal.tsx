import { useState } from "react";
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Circle, Square, Monitor, Camera, Mic, MicOff } from "lucide-react";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Switch } from "./ui/switch";

interface RecordingModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultMode?: "screen" | "camera";
}

export function RecordingModal({ isOpen, onClose, defaultMode = "screen" }: RecordingModalProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [micEnabled, setMicEnabled] = useState(true);
  const [recordingMode, setRecordingMode] = useState<"screen" | "camera">(defaultMode);

  const formatRecordingTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const handleStartRecording = () => {
    setIsRecording(true);
    // Simulate recording timer
    const interval = setInterval(() => {
      setRecordingTime((prev) => prev + 1);
    }, 1000);
    // Store interval ID to clear later
    (window as any).recordingInterval = interval;
  };

  const handleStopRecording = () => {
    setIsRecording(false);
    if ((window as any).recordingInterval) {
      clearInterval((window as any).recordingInterval);
    }
    setRecordingTime(0);
  };

  // Reset mode when modal opens
  const handleOpenChange = (open: boolean) => {
    if (open) {
      setRecordingMode(defaultMode);
    }
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            {recordingMode === "screen" ? "Record Screen" : "Record Camera"}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Preview Area */}
          <div className="aspect-video bg-black rounded-lg flex items-center justify-center relative overflow-hidden">
            {!isRecording ? (
              <div className="text-center text-muted-foreground">
                <div className="text-4xl mb-2">
                  {recordingMode === "screen" ? <Monitor className="h-16 w-16 mx-auto" /> : <Camera className="h-16 w-16 mx-auto" />}
                </div>
                <p className="text-sm">Click Start Recording to begin</p>
              </div>
            ) : (
              <>
                <div className="absolute inset-0 bg-gradient-to-br from-red-950/20 to-black" />
                <div className="relative z-10 text-center">
                  <Circle className="h-6 w-6 mx-auto mb-3 text-red-500 fill-red-500 animate-pulse" />
                  <div className="text-4xl font-mono text-white mb-2">
                    {formatRecordingTime(recordingTime)}
                  </div>
                  <p className="text-sm text-white/80">Recording in progress...</p>
                </div>
              </>
            )}
          </div>

          {/* Recording Settings */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {micEnabled ? <Mic className="h-4 w-4" /> : <MicOff className="h-4 w-4" />}
                <Label htmlFor="mic-toggle">Microphone</Label>
              </div>
              <Switch
                id="mic-toggle"
                checked={micEnabled}
                onCheckedChange={setMicEnabled}
                disabled={isRecording}
              />
            </div>

            {recordingMode === "screen" && (
              <div className="space-y-2">
                <Label>Screen Source</Label>
                <Select defaultValue="entire" disabled={isRecording}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="entire">Entire Screen</SelectItem>
                    <SelectItem value="window">Application Window</SelectItem>
                    <SelectItem value="tab">Browser Tab</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}

            {recordingMode === "camera" && (
              <div className="space-y-2">
                <Label>Camera Source</Label>
                <Select defaultValue="default" disabled={isRecording}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="default">Default Camera</SelectItem>
                    <SelectItem value="front">Front Camera</SelectItem>
                    <SelectItem value="back">Back Camera</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}

            <div className="space-y-2">
              <Label>Video Quality</Label>
              <Select defaultValue="1080p" disabled={isRecording}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="720p">720p HD</SelectItem>
                  <SelectItem value="1080p">1080p Full HD</SelectItem>
                  <SelectItem value="4k">4K Ultra HD</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Recording Controls */}
          <div className="flex gap-3">
            {!isRecording ? (
              <Button
                className="flex-1 h-12"
                onClick={handleStartRecording}
              >
                <Circle className="h-5 w-5 mr-2 fill-current" />
                Start Recording
              </Button>
            ) : (
              <Button
                variant="destructive"
                className="flex-1 h-12"
                onClick={handleStopRecording}
              >
                <Square className="h-5 w-5 mr-2 fill-current" />
                Stop Recording
              </Button>
            )}
            <Button variant="outline" onClick={onClose} disabled={isRecording}>
              Cancel
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}