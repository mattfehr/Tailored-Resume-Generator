"use client";
import { useState } from "react";
import { supabase } from "../../lib/supabase/client";
import { useRouter } from "next/navigation";

export default function SignupPage() {
  const router = useRouter();
  const client = supabase();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();

    const { data, error } = await client.auth.signUp({
      email,
      password,
    });

    if (error) {
      setError(error.message);
      return;
    }

    router.push("/");
    router.refresh();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <form
        onSubmit={handleSignup}
        className="bg-gray-800 p-8 rounded-xl shadow-xl w-full max-w-md"
      >
        <h1 className="text-3xl font-bold text-center text-white mb-6">
          Create Account
        </h1>

        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

        <label className="text-gray-300 text-sm">Email</label>
        <input
          className="w-full p-2 rounded bg-gray-700 text-white mb-4"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <label className="text-gray-300 text-sm">Password</label>
        <input
          className="w-full p-2 rounded bg-gray-700 text-white mb-6"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button
          type="submit"
          className="w-full py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg font-semibold"
        >
          Sign Up
        </button>
      </form>
    </div>
  );
}
