"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { supabase } from "../lib/supabase/client";
import { useRouter } from "next/navigation";

export default function NavBar() {
  const router = useRouter();
  const client = supabase();

  const [session, setSession] = useState<any>(null);

  useEffect(() => {
    client.auth.getSession().then(({ data }) => {
      setSession(data.session);
    });

    const {
      data: { subscription },
    } = client.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  async function handleLogout() {
    await client.auth.signOut();
    router.push("/login");
  }

  return (
    <nav className="w-full bg-gray-900 text-white px-6 py-4 flex justify-between items-center shadow">
      <Link href="/" className="text-xl font-bold">
        ResuMatch AI
      </Link>

      <div className="flex gap-6 items-center">
        {!session ? (
          <>
            <Link href="/login" className="hover:underline">
              Login
            </Link>
            <Link href="/signup" className="hover:underline">
              Signup
            </Link>
          </>
        ) : (
          <>
            <Link href="/saved/resumes" className="hover:underline">
              Saved Resumes
            </Link>

            <Link href="/saved/experiences" className="hover:underline">
              Experiences & Projects
            </Link>

            <button
              onClick={handleLogout}
              className="bg-red-600 px-4 py-1 rounded hover:bg-red-500"
            >
              Logout
            </button>
          </>
        )}
      </div>
    </nav>
  );
}
