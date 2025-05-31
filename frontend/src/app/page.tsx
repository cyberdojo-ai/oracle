import { Suspense } from "react";
import Navbar from "./components/Navbar";
import SourcesView from "./components/SourcesView";
import getEnv from "./tools/env";

export const dynamic = "force-dynamic";

export default function Home() {
  // Read the API base URL from the environment at runtime (server component)
  const {
    appName,
    apiBaseUrl,
    environment,
    faroUrl,
    faroTraceHeaderCorsUrls,
  } = getEnv();
  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      <Navbar appName={appName} environment={environment} faroUrl={faroUrl} faroTraceHeaderCorsUrls={faroTraceHeaderCorsUrls} />
      <main className="flex-1 flex flex-col items-center px-4 py-8 scrollbar-placeholder">
        <h1 className="text-3xl font-bold mb-6">Welcome to Oracle</h1>
        <Suspense>
          <SourcesView apiBaseUrl={apiBaseUrl} />
        </Suspense>
      </main>
    </div>
  );
}
