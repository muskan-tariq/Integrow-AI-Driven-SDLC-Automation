'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, Code, ArrowRight, Clock, FileCode, CheckCircle, Plus, Trash2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { CodeGenerationModal } from '@/components/code/CodeGenerationModal';

interface CodeSession {
  id: string;
  requirement_id: string;
  status: string;
  total_files: number;
  total_lines: number;
  generation_time: number;
  created_at: string;
}

export default function CodeGenerationPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
  const projectId = params.id as string;

  const [sessions, setSessions] = useState<CodeSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [token, setToken] = useState('');
  const [isGenerationModalOpen, setIsGenerationModalOpen] = useState(false);

  useEffect(() => {
    initializeSession();
  }, []);

  useEffect(() => {
    if (token) {
      fetchSessions();

      // Handle autoStart
      if (searchParams?.get('autoStart') === 'true') {
        // Redir to requirements to pick a source
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

  const fetchSessions = async () => {
    setIsLoading(true);
    try {
      // Fetch code generation sessions for this project
      const response = await fetch(`http://localhost:8000/api/code-generation/project/${projectId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSessions(data || []);
      }
    } catch (error) {
      console.error('Error fetching sessions:', error);
      // Sessions endpoint may not exist yet, gracefully handle
      setSessions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteSession = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this code generation session? This will only remove the session record, not the generated code files.')) return;

    try {
      const response = await fetch(`http://localhost:8000/api/code-generation/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setSessions(sessions.filter(s => s.id !== sessionId));
      } else {
        const error = await response.json();
        alert(`Failed to delete session: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error deleting session:', error);
      alert('Failed to delete session');
    }
  };

  const handleGenerateCode = async (umlId: string, requirementId: string) => {
    if (!token) return;

    try {
      const response = await fetch('http://localhost:8000/api/code-generation/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          project_id: projectId,
          requirement_id: requirementId,
          uml_diagram_id: umlId,
          generation_scope: ["models", "api", "services"], // Default scope
          // tech_stack defaults to configured defaults in backend model
        }),
      });

      if (response.ok) {
        await fetchSessions(); // Refresh list to show new session
      } else {
        console.error('Failed to start generation');
        const data = await response.json();
        alert(`Generation failed: ${data.detail}`);
      }
    } catch (error) {
      console.error('Error generating code:', error);
      alert('Failed to generate code.');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge className="bg-green-500"><CheckCircle className="h-3 w-3 mr-1" /> Completed</Badge>;
      case 'approved':
        return <Badge className="bg-blue-500">Approved</Badge>;
      case 'generating':
        return <Badge className="bg-yellow-500">Generating...</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50 text-gray-900">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4 shrink-0">
        <div className="max-w-5xl mx-auto w-full">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-gray-900">Code Generation</h1>
              <p className="text-gray-500 mt-1">
                Manage auto-generated code sessions from your architectural designs.
              </p>
            </div>
            <Button onClick={() => setIsGenerationModalOpen(true)} className="gap-2">
              <Plus className="h-4 w-4" />
              Generate New Code
            </Button>
          </div>
        </div>
      </div>

      <CodeGenerationModal
        open={isGenerationModalOpen}
        onOpenChange={setIsGenerationModalOpen}
        projectId={projectId}
        onGenerate={handleGenerateCode}
      />

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-5xl mx-auto w-full">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
          ) : sessions.length === 0 ? (
            <Card className="border-0 shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Code className="h-5 w-5" />
                  No Code Generated Yet
                </CardTitle>
                <CardDescription>
                  Code is generated from UML class diagrams
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  Create requirements, generate user stories, create UML diagrams, then generate code.
                </p>
                <Button onClick={() => router.push(`/project/${projectId}/requirements`)}>
                  Go to Requirements <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4 pb-10">
              {sessions.map((session) => (
                <Card
                  key={session.id}
                  className="cursor-pointer hover:shadow-lg transition-all duration-200 border-0 shadow-sm group bg-white/50 hover:bg-white hover:-translate-x-1"
                  onClick={() => router.push(`/project/${projectId}/requirements/${session.requirement_id}/code`)}
                >
                  <CardHeader className="pb-3 border-b border-gray-100">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                          <FileCode className="h-5 w-5 text-blue-600" />
                          Generation Session
                        </CardTitle>
                      </div>
                      <div className="flex items-center gap-2">
                        {getStatusBadge(session.status)}
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-gray-400 hover:text-red-500 hover:bg-red-50"
                          onClick={(e) => handleDeleteSession(e, session.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between">
                      <div className="flex gap-6 text-sm text-gray-600">
                        <div className="flex items-center gap-2">
                          <div className="p-1.5 bg-gray-100 rounded text-gray-500"><Code className="h-3 w-3" /></div>
                          <span><span className="font-semibold text-gray-900">{session.total_files}</span> files generated</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="p-1.5 bg-gray-100 rounded text-gray-500"><Clock className="h-3 w-3" /></div>
                          <span>took <span className="font-semibold text-gray-900">{session.generation_time.toFixed(1)}s</span></span>
                        </div>
                      </div>
                      <div className="text-xs text-gray-400 font-mono">
                        {new Date(session.created_at).toLocaleString()}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
