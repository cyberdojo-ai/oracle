import { Suspense } from "react";
import Navbar from "./components/Navbar";
import SourcesView from "./components/SourcesView";

export const dynamic = "force-dynamic";

export default function Home() {
  // Read the API base URL from the environment at runtime (server component)
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      <Navbar />
      <main className="flex-1 flex flex-col items-center px-4 py-8 scrollbar-placeholder">
        <h1 className="text-3xl font-bold mb-6">Welcome to Oracle</h1>
        <Suspense>
          <SourcesView apiBaseUrl={apiBaseUrl} />
        </Suspense>
      </main>
    </div>
  );
}
