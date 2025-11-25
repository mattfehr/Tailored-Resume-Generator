// frontend/components/LatexEditor.tsx
"use client";

import Editor from "@monaco-editor/react";

interface LatexEditorProps {
  value: string;
  onChange: (value: string) => void;
}

export default function LatexEditor({ value, onChange }: LatexEditorProps) {
  return (
    <Editor
      height="100%"
      defaultLanguage="latex"
      theme="vs-dark"
      value={value}
      onChange={(v) => onChange(v ?? "")}
      options={{
        minimap: { enabled: false },
        fontSize: 14,
        scrollBeyondLastLine: false,
        wordWrap: "on",
        automaticLayout: true,
        tabSize: 2,
      }}
    />
  );
}
