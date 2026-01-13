'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, GitBranch, ArrowRight, Clock, Eye, RefreshCw, Trash2, FileOutput } from 'lucide-react';
import { DiffPreviewModal } from '@/components/code/diff-preview-modal';
import { codeGenerationApi } from '@/lib/api/code-generation';
import { useToast } from '@/components/ui/use-toast';
import { Badge } from '@/components/ui/badge';

interface UMLDiagram {
  id: string;
  requirement_id: string;
  diagram_type: string;
  version: number;
  created_at: string;
  plantuml_code?: string;
  rendered_svg?: string;
}

export default function UMLDiagramsPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
  const projectId = params.id as string;

  const [diagrams, setDiagrams] = useState<UMLDiagram[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [token, setToken] = useState('');
  const { toast } = useToast();

  // Diff Preview State
  const [isDiffModalOpen, setIsDiffModalOpen] = useState(false);
  const [previewSessionId, setPreviewSessionId] = useState<string | null>(null);
  const [isGeneratingDiff, setIsGeneratingDiff] = useState(false);

  useEffect(() => {
    initializeSession();
  }, []);

  useEffect(() => {
    if (token) {
      fetchDiagrams();

      // Handle autoStart
      if (searchParams?.get('autoStart') === 'true') {
        router.push(`/project/${projectId}/requirements?autoStart=true`);
      }
    }
  }, [token]);

  const initializeSession = async () => {
    try {
      const authData = await window.electron.getAuth();
      if (authData?.accessToken) {
        setToken(authData.accessToken);
      } else {
        router.push('/');
      }
    } catch (error) {
      console.error('Auth error:', error);
      router.push('/');
    }
  };

  const fetchDiagrams = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/projects/${projectId}/uml`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDiagrams(data.diagrams || []);
      }
    } catch (error) {
      console.error('Error fetching diagrams:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteDiagram = async (e: React.MouseEvent, diagramId: string) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this UML diagram and its source files? This action cannot be undone.')) return;

    try {
      const response = await fetch(`http://localhost:8000/api/uml/${diagramId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setDiagrams(diagrams.filter(d => d.id !== diagramId));
      } else {
        const error = await response.json();
        alert(`Failed to delete diagram: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error deleting diagram:', error);
      alert('Failed to delete diagram');
    }
  };

  const handleViewDiagram = (diagram: UMLDiagram) => {
    if (diagram.requirement_id) {
      router.push(`/project/${projectId}/requirements/${diagram.requirement_id}/uml`);
    } else {
      alert("This diagram is a system-wide sync and not linked to a specific requirement yet.");
    }
  };

  const handleSyncFromCode = async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/projects/${projectId}/uml/sync`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        await fetchDiagrams();
        toast({ title: 'Synced successfully', description: 'UML diagram updated from codebase.' });
      } else {
        const errorData = await response.json();
        console.error('Sync failed:', errorData);
        alert(`Failed to sync: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Sync error:', error);
      alert('Failed to sync from code.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplyToCode = async (e: React.MouseEvent, diagram: UMLDiagram) => {
    e.stopPropagation();
    if (!token) return;

    setIsGeneratingDiff(true);
    try {
      // 1. Trigger Generation to get a Session ID (which contains the new code)
      // We use defaults for now. In a full version, we might ask for Tech Stack via a modal first.
      const result = await codeGenerationApi.generateCode({
        project_id: projectId,
        requirement_id: diagram.requirement_id, // We need requirement ID. If generic system diagram, we might need a workaround.
        uml_diagram_id: diagram.id,
        generation_scope: ['models', 'api', 'services'], // Default scope
      } as any, token); // Type casting as request structure might vary slightly

      // 2. Open Diff Modal with this Session ID
      setPreviewSessionId(result.session_id);
      setIsDiffModalOpen(true);

    } catch (error: any) {
      console.error('Failed to prepare apply:', error);
      toast({
        title: 'Preparation Failed',
        description: 'Could not generate code for comparison. ' + (error.response?.data?.detail || ''),
        variant: 'destructive',
      });
    } finally {
      setIsGeneratingDiff(false);
    }
  };

  const onApplySuccess = () => {
    // Refresh diagrams or other state if needed
    toast({ title: 'Applied to Code', description: 'Your codebase has been updated.' });
  };

  return (
    <div className="flex flex-col h-full bg-gray-50 text-gray-900">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4 shrink-0">
        <div className="max-w-5xl mx-auto w-full">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">UML Diagrams</h1>
          <p className="text-gray-500 mt-1">
            Visualize project architecture with generated UML diagrams.
          </p>
          <div className="mt-4 flex gap-2">
            <Button onClick={handleSyncFromCode} variant="outline" className="gap-2">
              <RefreshCw className="h-4 w-4" />
              Sync from Code
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-5xl mx-auto w-full">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
          ) : diagrams.length === 0 ? (
            <Card className="border-0 shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <GitBranch className="h-5 w-5" />
                  No UML Diagrams Yet
                </CardTitle>
                <CardDescription>
                  UML diagrams are generated from user stories
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  Create requirements, generate user stories, then create UML diagrams.
                </p>
                <Button onClick={() => router.push(`/project/${projectId}/requirements`)}>
                  Go to Requirements <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 pb-10">
              {diagrams.map((diagram) => (
                <Card
                  key={diagram.id}
                  className="cursor-pointer hover:shadow-lg transition-all duration-200 border-0 shadow-sm group bg-white hover:-translate-y-1"
                  onClick={() => handleViewDiagram(diagram)}
                >
                  <CardHeader className="pb-3 border-b border-gray-100 bg-gray-50/30">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg font-semibold text-gray-900 capitalize flex items-center gap-2">
                        <GitBranch className="h-4 w-4 text-purple-600" />
                        {diagram.diagram_type} Diagram
                      </CardTitle>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="bg-white">v{diagram.version}</Badge>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-gray-400 hover:text-red-500 hover:bg-red-50"
                          onClick={(e) => handleDeleteDiagram(e, diagram.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    <CardDescription className="flex items-center gap-2 mt-1">
                      <Clock className="h-3 w-3" />
                      {new Date(diagram.created_at).toLocaleDateString()}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="p-4">
                    {diagram.rendered_svg ? (
                      <div
                        className="h-40 overflow-hidden rounded-md border border-gray-100 bg-white shadow-inner flex items-center justify-center p-2"
                        dangerouslySetInnerHTML={{ __html: diagram.rendered_svg }}
                      />
                    ) : (
                      <div className="h-40 flex items-center justify-center bg-gray-50 rounded-md border border-dashed border-gray-200">
                        <div className="text-center text-gray-400">
                          <GitBranch className="h-8 w-8 mx-auto mb-2 opacity-50" />
                          <span className="text-xs">Preview unavailable</span>
                        </div>
                      </div>
                    )}
                    <div className="flex gap-2 w-full mt-4">
                      <Button variant="secondary" className="flex-1 gap-2 bg-gray-100 hover:bg-gray-200 text-gray-900">
                        <Eye className="h-4 w-4" /> View
                      </Button>
                      <Button
                        variant="outline"
                        className="flex-1 gap-2 border-purple-200 text-purple-700 hover:bg-purple-50"
                        onClick={(e) => handleApplyToCode(e, diagram)}
                        disabled={isGeneratingDiff}
                      >
                        {isGeneratingDiff ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileOutput className="h-4 w-4" />}
                        Apply to Code
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>

      <DiffPreviewModal
        isOpen={isDiffModalOpen}
        onClose={() => setIsDiffModalOpen(false)}
        sessionId={previewSessionId || ''}
        token={token}
        projectId={projectId}
        onApplySuccess={onApplySuccess}
      />
    </div>
  );
}
