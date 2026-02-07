import { Button } from "./ui/button";
import { ScrollArea } from "./ui/scroll-area";
import { Video, Folder, Circle, Monitor, Camera } from "lucide-react";
import { Separator } from "./ui/separator";

const mediaItems = [
  { id: 1, name: "intro.mp4", type: "video", duration: "0:15" },
  { id: 2, name: "scene1.mp4", type: "video", duration: "0:45" },
  { id: 3, name: "scene2.mp4", type: "video", duration: "0:30" },
  { id: 4, name: "transition.mp4", type: "video", duration: "0:05" },
  { id: 5, name: "outro.mp4", type: "video", duration: "0:20" },
  { id: 6, name: "demo.mp4", type: "video", duration: "1:15" },
];

interface RecordingPanelProps {
  onRecordScreen: () => void;
  onRecordCamera: () => void;
}

export function RecordingPanel({ onRecordScreen, onRecordCamera }: RecordingPanelProps) {
  return (
    <div className="h-full flex flex-col bg-background">
      {/* Recording Section */}
      <div className="p-3 border-b bg-muted/30">
        <h3 className="font-semibold mb-3">Record Video</h3>
        <div className="space-y-2">
          <Button 
            variant="destructive" 
            className="w-full justify-start h-12"
            onClick={onRecordScreen}
          >
            <Circle className="h-4 w-4 mr-2 fill-current" />
            <Monitor className="h-4 w-4 mr-2" />
            Record Screen
          </Button>
          <Button 
            variant="outline" 
            className="w-full justify-start h-12"
            onClick={onRecordCamera}
          >
            <Circle className="h-4 w-4 mr-2" />
            <Camera className="h-4 w-4 mr-2" />
            Record Camera
          </Button>
        </div>
      </div>

      <Separator />

      {/* Imported Videos Section */}
      <div className="flex-1 flex flex-col min-h-0">
        <div className="p-3 border-b">
          <h3 className="font-semibold">Imported Videos</h3>
        </div>

        <div className="p-3 border-b">
          <Button variant="outline" size="sm" className="w-full">
            <Folder className="h-4 w-4 mr-2" />
            Import Video
          </Button>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-3 space-y-2">
            {mediaItems.map((item) => (
              <MediaItem key={item.id} item={item} />
            ))}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
}

function MediaItem({ item }: { item: { id: number; name: string; type: string; duration: string } }) {
  return (
    <div className="aspect-video bg-muted rounded border flex flex-col items-center justify-center p-3 cursor-pointer hover:bg-accent transition-colors">
      <Video className="h-10 w-10 mb-2 text-muted-foreground" />
      <p className="text-sm truncate w-full text-center font-medium">{item.name}</p>
      <p className="text-xs text-muted-foreground">{item.duration}</p>
    </div>
  );
}
