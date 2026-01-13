"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  ArrowLeft,
  Download,
  Edit,
  Eye,
  Loader2,
  RefreshCw,
  Sparkles,
  HelpCircle,
  UploadCloud,
  ExternalLink
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { Skeleton } from "@/components/ui/skeleton";
import DiagramViewer from "@/components/uml/DiagramViewer";
import PlantUMLEditor from "@/components/uml/PlantUMLEditor";
import ExportDialog from "@/components/uml/ExportDialog";
import UMLApprovalDialog from "@/components/uml/UMLApprovalDialog";

export default function UMLDiagramPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();

  const projectId = params.id as string;
  const reqId = params.reqId as string;

  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [diagram, setDiagram] = useState<any>(null);
  const [plantUMLCode, setPlantUMLCode] = useState("");
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [showApprovalDialog, setShowApprovalDialog] = useState(false);
  const [isPushing, setIsPushing] = useState(false);
  const [token, setToken] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    initializeSession();
  }, []);

  useEffect(() => {
    if (token && reqId) {
      loadDiagram();
    }
  }, [reqId, token]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + S to save when editing
      if ((e.ctrlKey || e.metaKey) && e.key === "s" && isEditing) {
        e.preventDefault();
        handleSave();
      }
      // Escape to cancel editing
      if (e.key === "Escape" && isEditing) {
        setPlantUMLCode(diagram?.plantuml_code || "");
        setIsEditing(false);
      }
      // Ctrl/Cmd + E to toggle edit mode
      if ((e.ctrlKey || e.metaKey) && e.key === "e" && diagram) {
        e.preventDefault();
        setIsEditing(!isEditing);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isEditing, diagram, plantUMLCode]);

  const initializeSession = async () => {
    try {
      const authData = await window.electron.getAuth();
      if (authData && authData.accessToken) {
        setToken(authData.accessToken);
      } else {
        console.error("No auth token found");
        router.push("/");
      }
    } catch (error) {
      console.error("Error getting auth token:", error);
      router.push("/");
    }
  };

  const loadDiagram = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `http://localhost:8000/api/projects/${projectId}/requirements/${reqId}/uml`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        if (data.diagrams && data.diagrams.length > 0) {
          const latestDiagram = data.diagrams[0];
          setDiagram(latestDiagram);
          setPlantUMLCode(latestDiagram.plantuml_code);
        }
      } else if (response.status === 404) {
        // No diagrams found - this is normal for first visit
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Failed to load diagram");
      }
    } catch (error) {
      console.error("Error loading diagram:", error);
      setError("Network error. Please check your connection.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerate = async (regenerate = false) => {
    setIsGenerating(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/projects/${projectId}/requirements/${reqId}/uml/generate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ regenerate }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to generate diagram");
      }

      const data = await response.json();

      toast({
        title: "Success!",
        description: `Class diagram generated with ${data.analysis?.entities_found || 0} entities`,
      });

      await loadDiagram();
    } catch (error: any) {
      toast({
        title: "Generation Failed",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSave = async () => {
    if (!diagram) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/uml/${diagram.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ plantuml_code: plantUMLCode }),
        }
      );

      if (!response.ok) throw new Error("Failed to update diagram");

      const updated = await response.json();
      setDiagram(updated);
      setIsEditing(false);

      toast({
        title: "Saved!",
        description: "Diagram updated successfully",
      });
    } catch (error: any) {
      toast({
        title: "Save Failed",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const handleExport = async (format: "svg" | "png" | "code") => {
    if (!diagram) return;

    try {
      if (format === "code") {
        const blob = new Blob([plantUMLCode], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `diagram_${diagram.id}.puml`;
        a.click();
        URL.revokeObjectURL(url);
        return;
      }

      const response = await fetch(
        `http://localhost:8000/api/uml/${diagram.id}/render?format=${format}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) throw new Error("Failed to export diagram");

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `diagram_${diagram.id}.${format}`;
      a.click();
      URL.revokeObjectURL(url);

      toast({
        title: "Exported!",
        description: `Diagram exported as ${format.toUpperCase()}`,
      });
    } catch (error: any) {
      toast({
        title: "Export Failed",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const handlePush = async (commitMessage: string) => {
    if (!diagram) return;

    setIsPushing(true);
    try {
      const response = await fetch("http://localhost:8000/api/uml/approve", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          diagram_id: diagram.id,
          commit_message: commitMessage,
          branch: "main"
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to push to repository");
      }

      const result = await response.json();

      toast({
        title: "Pushed to Repository!",
        description: (
          <div className="flex flex-col gap-1">
            <span>Changes pushed successfully.</span>
            <a
              href={result.commit_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs underline flex items-center gap-1"
            >
              View Commit <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        ),
      });

      setShowApprovalDialog(false);
    } catch (error: any) {
      toast({
        title: "Push Failed",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsPushing(false);
    }
  };

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-background p-6">
        {/* Header */}
        <div className="max-w-7xl mx-auto mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => router.push(`/project/${projectId}/requirements`)}
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-3xl font-bold flex items-center gap-2">
                  UML Class Diagram
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-6 w-6">
                        <HelpCircle className="h-4 w-4 text-muted-foreground" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent side="right" className="max-w-xs">
                      <div className="space-y-2 text-sm">
                        <p className="font-semibold">Keyboard Shortcuts:</p>
                        <div className="grid grid-cols-2 gap-2">
                          <kbd className="px-2 py-1 bg-muted rounded">Ctrl+S</kbd>
                          <span>Save changes</span>
                          <kbd className="px-2 py-1 bg-muted rounded">Ctrl+E</kbd>
                          <span>Toggle edit</span>
                          <kbd className="px-2 py-1 bg-muted rounded">Esc</kbd>
                          <span>Cancel editing</span>
                        </div>
                      </div>
                    </TooltipContent>
                  </Tooltip>
                </h1>
                <p className="text-muted-foreground">
                  Generate and edit class diagrams from user stories
                </p>
              </div>
            </div>

            <div className="flex gap-2">
              {diagram && (
                <>
                  <Button
                    variant="outline"
                    onClick={() => setIsEditing(!isEditing)}
                  >
                    {isEditing ? (
                      <>
                        <Eye className="mr-2 h-4 w-4" />
                        Preview
                      </>
                    ) : (
                      <>
                        <Edit className="mr-2 h-4 w-4" />
                        Edit
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowExportDialog(true)}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Export
                  </Button>
                  <Button
                    variant="default"
                    className="gap-2"
                    onClick={() => setShowApprovalDialog(true)}
                  >
                    <UploadCloud className="h-4 w-4" />
                    Push to Repo
                  </Button>
                </>
              )}
              <Button
                onClick={() => handleGenerate(!!diagram)}
                disabled={isGenerating}
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : diagram ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Regenerate
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Generate
                  </>
                )}
              </Button>
              {diagram && (
                <Button
                  className="ml-2 gap-2"
                  onClick={() => router.push(`/project/${projectId}/requirements/${reqId}/code`)}
                >
                  Next: Generate Code <ArrowLeft className="h-4 w-4 rotate-180" />
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="max-w-7xl mx-auto">
          {isLoading ? (
            <Card>
              <CardContent className="p-6">
                <div className="space-y-4">
                  <Skeleton className="h-8 w-1/3" />
                  <Skeleton className="h-[400px] w-full" />
                  <div className="grid grid-cols-3 gap-4">
                    <Skeleton className="h-20 w-full" />
                    <Skeleton className="h-20 w-full" />
                    <Skeleton className="h-20 w-full" />
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : error ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center h-96 gap-4">
                <div className="text-center">
                  <h3 className="text-xl font-semibold mb-2 text-destructive">
                    Error Loading Diagram
                  </h3>
                  <p className="text-muted-foreground mb-4">{error}</p>
                  <Button onClick={loadDiagram} variant="outline">
                    Try Again
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : !diagram ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center h-96 gap-4">
                <Sparkles className="h-16 w-16 text-muted-foreground" />
                <div className="text-center">
                  <h3 className="text-xl font-semibold mb-2">
                    No diagram generated yet
                  </h3>
                  <p className="text-muted-foreground mb-4">
                    Generate a UML class diagram from your user stories
                  </p>
                  <Button onClick={() => handleGenerate(false)} disabled={isGenerating}>
                    {isGenerating ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Generate Diagram
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : isEditing ? (
            <PlantUMLEditor
              code={plantUMLCode}
              onChange={setPlantUMLCode}
              onSave={handleSave}
              onCancel={() => {
                setPlantUMLCode(diagram.plantuml_code);
                setIsEditing(false);
              }}
            />
          ) : (
            <DiagramViewer
              diagramId={diagram.id}
              svgContent={diagram.rendered_svg}
            />
          )}

          {/* Analysis Info */}
          {diagram?.analysis_metadata && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Analysis Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold">
                      {diagram.analysis_metadata.entities_found || 0}
                    </div>
                    <div className="text-sm text-muted-foreground">Classes</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold">
                      {diagram.analysis_metadata.relationships_found || 0}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Relationships
                    </div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold">
                      {diagram.analysis_metadata.total_stories || 0}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      User Stories
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Export Dialog */}
        {diagram && (
          <ExportDialog
            open={showExportDialog}
            onClose={() => setShowExportDialog(false)}
            onExport={handleExport}
            diagramId={diagram.id}
          />
        )}

        {diagram && (
          <UMLApprovalDialog
            open={showApprovalDialog}
            onClose={() => setShowApprovalDialog(false)}
            onConfirm={handlePush}
            isLoading={isPushing}
            defaultMessage={`docs: update UML diagram for REQ-${diagram.requirement_id.substring(0, 8)}`}
          />
        )}
      </div>
    </TooltipProvider>
  );
}
