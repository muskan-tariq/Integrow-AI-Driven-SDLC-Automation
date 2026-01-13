'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { RequirementsEditor } from '@/components/requirements-editor';
import { AnalysisPanel } from '@/components/analysis-panel';
import { UserStoriesList } from '@/components/user-stories-list';
import { UserStoriesChat } from '@/components/user-stories-chat';
import { useUserStories } from '@/hooks/use-user-stories';
import { ApprovalModal } from '@/components/approval-modal';
import { DeleteRequirementDialog } from '@/components/delete-requirement-dialog';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  FileText,
  GitCommit,
  ArrowLeft,
  MessageSquare,
  Plus,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  Trash2
} from 'lucide-react';


interface RequirementSummary {
  id: string;
  project_id: string;
  version: number;
  raw_text: string;
  overall_quality_score: number | null;
  status: string;
  created_at: string;
  updated_at: string;
}

interface AnalysisResult {
  requirement_id: string;
  quality_score: number;
  total_issues: number;
  ambiguity_issues: any[];
  completeness_issues: any[];
  ethics_issues: any[];
  parsed_entities: {
    actors: string[];
    actions: string[];
    entities: string[];
  };
  user_stories?: any[];
}

export default function RequirementsPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = params.id as string;

  // State
  const [existingRequirements, setExistingRequirements] = useState<RequirementSummary[]>([]);
  const [isLoadingList, setIsLoadingList] = useState(true);
  const [showEditor, setShowEditor] = useState(false);
  const [requirementText, setRequirementText] = useState('');
  const [requirementId, setRequirementId] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeView, setActiveView] = useState<'analysis' | 'stories' | 'chat'>('analysis');
  const [isApprovalModalOpen, setIsApprovalModalOpen] = useState(false);
  const [token, setToken] = useState<string>('');
  // const [isDeleting, setIsDeleting] = useState<string | null>(null); // Replaced by dialog internal state
  const [requirementToDelete, setRequirementToDelete] = useState<RequirementSummary | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  // Use custom hook for user stories
  const {
    currentStories,
    setCurrentStories,
    expandedStories,
    toggleStory,
    modifiedStories,
    selectedStories,
    toggleSelection,
    selectAll,
    addStory,
    deleteStory,
    chatHistory,
    isRefining,
    refinementPrompt,
    setRefinementPrompt,
    handleRefineStories
  } = useUserStories({
    initialStories: [],
    getAuthToken: () => token
  });

  // Initialize session
  useEffect(() => {
    initializeSession();
  }, []);

  // Fetch existing requirements when token is available
  useEffect(() => {
    if (token && projectId) {
      fetchExistingRequirements();

      // Handle autoStart
      if (searchParams.get('autoStart') === 'true') {
        handleCreateNew();
        // Clean up URL
        const newUrl = window.location.pathname;
        window.history.replaceState({}, '', newUrl);
      }
    }
  }, [token, projectId]);

  // Handle deep linking from User Stories page
  useEffect(() => {
    const reqIdToSelect = searchParams.get('selectRequirement');
    if (reqIdToSelect && existingRequirements.length > 0 && !showEditor && !requirementId) {
      const targetReq = existingRequirements.find(r => r.id === reqIdToSelect);
      if (targetReq) {
        handleSelectRequirement(targetReq);
      }
    }
  }, [existingRequirements, searchParams, showEditor, requirementId]);

  // Update stories when analysis result changes
  useEffect(() => {
    if (analysisResult?.user_stories) {
      setCurrentStories(analysisResult.user_stories);
      if (analysisResult.user_stories.length > 0) {
        setActiveView('stories');
      }
    }
  }, [analysisResult, setCurrentStories]);

  const initializeSession = async () => {
    try {
      const authData = await window.electron.getAuth();
      if (authData && authData.accessToken) {
        setToken(authData.accessToken);
      } else {
        console.error('No auth token found');
        router.push('/');
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
      router.push('/');
    }
  };

  const fetchExistingRequirements = async () => {
    setIsLoadingList(true);
    try {
      const response = await fetch(`http://localhost:8000/api/requirements/project/${projectId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setExistingRequirements(data);
        // If no requirements, show editor directly
        if (data.length === 0) {
          setShowEditor(true);
        }
      }
    } catch (error) {
      console.error('Error fetching requirements:', error);
    } finally {
      setIsLoadingList(false);
    }
  };

  const handleSelectRequirement = async (req: RequirementSummary) => {
    setRequirementId(req.id);
    setRequirementText(req.raw_text);
    setShowEditor(true);

    // Fetch user stories for this requirement
    try {
      const response = await fetch(`http://localhost:8000/api/user-stories/requirement/${req.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const stories = await response.json();
        if (stories.length > 0) {
          setCurrentStories(stories);
          setActiveView('stories');
        }
      }
    } catch (error) {
      console.error('Error fetching user stories:', error);
    }

    // Reconstruct analysis result from DB data
    if (req.overall_quality_score) {
      setAnalysisResult({
        requirement_id: req.id,
        quality_score: req.overall_quality_score,
        total_issues: 0,
        ambiguity_issues: [],
        completeness_issues: [],
        ethics_issues: [],
        parsed_entities: { actors: [], actions: [], entities: [] },
      });
    }
  };

  const handleCreateNew = () => {
    setRequirementId(null);
    setRequirementText('');
    setAnalysisResult(null);
    setCurrentStories([]);
    setShowEditor(true);
  };

  const handleBackToList = () => {
    setShowEditor(false);
    fetchExistingRequirements();
  };

  // Handle requirement analysis
  const handleAnalyze = async (text: string) => {
    if (!text.trim()) return;

    setIsAnalyzing(true);
    try {
      const response = await fetch('http://localhost:8000/api/requirements/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          project_id: projectId,
          text: text,
        }),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      setAnalysisResult(data);
      setRequirementId(data.requirement_id);
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Failed to analyze requirements. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle requirement save
  const handleSave = async (text: string) => {
    setRequirementText(text);
    //console.log('Auto-saving requirement:', text.substring(0, 50));
  };

  const handleDeleteRequirement = (e: React.MouseEvent, req: RequirementSummary) => {
    e.stopPropagation(); // Prevent card click
    setRequirementToDelete(req);
    setIsDeleteDialogOpen(true);
  };

  const confirmDelete = async (reqId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/requirements/${reqId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Deletion failed');
      }

      // Remove from state
      setExistingRequirements(prev => prev.filter(r => r.id !== reqId));

      // If currently selected, go back to new
      if (requirementId === reqId) {
        handleCreateNew();
      }
    } catch (error) {
      console.error('Error deleting requirement:', error);
      alert('Failed to delete requirement.');
      throw error; // Re-throw for dialog to catch
    }
  };

  // Handle approval
  const handleApprove = async (
    commitMessage: string,
    branch: string
  ): Promise<{ commit_url: string; version: number }> => {
    if (!requirementId) {
      throw new Error('No requirement to approve');
    }

    try {
      const response = await fetch('http://localhost:8000/api/requirements/approve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          requirement_id: requirementId,
          commit_message: commitMessage,
          branch: branch,
        }),
      });

      if (!response.ok) {
        throw new Error('Approval failed');
      }

      const data = await response.json();
      return {
        commit_url: data.commit_url,
        version: data.version,
      };
    } catch (error) {
      console.error('Approval error:', error);
      throw error;
    }
  };

  // Handle issue click (jump to location in editor)
  const handleIssueClick = (issue: any) => {
    console.log('Jump to issue:', issue);
  };

  // Convert analysis result to annotations for editor
  const getAnnotations = () => {
    if (!analysisResult) return [];

    const annotations: any[] = [];

    analysisResult.ambiguity_issues?.forEach((issue, idx) => {
      annotations.push({
        id: `ambiguity_${idx}`,
        type: 'ambiguity',
        startLine: issue.line || 1,
        endLine: issue.line || 1,
        startColumn: 1,
        endColumn: 100,
        message: issue.message,
        suggestions: issue.suggestions || [],
        severity: issue.severity || 'medium',
      });
    });

    analysisResult.completeness_issues?.forEach((issue, idx) => {
      annotations.push({
        id: `completeness_${idx}`,
        type: 'completeness',
        startLine: issue.line || 1,
        endLine: issue.line || 1,
        startColumn: 1,
        endColumn: 100,
        message: issue.message,
        suggestions: issue.suggestions || [],
        severity: issue.severity || 'medium',
      });
    });

    analysisResult.ethics_issues?.forEach((issue, idx) => {
      annotations.push({
        id: `ethics_${idx}`,
        type: 'ethics',
        startLine: issue.line || 1,
        endLine: issue.line || 1,
        startColumn: 1,
        endColumn: 100,
        message: issue.message,
        suggestions: issue.suggestions || [],
        severity: issue.severity || 'high',
      });
    });

    return annotations;
  };

  const handleCloseStories = () => {
    setCurrentStories([]);
    setActiveView('analysis');
  };

  const getStatusBadge = (status: string, score: number | null) => {
    if (status === 'approved') {
      return <Badge className="bg-green-500"><CheckCircle className="h-3 w-3 mr-1" /> Approved</Badge>;
    }
    if (score && score >= 70) {
      return <Badge className="bg-blue-500">Quality: {score}%</Badge>;
    }
    if (score && score < 70) {
      return <Badge className="bg-yellow-500"><AlertCircle className="h-3 w-3 mr-1" /> Needs Review</Badge>;
    }
    return <Badge variant="outline">Draft</Badge>;
  };

  // Render requirements list view
  if (!showEditor) {
    return (
      <div className="h-screen flex flex-col bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b px-6 py-4">
          <div className="max-w-5xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div>
                <h1 className="text-3xl font-bold tracking-tight text-gray-900">Requirements</h1>
                <p className="text-gray-500 mt-1">
                  Manage and analyze your project requirements
                </p>
              </div>
            </div>

            <Button onClick={handleCreateNew} className="gap-2">
              <Plus className="h-4 w-4" />
              New Requirement
            </Button>
          </div>
        </div>

        {/* Requirements List */}
        <div className="flex-1 p-6 overflow-auto">
          <div className="max-w-5xl mx-auto w-full">
            {isLoadingList ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : existingRequirements.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-[60vh] text-center">
                <div className="bg-blue-50 p-6 rounded-full mb-6">
                  <FileText className="h-12 w-12 text-blue-500" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">No requirements yet</h3>
                <p className="text-gray-500 mb-8 max-w-md">
                  Start by creating your first requirement. You can analyze it with AI to generate user stories automatically.
                </p>
                <Button onClick={handleCreateNew} size="lg" className="gap-2 shadow-sm hover:shadow-md transition-all">
                  <Plus className="h-5 w-5" />
                  Create First Requirement
                </Button>
              </div>
            ) : (
              <div className="grid gap-6 max-w-5xl mx-auto">
                {existingRequirements.map((req) => {
                  const getBorderColor = () => {
                    if (req.status === 'approved') return 'border-l-green-500';
                    if (req.overall_quality_score && req.overall_quality_score >= 70) return 'border-l-blue-500';
                    if (req.overall_quality_score && req.overall_quality_score < 70) return 'border-l-yellow-500';
                    return 'border-l-gray-300';
                  };

                  return (
                    <Card
                      key={req.id}
                      className={`cursor-pointer hover:shadow-lg transition-all duration-200 border-l-[6px] ${getBorderColor()} border-gray-100 group`}
                      onClick={() => handleSelectRequirement(req)}
                    >
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0 mr-4">
                            <div className="flex items-center gap-2 mb-1">
                              <CardTitle className="text-xl font-bold text-gray-900 truncate">
                                Requirement v{req.version}
                              </CardTitle>
                              {getStatusBadge(req.status, req.overall_quality_score)}
                            </div>
                            <CardDescription className="flex items-center gap-2 text-sm">
                              <Clock className="h-3.5 w-3.5" />
                              Created on {new Date(req.created_at).toLocaleDateString(undefined, {
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric'
                              })}
                            </CardDescription>
                          </div>
                          <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Button
                              variant="ghost"
                              size="icon"
                              className="hover:bg-red-50 hover:text-red-600 transition-colors"
                              onClick={(e) => handleDeleteRequirement(e, req)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <p className="text-gray-600 line-clamp-2 leading-relaxed">
                          {req.raw_text}
                        </p>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </div>
        </div>
        <DeleteRequirementDialog
          requirement={requirementToDelete}
          open={isDeleteDialogOpen}
          onOpenChange={setIsDeleteDialogOpen}
          onDelete={confirmDelete}
        />
      </div>
    );
  }

  // Render editor view (existing UI)
  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div>
              <h1 className="text-2xl font-bold">
                {requirementId ? 'Edit User Stories' : 'New User Stories'}
              </h1>
              <p className="text-sm text-gray-600">
                Write, analyze, and refine your requirements with AI assistance
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {currentStories.length === 0 && (
              <Button
                onClick={() => setIsApprovalModalOpen(true)}
                disabled={!requirementId || (analysisResult?.quality_score || 0) < 60}
                className="gap-2"
              >
                <GitCommit className="h-4 w-4" />
                Approve & Commit
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Editor OR User Stories List */}
        <div className="flex-1 p-6">
          {currentStories.length > 0 ? (
            <UserStoriesList
              stories={currentStories}
              expandedStories={expandedStories}
              modifiedStories={modifiedStories}
              selectedStories={selectedStories} // Pass selectedStories
              onToggleStory={toggleStory}
              onToggleSelection={toggleSelection} // Pass onToggleSelection
              onSelectAll={selectAll} // Pass onSelectAll
              onAddStory={addStory} // Pass onAddStory
              onDeleteStory={deleteStory} // Pass onDeleteStory
              onClose={handleCloseStories}
              requirementId={requirementId || ''}
              token={token}
            />
          ) : (
            <RequirementsEditor
              initialValue={requirementText}
              onAnalyze={handleAnalyze}
              annotations={getAnnotations()}
              isAnalyzing={isAnalyzing}
              onSave={handleSave}
              autoSaveInterval={30000}
            />
          )}
        </div>

        {/* Right: Analysis Panel / Chat Sidebar */}
        <div className="w-96 border-l bg-white">
          {currentStories.length > 0 ? (
            <Tabs defaultValue="chat" className="flex flex-col h-full">
              <div className="border-b">
                <TabsList className="w-full grid grid-cols-2">
                  <TabsTrigger value="chat" className="gap-2">
                    <MessageSquare className="h-4 w-4" />
                    AI Assistant
                  </TabsTrigger>
                  <TabsTrigger value="analysis" className="gap-2">
                    <FileText className="h-4 w-4" />
                    Analysis
                  </TabsTrigger>
                </TabsList>
              </div>

              <div className="flex-1 overflow-hidden">
                <TabsContent value="chat" className="h-full m-0">
                  <UserStoriesChat
                    chatHistory={chatHistory}
                    isRefining={isRefining}
                    prompt={refinementPrompt}
                    setPrompt={setRefinementPrompt}
                    onRefine={handleRefineStories}
                    storiesCount={currentStories.length}
                    totalPoints={currentStories.reduce((sum, s) => sum + (s.story_points || 0), 0)}
                    modifiedCount={modifiedStories.size}
                    selectedCount={selectedStories.size} // Pass selectedCount
                  />
                </TabsContent>

                <TabsContent value="analysis" className="h-full m-0">
                  <AnalysisPanel
                    analysisResult={analysisResult || undefined}
                    isAnalyzing={isAnalyzing}
                    onIssueClick={handleIssueClick}
                  />
                </TabsContent>
              </div>
            </Tabs>
          ) : (
            <Tabs value={activeView} onValueChange={(v) => setActiveView(v as any)}>
              <div className="border-b">
                <TabsList className="w-full grid grid-cols-1">
                  <TabsTrigger value="analysis" className="gap-2">
                    <FileText className="h-4 w-4" />
                    Analysis
                  </TabsTrigger>
                </TabsList>
              </div>

              <div className="h-[calc(100vh-180px)]">
                <TabsContent value="analysis" className="h-full m-0">
                  <AnalysisPanel
                    analysisResult={analysisResult || undefined}
                    isAnalyzing={isAnalyzing}
                    onIssueClick={handleIssueClick}
                  />
                </TabsContent>
              </div>
            </Tabs>
          )}
        </div>
      </div>

      {/* Modals */}
      <ApprovalModal
        isOpen={isApprovalModalOpen}
        onClose={() => setIsApprovalModalOpen(false)}
        requirementId={requirementId || ''}
        qualityScore={analysisResult?.quality_score || 0}
        totalIssues={analysisResult?.total_issues || 0}
        requirementText={requirementText}
        onApprove={handleApprove}
      />

      <DeleteRequirementDialog
        requirement={requirementToDelete}
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
        onDelete={confirmDelete}
      />
    </div>
  );
}
