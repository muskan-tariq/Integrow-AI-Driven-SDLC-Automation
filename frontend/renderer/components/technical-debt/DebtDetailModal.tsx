'use client';

import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
    AlertTriangle,
    AlertCircle,
    CheckCircle2,
    Github,
    Loader2,
    Calendar,
    Clock
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import { DebtSession, DebtIssue, technicalDebtApi } from '@/lib/api/technical-debt';
import { useToast } from '@/components/ui/use-toast';

interface DebtDetailModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    session: DebtSession | null;
}

export function DebtDetailModal({ open, onOpenChange, session }: DebtDetailModalProps) {
    const { toast } = useToast();
    const [token, setToken] = useState<string | null>(null);
    const [isBatchExporting, setIsBatchExporting] = useState(false);
    const [selectedIssueType, setSelectedIssueType] = useState<string>('all');

    useEffect(() => {
        if (open) {
            initializeSession();
        }
    }, [open]);

    const initializeSession = async () => {
        try {
            const authData = await window.electron.getAuth();
            if (authData?.accessToken) {
                setToken(authData.accessToken);
            }
        } catch (error) {
            console.error('Auth error:', error);
        }
    };

    const handleBatchExportToGitHub = async () => {
        if (!session || !token) return;

        setIsBatchExporting(true);
        try {
            const result = await technicalDebtApi.exportSessionToGitHub(session.id, token);
            toast({
                title: "Export Successful",
                description: `${result.issues_exported} issues exported to GitHub at ${result.github_path}`,
            });
            window.location.reload();
        } catch (error: any) {
            toast({
                title: "Export Failed",
                description: error.response?.data?.detail || "An unexpected error occurred",
                variant: "destructive",
            });
        } finally {
            setIsBatchExporting(false);
        }
    };

    if (!session) return null;

    const issues = session.debt_issues || [];
    const filteredIssues = selectedIssueType === 'all'
        ? issues
        : issues.filter(i => i.issue_type === selectedIssueType);

    const issueTypes = Array.from(new Set(issues.map(i => i.issue_type)));

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'critical': return 'bg-rose-600';
            case 'high': return 'bg-orange-500';
            case 'medium': return 'bg-yellow-500';
            case 'low': return 'bg-blue-400';
            default: return 'bg-slate-400';
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return 'text-emerald-500';
        if (score >= 60) return 'text-yellow-500';
        return 'text-rose-500';
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-6xl max-h-[90vh] flex flex-col p-0 overflow-hidden border-none shadow-2xl">
                <DialogHeader className="p-8 bg-slate-900 text-white shrink-0 relative overflow-hidden">
                    {/* Decorative background */}
                    <div className="absolute top-0 right-0 w-64 h-64 bg-amber-500/10 blur-3xl rounded-full -mr-32 -mt-32" />

                    <div className="relative z-10 flex items-start justify-between">
                        <div className="space-y-1">
                            <div className="flex items-center gap-2 mb-1">
                                <Badge className="bg-amber-500 hover:bg-amber-500 border-none text-[10px] font-black uppercase tracking-widest px-2 py-0">
                                    Debt Analysis
                                </Badge>
                                <Badge variant="outline" className="bg-white/10 text-white border-white/20 font-mono text-[10px]">
                                    V{session.version}
                                </Badge>
                                {session.github_exported && (
                                    <Badge className="bg-emerald-500 hover:bg-emerald-500 border-none text-[10px] font-black uppercase tracking-widest px-2 py-0 flex items-center gap-1">
                                        <Github className="h-3 w-3" /> Committed
                                    </Badge>
                                )}
                            </div>
                            <DialogTitle className="text-3xl font-black tracking-tight flex items-center gap-3">
                                <AlertTriangle className="h-8 w-8 text-amber-400" />
                                Technical Debt Report
                            </DialogTitle>
                            <p className="text-slate-400 font-mono text-sm max-w-md">
                                {session.summary}
                            </p>
                        </div>

                        <div className="flex flex-col items-end gap-4">
                            <div className="h-20 w-20 rounded-2xl bg-white/10 backdrop-blur-md border border-white/10 flex flex-col items-center justify-center shadow-inner">
                                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Score</span>
                                <span className={cn("text-3xl font-black", getScoreColor(session.overall_score))}>{session.overall_score}</span>
                            </div>
                            <Button
                                size="sm"
                                className="bg-emerald-600 hover:bg-emerald-700 shadow-lg text-white"
                                onClick={handleBatchExportToGitHub}
                                disabled={isBatchExporting || !token || session.github_exported}
                            >
                                {isBatchExporting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Github className="h-4 w-4 mr-2" />}
                                {session.github_exported ? 'Exported to GitHub' : 'Export to GitHub'}
                            </Button>
                        </div>
                    </div>

                    {/* Metrics Row */}
                    <div className="grid grid-cols-4 gap-4 mt-6">
                        <div className="bg-white/5 rounded-lg p-3 backdrop-blur-sm">
                            <p className="text-xs text-slate-400">Total Issues</p>
                            <p className="text-2xl font-bold">{session.total_issues}</p>
                        </div>
                        <div className="bg-white/5 rounded-lg p-3 backdrop-blur-sm">
                            <p className="text-xs text-slate-400">Critical</p>
                            <p className="text-2xl font-bold text-rose-400">{session.critical_issues}</p>
                        </div>
                        <div className="bg-white/5 rounded-lg p-3 backdrop-blur-sm">
                            <p className="text-xs text-slate-400">Complexity</p>
                            <p className={cn("text-2xl font-bold", getScoreColor(session.complexity_score))}>{session.complexity_score}</p>
                        </div>
                        <div className="bg-white/5 rounded-lg p-3 backdrop-blur-sm">
                            <p className="text-xs text-slate-400">Est. Effort</p>
                            <p className="text-2xl font-bold">{session.estimated_hours.toFixed(1)}h</p>
                        </div>
                    </div>
                </DialogHeader>

                <div className="flex-1 min-h-0 bg-white overflow-hidden">
                    <ScrollArea className="h-full">
                        <div className="p-8 space-y-6">
                            {/* Filter Tabs */}
                            <div className="flex gap-2 flex-wrap">
                                <Button
                                    size="sm"
                                    variant={selectedIssueType === 'all' ? 'default' : 'outline'}
                                    onClick={() => setSelectedIssueType('all')}
                                >
                                    All ({issues.length})
                                </Button>
                                {issueTypes.map(type => (
                                    <Button
                                        key={type}
                                        size="sm"
                                        variant={selectedIssueType === type ? 'default' : 'outline'}
                                        onClick={() => setSelectedIssueType(type)}
                                    >
                                        {type} ({issues.filter(i => i.issue_type === type).length})
                                    </Button>
                                ))}
                            </div>

                            {/* Issues List */}
                            <div className="space-y-4">
                                {filteredIssues.length === 0 ? (
                                    <div className="text-center py-12 text-slate-500">
                                        <CheckCircle2 className="h-12 w-12 mx-auto mb-4 text-emerald-500" />
                                        <p className="text-lg font-semibold">No issues found in this category</p>
                                    </div>
                                ) : (
                                    filteredIssues.map((issue) => (
                                        <div
                                            key={issue.id}
                                            className="border rounded-lg p-6 hover:shadow-md transition-shadow bg-white"
                                        >
                                            <div className="flex items-start justify-between mb-3">
                                                <div className="flex items-start gap-3 flex-1">
                                                    <Badge className={cn(getSeverityColor(issue.severity), "text-white border-none")}>
                                                        {issue.severity}
                                                    </Badge>
                                                    <div className="flex-1">
                                                        <h4 className="font-bold text-slate-900 mb-1">{issue.title}</h4>
                                                        <p className="text-sm text-slate-600 mb-2">{issue.description}</p>
                                                        <div className="flex items-center gap-4 text-xs text-slate-500">
                                                            <span className="font-mono">{issue.file_path}</span>
                                                            {issue.line_start && (
                                                                <span>Lines {issue.line_start}-{issue.line_end}</span>
                                                            )}
                                                            <Badge variant="outline" className="text-[10px]">{issue.category}</Badge>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-2 text-slate-500">
                                                    <Clock className="h-4 w-4" />
                                                    <span className="text-sm font-semibold">{issue.estimated_hours}h</span>
                                                </div>
                                            </div>

                                            {issue.suggested_fix && (
                                                <div className="mt-3 pt-3 border-t bg-slate-50 rounded p-3">
                                                    <p className="text-xs font-semibold text-slate-700 mb-1">💡 Suggested Fix:</p>
                                                    <p className="text-sm text-slate-600">{issue.suggested_fix}</p>
                                                </div>
                                            )}
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </ScrollArea>
                </div>
            </DialogContent>
        </Dialog>
    );
}
