import { supabase } from "../../../lib/supabase/server";

export default async function SavedResumesPage() {
  const client = await supabase();

  // Get the logged in user
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

  // Call FastAPI to fetch resumes
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
      <h1 className="text-3xl font-bold mb-4">Saved Resumes</h1>

      <ul className="space-y-4">
        {resumes?.map((resume: any) => (
          <li key={resume.id} className="bg-gray-800 p-4 rounded-md">
            <div className="flex justify-between items-center">
              <span>{resume.title}</span>

              <div className="space-x-4">
                <button className="text-blue-400">Rename</button>
                <button className="text-red-400">Delete</button>
              </div>
            </div>
          </li>
        ))}

        {!resumes.length && (
          <p className="text-gray-400">No saved resumes yet.</p>
        )}
      </ul>
    </div>
  );
}
