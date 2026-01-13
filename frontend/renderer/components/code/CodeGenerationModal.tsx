
import { useEffect, useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, GitBranch, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface UMLDiagram {
    id: string;
    requirement_id: string;
    version: number;
    created_at: string;
    analysis_metadata?: {
        entities_found?: number;
    };
}

interface CodeGenerationModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    projectId: string;
    onGenerate: (umlId: string, requirementId: string) => Promise<void>;
}

export function CodeGenerationModal({
    open,
    onOpenChange,
    projectId,
    onGenerate, // Passing this handler allows parent to handle API call complexity
}: CodeGenerationModalProps) {
    const [diagrams, setDiagrams] = useState<UMLDiagram[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedDiagramId, setSelectedDiagramId] = useState<string>('');
    const [isGenerating, setIsGenerating] = useState(false);

    useEffect(() => {
        if (open && projectId) {
            fetchDiagrams();
        }
    }, [open, projectId]);

    const fetchDiagrams = async () => {
        setIsLoading(true);
        try {
            const authData = await window.electron.getAuth();
            const token = authData?.accessToken;
            if (!token) return;

            const response = await fetch(`http://localhost:8000/api/projects/${projectId}/uml`, {
                headers: { Authorization: `Bearer ${token}` },
            });

            if (response.ok) {
                const data = await response.json();
                const sorted = (data.diagrams || []).sort((a: UMLDiagram, b: UMLDiagram) => b.version - a.version);
                setDiagrams(sorted);
                if (sorted.length > 0) {
                    setSelectedDiagramId(sorted[0].id);
                }
            }
        } catch (error) {
            console.error('Failed to fetch diagrams', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleGenerate = async () => {
        if (!selectedDiagramId) return;

        const selectedDiagram = diagrams.find(d => d.id === selectedDiagramId);
        if (!selectedDiagram) return;

        setIsGenerating(true);
        try {
            await onGenerate(selectedDiagramId, selectedDiagram.requirement_id);
            onOpenChange(false);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Generate New Code</DialogTitle>
                    <DialogDescription>
                        Select a UML architecture diagram version to generate code from.
                    </DialogDescription>
                </DialogHeader>

                <div className="py-4 space-y-4">
                    {isLoading ? (
                        <div className="flex justify-center p-4">
                            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                        </div>
                    ) : diagrams.length === 0 ? (
                        <Alert variant="destructive">
                            <AlertCircle className="h-4 w-4" />
                            <AlertDescription>
                                No UML diagrams found. Please generate a UML diagram first.
                            </AlertDescription>
                        </Alert>
                    ) : (
                        <div className="space-y-2">
                            <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                Architecture Version
                            </label>
                            <Select value={selectedDiagramId} onValueChange={setSelectedDiagramId}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select version" />
                                </SelectTrigger>
                                <SelectContent>
                                    {diagrams.map((d) => (
                                        <SelectItem key={d.id} value={d.id}>
                                            <div className="flex items-center gap-2">
                                                <GitBranch className="h-3 w-3 text-muted-foreground" />
                                                <span>v{d.version}</span>
                                                <span className="text-muted-foreground text-xs">
                                                    ({d.analysis_metadata?.entities_found || 0} entities)
                                                    - {new Date(d.created_at).toLocaleDateString()}
                                                </span>
                                            </div>
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    )}
                </div>

                <DialogFooter>
                    <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isGenerating}>Cancel</Button>
                    <Button onClick={handleGenerate} disabled={!selectedDiagramId || isGenerating || diagrams.length === 0}>
                        {isGenerating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Generate Code
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
