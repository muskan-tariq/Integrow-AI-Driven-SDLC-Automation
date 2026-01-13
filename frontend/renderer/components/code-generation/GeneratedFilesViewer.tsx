"use client";

import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import { GeneratedFile } from '@/lib/api/code-generation';
import { Folder, FileCode, CheckCircle, XCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';

interface GeneratedFilesViewerProps {
  files: GeneratedFile[];
  onApprove?: () => void;
  onReject?: () => void;
}

export function GeneratedFilesViewer({ files, onApprove, onReject }: GeneratedFilesViewerProps) {
  const [selectedFile, setSelectedFile] = useState<GeneratedFile | null>(files.length > 0 ? files[0] : null);

  if (!files || files.length === 0) {
    return (
      <div className="text-center p-8 text-gray-500">
        No files generated yet.
      </div>
    );
  }

  const getLanguage = (file: GeneratedFile) => {
    switch (file.language) {
      case 'python': return 'python';
      case 'typescript': return 'typescript';
      case 'javascript': return 'javascript';
      case 'sql': return 'sql';
      default: return 'plaintext';
    }
  };

  return (
    <div className="flex h-[calc(100vh-200px)] border rounded-lg overflow-hidden bg-background">
      {/* File Tree / List */}
      <div className="w-1/4 border-r bg-muted/30 flex flex-col">
        <div className="p-4 border-b font-semibold flex items-center gap-2">
          <Folder className="w-4 h-4" />
          Generated Files ({files.length})
        </div>
        <ScrollArea className="flex-1">
          <div className="p-2 space-y-1">
            {files.map((file) => (
              <button
                key={file.file_path}
                onClick={() => setSelectedFile(file)}
                className={`w-full text-left px-3 py-2 rounded-md text-sm flex items-center gap-2 transition-colors ${
                  selectedFile?.file_path === file.file_path
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-accent hover:text-accent-foreground'
                }`}
              >
                <FileCode className="w-4 h-4 shrink-0" />
                <span className="truncate">{file.file_path}</span>
              </button>
            ))}
          </div>
        </ScrollArea>
        {/* Approve Actions */}
        <div className="p-4 border-t space-y-2">
          <Button onClick={onApprove} className="w-full gap-2" variant="default">
            <CheckCircle className="w-4 h-4" /> Approve & Save
          </Button>
          <Button onClick={onReject} className="w-full gap-2" variant="outline">
            <XCircle className="w-4 h-4" /> Reject
          </Button>
        </div>
      </div>

      {/* Code Editor Preview */}
      <div className="flex-1 flex flex-col">
        {selectedFile ? (
            <>
            <div className="p-4 border-b flex items-center justify-between bg-card text-card-foreground">
              <div className="font-mono text-sm">{selectedFile.file_path}</div>
              <Badge variant="outline">{selectedFile.file_type}</Badge>
            </div>
            <div className="flex-1">
              <Editor
                height="100%"
                defaultLanguage={getLanguage(selectedFile)}
                language={getLanguage(selectedFile)}
                value={selectedFile.content}
                theme="vs-dark"
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  fontSize: 14,
                }}
              />
            </div>
            </>
        ) : (
             <div className="flex-1 flex items-center justify-center text-muted-foreground">
                 Select a file to view content
             </div>
        )}
      </div>
    </div>
  );
}
