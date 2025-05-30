import React from "react";
import Link from "next/link";

const Navbar: React.FC = () => (
  <nav
    className="sticky top-0 z-50 w-full flex items-center justify-between px-8 py-4 border-b"
    style={{
      background: 'var(--background)',
      color: 'var(--foreground)',
      borderColor: 'var(--border)',
      overflow: 'visible', // Prevent scroll bar on navbar
    }}
  >
    <div className="text-2xl font-bold tracking-tight">Oracle</div>
    <div>
      <Link
        href="/"
        className="text-lg font-medium hover:underline"
        style={{ color: 'var(--primary)' }}
      >
        Home
      </Link>
    </div>
  </nav>
);

export default Navbar;
