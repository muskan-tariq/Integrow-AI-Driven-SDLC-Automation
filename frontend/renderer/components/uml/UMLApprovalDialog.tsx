import { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Loader2, GitCommit, UploadCloud } from "lucide-react";

interface UMLApprovalDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: (message: string) => Promise<void>;
  isLoading: boolean;
  defaultMessage?: string;
}

export default function UMLApprovalDialog({ 
  open, 
  onClose, 
  onConfirm,
  isLoading,
  defaultMessage = ""
}: UMLApprovalDialogProps) {
  const [message, setMessage] = useState(defaultMessage);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    await onConfirm(message);
    setMessage(""); // Reset after success
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <UploadCloud className="h-5 w-5" />
            Push to Repository
          </DialogTitle>
          <DialogDescription>
            This will save the UML diagram files (.puml and .svg) to your local repository and push them to the remote "main" branch.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="commit-message">Commit Message</Label>
            <div className="relative">
              <GitCommit className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                id="commit-message"
                placeholder="docs: update UML diagram"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="pl-9"
                disabled={isLoading}
                required
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
              Cancel
            </Button>
            <Button type="submit" disabled={!message.trim() || isLoading} className="gap-2">
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Pushing...
                </>
              ) : (
                <>
                  <UploadCloud className="h-4 w-4" />
                  Push Changes
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
