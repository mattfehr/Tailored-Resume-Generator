"use client";

import { useRouter } from "next/navigation";
import { supabase } from "../lib/supabase/client";
import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function ExperienceList({ experiences }: { experiences: any[] }) {
  const router = useRouter();
  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [bullets, setBullets] = useState("");

  const handleAdd = async () => {
    const client = supabase();
    const session = (await client.auth.getSession()).data.session;
    const token = session?.access_token;

    const form = new FormData();
    form.append("company", company);
    form.append("role", role);
    form.append("start_date", startDate);
    form.append("end_date", endDate);
    form.append("bullets_json", JSON.stringify(bullets.split("\n")));

    await fetch(`${API_URL}/experiences/add`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: form,
    });

    router.refresh();
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this experience?")) return;

    const client = supabase();
    const session = (await client.auth.getSession()).data.session;
    const token = session?.access_token;

    await fetch(`${API_URL}/experiences/${id}/delete`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });

    router.refresh();
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Experiences</h2>

      {/* ADD EXPERIENCE */}
      <div className="space-y-3 mb-6">
        <input
          className="p-2 bg-gray-800 rounded border border-gray-700 w-full"
          placeholder="Company"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
        />

        <input
          className="p-2 bg-gray-800 rounded border border-gray-700 w-full"
          placeholder="Role"
          value={role}
          onChange={(e) => setRole(e.target.value)}
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
          Add Experience
        </button>
      </div>

      {/* LIST EXPERIENCES */}
      <ul className="space-y-4">
        {experiences.map((exp) => (
          <li
            key={exp.id}
            className="p-4 bg-gray-900 rounded border border-gray-700 flex justify-between"
          >
            <div>
              <div className="font-semibold">
                {exp.role} @ {exp.company}
              </div>

              {/* DATE RANGE */}
              <div className="text-sm text-gray-400 mt-1">
                {exp.start_date ?? "?"} → {exp.end_date || "Present"}
              </div>

              {/* Bullets */}
              <ul className="text-sm text-gray-400 mt-2">
                {exp.bullets.map((b: string, i: number) => (
                  <li key={i}>• {b}</li>
                ))}
              </ul>
            </div>

            <button
              onClick={() => handleDelete(exp.id)}
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
