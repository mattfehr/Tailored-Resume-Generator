"use client";

import { useEffect, useState } from "react";
import UploadForm from "../components/UploadForm";
import LatexEditor from "../components/LatexEditor";
import api from "../lib/api";
import { supabase } from "../lib/supabase/client";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

interface TailorResult {
  tailored_resume: string;
  ats_score?: number;
  keywords?: string[];
  job_description?: string;
  [key: string]: any;
}

interface ScoreResponse {
  ats_score: number;
  keywords: string[];
}

type TemplateOption = { id: string; title: string };

// ---- ASCII NORMALIZER ----
function normalizeToASCII(str: string) {
  return str
    .normalize("NFKD")
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u201C\u201D]/g, '"')
    .replace(/\u2014/g, "--")
    .replace(/\u2013/g, "-")
    .replace(/\u00A0/g, " ")
    .replace(/[^\x00-\x7F]/g, "");
}

export default function HomePage() {
  const [result, setResult] = useState<TailorResult | null>(null);
  const [latex, setLatex] = useState<string>("");
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [compiling, setCompiling] = useState(false);
  const [recalculating, setRecalculating] = useState(false);

  // ---- Track auth session ----
  const [session, setSession] = useState<any>(null);

  // ---- Templates ----
  const [templates, setTemplates] = useState<TemplateOption[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>(""); // "" = default Jake

  useEffect(() => {
    const client = supabase();

    client.auth.getSession().then(({ data }) => {
      setSession(data.session);
    });

    const { data: listener } = client.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => {
      listener.subscription.unsubscribe();
    };
  }, []);

  // Fetch templates when logged in
  useEffect(() => {
    const loadTemplates = async () => {
      if (!session?.access_token) {
        setTemplates([]);
        setSelectedTemplateId("");
        return;
      }

      try {
        const res = await fetch(`${API_URL}/templates`, {
          headers: { Authorization: `Bearer ${session.access_token}` },
        });

        if (!res.ok) {
          setTemplates([]);
          return;
        }

        const data = await res.json();
        setTemplates(
          (data || []).map((t: any) => ({
            id: t.id,
            title: t.title,
          }))
        );
      } catch (err) {
        console.error("Failed to load templates:", err);
        setTemplates([]);
      }
    };

    loadTemplates();
  }, [session]);

  // Load LaTeX into editor when new result arrives
  useEffect(() => {
    if (result?.tailored_resume) {
      setLatex(result.tailored_resume);
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
        setPdfUrl(null);
      }
    }
  }, [result?.tailored_resume]); // eslint-disable-line react-hooks/exhaustive-deps

  /** PDF COMPILE */
  const handleCompile = async () => {
    if (compiling || !latex.trim()) return;

    setCompiling(true);
    setPdfUrl(null);

    try {
      const formData = new FormData();
      formData.append("latex_content", latex);

      // ✅ DO NOT set Content-Type manually; axios will set boundary correctly
      const res = await api.post<ArrayBuffer>("/compile", formData, {
        responseType: "arraybuffer",
      });

      if (pdfUrl) URL.revokeObjectURL(pdfUrl);

      const blob = new Blob([res.data as ArrayBuffer], {
        type: "application/pdf",
      });

      const url = URL.createObjectURL(blob);
      setPdfUrl(url);
    } catch (err) {
      console.error("Compile failed:", err);
    } finally {
      setCompiling(false);
    }
  };

  /** RE-CALCULATE ATS SCORE */
  const handleRecalculateATS = async () => {
    if (!latex.trim()) return;
    if (!result?.job_description || !result?.keywords) return;

    try {
      setRecalculating(true);

      const cleanedLatex = normalizeToASCII(
        latex
          .replace(/^```[a-zA-Z]*\s*/m, "")
          .replace(/```$/m, "")
          .trim()
      );

      const cleanedJobDesc = normalizeToASCII(result.job_description);
      const cleanedKeywords = result.keywords.map(normalizeToASCII);

      const formData = new FormData();
      formData.append("latex_body", cleanedLatex);
      formData.append("job_description", cleanedJobDesc);
      formData.append("keywords_json", JSON.stringify(cleanedKeywords));

      // ✅ DO NOT set Content-Type manually
      const res = await api.post<ScoreResponse>("/score", formData);

      setResult((prev) => ({
        ...prev!,
        ats_score: res.data.ats_score,
        keywords: res.data.keywords,
      }));
    } catch (err) {
      console.error("Error recalculating ATS score:", err);
    } finally {
      setRecalculating(false);
    }
  };

  // ---- Save Resume handler ----
  const handleSaveResume = async () => {
    if (!latex.trim()) {
      alert("Generate or edit a resume first!");
      return;
    }

    const title = prompt("Enter a title for this resume:", "My Tailored Resume");
    if (!title) return;

    const client = supabase();
    const session = (await client.auth.getSession()).data.session;

    if (!session) {
      alert("You must be logged in to save resumes.");
      return;
    }

    const token = session.access_token;

    const formData = new FormData();
    formData.append("title", title);
    formData.append("latex", latex);

    const res = await fetch(`${API_URL}/save-resume`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json();
      alert("Failed to save resume: " + err.detail);
      return;
    }

    alert("Resume saved!");
  };

  return (
    <main className="max-w-6xl mx-auto py-10 px-4 space-y-8">
      <section className="bg-white rounded-xl border p-6 shadow-sm">
        {/* TEMPLATE SELECT BAR */}
        <div className="flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between mb-4">
          <div className="flex items-center gap-3">
            <label className="text-sm font-semibold">Template:</label>

            <select
              className="border rounded-md px-3 py-2 text-sm bg-white"
              value={selectedTemplateId}
              onChange={(e) => setSelectedTemplateId(e.target.value)}
              disabled={!session}
              title={!session ? "Login to use custom templates" : ""}
            >
              <option value="">Jake (Default)</option>
              {templates.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.title}
                </option>
              ))}
            </select>

            {!session && (
              <span className="text-xs text-gray-500">
                (login to use custom templates)
              </span>
            )}
          </div>

          <a href="/templates" className="text-sm text-blue-600 hover:underline">
            Manage templates →
          </a>
        </div>

        <UploadForm
          selectedTemplateId={selectedTemplateId}
          onResult={(data: TailorResult) => setResult(data)}
        />
      </section>

      {result && (
        <section className="space-y-6">
          {/* ATS SECTION */}
          <div className="bg-white rounded-xl border p-5 shadow-sm flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row justify-between sm:items-center">
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
                Tweak your LaTeX and re-run ATS scoring to optimize your resume.
              </p>
            </div>

            {result.keywords && (
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

          {/* EDITOR + PREVIEW */}
          <div className="w-full h-[650px] flex border rounded-xl overflow-hidden bg-white">
            <div className="w-1/2 h-full border-r flex flex-col">
              <div className="px-3 py-2 border-b bg-gray-50 flex items-center justify-between">
                <h2 className="text-sm font-semibold">LaTeX Editor</h2>
                <span className="text-xs text-gray-500">Edit the LaTeX</span>
              </div>
              <div className="flex-1 min-h-0">
                <LatexEditor value={latex} onChange={setLatex} />
              </div>
            </div>

            <div className="w-1/2 h-full flex flex-col">
              <div className="px-3 py-2 border-b bg-gray-50 flex items-center justify-between">
                <h2 className="text-sm font-semibold">PDF Preview</h2>
                <span className="text-xs text-gray-500">Click "Compile PDF"</span>
              </div>

              {pdfUrl ? (
                <iframe src={pdfUrl} className="flex-1 w-full h-full min-h-0" />
              ) : (
                <div className="flex-1 w-full h-full flex items-center justify-center text-gray-500 text-sm">
                  No PDF yet. Click "Compile PDF" below.
                </div>
              )}
            </div>
          </div>

          {/* ACTION BAR */}
          <div className="border px-4 py-3 flex flex-wrap gap-3 items-center justify-between bg-white rounded-xl">
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

              {session && (
                <button
                  onClick={handleSaveResume}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Save Resume
                </button>
              )}
            </div>

            <span className="text-xs text-gray-400">
              Tip: Make small edits and recompile for the best PDF output.
            </span>
          </div>
        </section>
      )}
    </main>
  );
}
