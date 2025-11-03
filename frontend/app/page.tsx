"use client";

import { useState } from "react";
import UploadForm from "../components/UploadForm";

export default function HomePage() {
  const [result, setResult] = useState<any>(null);

  return (
    <main className="max-w-3xl mx-auto py-10 px-4">
      <h1 className="text-3xl font-bold mb-6 text-center">ResuMatch AI</h1>

      <UploadForm onResult={setResult} />

      {result && (
        <div className="mt-8 bg-gray-50 p-6 rounded-xl border">
          <h2 className="text-xl font-semibold mb-2">Rewritten Resume</h2>
          <pre className="whitespace-pre-wrap text-sm">
            {result.rewritten_text || "No rewritten text found"}
          </pre>

          <div className="mt-4">
            <p className="font-semibold">ATS Match Score:</p>
            <p>{result.match_score ? `${result.match_score}%` : "N/A"}</p>
          </div>

          <div className="mt-2">
            <p className="font-semibold">Extracted Keywords:</p>
            <p className="text-sm text-gray-700">
              {result.keywords?.join(", ") || "None"}
            </p>
          </div>
        </div>
      )}
    </main>
  );
}

