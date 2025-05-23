"use client";
import React, { useEffect, useState, useRef } from "react";
import SourcePreview, { SourcePreviewProps } from "./SourcePreview";
import SourcesGrid from "./SourcesGrid";
import SourcesList from "./SourcesList";
import { useRouter, useSearchParams } from "next/navigation";

const PAGE_SIZE = 9;
const API_URL = "http://localhost:8000/api/source";

const SourcesView: React.FC = () => {
  const [sources, setSources] = useState<SourcePreviewProps[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [viewMode, setViewMode] = useState<'grid' | 'list'>("grid");
  const searchInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const searchParams = useSearchParams();

  // Debounce search input
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedSearch(search), 400);
    return () => clearTimeout(handler);
  }, [search]);

  // Keep focus on search field when searching
  useEffect(() => {
    if (searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [debouncedSearch]);

  // Sync search input with URL query param
  useEffect(() => {
    const urlSearch = searchParams.get("search") || "";
    setSearch(urlSearch);
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (search) {
      params.set("search", search);
    } else {
      params.delete("search");
    }
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState(null, "", newUrl);
  }, [search]);

  // Helper to build API params based on backend API
  const buildApiParams = () => {
    const params = new URLSearchParams({
      limit: PAGE_SIZE.toString(),
      offset: ((page - 1) * PAGE_SIZE).toString(),
      order_by: "published_on",
      asc: "false",
    });
    // Only use content_like for searching
    if (debouncedSearch) {
      params.append("content_like", debouncedSearch);
    }
    return params;
  };

  useEffect(() => {
    setLoading(true);
    const params = buildApiParams();
    fetch(`${API_URL}?${params.toString()}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch sources");
        return res.json();
      })
      .then((data) => {
        setSources(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [page, debouncedSearch]);

  useEffect(() => {
    const params = buildApiParams();
    fetch(`${API_URL}/count?${params.toString()}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch source count");
        return res.json();
      })
      .then((data) => setTotal(data.count || 0))
      .catch(() => setTotal(0));
  }, [debouncedSearch, page]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="w-full max-w-6xl mx-auto mt-8" style={{ background: 'var(--background)' }}>
      <div className="mb-6 flex flex-col sm:flex-row sm:justify-between gap-2">
        <div className="flex-1 flex justify-end">
          <input
            ref={searchInputRef}
            type="text"
            placeholder="Search sources..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="border rounded px-3 py-2 w-full max-w-xs focus:outline-none focus:ring focus:border-blue-400"
            style={{
              background: 'var(--input-bg)',
              color: 'var(--input-text)',
              borderColor: 'var(--input-border)',
              boxShadow: '0 1px 3px 0 var(--border)'
            }}
          />
        </div>
        <div className="flex items-center gap-2 mt-2 sm:mt-0">
          {/* Toggle Switch - improved for sharp text */}
          <div
            className="relative w-28 h-10 bg-[var(--card-bg)] rounded-full border border-[var(--primary)] flex items-center cursor-pointer select-none transition-colors"
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            role="switch"
            aria-checked={viewMode === 'list'}
            tabIndex={0}
            onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') setViewMode(viewMode === 'grid' ? 'list' : 'grid'); }}
          >
            {/* Sliding background only */}
            <span
              className={`absolute top-1 left-1 w-12 h-8 rounded-full transition-transform duration-200 pointer-events-none ${viewMode === 'grid' ? 'translate-x-0' : 'translate-x-14'} bg-[var(--primary)]`}
              style={{ boxShadow: '0 2px 8px 0 var(--border)' }}
            />
            {/* Text always sharp, color changes based on state */}
            <span className="flex-1 flex justify-between w-full z-10 px-4 text-sm font-semibold">
              <span className={viewMode === 'grid' ? 'text-white' : 'text-[var(--primary)]'} style={{transition: 'color 0.2s'}}>Grid</span>
              <span className={viewMode === 'list' ? 'text-white' : 'text-[var(--primary)]'} style={{transition: 'color 0.2s'}}>List</span>
            </span>
          </div>
        </div>
      </div>
      {viewMode === 'grid' ? (
        <SourcesGrid sources={sources} loading={loading} error={error} />
      ) : (
        <SourcesList sources={sources} loading={loading} error={error} />
      )}
      <div className="flex justify-center gap-2 mb-4">
        <button
          className="px-3 py-1 rounded border disabled:opacity-50 hover:bg-[#f0f6ff]"
          style={{
            background: 'var(--card-bg)',
            color: 'var(--primary)',
            borderColor: 'var(--primary)'
          }}
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1}
        >
          Previous
        </button>
        <span className="px-3 py-1" style={{ color: 'var(--foreground)' }}>Page {page} of {totalPages || 1}</span>
        <button
          className="px-3 py-1 rounded border disabled:opacity-50 hover:bg-[#f0f6ff]"
          style={{
            background: 'var(--card-bg)',
            color: 'var(--primary)',
            borderColor: 'var(--primary)'
          }}
          onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          disabled={page === totalPages || totalPages === 0}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default SourcesView;
