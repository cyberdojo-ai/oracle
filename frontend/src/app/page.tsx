import { Suspense } from "react";
import Navbar from "./components/Navbar";
import SourcesView from "./components/SourcesView";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      <Navbar />
      <main className="flex-1 flex flex-col items-center px-4 py-8 scrollbar-placeholder">
        <h1 className="text-3xl font-bold mb-6">Welcome to Oracle</h1>
        <Suspense>
          <SourcesView />
        </Suspense>
      </main>
    </div>
  );
}
