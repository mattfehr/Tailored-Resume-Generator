import { supabase } from "../../../lib/supabase/server";

export default async function SavedResumesPage() {
  const client = await supabase();

  const { data: resumes } = await client
    .from("resumes")
    .select("*")
    .order("updated_at", { ascending: false });

  return (
    <div className="p-6 text-white">
      <h1 className="text-3xl font-bold mb-4">Saved Resumes</h1>

      <ul className="space-y-4">
        {resumes?.map((resume) => (
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
      </ul>
    </div>
  );
}

