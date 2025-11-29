import { supabase } from "../../../lib/supabase/server";

export default async function ExperiencesPage() {
  const client = await supabase();

  const { data: experiences } = await client
    .from("experiences")
    .select("*");

  const { data: projects } = await client
    .from("projects")
    .select("*");

  return (
    <div className="p-6 text-white">
      <h1 className="text-3xl font-bold mb-4">Experiences & Projects</h1>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-3">Experiences</h2>
        <ul className="space-y-3">
          {experiences?.map((exp) => (
            <li key={exp.id} className="bg-gray-800 p-4 rounded-md">
              <div className="flex justify-between">
                <div>
                  <p>{exp.role} @ {exp.company}</p>
                </div>
                <button className="text-red-400">Delete</button>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="text-xl font-semibold mb-3">Projects</h2>
        <ul className="space-y-3">
          {projects?.map((proj) => (
            <li key={proj.id} className="bg-gray-800 p-4 rounded-md">
              <div className="flex justify-between">
                <div>
                  <p>{proj.name}</p>
                </div>
                <button className="text-red-400">Delete</button>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
