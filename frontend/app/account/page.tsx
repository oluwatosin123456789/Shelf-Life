"use client";

import Link from "next/link";
import { Button } from "@/components/ui/Button";

export default function AccountPage() {
  return (
    <div className="flex flex-col px-4 pt-4 pb-24">
      <h1 className="text-2xl font-bold mb-6">Account</h1>

      {/* Profile card */}
      <div className="flex items-center gap-4 p-4 bg-surface border border-border rounded-xl mb-6">
        <div className="w-12 h-12 rounded-full bg-accent text-white flex items-center justify-center text-lg font-bold">
          U
        </div>
        <div>
          <p className="font-semibold">User</p>
          <p className="text-sm text-text-muted">user@fresco.app</p>
        </div>
      </div>

      {/* Settings links */}
      <div className="flex flex-col gap-2 mb-8">
        {[
          { label: "Edit Profile", href: "#" },
          { label: "Notification Settings", href: "#" },
          { label: "Help & Support", href: "#" },
          { label: "About Fresco", href: "#" },
        ].map((item) => (
          <Link
            key={item.label}
            href={item.href}
            className="flex items-center justify-between py-3 px-4 bg-surface border border-border rounded-xl text-sm font-medium hover:bg-bg transition-colors"
          >
            {item.label}
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
          </Link>
        ))}
      </div>

      <Button variant="secondary" fullWidth>
        Sign Out
      </Button>
    </div>
  );
}
