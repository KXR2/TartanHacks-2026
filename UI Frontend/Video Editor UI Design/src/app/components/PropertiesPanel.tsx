import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { ScrollArea } from "./ui/scroll-area";
import { Label } from "./ui/label";
import { Input } from "./ui/input";
import { Slider } from "./ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Switch } from "./ui/switch";

export function PropertiesPanel() {
  return (
    <div className="h-full flex flex-col bg-background">
      <div className="p-3 border-b">
        <h3 className="font-semibold">Properties</h3>
      </div>

      <Tabs defaultValue="video" className="flex-1 flex flex-col">
        <TabsList className="w-full grid grid-cols-2 rounded-none border-b h-10">
          <TabsTrigger value="video" className="text-xs">Transform</TabsTrigger>
          <TabsTrigger value="effects" className="text-xs">Effects</TabsTrigger>
        </TabsList>

        <TabsContent value="video" className="flex-1 mt-0">
          <ScrollArea className="h-full">
            <div className="p-4 space-y-4">
              <div className="space-y-2">
                <Label>Position</Label>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <Label className="text-xs text-muted-foreground">X</Label>
                    <Input type="number" defaultValue="0" className="h-8" />
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">Y</Label>
                    <Input type="number" defaultValue="0" className="h-8" />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Scale</Label>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <Label className="text-xs text-muted-foreground">Width</Label>
                    <Input type="number" defaultValue="100" className="h-8" />
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">Height</Label>
                    <Input type="number" defaultValue="100" className="h-8" />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Rotation</Label>
                <Input type="number" defaultValue="0" className="h-8" />
              </div>

              <div className="space-y-2">
                <Label>Opacity</Label>
                <Slider defaultValue={[100]} max={100} step={1} />
                <div className="text-right text-xs text-muted-foreground">100%</div>
              </div>

              <div className="space-y-2">
                <Label>Blend Mode</Label>
                <Select defaultValue="normal">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="normal">Normal</SelectItem>
                    <SelectItem value="multiply">Multiply</SelectItem>
                    <SelectItem value="screen">Screen</SelectItem>
                    <SelectItem value="overlay">Overlay</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </ScrollArea>
        </TabsContent>

        <TabsContent value="effects" className="flex-1 mt-0">
          <ScrollArea className="h-full">
            <div className="p-4 space-y-4">
              <div className="space-y-2">
                <Label>Brightness</Label>
                <Slider defaultValue={[0]} min={-100} max={100} step={1} />
                <div className="text-right text-xs text-muted-foreground">0</div>
              </div>

              <div className="space-y-2">
                <Label>Contrast</Label>
                <Slider defaultValue={[0]} min={-100} max={100} step={1} />
                <div className="text-right text-xs text-muted-foreground">0</div>
              </div>

              <div className="space-y-2">
                <Label>Saturation</Label>
                <Slider defaultValue={[0]} min={-100} max={100} step={1} />
                <div className="text-right text-xs text-muted-foreground">0</div>
              </div>

              <div className="space-y-2">
                <Label>Blur</Label>
                <Slider defaultValue={[0]} max={20} step={0.1} />
                <div className="text-right text-xs text-muted-foreground">0</div>
              </div>

              <div className="space-y-2">
                <Label>Hue</Label>
                <Slider defaultValue={[0]} min={0} max={360} step={1} />
                <div className="text-right text-xs text-muted-foreground">0°</div>
              </div>

              <div className="flex items-center justify-between">
                <Label>Black & White</Label>
                <Switch />
              </div>

              <div className="flex items-center justify-between">
                <Label>Invert Colors</Label>
                <Switch />
              </div>
            </div>
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
  );
}