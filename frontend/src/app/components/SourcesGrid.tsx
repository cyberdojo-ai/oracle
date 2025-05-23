import React from "react";
import SourcePreview, { SourcePreviewProps } from "./SourcePreview";

interface SourcesGridProps {
  sources: SourcePreviewProps[];
  loading: boolean;
  error: string | null;
}

const SourcesGrid: React.FC<SourcesGridProps> = ({ sources, loading, error }) => (
  <div
    className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8 min-h-[340px]"
    style={{ minHeight: '340px' }}
  >
    {loading
      ? Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="border rounded-lg p-4 flex flex-col gap-2 animate-pulse"
            style={{
              background: 'var(--card-bg)',
              borderColor: 'var(--border)',
              minHeight: 120
            }}
          >
            <div className="h-6 w-2/3 mb-2 rounded bg-[#e6f9f5]" />
            <div className="h-4 w-1/2 mb-2 rounded bg-[#e6f9f5]" />
            <div className="h-16 w-full rounded bg-[#e6f9f5]" />
          </div>
        ))
      : error
      ? <div className="text-center text-red-500 py-8 col-span-full">{error}</div>
      : !sources.length
      ? <div className="text-center py-8 col-span-full">No sources found.</div>
      : sources.map((source) => (
          <SourcePreview key={source.id || source.url || source.title} {...source} />
        ))}
  </div>
);

export default SourcesGrid;
