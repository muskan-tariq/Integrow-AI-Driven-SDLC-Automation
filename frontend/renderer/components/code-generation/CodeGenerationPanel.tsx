"use client";

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Sparkles, RefreshCw, CheckCircle } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { codeGenerationApi, CodeGenerationResult, GeneratedFile } from '@/lib/api/code-generation';
import { GeneratedFilesViewer } from './GeneratedFilesViewer';

interface CodeGenerationPanelProps {
  projectId: string;
  requirementId: string;
  token: string;
}

import CodeApprovalDialog from './CodeApprovalDialog';

// ... (existing helper function if any)

export function CodeGenerationPanel({ projectId, requirementId, token }: CodeGenerationPanelProps) {
  const [loading, setLoading] = useState(false);
  const [approving, setApproving] = useState(false);
  const [result, setResult] = useState<CodeGenerationResult | null>(null);
  const [showApprovalDialog, setShowApprovalDialog] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
     // Check for existing session
     const fetchLatest = async () => {
         try {
             const session = await codeGenerationApi.getLatestForRequirement(requirementId, token);
             if (session) {
                 setResult(session);
             }
         } catch (error) {
             console.error("Failed to fetch latest session", error);
         }
     };
     fetchLatest();
  }, [requirementId, token]);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const data = await codeGenerationApi.generateCode({
        project_id: projectId,
        requirement_id: requirementId,
        tech_stack: {
           backend: 'python-fastapi',
           database: 'postgresql',
           frontend: 'react-typescript',
           orm: 'sqlalchemy'
        },
        generation_scope: ['models', 'api', 'services']
      }, token);

      setResult(data);
      toast({
        title: "Code Generated Successfully",
        description: `Generated ${data.total_files} files in ${data.generation_time.toFixed(2)}s`,
      });
    } catch (error: any) {
      toast({
        title: "Generation Failed",
        description: error.message || "An error occurred during code generation",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleApproveClick = () => {
      setShowApprovalDialog(true);
  };

  const handleConfirmApproval = async (commitMessage: string) => {
      if (!result) return;
      
      setApproving(true);
      try {
          const response = await codeGenerationApi.approveCode({
              session_id: result.session_id,
              commit_message: commitMessage,
              branch: "main",
              target_directory: "src" // Default target
          }, token);
          
          toast({
              title: "Code Approved & Committed",
              description: `Committed ${response.files_committed} files to ${response.branch} branch.`,
          });
          
          // Refresh session to show committed status if needed, or update local state
          setResult({
              ...result,
              status: 'committed'
          });
          
          setShowApprovalDialog(false);
          
      } catch (error: any) {
          console.error("Approval failed", error);
          toast({
              title: "Approval Failed",
              description: error.message || error.response?.data?.detail || "Failed to commit code.",
              variant: "destructive",
          });
      } finally {
          setApproving(false);
      }
  };

   const handleReject = () => {
       setResult(null);
       toast({
           title: "Rejected",
           description: "Generated code rejected. You can regenerate.",
       });
   };

  if (!result) {
    // ... (rest of initial view)
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-yellow-500" />
            AI Code Generation
          </CardTitle>
          <CardDescription>
            Generate production-ready code from your requirements and user stories.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center p-12 gap-4">
           {loading ? (
             <div className="flex flex-col items-center gap-2 text-muted-foreground">
               <Loader2 className="w-8 h-8 animate-spin" />
               <p>Analyzing requirements and generating code...</p>
             </div>
           ) : (
            <div className="text-center space-y-4">
                <p className="text-muted-foreground max-w-md">
                    We will generate Models, API Routers, and Service layers based on the approved User Stories and Class Diagram.
                </p>
                <Button size="lg" onClick={handleGenerate} className="gap-2">
                    <Sparkles className="w-4 h-4" /> Generate Code
                </Button>
            </div>
           )}
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
        <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-yellow-500" /> Generated Code
            </h2>
            <div className="flex gap-2">
                {result.status === 'committed' && (
                    <span className="text-sm bg-green-100 text-green-800 px-3 py-1 rounded-full flex items-center gap-1">
                        <CheckCircle className="w-3 h-3" /> Committed
                    </span>
                )}
                <Button variant="outline" size="sm" onClick={handleGenerate} disabled={loading || approving} className="gap-2">
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                    Regenerate
                </Button>
            </div>
        </div>
        
        <GeneratedFilesViewer 
            files={result.files} 
            onApprove={result.status !== 'committed' ? handleApproveClick : undefined}
            onReject={handleReject}
        />
        
        <CodeApprovalDialog 
            open={showApprovalDialog}
            onClose={() => setShowApprovalDialog(false)}
            onConfirm={handleConfirmApproval}
            isLoading={approving}
            filesCount={result.total_files}
        />
    </div>
  );
}

