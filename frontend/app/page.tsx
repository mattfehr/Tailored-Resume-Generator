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

interface ScoreResponse {
  ats_score: number;
  keywords: string[];
}

export default function HomePage() {
  const [result, setResult] = useState<TailorResult | null>(null);
  const [latex, setLatex] = useState<string>("");
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [compiling, setCompiling] = useState(false);
  const [recalculating, setRecalculating] = useState(false);

  // Load LaTeX into editor when new result arrives
  useEffect(() => {
    if (result?.tailored_resume) {
      setLatex(result.tailored_resume);
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
        setPdfUrl(null);
      }
    }
  }, [result]);

  // Auto-compile PDF (debounced 800ms)
  useEffect(() => {
    if (!latex || latex.trim() === "") return;

    const timeout = setTimeout(() => {
      handleCompile();
    }, 800);

    return () => clearTimeout(timeout);
  }, [latex]);

  /** --------------------------------------------
   *   PDF COMPILE (FIXED TYPE ERROR)
   * --------------------------------------------- */
  const handleCompile = async () => {
    if (compiling) return;
    if (!latex.trim()) return;

    setCompiling(true);
    setPdfUrl(null);

    try {
      const formData = new FormData();
      formData.append("latex_content", latex);

      // Fully typed Axios response
      const res = await api.post<ArrayBuffer>("/compile", formData, {
        responseType: "arraybuffer",
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (pdfUrl) URL.revokeObjectURL(pdfUrl);

      // FIX: cast ArrayBuffer into Blob
      const blob = new Blob([res.data as ArrayBuffer], {
        type: "application/pdf",
      });

      const url = URL.createObjectURL(blob);
      setPdfUrl(url);
    } catch (err) {
      console.error("Auto-compile failed:", err);
    } finally {
      setCompiling(false);
    }
  };

  /** --------------------------------------------
   *   RESCORE ATS (FULLY TYPED)
   * --------------------------------------------- */
  const handleRecalculateATS = async () => {
    if (!latex.trim()) return;

    try {
      setRecalculating(true);

      const formData = new FormData();
      formData.append("latex_content", latex);

      // Fully typed score response
      const res = await api.post<ScoreResponse>("/score", formData);

      setResult(prev => ({
        ...prev!,
        ats_score: res.data.ats_score,
        keywords: res.data.keywords || prev?.keywords,
      }));
    } catch (err) {
      console.error("Error recalculating ATS score:", err);
    } finally {
      setRecalculating(false);
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

      {/* Step 1: Upload */}
      <section className="bg-white rounded-xl border p-6 shadow-sm">
        <UploadForm onResult={(data: TailorResult) => setResult(data)} />
      </section>

      {/* Step 2 */}
      {result && (
        <section className="space-y-4">

          {/* ------------------------ ATS SECTION ------------------------ */}
          <div className="bg-white rounded-xl border p-5 shadow-sm flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row justify-between sm:items-center">

              {/* Score + button */}
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold">ATS Match Score:</span>

                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      (result.ats_score ?? 0) >= 70
                        ? "bg-green-100 text-green-700"
                        : (result.ats_score ?? 0) >= 40
                        ? "bg-yellow-100 text-yellow-700"
                        : "bg-red-100 text-red-700"
                    }`}
                  >
                    {result.ats_score !== undefined ? `${result.ats_score}%` : "N/A"}
                  </span>
                </div>

                <button
                  onClick={handleRecalculateATS}
                  disabled={recalculating}
                  className="px-3 py-1 text-xs bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {recalculating ? "Recalculating…" : "Recalculate"}
                </button>
              </div>

              <p className="text-xs text-gray-500 max-w-sm">
                Edit your LaTeX below — the ATS score and keywords help you optimize your resume.
              </p>
            </div>

            {/* Keywords */}
            {result.keywords && Array.isArray(result.keywords) && (
              <div>
                <p className="font-semibold text-sm mb-2">Key Keywords:</p>
                <div className="flex flex-wrap gap-2 text-xs">
                  {result.keywords.map((kw, i) => (
                    <span
                      key={i}
                      className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full"
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* ------------------------ SPLIT VIEW ------------------------ */}
          <div className="h-[650px] w-full flex flex-col border rounded-xl overflow-hidden bg-white">
            <div className="flex flex-1 flex-col md:flex-row">

              {/* LEFT — EDITOR */}
              <div className="md:w-1/2 w-full border-b md:border-b-0 md:border-r flex flex-col">
                <div className="px-3 py-2 border-b bg-gray-50 flex items-center justify-between">
                  <h2 className="text-sm font-semibold">LaTeX Editor</h2>
                  <span className="text-xs text-gray-500">Edit the generated LaTeX</span>
                </div>
                <div className="flex-1 min-h-[300px]">
                  <LatexEditor value={latex} onChange={setLatex} />
                </div>
              </div>

              {/* RIGHT — PDF */}
              <div className="md:w-1/2 w-full flex flex-col">
                <div className="px-3 py-2 border-b bg-gray-50 flex items-center justify-between">
                  <h2 className="text-sm font-semibold">PDF Preview</h2>
                  <span className="text-xs text-gray-500">Auto-compiling enabled</span>
                </div>

                {compiling && (
                  <p className="text-xs text-gray-500 px-3">Auto-compiling…</p>
                )}

                {pdfUrl ? (
                  <iframe src={pdfUrl} className="flex-1 w-full h-full" />
                ) : (
                  <div className="flex-1 flex items-center justify-center text-gray-500 text-sm">
                    No PDF yet. Click "Compile PDF" below.
                  </div>
                )}
              </div>
            </div>

            {/* ------------------------ BOTTOM ACTION BAR ------------------------ */}
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

                <button
                  onClick={() => {
                    const blob = new Blob([latex], { type: "text/plain" });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = "tailored_resume.tex";
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                  className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
                >
                  Download LaTeX
                </button>
              </div>

              <span className="text-xs text-gray-400">
                Tip: Make small edits and recompile for the best PDF output.
              </span>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}
