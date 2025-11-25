// frontend/app/page.tsx
"use client";

import { useEffect, useState } from "react";
import UploadForm from "../components/UploadForm";
import LatexEditor from "../components/LatexEditor";
import api from "../lib/api";

interface TailorResult {
  tailored_resume: string;
  ats_score?: number;
  keywords?: string[];
  [key: string]: any;
}

export default function HomePage() {
  const [result, setResult] = useState<TailorResult | null>(null);
  const [latex, setLatex] = useState<string>("");
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [compiling, setCompiling] = useState(false);

  // When a new result comes in, load its LaTeX into the editor
  useEffect(() => {
    if (result?.tailored_resume) {
      setLatex(result.tailored_resume);
      // clear old preview because content changed
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
        setPdfUrl(null);
      }
    }
  }, [result]);

  // Auto-compile after user stops typing (e.g., 800ms)
  useEffect(() => {
    if (!latex || latex.trim() === "") return;

    const timeout = setTimeout(() => {
      handleCompile();  // compile automatically
    }, 800); // milliseconds debounce

    return () => clearTimeout(timeout);
  }, [latex]);

  const handleCompile = async () => {
    if (compiling) return;           // prevent spam
    if (!latex.trim()) return;       // safety check

    setCompiling(true);
    setPdfUrl(null); // optional: clear old preview

    try {
      const formData = new FormData();
      formData.append("latex_content", latex);

      const res = await api.post("/compile", formData, {
        responseType: "arraybuffer",
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (pdfUrl) URL.revokeObjectURL(pdfUrl);
      const blob = new Blob([res.data], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);
      setPdfUrl(url);

    } catch (err) {
      console.error("Auto-compile failed:", err);
    } finally {
      setCompiling(false);
    }
  };


  return (
    <main className="max-w-6xl mx-auto py-10 px-4 space-y-8">
      <header className="text-center">
        <h1 className="text-3xl font-bold mb-2">ResuMatch AI</h1>
        <p className="text-gray-600">
          Upload your resume & job description, tailor it with AI, then edit the LaTeX and export a polished PDF — all on one page.
        </p>
      </header>

      {/* Step 1: Upload resume + job description + generate tailored resume */}
      <section className="bg-white rounded-xl border p-6 shadow-sm">
        <UploadForm
          onResult={(data: TailorResult) => {
            setResult(data);
          }}
        />
      </section>

      {/* Step 2: Show ATS info + LaTeX editor + PDF split view once a result exists */}
      {result && (
        <section className="space-y-4">
          {/* ATS score + keywords */}
          <div className="bg-gray-50 rounded-xl border p-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="font-semibold">
                ATS Match Score:{" "}
                <span className="font-normal">
                  {result.ats_score !== undefined
                    ? `${result.ats_score}%`
                    : "N/A"}
                </span>
              </p>
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

            <p className="text-xs text-gray-500 max-w-sm">
              You can edit the LaTeX resume below, then compile and download the
              final PDF. Changes you make in the editor are what go into the PDF.
            </p>
          </div>

          {/* Split view: LaTeX editor (left) + PDF preview (right) */}
          <div className="h-[650px] w-full flex flex-col border rounded-xl overflow-hidden bg-white">
            <div className="flex flex-1 flex-col md:flex-row">
              {/* Left: LaTeX editor */}
              <div className="md:w-1/2 w-full border-b md:border-b-0 md:border-r flex flex-col">
                <div className="px-3 py-2 border-b bg-gray-50 flex items-center justify-between">
                  <h2 className="text-sm font-semibold">LaTeX Editor</h2>
                  <span className="text-xs text-gray-500">
                    Edit the generated LaTeX here
                  </span>
                </div>
                <div className="flex-1 min-h-[300px]">
                  <LatexEditor value={latex} onChange={setLatex} />
                </div>
              </div>

              {/* Right: PDF preview */}
              <div className="md:w-1/2 w-full flex flex-col">
                <div className="px-3 py-2 border-b bg-gray-50 flex items-center justify-between">
                  <h2 className="text-sm font-semibold">PDF Preview</h2>
                  <span className="text-xs text-gray-500">
                    Click &quot;Compile PDF&quot; to update preview
                  </span>
                </div>

                {/* Auto compiling indicator */}
                {compiling && (
                  <p className="text-xs text-gray-500 px-3">Auto-compiling…</p>
                )}

                {pdfUrl ? (
                  <iframe
                    src={pdfUrl}
                    className="flex-1 w-full h-full"
                    title="Resume PDF Preview"
                  />
                ) : (
                  <div className="flex-1 flex items-center justify-center text-gray-500 text-sm">
                    No PDF yet. Click &quot;Compile PDF&quot; below to generate a preview.
                  </div>
                )}
              </div>
            </div>

            {/* Bottom action bar */}
            <div className="border-t px-4 py-3 flex flex-wrap gap-3 items-center justify-between">
              <div className="flex gap-3">
                <button
                  onClick={handleCompile}
                  disabled={compiling || !latex.trim()}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
                >
                  {compiling ? "Compiling..." : "Compile PDF"}
                </button>

                {pdfUrl && (
                  <a
                    href={pdfUrl}
                    download="tailored_resume.pdf"
                    className="px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-900"
                  >
                    Download PDF
                  </a>
                )}
              </div>

              <span className="text-xs text-gray-400">
                Tip: Make small LaTeX edits (sections, bullet points, keywords) and recompile.
              </span>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}
