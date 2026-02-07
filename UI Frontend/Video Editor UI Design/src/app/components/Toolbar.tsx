import { Button } from "./ui/button";
import {
  Menu,
  Save,
  Undo,
  Redo,
  Scissors,
  Copy,
  Clipboard,
  ChevronDown,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";

export function Toolbar() {
  return (
    <div className="h-14 border-b bg-background px-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        {/* File Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm">
              <Menu className="h-4 w-4 mr-2" />
              File
              <ChevronDown className="h-3 w-3 ml-1" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuItem>New Project</DropdownMenuItem>
            <DropdownMenuItem>Open Project</DropdownMenuItem>
            <DropdownMenuItem>Save Project</DropdownMenuItem>
            <DropdownMenuItem>Save As...</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Export Video</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm">
              Edit
              <ChevronDown className="h-3 w-3 ml-1" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuItem>Undo</DropdownMenuItem>
            <DropdownMenuItem>Redo</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Cut</DropdownMenuItem>
            <DropdownMenuItem>Copy</DropdownMenuItem>
            <DropdownMenuItem>Paste</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Split at Playhead</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <div className="h-6 w-px bg-border mx-2" />

        {/* Quick Actions */}
        <Button variant="ghost" size="icon" title="Save">
          <Save className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" title="Undo">
          <Undo className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" title="Redo">
          <Redo className="h-4 w-4" />
        </Button>

        <div className="h-6 w-px bg-border mx-2" />

        {/* Edit Tools */}
        <Button variant="ghost" size="icon" title="Cut">
          <Scissors className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" title="Copy">
          <Copy className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" title="Paste">
          <Clipboard className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground">Untitled Project</span>
      </div>
    </div>
  );
}