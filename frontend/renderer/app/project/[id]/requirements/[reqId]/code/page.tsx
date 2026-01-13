"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { CodeGenerationPanel } from "@/components/code-generation/CodeGenerationPanel";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { Toaster } from "@/components/ui/toaster";

export default function CodeGenerationPage() {
  const params = useParams();
  const router = useRouter();
  const [token, setToken] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);

  const projectId = params.id as string;
  const reqId = params.reqId as string;

  useEffect(() => {
    initializeSession();
  }, []);

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
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto mb-6">
        <div className="flex items-center gap-4 mb-6">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.push(`/project/${projectId}/requirements/${reqId}/uml`)}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Code Generation</h1>
            <p className="text-muted-foreground">
              Generate and review code based on your analysis and diagrams
            </p>
          </div>
        </div>

        <CodeGenerationPanel 
          projectId={projectId} 
          requirementId={reqId} 
          token={token} 
        />
      </div>
      <Toaster />
    </div>
  );
}
