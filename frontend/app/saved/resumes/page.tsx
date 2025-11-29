import { supabase } from "../../../lib/supabase/server";
import ResumeEntry from "../../../components/ResumeEntry";

export default async function SavedResumesPage() {
  const client = await supabase();

  const {
    data: { session },
  } = await client.auth.getSession();

  if (!session) {
    return (
      <div className="p-6 text-red-500">
        You must be logged in to view saved resumes.
      </div>
    );
  }

  const token = session.access_token;

  const response = await fetch("http://localhost:8000/api/resumes", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    return (
      <div className="p-6 text-red-500">
        Failed to load saved resumes.
      </div>
    );
  }

  const resumes = await response.json();

  return (
    <div className="p-6 text-white">
      <h1 className="text-3xl font-bold mb-6">Saved Resumes</h1>

      <ul className="space-y-6">
        {resumes?.map((resume: any) => (
          <ResumeEntry key={resume.id} resume={resume} />
        ))}

        {!resumes.length && (
          <p className="text-gray-400">No saved resumes yet.</p>
        )}
      </ul>
    </div>
  );
}
