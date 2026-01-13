import React, { useEffect, useState } from 'react';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Loader2, AlertTriangle, FileCode, CheckCircle2 } from 'lucide-react';
import { codeGenerationApi, ComparisonResult, FileDiff, ApproveCodeRequest } from '@/lib/api/code-generation';
import { useToast } from '@/components/ui/use-toast';

interface DiffPreviewModalProps {
    isOpen: boolean;
    onClose: () => void;
    sessionId: string;
    projectId: string; // Not strictly needed for the API call but useful context
    token: string;
    onApplySuccess: () => void;
}

export function DiffPreviewModal({
    isOpen,
    onClose,
    sessionId,
    token,
    onApplySuccess,
}: DiffPreviewModalProps) {
    const { toast } = useToast();
    const [loading, setLoading] = useState(false);
    const [applying, setApplying] = useState(false);
    const [comparison, setComparison] = useState<ComparisonResult | null>(null);
    const [selectedFile, setSelectedFile] = useState<string | null>(null);
    const [commitMessage, setCommitMessage] = useState('feat: apply generated code updates');

    useEffect(() => {
        if (isOpen && sessionId) {
            loadComparison();
        } else {
            setComparison(null);
            setSelectedFile(null);
        }
    }, [isOpen, sessionId]);

    const loadComparison = async () => {
        setLoading(true);
        try {
            const result = await codeGenerationApi.compareSession(sessionId, token);
            setComparison(result);
            if (result.diffs.length > 0) {
                setSelectedFile(result.diffs[0].file_path);
            }
        } catch (error) {
            console.error('Failed to load comparison:', error);
            toast({
                title: 'Error loading diff',
                description: 'Could not compare generated code with local files.',
                variant: 'destructive',
            });
            onClose();
        } finally {
            setLoading(false);
        }
    };

    const handleApply = async () => {
        if (!sessionId) return;
        setApplying(true);
        try {
            const request: ApproveCodeRequest = {
                session_id: sessionId,
                commit_message: commitMessage,
                branch: 'main', // Could be configurable
            };
            await codeGenerationApi.applySession(sessionId, request, token);
            toast({
                title: 'Changes Applied',
                description: 'Code has been successfully merged and committed.',
            });
            onApplySuccess();
            onClose();
        } catch (error: any) {
            console.error('Failed to apply changes:', error);
            toast({
                title: 'Apply Failed',
                description: error.response?.data?.detail || 'Could not apply changes.',
                variant: 'destructive',
            });
        } finally {
            setApplying(false);
        }
    };

    const renderDiffContent = (diff: FileDiff) => {
        if (diff.change_type === 'identical') {
            return (
                <div className="text-center p-10 text-muted-foreground">
                    <CheckCircle2 className="w-12 h-12 mx-auto mb-2 text-green-500" />
                    <p>Files are identical.</p>
                </div>
            );
        }
        // Simple naive diff view since we don't have a diff component installed
        // Ideally we would use 'react-diff-viewer' or similar
        return (
            <div className="grid grid-cols-2 gap-4 h-[400px]">
                <div className="border rounded-md overflow-hidden flex flex-col">
                    <div className="bg-muted px-3 py-2 text-xs font-semibold border-b">Current Local</div>
                    <ScrollArea className="flex-1 bg-background p-2 font-mono text-xs whitespace-pre overflow-auto">
                        {diff.old_content || <span className="text-muted-foreground italic">(File does not exist)</span>}
                    </ScrollArea>
                </div>
                <div className="border rounded-md overflow-hidden flex flex-col">
                    <div className="bg-muted px-3 py-2 text-xs font-semibold border-b flex justify-between">
                        <span>Generated New</span>
                        <Badge variant={diff.change_type === 'create' ? 'default' : 'secondary'}>{diff.change_type}</Badge>
                    </div>
                    <ScrollArea className="flex-1 bg-background p-2 font-mono text-xs whitespace-pre overflow-auto">
                        {diff.new_content}
                    </ScrollArea>
                </div>
            </div>
        );
    };

    const selectedDiff = comparison?.diffs.find(d => d.file_path === selectedFile);

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="max-w-5xl h-[80vh] flex flex-col">
                <DialogHeader>
                    <DialogTitle>Apply Changes</DialogTitle>
                    <DialogDescription>
                        Review the differences between the generated code and your local codebase.
                    </DialogDescription>
                </DialogHeader>

                {loading ? (
                    <div className="flex-1 flex items-center justify-center">
                        <Loader2 className="w-8 h-8 animate-spin text-primary" />
                    </div>
                ) : !comparison ? (
                    <div className="flex-1 flex items-center justify-center text-muted-foreground">
                        No comparison data available.
                    </div>
                ) : (
                    <div className="flex-1 flex gap-4 min-h-0">
                        {/* File List */}
                        <div className="w-1/4 border-r pr-4 flex flex-col gap-2">
                            <h4 className="text-sm font-semibold mb-2">Files ({comparison.total_changes})</h4>
                            <ScrollArea className="flex-1">
                                <div className="flex flex-col gap-1">
                                    {comparison.diffs.map(diff => (
                                        <button
                                            key={diff.file_path}
                                            onClick={() => setSelectedFile(diff.file_path)}
                                            className={`text-left px-3 py-2 rounded-md text-xs truncate flex items-center justify-between group ${selectedFile === diff.file_path ? 'bg-primary/10 text-primary' : 'hover:bg-muted'
                                                }`}
                                        >
                                            <div className="flex items-center gap-2 truncate">
                                                <FileCode className="w-3 h-3 flex-shrink-0" />
                                                <span className="truncate" title={diff.file_path}>{diff.file_path}</span>
                                            </div>
                                            <span className={`text-[10px] px-1.5 py-0.5 rounded ${diff.change_type === 'modify' ? 'bg-yellow-500/10 text-yellow-600' :
                                                    diff.change_type === 'create' ? 'bg-green-500/10 text-green-600' :
                                                        'text-muted-foreground'
                                                }`}>
                                                {diff.change_type === 'modify' ? 'M' : diff.change_type === 'create' ? 'A' : ''}
                                            </span>
                                        </button>
                                    ))}
                                </div>
                            </ScrollArea>
                        </div>

                        {/* Diff View */}
                        <div className="flex-1 flex flex-col min-h-0">
                            {selectedDiff ? (
                                <>
                                    <div className="mb-2 flex items-center justify-between">
                                        <code className="text-sm font-semibold bg-muted px-2 py-1 rounded">{selectedDiff.file_path}</code>
                                        <div className="text-xs text-muted-foreground space-x-2">
                                            <span>{selectedDiff.diff_stat}</span>
                                        </div>
                                    </div>
                                    <div className="flex-1 border rounded-md overflow-hidden bg-slate-50 dark:bg-slate-950">
                                        {renderDiffContent(selectedDiff)}
                                    </div>
                                </>
                            ) : (
                                <div className="flex-1 flex items-center justify-center text-muted-foreground">
                                    Select a file to view changes.
                                </div>
                            )}
                        </div>
                    </div>
                )}

                <DialogFooter className="mt-4 gap-2">
                    <div className="flex-1">
                        {/* Optional: Input for commit message */}
                        <input
                            type="text"
                            value={commitMessage}
                            onChange={(e) => setCommitMessage(e.target.value)}
                            className="w-full text-sm px-3 py-2 border rounded-md bg-transparent"
                            placeholder="Commit message..."
                        />
                    </div>
                    <Button variant="outline" onClick={onClose} disabled={applying}>
                        Cancel
                    </Button>
                    <Button onClick={handleApply} disabled={loading || !comparison || applying}>
                        {applying && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Apply & Commit
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
