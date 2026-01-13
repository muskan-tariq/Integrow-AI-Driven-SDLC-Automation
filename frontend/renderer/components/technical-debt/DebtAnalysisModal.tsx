'use client';

import React, { useState } from 'react';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Loader2, AlertTriangle, CheckCircle2, FileCode } from 'lucide-react';
import { technicalDebtApi } from '@/lib/api/technical-debt';
import { useToast } from '@/components/ui/use-toast';
import { FileSelectorModal } from './FileSelectorModal';

interface DebtAnalysisModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    projectId: string;
    token: string;
    onAnalysisComplete: () => void;
}

export function DebtAnalysisModal({ open, onOpenChange, projectId, token, onAnalysisComplete }: DebtAnalysisModalProps) {
    const { toast } = useToast();
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [includeTests, setIncludeTests] = useState(true);
    const [analysisResult, setAnalysisResult] = useState<any>(null);
    const [analysisMode, setAnalysisMode] = useState<'project' | 'files'>('project');
    const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
    const [isFileSelectorOpen, setIsFileSelectorOpen] = useState(false);

    const handleSelectFiles = (files: string[]) => {
        setSelectedFiles(files);
    };

    const handleAnalyze = async () => {
        setIsAnalyzing(true);
        setAnalysisResult(null);

        try {
            const result = await technicalDebtApi.analyzeProject(
                {
                    project_id: projectId,
                    include_tests: includeTests,
                    max_depth: 10,
                    specific_files: analysisMode === 'files' ? selectedFiles : undefined
                },
                token
            );

            setAnalysisResult(result);
            toast({
                title: "Analysis Complete",
                description: `Found ${result.total_issues} issues. Overall score: ${result.overall_score}/100`,
            });

            setTimeout(() => {
                onAnalysisComplete();
                onOpenChange(false);
                setAnalysisResult(null);
                setSelectedFiles([]);
            }, 2000);

        } catch (error: any) {
            toast({
                title: "Analysis Failed",
                description: error.response?.data?.detail || "An unexpected error occurred",
                variant: "destructive",
            });
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-md">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-amber-600" />
                        Analyze Technical Debt
                    </DialogTitle>
                    <DialogDescription>
                        Scan your codebase for complexity, duplication, and architectural issues.
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-6 py-4">
                    {!analysisResult && !isAnalyzing && (
                        <div className="space-y-4">
                            {/* Analysis Mode Selection */}
                            <div className="space-y-3">
                                <Label className="text-sm font-semibold">Analysis Scope</Label>
                                <RadioGroup value={analysisMode} onValueChange={(v) => setAnalysisMode(v as 'project' | 'files')}>
                                    <div className="flex items-center space-x-2">
                                        <RadioGroupItem value="project" id="mode-project" />
                                        <Label htmlFor="mode-project" className="font-normal cursor-pointer">
                                            Analyze Entire Project
                                        </Label>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <RadioGroupItem value="files" id="mode-files" />
                                        <Label htmlFor="mode-files" className="font-normal cursor-pointer">
                                            Analyze Specific Files
                                        </Label>
                                    </div>
                                </RadioGroup>
                            </div>

                            {/* File Selection for Specific Files Mode */}
                            {analysisMode === 'files' && (
                                <div className="space-y-2">
                                    <Button
                                        variant="outline"
                                        onClick={() => setIsFileSelectorOpen(true)}
                                        className="w-full"
                                    >
                                        <FileCode className="mr-2 h-4 w-4" />
                                        Select Files ({selectedFiles.length} selected)
                                    </Button>
                                    {selectedFiles.length > 0 && (
                                        <div className="text-xs text-slate-600 max-h-24 overflow-y-auto bg-slate-50 p-2 rounded">
                                            {selectedFiles.map((file, idx) => (
                                                <div key={idx} className="truncate">{file}</div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Options */}
                            <div className="flex items-center space-x-2">
                                <Checkbox
                                    id="include-tests"
                                    checked={includeTests}
                                    onCheckedChange={(checked) => setIncludeTests(checked as boolean)}
                                />
                                <Label htmlFor="include-tests" className="text-sm font-normal cursor-pointer">
                                    Include test files in analysis
                                </Label>
                            </div>

                            <div className="bg-slate-50 p-4 rounded-lg space-y-2 text-sm">
                                <p className="font-semibold text-slate-700">Analysis will detect:</p>
                                <ul className="list-disc list-inside space-y-1 text-slate-600">
                                    <li>High cyclomatic complexity (Python & JS/TS)</li>
                                    <li>Large classes and long methods</li>
                                    <li>Code duplication patterns</li>
                                    <li>Unused variables and dead code</li>
                                    <li>Outdated dependencies</li>
                                </ul>
                            </div>
                        </div>
                    )}

                    {isAnalyzing && (
                        <div className="flex flex-col items-center justify-center py-8 space-y-4">
                            <Loader2 className="h-12 w-12 animate-spin text-amber-600" />
                            <p className="text-sm text-slate-600">
                                {analysisMode === 'project' ? 'Analyzing your codebase...' : `Analyzing ${selectedFiles.length} file(s)...`}
                            </p>
                        </div>
                    )}

                    {analysisResult && (
                        <div className="flex flex-col items-center justify-center py-8 space-y-4">
                            <CheckCircle2 className="h-12 w-12 text-emerald-600" />
                            <div className="text-center space-y-2">
                                <p className="text-lg font-semibold text-slate-900">Analysis Complete!</p>
                                <p className="text-sm text-slate-600">
                                    Found {analysisResult.total_issues} issues
                                </p>
                                <p className="text-2xl font-bold text-amber-600">
                                    Score: {analysisResult.overall_score}/100
                                </p>
                            </div>
                        </div>
                    )}
                </div>

                <div className="flex justify-end gap-2">
                    <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isAnalyzing}>
                        Cancel
                    </Button>
                    {!analysisResult && (
                        <Button
                            onClick={handleAnalyze}
                            disabled={isAnalyzing || (analysisMode === 'files' && selectedFiles.length === 0)}
                            className="bg-amber-600 hover:bg-amber-700"
                        >
                            {isAnalyzing ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Analyzing...
                                </>
                            ) : (
                                'Start Analysis'
                            )}
                        </Button>
                    )}
                </div>
            </DialogContent>

            <FileSelectorModal
                open={isFileSelectorOpen}
                onOpenChange={setIsFileSelectorOpen}
                projectId={projectId}
                token={token}
                onSelect={handleSelectFiles}
            />
        </Dialog>
    );
}
