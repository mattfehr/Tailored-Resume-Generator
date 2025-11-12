"use client";

import { useState } from "react";
import UploadForm from "../components/UploadForm";
import api from "../lib/api";

export default function HomePage() {
  const [result, setResult] = useState<any>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [compiling, setCompiling] = useState(false);

  const handleCompile = async () => {
    if (!result?.tailored_resume) {
      alert("No tailored LaTeX content to compile.");
      return;
    }

    try {
      setCompiling(true);

      const formData = new FormData();
      formData.append("latex_content", result.tailored_resume);

      const res = await api.post<Blob>("/compile", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        responseType: "blob",
      });

      const blob = new Blob([res.data], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);
      setPdfUrl(url);
    } catch (err) {
      console.error(err);
      alert("PDF compilation failed. Check LaTeX syntax or backend logs.");
    } finally {
      setCompiling(false);
    }
  };

  return (
    <main className="max-w-3xl mx-auto py-10 px-4">
      <h1 className="text-3xl font-bold mb-6 text-center">ResuMatch AI</h1>

      <UploadForm onResult={(data) => setResult(data)} />

      {result && (
        <div className="mt-8 bg-gray-50 p-6 rounded-xl border">
          <h2 className="text-xl font-semibold mb-2">Tailored Resume</h2>

          <pre className="whitespace-pre-wrap text-sm bg-white border p-3 rounded-md overflow-x-auto">
            {result.tailored_resume || "No rewritten text found"}
          </pre>

          <div className="mt-4">
            <p className="font-semibold">ATS Match Score:</p>
            <p>{result.ats_score ? `${result.ats_score}%` : "N/A"}</p>
          </div>

          <div className="mt-2">
            <p className="font-semibold">Extracted Keywords:</p>
            <p className="text-sm text-gray-700">
              {result.keywords?.join(", ") || "None"}
            </p>
          </div>

          <div className="mt-6 flex gap-4">
            <button
              onClick={handleCompile}
              disabled={compiling}
              className="bg-green-600 text-white rounded-md px-4 py-2 hover:bg-green-700 disabled:opacity-50"
            >
              {compiling ? "Compiling..." : "Compile & Preview PDF"}
            </button>
          </div>
        </div>
      )}

      {pdfUrl && (
        <div className="mt-10">
          <h2 className="text-xl font-semibold mb-2">PDF Preview</h2>
          <iframe
            src={pdfUrl}
            className="w-full h-[80vh] border rounded-lg"
            title="Resume PDF Preview"
          />
          <a
            href={pdfUrl}
            download="tailored_resume.pdf"
            className="inline-block mt-4 px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-900"
          >
            Download PDF
          </a>
        </div>
      )}
    </main>
  );
}
