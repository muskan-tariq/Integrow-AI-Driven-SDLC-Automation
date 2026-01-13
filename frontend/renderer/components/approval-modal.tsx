'use client';

import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';
import { GitCommit, AlertTriangle, CheckCircle2, Loader2, ExternalLink } from 'lucide-react';

interface ApprovalModalProps {
  isOpen: boolean;
  onClose: () => void;
  requirementId: string;
  qualityScore: number;
  totalIssues: number;
  requirementText: string;
  onApprove?: (commitMessage: string, branch: string) => Promise<{ commit_url: string; version: number }>;
}

export function ApprovalModal({
  isOpen,
  onClose,
  requirementId,
  qualityScore,
  totalIssues,
  requirementText,
  onApprove,
}: ApprovalModalProps) {
  const [commitMessage, setCommitMessage] = useState(
    `Add requirements v1 - ${requirementText.substring(0, 50)}${requirementText.length > 50 ? '...' : ''}`
  );
  const [selectedBranch, setSelectedBranch] = useState('main');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [commitResult, setCommitResult] = useState<{ commit_url: string; version: number } | null>(null);

  const handleApprove = async () => {
    if (!onApprove) return;

    setIsSubmitting(true);
    try {
      const result = await onApprove(commitMessage, selectedBranch);
      setCommitResult(result);
    } catch (error) {
      console.error('Approval failed:', error);
      alert('Failed to commit requirements. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setCommitResult(null);
    onClose();
  };

  if (commitResult) {
    return (
      <Dialog open={isOpen} onOpenChange={handleClose}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-green-600">
              <CheckCircle2 className="h-5 w-5" />
              Requirements Approved!
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <GitCommit className="h-8 w-8 text-green-600" />
              </div>
              <p className="text-sm text-gray-600 mb-4">
                Your requirements have been committed to GitHub successfully!
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Version:</span>
                <Badge variant="outline">v{commitResult.version}</Badge>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Branch:</span>
                <Badge variant="outline">{selectedBranch}</Badge>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">File:</span>
                <span className="text-xs font-mono">
                  .integrow/requirements/requirements_v{commitResult.version}.yaml
                </span>
              </div>
            </div>

            <Button
              className="w-full gap-2"
              onClick={() => window.open(commitResult.commit_url, '_blank')}
            >
              <ExternalLink className="h-4 w-4" />
              View on GitHub
            </Button>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={handleClose}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <GitCommit className="h-5 w-5" />
            Approve & Commit Requirements
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Quality Warning */}
          {qualityScore < 80 && (
            <div className="flex items-start gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-yellow-800">Quality Score Below 80%</p>
                <p className="text-xs text-yellow-700 mt-1">
                  Consider resolving the {totalIssues} issue{totalIssues !== 1 ? 's' : ''} found before approving.
                  You can still proceed, but improving the requirements is recommended.
                </p>
              </div>
            </div>
          )}

          {/* Summary */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Quality Score</p>
              <p className={`text-2xl font-bold ${
                qualityScore >= 80 ? 'text-green-600' :
                qualityScore >= 60 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {qualityScore}%
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Issues Found</p>
              <p className="text-2xl font-bold text-gray-900">{totalIssues}</p>
            </div>
          </div>

          {/* Branch Selection */}
          <div className="space-y-3">
            <Label className="text-sm font-medium">Target Branch</Label>
            <RadioGroup value={selectedBranch} onValueChange={setSelectedBranch}>
              <div className="flex gap-4">
                <div
                  className={`flex items-center space-x-2 flex-1 rounded-lg border p-3 cursor-pointer transition-colors ${
                    selectedBranch === 'main'
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                  onClick={() => setSelectedBranch('main')}
                >
                  <RadioGroupItem value="main" id="branch-main" />
                  <Label htmlFor="branch-main" className="cursor-pointer font-medium">
                    main
                  </Label>
                </div>
                <div
                  className={`flex items-center space-x-2 flex-1 rounded-lg border p-3 cursor-pointer transition-colors ${
                    selectedBranch === 'develop'
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                  onClick={() => setSelectedBranch('develop')}
                >
                  <RadioGroupItem value="develop" id="branch-develop" />
                  <Label htmlFor="branch-develop" className="cursor-pointer font-medium">
                    develop
                  </Label>
                </div>
              </div>
            </RadioGroup>
          </div>

          {/* Commit Message */}
          <div className="space-y-3">
            <Label htmlFor="commit-message" className="text-sm font-medium">
              Commit Message
            </Label>
            <Textarea
              id="commit-message"
              value={commitMessage}
              onChange={(e) => setCommitMessage(e.target.value)}
              placeholder="Enter commit message..."
              rows={3}
              className="resize-none"
            />
          </div>

          {/* Preview */}
          <div className="space-y-3">
            <Label className="text-sm font-medium">What will be committed:</Label>
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full" />
                <span className="font-mono text-xs">
                  .integrow/requirements/requirements_v1.yaml
                </span>
              </div>
              <div className="text-xs text-gray-600 ml-4">
                Structured requirements with analysis results
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            onClick={handleApprove}
            disabled={isSubmitting || !commitMessage.trim()}
            className="gap-2"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Committing...
              </>
            ) : (
              <>
                <GitCommit className="h-4 w-4" />
                Approve & Commit
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
