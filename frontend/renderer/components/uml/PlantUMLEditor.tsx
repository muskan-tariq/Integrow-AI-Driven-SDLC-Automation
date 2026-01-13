"use client";

import { useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Save, X } from "lucide-react";
import Editor from "@monaco-editor/react";

interface PlantUMLEditorProps {
  code: string;
  onChange: (code: string) => void;
  onSave: () => void;
  onCancel: () => void;
}

export default function PlantUMLEditor({
  code,
  onChange,
  onSave,
  onCancel,
}: PlantUMLEditorProps) {
  const editorRef = useRef<any>(null);

  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;
    editor.focus();
  };

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      onChange(value);
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle>Edit PlantUML Code</CardTitle>
        <div className="flex gap-2">
          <Button variant="outline" onClick={onCancel}>
            <X className="mr-2 h-4 w-4" />
            Cancel
          </Button>
          <Button onClick={onSave}>
            <Save className="mr-2 h-4 w-4" />
            Save Changes
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="border-t">
          <Editor
            height="600px"
            defaultLanguage="plaintext"
            value={code}
            onChange={handleEditorChange}
            onMount={handleEditorDidMount}
            theme="vs-light"
            options={{
              minimap: { enabled: true },
              fontSize: 14,
              lineNumbers: "on",
              rulers: [80],
              wordWrap: "on",
              tabSize: 2,
              scrollBeyondLastLine: false,
              automaticLayout: true,
            }}
          />
        </div>
      </CardContent>
    </Card>
  );
}
