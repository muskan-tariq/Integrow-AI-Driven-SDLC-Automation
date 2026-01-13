'use client';

import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
} from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
    FileCheck,
    AlertCircle,
    CheckCircle2,
    ShieldAlert,
    Zap,
    AlertTriangle,
    Code,
    Calendar,
    Layers
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { CodeReviewReport, ReviewSession, codeReviewApi } from '@/lib/api/code-review';
import { Github, Loader2 } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';

interface ReviewDetailModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    session: ReviewSession | null;
}

export function ReviewDetailModal({ open, onOpenChange, session }: ReviewDetailModalProps) {
    const { toast } = useToast();
    const [token, setToken] = useState<string | null>(null);
    const [isExporting, setIsExporting] = useState(false);
    const [isBatchExporting, setIsBatchExporting] = useState(false);
    const [selectedReportId, setSelectedReportId] = useState<string | null>(null);

    useEffect(() => {
        if (open) {
            initializeSession();
            // Default to first report if available
            if (session?.code_reviews && session.code_reviews.length > 0) {
                setSelectedReportId(session.code_reviews[0].id);
            }
        }
    }, [open, session]);

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

    const selectedReport = session?.code_reviews?.find(r => r.id === selectedReportId) || null;

    const handleExportToGitHub = async () => {
        if (!selectedReport || !token) return;

        setIsExporting(true);
        try {
            const result = await codeReviewApi.exportReviewToGitHub(selectedReport.id, token);
            toast({
                title: "Export Successful",
                description: `Review saved to GitHub at ${result.github_path}`,
            });
        } catch (error: any) {
            toast({
                title: "Export Failed",
                description: error.response?.data?.detail || "An unexpected error occurred",
                variant: "destructive",
            });
        } finally {
            setIsExporting(false);
        }
    };

    const handleBatchExportToGitHub = async () => {
        if (!session || !token) return;

        setIsBatchExporting(true);
        try {
            const result = await codeReviewApi.exportSessionToGitHub(session.id, token);
            toast({
                title: "Batch Export Successful",
                description: `${result.files_exported} files exported to GitHub at ${result.github_path}`,
            });
            // Refresh session to show updated export status
            window.location.reload();
        } catch (error: any) {
            toast({
                title: "Batch Export Failed",
                description: error.response?.data?.detail || "An unexpected error occurred",
                variant: "destructive",
            });
        } finally {
            setIsBatchExporting(false);
        }
    };

    if (!session) return null;

    const getSeverityIcon = (severity: string) => {
        switch (severity.toLowerCase()) {
            case 'critical': return <ShieldAlert className="h-5 w-5 text-rose-600" />;
            case 'high': return <AlertCircle className="h-5 w-5 text-rose-500" />;
            case 'medium': return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
            case 'low': return <Zap className="h-5 w-5 text-blue-400" />;
            default: return <AlertCircle className="h-5 w-5 text-slate-400" />;
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 90) return 'text-emerald-500';
        if (score >= 70) return 'text-yellow-500';
        return 'text-rose-500';
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-6xl max-h-[90vh] flex flex-col p-0 overflow-hidden border-none shadow-2xl">
                <DialogHeader className="p-8 bg-slate-900 text-white shrink-0 relative overflow-hidden">
                    {/* Decorative background elements */}
                    <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 blur-3xl rounded-full -mr-32 -mt-32" />
                    <div className="absolute bottom-0 left-0 w-48 h-48 bg-emerald-500/10 blur-3xl rounded-full -ml-24 -mb-24" />

                    <div className="relative z-10 flex items-start justify-between">
                        <div className="space-y-1">
                            <div className="flex items-center gap-2 mb-1">
                                <Badge className="bg-indigo-500 hover:bg-indigo-500 border-none text-[10px] font-black uppercase tracking-widest px-2 py-0">Review Session</Badge>
                                <Badge variant="outline" className="bg-white/10 text-white border-white/20 font-mono text-[10px]">V{session.version}</Badge>
                                {session.github_exported && (
                                    <Badge className="bg-emerald-500 hover:bg-emerald-500 border-none text-[10px] font-black uppercase tracking-widest px-2 py-0 flex items-center gap-1">
                                        <Github className="h-3 w-3" /> Committed
                                    </Badge>
                                )}
                                <span className="text-slate-500 text-xs font-mono">{session.id}</span>
                            </div>
                            <DialogTitle className="text-3xl font-black tracking-tight flex items-center gap-3">
                                <FileCheck className="h-8 w-8 text-emerald-400" />
                                Project Batch Review
                            </DialogTitle>
                            <DialogDescription className="text-slate-400 font-mono text-sm max-w-md">
                                {session.summary}
                            </DialogDescription>
                        </div>

                        <div className="flex flex-col items-end">
                            <div className="h-20 w-20 rounded-2xl bg-white/10 backdrop-blur-md border border-white/10 flex flex-col items-center justify-center shadow-inner">
                                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Batch Score</span>
                                <span className={cn("text-3xl font-black", getScoreColor(session.score))}>{session.score}</span>
                            </div>
                            <div className="mt-4 flex flex-col items-end gap-2">
                                <Button
                                    size="sm"
                                    className="bg-emerald-600 hover:bg-emerald-700 shadow-lg text-white"
                                    onClick={handleBatchExportToGitHub}
                                    disabled={isBatchExporting || !token || session.github_exported}
                                >
                                    {isBatchExporting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Github className="h-4 w-4 mr-2" />}
                                    {session.github_exported ? 'Exported to GitHub' : 'Export Batch to GitHub'}
                                </Button>
                                <div className="flex items-center gap-2 text-slate-400 text-xs">
                                    <Calendar className="h-3 w-3" />
                                    {new Date(session.created_at).toLocaleDateString()}
                                </div>
                            </div>
                        </div>
                    </div>
                </DialogHeader>

                <div className="flex-1 min-h-0 bg-white overflow-hidden flex">
                    {/* File Sidebar */}
                    <div className="w-72 border-r bg-slate-50/50 flex flex-col">
                        <div className="p-4 border-b bg-white">
                            <h4 className="text-xs font-black text-slate-400 uppercase tracking-widest">Files Reviewed ({session.code_reviews?.length || 0})</h4>
                        </div>
                        <ScrollArea className="flex-1">
                            <div className="p-2 space-y-1">
                                {session.code_reviews?.map((report) => (
                                    <button
                                        key={report.id}
                                        onClick={() => setSelectedReportId(report.id)}
                                        className={cn(
                                            "w-full text-left p-3 rounded-xl transition-all flex items-center gap-3 group",
                                            selectedReportId === report.id
                                                ? "bg-white shadow-sm border border-slate-200"
                                                : "hover:bg-slate-100/50"
                                        )}
                                    >
                                        <div className={cn(
                                            "h-2 w-2 rounded-full shrink-0",
                                            report.score >= 80 ? "bg-emerald-500" : report.score >= 60 ? "bg-yellow-500" : "bg-rose-500"
                                        )} />
                                        <div className="min-w-0 flex-1">
                                            <p className={cn(
                                                "text-sm font-bold truncate flex items-center gap-2",
                                                selectedReportId === report.id ? "text-indigo-600" : "text-slate-700"
                                            )}>
                                                {report.file_path?.split('/').pop() || 'Untitled'}
                                                {report.github_exported && (
                                                    <Github className="h-3 w-3 text-emerald-500" />
                                                )}
                                            </p>
                                            <p className="text-[10px] text-slate-400 truncate">{report.file_path || 'No path'}</p>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </ScrollArea>
                    </div>

                    {/* Report Content */}
                    <div className="flex-1 flex flex-col min-w-0">
                        {selectedReport ? (
                            <>
                                <div className="p-6 border-b bg-white flex items-center justify-between">
                                    <div className="min-w-0">
                                        <h3 className="font-black text-xl text-slate-900 truncate tracking-tight">{selectedReport.file_path || 'Unknown File'}</h3>
                                        <p className="text-slate-400 text-xs italic mt-1 line-clamp-1">"{selectedReport.summary}"</p>
                                    </div>
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        className="h-9 hover:bg-slate-900 hover:text-white group border-slate-200"
                                        onClick={handleExportToGitHub}
                                        disabled={isExporting || !token}
                                    >
                                        {isExporting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Github className="h-4 w-4 mr-2" />}
                                        Export File Report
                                    </Button>
                                </div>

                                <ScrollArea className="flex-1">
                                    <div className="p-8 space-y-6">
                                        <h4 className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] flex items-center gap-2">
                                            <Code className="h-4 w-4" /> Detected Issues ({selectedReport.issues?.length || 0})
                                        </h4>

                                        {selectedReport.issues?.length === 0 ? (
                                            <div className="p-12 text-center bg-emerald-50 rounded-2xl border border-emerald-100">
                                                <CheckCircle2 className="h-12 w-12 text-emerald-500 mx-auto mb-3" />
                                                <p className="font-bold text-emerald-900">Spotless code!</p>
                                                <p className="text-emerald-700 text-sm">No issues were detected in this analysis.</p>
                                            </div>
                                        ) : (
                                            <div className="grid gap-4">
                                                {selectedReport.issues?.map((issue, idx) => (
                                                    <div
                                                        key={idx}
                                                        className="group bg-white border border-slate-100 rounded-2xl overflow-hidden hover:border-indigo-200 transition-all shadow-sm hover:shadow-md"
                                                    >
                                                        <div className="px-6 py-4 bg-slate-50 border-b flex items-center justify-between group-hover:bg-indigo-50/30 transition-colors">
                                                            <div className="flex items-center gap-3">
                                                                <div className="p-2 bg-white rounded-lg shadow-sm">
                                                                    {getSeverityIcon(issue.severity)}
                                                                </div>
                                                                <div>
                                                                    <div className="flex items-center gap-2">
                                                                        <span className="font-black text-slate-900 text-sm uppercase tracking-tight">{issue.issue_type}</span>
                                                                        <Badge variant="outline" className={cn(
                                                                            "text-[10px] uppercase font-bold px-1.5 py-0 border-none",
                                                                            issue.severity === 'critical' ? "bg-rose-100 text-rose-700" :
                                                                                issue.severity === 'high' ? "bg-orange-100 text-orange-700" :
                                                                                    issue.severity === 'medium' ? "bg-yellow-100 text-yellow-700" : "bg-blue-100 text-blue-700"
                                                                        )}>
                                                                            {issue.severity}
                                                                        </Badge>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                            <div className="flex items-center gap-2">
                                                                <span className="text-[10px] font-black text-slate-400 uppercase">Line</span>
                                                                <Badge className="bg-slate-900 text-white font-mono rounded-md h-7 min-w-8 flex items-center justify-center">
                                                                    {issue.line_number}
                                                                </Badge>
                                                            </div>
                                                        </div>
                                                        <div className="p-6">
                                                            <p className="text-slate-600 text-sm leading-relaxed mb-4">{issue.description}</p>

                                                            {issue.suggested_fix && (
                                                                <div className="relative pt-4">
                                                                    <div className="absolute top-0 left-0 w-8 h-px bg-indigo-500" />
                                                                    <h5 className="text-[10px] font-black text-indigo-600 uppercase tracking-widest mb-2">Recommended Fix</h5>
                                                                    <div className="bg-slate-900 rounded-xl p-5 relative overflow-hidden group/code">
                                                                        <div className="absolute top-0 right-0 p-2 opacity-0 group-hover/code:opacity-100 transition-opacity">
                                                                            <Badge className="bg-white/10 hover:bg-white/20 text-white border-none text-[10px] backdrop-blur-md">Copy</Badge>
                                                                        </div>
                                                                        <pre className="text-indigo-100 text-xs font-mono overflow-x-auto whitespace-pre-wrap leading-relaxed">
                                                                            {issue.suggested_fix}
                                                                        </pre>
                                                                    </div>
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </ScrollArea>
                            </>
                        ) : (
                            <div className="flex-1 flex flex-col items-center justify-center text-slate-400 p-8 text-center">
                                <Layers className="h-16 w-16 mb-4 opacity-20" />
                                <p>Select a file from the sidebar to view detailed AI analysis.</p>
                            </div>
                        )}
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
