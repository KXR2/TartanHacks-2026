import { useState } from "react";
import { Toolbar } from "./components/Toolbar";
import { RecordingPanel } from "./components/RecordingPanel";
import { PreviewWindow } from "./components/PreviewWindow";
import { PropertiesPanel } from "./components/PropertiesPanel";
import { Timeline } from "./components/Timeline";
import { PlaybackControls } from "./components/PlaybackControls";
import { RecordingModal } from "./components/RecordingModal";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "./components/ui/resizable";

export default function App() {
  const [isRecordingModalOpen, setIsRecordingModalOpen] = useState(false);
  const [recordingMode, setRecordingMode] = useState<"screen" | "camera">("screen");

  const handleRecordScreen = () => {
    setRecordingMode("screen");
    setIsRecordingModalOpen(true);
  };

  const handleRecordCamera = () => {
    setRecordingMode("camera");
    setIsRecordingModalOpen(true);
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-background">
      {/* Top Toolbar */}
      <Toolbar />

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden">
        <ResizablePanelGroup direction="horizontal">
          {/* Left Sidebar - Recording & Media */}
          <ResizablePanel defaultSize={20} minSize={15} maxSize={30}>
            <RecordingPanel
              onRecordScreen={handleRecordScreen}
              onRecordCamera={handleRecordCamera}
            />
          </ResizablePanel>

          <ResizableHandle />

          {/* Center - Preview and Timeline */}
          <ResizablePanel defaultSize={60} minSize={40}>
            <ResizablePanelGroup direction="vertical">
              {/* Preview Window */}
              <ResizablePanel defaultSize={70} minSize={40}>
                <div className="h-full flex flex-col">
                  <PreviewWindow />
                  <PlaybackControls />
                </div>
              </ResizablePanel>

              <ResizableHandle />

              {/* Timeline */}
              <ResizablePanel defaultSize={30} minSize={15}>
                <Timeline />
              </ResizablePanel>
            </ResizablePanelGroup>
          </ResizablePanel>

          <ResizableHandle />

          {/* Right Sidebar - Properties */}
          <ResizablePanel defaultSize={20} minSize={15} maxSize={30}>
            <PropertiesPanel />
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>

      {/* Recording Modal */}
      <RecordingModal
        isOpen={isRecordingModalOpen}
        onClose={() => setIsRecordingModalOpen(false)}
        defaultMode={recordingMode}
      />
    </div>
  );
}