"use client";

import { useEffect, useMemo, useState } from "react";
import { supabase } from "../../lib/supabase/client";

type TemplateRow = { id: string; title: string; latex: string };

const JAKE_SEED = `% Paste a full LaTeX template here.
% Placeholders supported:
% {NAME} {CONTACT_LINE} {EDU} {EXP} {PROJ} {SKILLS}

% Tip: start by copying your Jake template and adjust styling.
`;

export default function TemplatesPage() {
  const [session, setSession] = useState<any>(null);
  const [templates, setTemplates] = useState<TemplateRow[]>([]);
  const [activeId, setActiveId] = useState<string>("");
  const active = useMemo(() => templates.find(t => t.id === activeId), [templates, activeId]);

  const [draftTitle, setDraftTitle] = useState("");
  const [draftLatex, setDraftLatex] = useState(JAKE_SEED);

  useEffect(() => {
    const client = supabase();
    client.auth.getSession().then(({ data }) => setSession(data.session));
    const { data: listener } = client.auth.onAuthStateChange((_e, s) => setSession(s));
    return () => listener.subscription.unsubscribe();
  }, []);

  const loadTemplates = async (token: string) => {
    const res = await fetch("http://localhost:8000/api/templates", {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return;
    const data = await res.json();
    setTemplates(data);
    if (data.length && !activeId) setActiveId(data[0].id);
  };

  useEffect(() => {
    if (!session) return;
    loadTemplates(session.access_token);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session]);

  const createTemplate = async () => {
    if (!session) return alert("Login required.");
    if (!draftTitle.trim() || !draftLatex.trim()) return alert("Title and LaTeX required.");

    const form = new FormData();
    form.append("title", draftTitle.trim());
    form.append("latex", draftLatex);

    const res = await fetch("http://localhost:8000/api/templates/save", {
      method: "POST",
      headers: { Authorization: `Bearer ${session.access_token}` },
      body: form,
    });

    if (!res.ok) return alert("Failed to save template.");
    setDraftTitle("");
    setDraftLatex(JAKE_SEED);
    await loadTemplates(session.access_token);
  };

  const renameTemplate = async (id: string) => {
    if (!session) return;
    const newTitle = prompt("New template name:", active?.title ?? "");
    if (!newTitle) return;

    const form = new FormData();
    form.append("new_title", newTitle);

    const res = await fetch(`http://localhost:8000/api/templates/${id}/rename`, {
      method: "POST",
      headers: { Authorization: `Bearer ${session.access_token}` },
      body: form,
    });
    if (!res.ok) return alert("Rename failed.");
    await loadTemplates(session.access_token);
  };

  const deleteTemplate = async (id: string) => {
    if (!session) return;
    if (!confirm("Delete this template?")) return;

    const res = await fetch(`http://localhost:8000/api/templates/${id}/delete`, {
      method: "POST",
      headers: { Authorization: `Bearer ${session.access_token}` },
    });
    if (!res.ok) return alert("Delete failed.");

    setActiveId("");
    await loadTemplates(session.access_token);
  };

  const updateDraftFromActive = () => {
    if (!active) return;
    setDraftTitle(active.title);
    setDraftLatex(active.latex);
  };

  const saveOverActive = async () => {
    // simplest approach for MVP: "save" creates a new row.
    // If you want true update-in-place, add a PATCH route like /templates/{id}/update
    alert("MVP note: add an update endpoint to overwrite an existing template.");
  };

  if (!session) {
    return (
      <main className="max-w-6xl mx-auto py-10 px-4">
        <div className="bg-white border rounded-xl p-6 shadow-sm">
          <h1 className="text-xl font-bold mb-2">Resume Templates</h1>
          <p className="text-sm text-gray-600">Please log in to create and manage templates.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="max-w-6xl mx-auto py-10 px-4 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">Resume Templates</h1>
        <a className="text-sm text-blue-600 hover:underline" href="/">← Back to builder</a>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* LIST */}
        <div className="bg-white border rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold">Your templates</h2>
            <button
              className="text-xs px-2 py-1 rounded bg-gray-100 hover:bg-gray-200"
              onClick={() => loadTemplates(session.access_token)}
            >
              Refresh
            </button>
          </div>

          <div className="space-y-2">
            <button
              className={`w-full text-left px-3 py-2 rounded border ${activeId === "" ? "bg-blue-50 border-blue-200" : "bg-white"}`}
              onClick={() => setActiveId("")}
            >
              Jake (Default)
              <div className="text-xs text-gray-500">Built-in</div>
            </button>

            {templates.map(t => (
              <button
                key={t.id}
                className={`w-full text-left px-3 py-2 rounded border ${activeId === t.id ? "bg-blue-50 border-blue-200" : "bg-white"}`}
                onClick={() => setActiveId(t.id)}
              >
                {t.title}
              </button>
            ))}
          </div>

          {activeId && (
            <div className="flex gap-2 mt-4">
              <button
                className="flex-1 px-3 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-900"
                onClick={() => renameTemplate(activeId)}
              >
                Rename
              </button>
              <button
                className="flex-1 px-3 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                onClick={() => deleteTemplate(activeId)}
              >
                Delete
              </button>
            </div>
          )}

          {activeId && (
            <button
              className="w-full mt-2 px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
              onClick={updateDraftFromActive}
            >
              Load into editor
            </button>
          )}
        </div>

        {/* EDITOR */}
        <div className="md:col-span-2 bg-white border rounded-xl p-4 shadow-sm">
          <h2 className="font-semibold mb-2">Template editor</h2>

          <div className="flex flex-col sm:flex-row gap-3 mb-3">
            <input
              className="flex-1 border rounded px-3 py-2 text-sm"
              placeholder="Template title"
              value={draftTitle}
              onChange={(e) => setDraftTitle(e.target.value)}
            />
            <button
              className="px-4 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700"
              onClick={createTemplate}
            >
              Save as new
            </button>
            <button
              className="px-4 py-2 text-sm bg-gray-100 rounded hover:bg-gray-200"
              onClick={() => setDraftLatex(JAKE_SEED)}
            >
              Reset seed
            </button>
          </div>

          <textarea
            className="w-full h-[520px] border rounded p-3 font-mono text-xs"
            value={draftLatex}
            onChange={(e) => setDraftLatex(e.target.value)}
          />

          <p className="text-xs text-gray-500 mt-2">
            Supported placeholders: <code>{"{NAME}"}</code>{" "}
            <code>{"{CONTACT_LINE}"}</code>{" "}
            <code>{"{EDU}"}</code>{" "}
            <code>{"{EXP}"}</code>{" "}
            <code>{"{PROJ}"}</code>{" "}
            <code>{"{SKILLS}"}</code>
          </p>

          <button
            className="mt-3 px-4 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-900"
            onClick={saveOverActive}
          >
            Overwrite active (add update endpoint)
          </button>
        </div>
      </div>
    </main>
  );
}
