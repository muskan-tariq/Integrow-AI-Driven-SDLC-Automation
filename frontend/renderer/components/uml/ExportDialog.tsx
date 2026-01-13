"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { FileImage, FileCode, Download } from "lucide-react";

interface ExportDialogProps {
  open: boolean;
  onClose: () => void;
  onExport: (format: "svg" | "png" | "code") => void;
  diagramId: string;
}

export default function ExportDialog({
  open,
  onClose,
  onExport,
  diagramId,
}: ExportDialogProps) {
  const handleExport = (format: "svg" | "png" | "code") => {
    onExport(format);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Export Diagram</DialogTitle>
          <DialogDescription>
            Choose the format to export your UML diagram
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-3 py-4">
          <Button
            variant="outline"
            className="justify-start h-auto py-4"
            onClick={() => handleExport("svg")}
          >
            <div className="flex items-start gap-3">
              <FileImage className="h-5 w-5 mt-0.5" />
              <div className="text-left">
                <div className="font-semibold">SVG (Vector)</div>
                <div className="text-sm text-muted-foreground">
                  Scalable vector graphics - best for web and presentations
                </div>
              </div>
            </div>
          </Button>

          <Button
            variant="outline"
            className="justify-start h-auto py-4"
            onClick={() => handleExport("png")}
          >
            <div className="flex items-start gap-3">
              <FileImage className="h-5 w-5 mt-0.5" />
              <div className="text-left">
                <div className="font-semibold">PNG (Raster)</div>
                <div className="text-sm text-muted-foreground">
                  Portable Network Graphics - best for documents and reports
                </div>
              </div>
            </div>
          </Button>

          <Button
            variant="outline"
            className="justify-start h-auto py-4"
            onClick={() => handleExport("code")}
          >
            <div className="flex items-start gap-3">
              <FileCode className="h-5 w-5 mt-0.5" />
              <div className="text-left">
                <div className="font-semibold">PlantUML Code</div>
                <div className="text-sm text-muted-foreground">
                  Source code (.puml) - editable in any PlantUML editor
                </div>
              </div>
            </div>
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
