'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Loader2, AlertTriangle, Trash2 } from 'lucide-react';

interface RequirementSummary {
  id: string;
  version: number;
  raw_text: string;
}

interface DeleteRequirementDialogProps {
  requirement: RequirementSummary | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onDelete: (reqId: string) => Promise<void>;
}

export function DeleteRequirementDialog({
  requirement,
  open,
  onOpenChange,
  onDelete,
}: DeleteRequirementDialogProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!requirement) return;
    
    setIsDeleting(true);
    try {
      await onDelete(requirement.id);
      onOpenChange(false);
    } catch (error) {
      console.error('Delete failed:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleClose = () => {
    if (!isDeleting) {
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-red-600">
            <AlertTriangle className="h-5 w-5" />
            Delete Requirement
          </DialogTitle>
          <DialogDescription>
            Are you sure you want to delete <strong>Requirement v{requirement?.version}</strong>?
            <br />
            <span className="text-xs text-muted-foreground block mt-1 line-clamp-2">
              "{requirement?.raw_text.substring(0, 100)}..."
            </span>
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          <div className="text-sm text-muted-foreground">
            This action cannot be undone. It will permanently remove:
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>The requirement from the database</li>
              <li>Associated user stories and analysis</li>
              <li>Files from the Git repository (local & remote)</li>
            </ul>
          </div>
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={isDeleting}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={isDeleting}
            className="gap-2"
          >
            {isDeleting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Deleting...
              </>
            ) : (
              <>
                <Trash2 className="h-4 w-4" />
                Delete
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
