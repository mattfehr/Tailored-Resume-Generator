"use client";
import { useState } from "react";
import api from "../lib/api";

interface UploadFormProps {
  onResult: (data: any) => void;
}

export default function UploadForm({ onResult }: UploadFormProps) {
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

    // CASE 1: User uploads a .tex LaTeX resume
    if (resumeFile.name.endsWith(".tex")) {
      const text = await resumeFile.text(); // read raw LaTeX
      formData.append("latex_resume", text); // backend expects 'latex_resume'
    } 
    
    // CASE 2: User uploads a PDF/DOCX/TXT resume
    else {
      formData.append("resume", resumeFile); // backend expects 'resume'
    }

    try {
      setLoading(true);
      const res = await api.post("/rewrite", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      onResult(res.data);
    } catch (err: any) {
      console.error("UPLOAD ERROR:", err);
      setError("Failed to process the input. Please try again.");
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
