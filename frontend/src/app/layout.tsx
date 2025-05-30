import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Oracle | AI-powered Source Aggregator & Analyzer",
  description:
    "Oracle is an AI-powered platform for aggregating, searching, and analyzing diverse sources. Discover, filter, and explore content with advanced search and modern UI. Powered by LLMs and MCP, Oracle is ideal for cybersecurity, SANS, threat intelligence, and threat analysis workflows.",
  keywords: [
    "AI",
    "LLM",
    "MCP",
    "Oracle",
    "cybersecurity",
    "SANS",
    "threat intelligence",
    "threat analysis",
    "data discovery",
    "semantic search",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
