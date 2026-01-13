'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Loader2, Save, FileText, AlertCircle } from 'lucide-react';

interface Annotation {
  id: string;
  type: 'ambiguity' | 'completeness' | 'ethics';
  startLine: number;
  endLine: number;
  startColumn: number;
  endColumn: number;
  message: string;
  suggestions: string[];
  severity: 'high' | 'medium' | 'low';
}

interface RequirementsEditorProps {
  initialValue?: string;
  onAnalyze?: (text: string) => void;
  annotations?: Annotation[];
  isAnalyzing?: boolean;
  onSave?: (text: string) => void;
  autoSaveInterval?: number; // in milliseconds
}

export function RequirementsEditor({
  initialValue = '',
  onAnalyze,
  annotations = [],
  isAnalyzing = false,
  onSave,
  autoSaveInterval = 30000, // 30 seconds
}: RequirementsEditorProps) {
  const [content, setContent] = useState(initialValue);
  const [wordCount, setWordCount] = useState(0);
  const [charCount, setCharCount] = useState(0);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [editor, setEditor] = useState<any>(null);

  // Calculate word and character count
  const updateCounts = useCallback((text: string) => {
    setCharCount(text.length);
    const words = text.trim().split(/\s+/).filter(word => word.length > 0);
    setWordCount(words.length);
  }, []);

  // Auto-save functionality
  useEffect(() => {
    if (!onSave) return;

    const timer = setInterval(() => {
      if (content.trim()) {
        handleSave();
      }
    }, autoSaveInterval);

    return () => clearInterval(timer);
  }, [content, autoSaveInterval, onSave]);

  // Handle content change
  const handleEditorChange = (value: string | undefined) => {
    const newContent = value || '';
    setContent(newContent);
    updateCounts(newContent);
  };

  // Handle save
  const handleSave = async () => {
    if (!onSave) return;
    
    setIsSaving(true);
    try {
      await onSave(content);
      setLastSaved(new Date());
    } catch (error) {
      console.error('Save failed:', error);
    } finally {
      setIsSaving(false);
    }
  };

  // Handle analyze
  const handleAnalyze = () => {
    if (onAnalyze && content.trim()) {
      onAnalyze(content);
    }
  };

  // Apply annotations to editor
  useEffect(() => {
    if (!editor) return;

    const decorations = annotations.map(annotation => ({
      range: {
        startLineNumber: annotation.startLine,
        startColumn: annotation.startColumn,
        endLineNumber: annotation.endLine,
        endColumn: annotation.endColumn,
      },
      options: {
        className: `annotation-${annotation.type}`,
        hoverMessage: {
          value: `**${annotation.type.toUpperCase()}** (${annotation.severity})\\n\\n${annotation.message}${
            annotation.suggestions.length > 0
              ? `\\n\\n**Suggestions:**\\n${annotation.suggestions.map((s, i) => `${i + 1}. ${s}`).join('\\n')}`
              : ''
          }`,
        },
        inlineClassName: `inline-annotation-${annotation.type}`,
      },
    }));

    editor.deltaDecorations([], decorations);
  }, [editor, annotations]);

  // Handle editor mount
  const handleEditorDidMount = (mountedEditor: any, monaco: any) => {
    setEditor(mountedEditor);

    // Add keyboard shortcuts
    mountedEditor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS,
      handleSave
    );

    mountedEditor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyE,
      handleAnalyze
    );
  };

  // Get annotation counts
  const getAnnotationCounts = () => {
    const counts = {
      ambiguity: 0,
      completeness: 0,
      ethics: 0,
    };

    annotations.forEach(ann => {
      counts[ann.type]++;
    });

    return counts;
  };

  const counts = getAnnotationCounts();

  return (
    <div className="flex flex-col h-full gap-4">
      {/* Toolbar */}
      <Card className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              onClick={handleAnalyze}
              disabled={isAnalyzing || !content.trim()}
              className="gap-2"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <FileText className="h-4 w-4" />
                  Analyze Requirements
                </>
              )}
            </Button>

            <Button
              onClick={handleSave}
              variant="outline"
              disabled={isSaving || !content.trim()}
              className="gap-2"
            >
              {isSaving ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  Save
                </>
              )}
            </Button>

            {annotations.length > 0 && (
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-yellow-600" />
                <span className="text-sm font-medium">Issues found:</span>
                {counts.ambiguity > 0 && (
                  <Badge variant="outline" className="bg-yellow-100 text-yellow-800">
                    {counts.ambiguity} Ambiguous
                  </Badge>
                )}
                {counts.completeness > 0 && (
                  <Badge variant="outline" className="bg-orange-100 text-orange-800">
                    {counts.completeness} Incomplete
                  </Badge>
                )}
                {counts.ethics > 0 && (
                  <Badge variant="outline" className="bg-red-100 text-red-800">
                    {counts.ethics} Ethics
                  </Badge>
                )}
              </div>
            )}
          </div>

          <div className="flex items-center gap-4 text-sm text-gray-600">
            <span>{wordCount} words</span>
            <span>{charCount} characters</span>
            {lastSaved && (
              <span className="text-xs">
                Last saved: {lastSaved.toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>
      </Card>

      {/* Editor */}
      <Card className="flex-1 overflow-hidden">
        <Editor
          height="100%"
          defaultLanguage="plaintext"
          value={content}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          theme="vs-light"
          options={{
            minimap: { enabled: false },
            lineNumbers: 'on',
            wordWrap: 'on',
            fontSize: 14,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            insertSpaces: true,
          }}
        />
      </Card>

      {/* Custom CSS for annotations */}
      <style jsx global>{`
        .annotation-ambiguity {
          background-color: rgba(255, 193, 7, 0.2);
          border-bottom: 2px solid #ffc107;
        }
        .annotation-completeness {
          background-color: rgba(255, 152, 0, 0.2);
          border-bottom: 2px solid #ff9800;
        }
        .annotation-ethics {
          background-color: rgba(244, 67, 54, 0.2);
          border-bottom: 2px solid #f44336;
        }
        .inline-annotation-ambiguity {
          text-decoration: underline wavy #ffc107;
        }
        .inline-annotation-completeness {
          text-decoration: underline wavy #ff9800;
        }
        .inline-annotation-ethics {
          text-decoration: underline wavy #f44336;
        }
      `}</style>
    </div>
  );
}
