import { supabase } from "../../../lib/supabase/server";
import ExperienceList from "../../../components/ExperienceList";
import ProjectList from "../../../components/ProjectList";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default async function ExperiencesPage() {
  const client = await supabase();
  const { data: { session } } = await client.auth.getSession();

  if (!session) {
    return (
      <div className="p-6 text-red-500">
        You must be logged in to view this page.
      </div>
    );
  }

  const token = session.access_token;

  const [experienceRes, projectRes] = await Promise.all([
    fetch(`${API_URL}/experiences`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    }),
    fetch(`${API_URL}/projects`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    }),
  ]);

  if (!experienceRes.ok || !projectRes.ok) {
    return (
      <div className="p-6 text-red-500">
        Failed to load experiences or projects.
      </div>
    );
  }

  const experiences = (await experienceRes.json()) ?? [];
  const projects = (await projectRes.json()) ?? [];

  return (
    <div className="p-6 text-white space-y-10">
      <ExperienceList experiences={experiences} />
      <ProjectList projects={projects} />
    </div>
  );
}
