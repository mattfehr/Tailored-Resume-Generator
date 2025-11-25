"use client";

import { useEffect, useState } from "react";
import UploadForm from "../components/UploadForm";
import api from "../lib/api";

export default function HomePage() {
  const [result, setResult] = useState<any>(null);
  const [latexContent, setLatexContent] = useState<string>("");
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [compiling, setCompiling] = useState(false);

  // Whenever we get a new tailored resume from the backend,
  // initialize the editable LaTeX field with it.
  useEffect(() => {
    if (result?.tailored_resume) {
      setLatexContent(result.tailored_resume);
      // Clear any previous PDF preview because content changed
      setPdfUrl(null);
    }
  }, [result]);

  const handleCompile = async () => {
    if (!latexContent.trim()) {
      alert("No LaTeX content to compile.");
      return;
    }

    try {
      setCompiling(true);

      const formData = new FormData();
      // Backend /api/compile expects a 'latex_content' form field
      formData.append("latex_content", latexContent);

      const res = await api.post("/compile", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        responseType: "arraybuffer", // we expect a PDF binary
      });

      // Revoke old blob URL if any
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }

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

      {/* Upload + job description form */}
      <UploadForm onResult={(data) => setResult(data)} />

      {/* Tailored result + live LaTeX editor */}
      {result && (
        <div className="mt-8 bg-gray-50 p-6 rounded-xl border">
          <h2 className="text-xl font-semibold mb-2">
            Tailored Resume (LaTeX)
          </h2>

          <p className="text-sm text-gray-600 mb-2">
            You can edit the generated LaTeX below. Any changes you make here
            will be used when compiling the PDF.
          </p>

          <textarea
            value={latexContent}
            onChange={(e) => setLatexContent(e.target.value)}
            rows={24}
            className="w-full border rounded-md p-3 bg-white font-mono text-xs whitespace-pre overflow-auto"
            spellCheck={false}
          />

          <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="font-semibold">ATS Match Score:</p>
              <p>{result.ats_score ? `${result.ats_score}%` : "N/A"}</p>
              {result.keywords && Array.isArray(result.keywords) && (
                <div className="mt-2">
                  <p className="font-semibold text-sm mb-1">Key Keywords:</p>
                  <div className="flex flex-wrap gap-2 text-xs">
                    {result.keywords.map((kw: string, idx: number) => (
                      <span
                        key={idx}
                        className="inline-flex items-center rounded-full bg-blue-100 px-2 py-1 text-blue-800"
                      >
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

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

      {/* PDF preview + download */}
      {pdfUrl && (
        <div className="mt-10">
          <h2 className="text-xl font-semibold mb-2">PDF Preview</h2>
          <iframe
            src={pdfUrl}
            className="w-full h-[600px] border rounded-md"
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
