'use client';

import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
    FileCode,
    Search,
    Loader2,
    ChevronRight,
    AlertTriangle,
    FileCheck,
    CheckCircle2,
    AlertCircle,
    ShieldAlert,
    Zap,
    Code,
    Layers
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { codeReviewApi, CodeReviewReport } from '@/lib/api/code-review';
import { cn } from '@/lib/utils';

interface FileReviewModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    projectId: string;
    token: string;
    onReviewComplete: () => void;
}

export function FileReviewModal({
    open,
    onOpenChange,
    projectId,
    token,
    onReviewComplete
}: FileReviewModalProps) {
    const [files, setFiles] = useState<any[]>([]);
    const [isLoadingFiles, setIsLoadingFiles] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [reviewResults, setReviewResults] = useState<CodeReviewReport[] | null>(null);

    useEffect(() => {
        if (open) {
            loadFiles();
            setReviewResults(null);
            setSelectedFiles(new Set());
        }
    }, [open]);

    const toggleFileSelection = (path: string) => {
        const newSelection = new Set(selectedFiles);
        if (newSelection.has(path)) {
            newSelection.delete(path);
        } else {
            newSelection.add(path);
        }
        setSelectedFiles(newSelection);
    };

    const selectAllRelevantFiles = () => {
        const newSelection = new Set<string>();
        filteredFiles.forEach(f => newSelection.add(f.path));
        setSelectedFiles(newSelection);
    };

    const loadFiles = async () => {
        setIsLoadingFiles(true);
        try {
            if (token) {
                api.setToken(token);
            }
            const response = await api.getProjectFiles(projectId);
            setFiles(response.files || []);
        } catch (error) {
            console.error('Error loading files:', error);
        } finally {
            setIsLoadingFiles(false);
        }
    };

    const filteredFiles = files.filter(f =>
        f.path.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const handleStartReview = async () => {
        if (selectedFiles.size === 0) return;

        setIsAnalyzing(true);
        try {
            const response = await codeReviewApi.analyzeFiles({
                project_id: projectId,
                file_paths: Array.from(selectedFiles)
            }, token);
            setReviewResults(response.results);
            onReviewComplete();
        } catch (error) {
            console.error('Error starting review:', error);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const getSeverityIcon = (severity: string) => {
        switch (severity.toLowerCase()) {
            case 'critical': return <ShieldAlert className="h-4 w-4 text-rose-600" />;
            case 'high': return <AlertCircle className="h-4 w-4 text-rose-500" />;
            case 'medium': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
            case 'low': return <Zap className="h-4 w-4 text-blue-400" />;
            default: return <AlertCircle className="h-4 w-4 text-slate-400" />;
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col p-0 overflow-hidden border-none shadow-2xl">
                <DialogHeader className="p-6 bg-slate-900 text-white shrink-0">
                    <DialogTitle className="text-2xl flex items-center gap-2">
                        <Zap className="h-6 w-6 text-yellow-400 fill-yellow-400" />
                        AI Code Review
                    </DialogTitle>
                    <DialogDescription className="text-slate-400 text-base flex justify-between items-center">
                        <span>Select files for AI analysis or scan the entire project.</span>
                        <Button
                            variant="ghost"
                            size="sm"
                            className="text-indigo-400 hover:text-indigo-300 hover:bg-white/5 h-7 text-[10px] font-black uppercase tracking-widest border border-indigo-500/30"
                            onClick={selectAllRelevantFiles}
                        >
                            Select All
                        </Button>
                    </DialogDescription>
                </DialogHeader>

                <div className="flex-1 min-h-0 flex bg-white">
                    {!reviewResults ? (
                        <div className="flex flex-col w-full">
                            <div className="p-4 border-b border-slate-100 bg-slate-50/50">
                                <div className="relative">
                                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                                    <input
                                        type="text"
                                        placeholder="Search files..."
                                        className="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition-all"
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                    />
                                </div>
                            </div>

                            <ScrollArea className="flex-1">
                                <div className="p-2 space-y-1">
                                    {isLoadingFiles ? (
                                        <div className="flex flex-col items-center justify-center py-20 text-slate-400">
                                            <Loader2 className="h-8 w-8 animate-spin mb-2 text-indigo-500" />
                                            <p>Scanning project directory...</p>
                                        </div>
                                    ) : filteredFiles.length === 0 ? (
                                        <div className="flex flex-col items-center justify-center py-20 text-slate-400">
                                            <FileCode className="h-12 w-12 mb-2 opacity-20" />
                                            <p>No suitable files found.</p>
                                        </div>
                                    ) : (
                                        filteredFiles.map((file) => (
                                            <button
                                                key={file.path}
                                                onClick={() => toggleFileSelection(file.path)}
                                                className={cn(
                                                    "w-full flex items-center justify-between p-3 rounded-xl text-left transition-all group",
                                                    selectedFiles.has(file.path)
                                                        ? "bg-indigo-50 border-indigo-200"
                                                        : "hover:bg-slate-50 border-transparent"
                                                )}
                                            >
                                                <div className="flex items-center gap-3 min-w-0">
                                                    <div className={cn(
                                                        "h-10 w-10 rounded-lg flex items-center justify-center shrink-0 transition-colors",
                                                        selectedFiles.has(file.path) ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-400 group-hover:bg-slate-200 group-hover:text-slate-600"
                                                    )}>
                                                        <FileCode className="h-5 w-5" />
                                                    </div>
                                                    <div className="min-w-0">
                                                        <p className={cn("text-sm font-bold truncate", selectedFiles.has(file.path) ? "text-indigo-900" : "text-slate-700")}>
                                                            {file.name}
                                                        </p>
                                                        <p className="text-xs text-slate-400 truncate">{file.path}</p>
                                                    </div>
                                                </div>
                                                {selectedFiles.has(file.path) ? (
                                                    <div className="h-6 w-6 rounded-full bg-indigo-600 flex items-center justify-center text-white">
                                                        <CheckCircle2 className="h-4 w-4" />
                                                    </div>
                                                ) : (
                                                    <ChevronRight className="h-4 w-4 text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity" />
                                                )}
                                            </button>
                                        ))
                                    )}
                                </div>
                            </ScrollArea>

                            <div className="p-6 border-t border-slate-100 bg-slate-50/50 flex justify-between items-center">
                                <div className="text-sm text-slate-500">
                                    {selectedFiles.size > 0 ? `${selectedFiles.size} files selected` : 'Select files to begin'}
                                </div>
                                <div className="flex gap-3">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="h-9 relative group overflow-hidden border-indigo-200 text-indigo-700 hover:text-white"
                                        onClick={() => {
                                            const srcFiles = files.filter(f => f.path.startsWith('src/'));
                                            const newSelection = new Set(selectedFiles);
                                            srcFiles.forEach(f => newSelection.add(f.path));
                                            setSelectedFiles(newSelection);
                                        }}
                                    >
                                        <div className="absolute inset-0 bg-indigo-600 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                                        <span className="relative flex items-center gap-2">
                                            <Layers className="h-4 w-4" /> Review src/
                                        </span>
                                    </Button>
                                    <Button
                                        disabled={selectedFiles.size === 0 || isAnalyzing}
                                        onClick={handleStartReview}
                                        className="bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-100 px-8"
                                    >
                                        {isAnalyzing ? (
                                            <>
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                Analyzing...
                                            </>
                                        ) : (
                                            <>
                                                <Zap className="mr-2 h-4 w-4" />
                                                Start Analysis
                                            </>
                                        )}
                                    </Button>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col w-full overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <ScrollArea className="flex-1">
                                <div className="p-8 space-y-12">
                                    <div className="flex items-center justify-between border-b pb-6">
                                        <div>
                                            <h3 className="text-3xl font-black text-slate-900 flex items-center gap-3">
                                                <CheckCircle2 className="h-8 w-8 text-emerald-500" />
                                                Analysis Complete
                                            </h3>
                                            <p className="text-slate-500 mt-1 font-medium">Reviewed {reviewResults.length} files with automated AI insights</p>
                                        </div>
                                        <Badge className="bg-emerald-500 text-white border-none py-1.5 px-4 rounded-full text-xs font-black uppercase tracking-widest">
                                            {Math.round(reviewResults.reduce((acc, r) => acc + r.score, 0) / reviewResults.length)} Avg Score
                                        </Badge>
                                    </div>

                                    {reviewResults.map((result, rIdx) => (
                                        <div key={rIdx} className="space-y-6">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-3">
                                                    <div className="h-10 w-10 rounded-xl bg-slate-900 text-white flex items-center justify-center font-mono text-sm shadow-lg">
                                                        {rIdx + 1}
                                                    </div>
                                                    <div>
                                                        <h4 className="font-black text-slate-900 text-lg">{result.file_path.split('/').pop()}</h4>
                                                        <p className="text-xs font-mono text-slate-400">{result.file_path}</p>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-3">
                                                    <div className="text-right">
                                                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">Score</p>
                                                        <p className={cn(
                                                            "text-2xl font-black leading-none",
                                                            result.score >= 90 ? "text-emerald-500" : result.score >= 70 ? "text-yellow-500" : "text-rose-500"
                                                        )}>{result.score}</p>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="bg-slate-50 rounded-2xl p-6 border border-slate-100">
                                                <p className="text-slate-700 leading-relaxed italic border-l-4 border-indigo-200 pl-4 py-1">
                                                    "{result.summary}"
                                                </p>
                                            </div>

                                            <div className="grid gap-4">
                                                {result.issues?.map((issue, idx) => (
                                                    <div
                                                        key={idx}
                                                        className="bg-white border border-slate-100 rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-all group/issue"
                                                    >
                                                        <div className="px-5 py-3 bg-white border-b flex items-center justify-between group-hover/issue:bg-slate-50 transition-colors">
                                                            <div className="flex items-center gap-3">
                                                                <div className="p-1.5 bg-slate-100 rounded-lg">
                                                                    {getSeverityIcon(issue.severity)}
                                                                </div>
                                                                <span className="font-bold text-slate-800 text-sm">{issue.issue_type}</span>
                                                                <Badge className={cn(
                                                                    "text-[9px] uppercase font-black px-1.5 py-0 border-none",
                                                                    issue.severity === 'critical' ? "bg-rose-100 text-rose-700" :
                                                                        issue.severity === 'high' ? "bg-orange-100 text-orange-700" :
                                                                            issue.severity === 'medium' ? "bg-yellow-100 text-yellow-700" : "bg-blue-100 text-blue-700"
                                                                )}>
                                                                    {issue.severity}
                                                                </Badge>
                                                            </div>
                                                            <Badge variant="outline" className="font-mono text-[10px] bg-slate-50 border-slate-200">
                                                                L{issue.line_number}
                                                            </Badge>
                                                        </div>
                                                        <div className="p-5">
                                                            <p className="text-slate-600 text-sm leading-relaxed mb-4">{issue.description}</p>
                                                            {issue.suggested_fix && (
                                                                <div className="bg-slate-900 rounded-xl p-4 relative group/fix overflow-hidden">
                                                                    <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500" />
                                                                    <h5 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-2">Recommended Fix</h5>
                                                                    <pre className="text-indigo-50 text-xs font-mono overflow-x-auto whitespace-pre-wrap">
                                                                        {issue.suggested_fix}
                                                                    </pre>
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                ))}
                                                {(!result.issues || result.issues.length === 0) && (
                                                    <div className="flex items-center gap-3 p-4 bg-emerald-50 rounded-2xl border border-emerald-100 text-emerald-700">
                                                        <CheckCircle2 className="h-5 w-5" />
                                                        <span className="text-sm font-bold">No issues detected in this file.</span>
                                                    </div>
                                                )}
                                            </div>
                                            {rIdx < reviewResults.length - 1 && <hr className="border-slate-100" />}
                                        </div>
                                    ))}
                                </div>
                            </ScrollArea>

                            <div className="p-6 border-t bg-slate-50/50 flex justify-end">
                                <Button
                                    onClick={() => onOpenChange(false)}
                                    className="bg-slate-900 text-white hover:bg-slate-800"
                                >
                                    Done
                                </Button>
                            </div>
                        </div>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
