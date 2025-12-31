"use client";

import { useRouter } from "next/navigation";
import { supabase } from "../lib/supabase/client";
import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function ProjectList({ projects }: { projects: any[] }) {
  const router = useRouter();
  const [name, setName] = useState("");
  const [tech, setTech] = useState("");
  const [bullets, setBullets] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const handleAdd = async () => {
    const client = supabase();
    const session = (await client.auth.getSession()).data.session;
    const token = session?.access_token;

    const form = new FormData();
    form.append("name", name);
    form.append("tech_stack_json", JSON.stringify(tech.split(",")));
    form.append("bullets_json", JSON.stringify(bullets.split("\n")));
    form.append("start_date", startDate);
    form.append("end_date", endDate);

    await fetch(`${API_URL}/projects/add`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: form,
    });

    router.refresh();
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this project?")) return;

    const client = supabase();
    const session = (await client.auth.getSession()).data.session;
    const token = session?.access_token;

    await fetch(`${API_URL}/projects/${id}/delete`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });

    router.refresh();
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Projects</h2>

      {/* ADD PROJECT */}
      <div className="space-y-3 mb-6">
        <input
          className="p-2 bg-gray-800 rounded border border-gray-700 w-full"
          placeholder="Project Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <input
          className="p-2 bg-gray-800 rounded border border-gray-700 w-full"
          placeholder="Tech stack (comma separated)"
          value={tech}
          onChange={(e) => setTech(e.target.value)}
        />

        {/* Start Date */}
        <input
          type="date"
          className="p-2 bg-gray-800 rounded border border-gray-700 w-full"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
        />

        {/* End Date */}
        <input
          type="date"
          className="p-2 bg-gray-800 rounded border border-gray-700 w-full"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
        />

        <textarea
          className="p-2 bg-gray-800 rounded border border-gray-700 w-full h-28"
          placeholder="Bullets (one per line)"
          value={bullets}
          onChange={(e) => setBullets(e.target.value)}
        />

        <button
          onClick={handleAdd}
          className="px-4 py-2 bg-green-600 rounded hover:bg-green-700"
        >
          Add Project
        </button>
      </div>

      {/* LIST PROJECTS */}
      <ul className="space-y-4">
        {projects.map((proj) => (
          <li
            key={proj.id}
            className="p-4 bg-gray-900 rounded border border-gray-700 flex justify-between"
          >
            <div>
              <div className="font-semibold">{proj.name}</div>

              {/* DATE RANGE */}
              <div className="text-sm text-gray-400 mt-1">
                {proj.start_date ?? "?"} → {proj.end_date || "Present"}
              </div>

              <div className="text-sm text-gray-400 mt-1">
                Tech: {proj.tech_stack.join(", ")}
              </div>

              <ul className="text-sm text-gray-400 mt-2">
                {proj.bullets.map((b: string, i: number) => (
                  <li key={i}>• {b}</li>
                ))}
              </ul>
            </div>

            <button
              onClick={() => handleDelete(proj.id)}
              className="text-red-400 hover:underline"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
