import { supabase } from "../../lib/supabase/server";
import { redirect } from "next/navigation";

interface SavedLayoutProps {
  children: React.ReactNode;
}

export default async function SavedLayout({ children }: SavedLayoutProps) {
  const client = await supabase();

  const {
    data: { session },
  } = await client.auth.getSession();

  if (!session) {
    redirect("/login");
  }

  return <>{children}</>;
}
