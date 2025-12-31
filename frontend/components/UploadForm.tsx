"use client";
import { useState } from "react";
import api from "../lib/api";
import { supabase } from "../lib/supabase/client";

interface UploadFormProps {
  onResult: (data: any) => void;
  selectedTemplateId?: string;
}

export default function UploadForm({ onResult, selectedTemplateId }: UploadFormProps) {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!resumeFile) {
      setError("Please upload a resume (PDF or .tex)");
      return;
    }
    if (!jobDescription.trim()) {
      setError("Please paste a job description.");
      return;
    }

    const formData = new FormData();
    formData.append("job_description", jobDescription);

    const isTex = resumeFile.name.toLowerCase().endsWith(".tex");

    if (isTex) {
      const text = await resumeFile.text();
      formData.append("latex_resume", text);
      // We intentionally do NOT send template_id for .tex uploads
      // because the .tex already defines the template/layout.
    } else {
      formData.append("resume", resumeFile);

      if (selectedTemplateId) {
        formData.append("template_id", selectedTemplateId);
      }
    }

    try {
      setLoading(true);

      // Grab auth token if logged in
      const client = supabase();
      const session = (await client.auth.getSession()).data.session;
      const token = session?.access_token ?? null;

      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const res = await api.post("/rewrite", formData, { headers });
      onResult(res.data);
    } catch (err: any) {
      console.error("UPLOAD ERROR:", err);

      const detail = err?.response?.data?.detail;

      let msg = "Failed to process the input. Please try again.";

      // FastAPI validation error shape: { detail: [ {loc,msg,type,...}, ... ] }
      if (Array.isArray(detail)) {
        msg = detail
          .map((d: any) => `${(d.loc || []).join(".")}: ${d.msg}`)
          .join(" | ");
      } else if (typeof detail === "string") {
        msg = detail;
      } else if (typeof err?.response?.data === "string") {
        msg = err.response.data;
      } else if (err?.message) {
        msg = err.message;
      }

      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-4 p-6 bg-white border rounded-xl shadow-sm"
    >
      <h2 className="text-xl font-semibold text-center">
        Upload Resume + Job Description
      </h2>

      <div>
        <label className="block text-sm font-medium mb-1">
          Resume File (.pdf, .docx, .txt, .tex)
        </label>
        <input
          type="file"
          accept=".pdf,.docx,.txt,.tex"
          onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
          className="border p-2 rounded-md w-full"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Job Description</label>
        <textarea
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          rows={6}
          placeholder="Paste the job description here..."
          className="border p-2 rounded-md w-full font-mono text-sm"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="bg-blue-600 text-white rounded-md p-2 hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Processing..." : "Generate Tailored Resume"}
      </button>

      {error && <p className="text-red-600 text-sm text-center">{error}</p>}
    </form>
  );
}
