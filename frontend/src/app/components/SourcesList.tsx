import React from "react";
import { SourcePreviewProps } from "./SourcePreview";

interface SourcesListProps {
  sources: SourcePreviewProps[];
  loading: boolean;
  error: string | null;
}

const SourcesList: React.FC<SourcesListProps> = ({ sources, loading, error }) => (
  <div className="mb-8 min-h-[340px]">
    <div className="hidden sm:grid grid-cols-12 gap-2 px-2 py-1 text-xs font-semibold border-b border-[#d3e4cd] text-[#7ca982]">
      <div className="col-span-4">Title</div>
      <div className="col-span-2">Type</div>
      <div className="col-span-2">Published</div>
      <div className="col-span-2">Updated</div>
      <div className="col-span-2">Link</div>
    </div>
    {loading
      ? Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="flex flex-col sm:grid grid-cols-12 gap-2 p-4 border-b animate-pulse" style={{background: 'var(--card-bg)', borderColor: 'var(--border)'}}>
            <div className="col-span-4 h-4 bg-[#e6f9f5] rounded mb-2" />
            <div className="col-span-2 h-4 bg-[#e6f9f5] rounded mb-2" />
            <div className="col-span-2 h-4 bg-[#e6f9f5] rounded mb-2" />
            <div className="col-span-2 h-4 bg-[#e6f9f5] rounded mb-2" />
            <div className="col-span-2 h-4 bg-[#e6f9f5] rounded mb-2" />
          </div>
        ))
      : error
      ? <div className="text-center text-red-500 py-8">{error}</div>
      : !sources.length
      ? <div className="text-center py-8">No sources found.</div>
      : sources.map((source) => (
          <div key={source.id || source.url || source.title} className="flex flex-col sm:grid grid-cols-12 gap-2 p-4 border-b" style={{background: 'var(--card-bg)', borderColor: 'var(--border)'}}>
            <div className="col-span-4 font-semibold text-base" style={{color: 'var(--primary)'}}>{source.title}</div>
            <div className="col-span-2 text-xs font-semibold" style={{color: 'var(--primary)'}}>{source.type || '-'}</div>
            <div className="col-span-2 text-xs text-[#7ca982]">{source.published_on ? new Date(source.published_on).toLocaleDateString() : '-'}</div>
            <div className="col-span-2 text-xs text-[#7ca982]">{source.updated_on ? new Date(source.updated_on).toLocaleDateString() : '-'}</div>
            <div className="col-span-2 text-xs truncate"><a href={source.url || '#'} target="_blank" rel="noopener noreferrer" className="hover:underline" style={{color: 'var(--primary)'}}>Open</a></div>
            <div className="col-span-12 mt-2 text-sm text-[#234e23] whitespace-pre-line">{source.content ? source.content.split("\n").slice(0, 2).join(" ") : ''}{source.content && source.content.split("\n").length > 2 ? '...' : ''}</div>
          </div>
        ))}
  </div>
);

export default SourcesList;
