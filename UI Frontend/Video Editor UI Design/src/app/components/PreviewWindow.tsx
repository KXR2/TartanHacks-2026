export function PreviewWindow() {
  return (
    <div className="h-full flex flex-col bg-background">
      <div className="p-3 border-b flex items-center justify-between">
        <h3 className="font-semibold">Preview</h3>
        <div className="flex items-center gap-2">
          <select className="text-sm border rounded px-2 py-1">
            <option>Fit</option>
            <option>25%</option>
            <option>50%</option>
            <option>75%</option>
            <option>100%</option>
            <option>150%</option>
            <option>200%</option>
          </select>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center bg-zinc-950 p-4">
        <div className="relative bg-black aspect-video w-full max-w-full max-h-full flex items-center justify-center border border-zinc-800">
          {/* Preview Canvas */}
          <div className="absolute inset-0 flex items-center justify-center text-zinc-600">
            <div className="text-center">
              <div className="text-6xl mb-2">▶</div>
              <p className="text-sm">No media in timeline</p>
            </div>
          </div>

          {/* Timecode overlay */}
          <div className="absolute top-2 left-2 bg-black/80 px-2 py-1 rounded text-sm font-mono text-white">
            00:00:00:00
          </div>

          {/* Resolution indicator */}
          <div className="absolute top-2 right-2 bg-black/80 px-2 py-1 rounded text-sm text-white">
            1920 × 1080
          </div>
        </div>
      </div>
    </div>
  );
}
