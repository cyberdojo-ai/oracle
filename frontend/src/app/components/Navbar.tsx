"use client";
import React, { useEffect, useRef } from "react";
import Link from "next/link";
import initFaro, { Faro } from "../tools/faro";
import { EnvType } from "../tools/env";

interface NavbarProps {
  appName: string;
  environment?: EnvType;
  faroUrl?: string | undefined;
  faroTraceHeaderCorsUrls?: RegExp[] | undefined;
}

const Navbar: React.FC<NavbarProps> = ({ 
  appName,
  faroUrl, 
  environment = "development", 
  faroTraceHeaderCorsUrls
 }) => {
  const faroRef = useRef<Faro | null>(null);  
  
  useEffect(() => {
    if (!faroRef.current && faroUrl) {
      faroRef.current = initFaro({
        url: faroUrl,
        name: appName,
        environment: environment,
        propagateTraceHeaderCorsUrls: faroTraceHeaderCorsUrls || [
          new RegExp("http://localhost:*"),
          new RegExp("http://127.0.0.1:*")
        ]
      })
    }
  }, [])
  return (
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
  )
};

export default Navbar;
