"use client";

import { supabase } from "../lib/supabase/client";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function ResumeEntry({ resume }: { resume: any }) {
  const router = useRouter();

  // DELETE RESUME
  const handleDelete = async () => {
    if (!confirm("Delete this resume?")) return;

    const client = supabase();
    const session = (await client.auth.getSession()).data.session;
    const token = session?.access_token;

    await fetch(`${API_URL}/resumes/${resume.id}/delete`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });

    router.refresh(); // refresh saved list
  };

  // RENAME RESUME
  const handleRename = async () => {
    const newTitle = prompt("Enter new title:", resume.title);
    if (!newTitle) return;

    const client = supabase();
    const session = (await client.auth.getSession()).data.session;
    const token = session?.access_token;

    const formData = new FormData();
    formData.append("new_title", newTitle);

    await fetch(`${API_URL}/resumes/${resume.id}/rename`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });

    router.refresh(); // reload updated title
  };

  // COPY LATEX
  const handleCopy = async () => {
    await navigator.clipboard.writeText(resume.latex);
    alert("Copied LaTeX!");
  };

  return (
    <li className="bg-gray-900 p-5 rounded-lg shadow border border-gray-700">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">{resume.title}</h2>

        <div className="space-x-4">
          <button onClick={handleRename} className="text-blue-400 hover:underline">
            Rename
          </button>

          <button onClick={handleDelete} className="text-red-400 hover:underline">
            Delete
          </button>
        </div>
      </div>

      <textarea
        readOnly
        value={resume.latex}
        className="w-full h-48 p-3 bg-gray-800 text-white rounded border border-gray-700"
      />

      <button
        onClick={handleCopy}
        className="mt-3 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Copy LaTeX
      </button>
    </li>
  );
}
