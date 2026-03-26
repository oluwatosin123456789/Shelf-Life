"use client";

import { useState } from "react";
import Link from "next/link";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

export default function SignUpPage() {
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // Phase 2: call auth API
    setTimeout(() => setLoading(false), 1500);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-6 -mt-20">
      <h1 className="text-2xl font-bold tracking-tight">fresco</h1>
      <p className="text-sm text-text-muted mt-1">Know your fruit.</p>

      <form onSubmit={handleSubmit} className="w-full max-w-[400px] mt-8 flex flex-col gap-4">
        <Input placeholder="Username" autoComplete="username" />
        <Input placeholder="Email" type="email" autoComplete="email" />
        <Input placeholder="Password" type="password" autoComplete="new-password" />
        <Input placeholder="Confirm Password" type="password" autoComplete="new-password" />

        <Button type="submit" fullWidth loading={loading} className="mt-2">
          Create Account
        </Button>
      </form>

      <p className="text-sm text-text-muted mt-4">
        Already have an account?{" "}
        <Link href="/auth/signin" className="text-accent font-medium">
          Sign in
        </Link>
      </p>
    </div>
  );
}
