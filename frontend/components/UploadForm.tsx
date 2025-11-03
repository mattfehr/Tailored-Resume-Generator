"use client";
import { useState } from "react";
import api from "../lib/api";

interface UploadFormProps {
  onResult: (data: any) => void;
}

export default function UploadForm({ onResult }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setError(null);
      const res = await api.post("/rewrite", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      onResult(res.data);
    } catch (err: any) {
      console.error(err);
      setError("Failed to process the file. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-4 p-6 bg-white border rounded-xl shadow-sm"
    >
      <h2 className="text-xl font-semibold">Upload Resume or Job Description</h2>
      <input
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        className="border p-2 rounded-md"
      />
      <button
        type="submit"
        disabled={!file || loading}
        className="bg-blue-600 text-white rounded-md p-2 hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Processing..." : "Generate Tailored Resume"}
      </button>
      {error && <p className="text-red-600 text-sm">{error}</p>}
    </form>
  );
}
