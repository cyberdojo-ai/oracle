import React from "react";

export interface SourcePreviewProps {
  id?: number;
  title: string;
  url?: string;
  content?: string;
  published_on?: string;
  updated_on?: string;
  type?: string;
}

const getFirst5Lines = (content?: string) => {
  if (!content) return { preview: "", isTruncated: false };
  const lines = content.split("\n");
  const preview = lines.slice(0, 5).join("\n");
  return {
    preview,
    isTruncated: lines.length > 5,
  };
};

const SourcePreview: React.FC<SourcePreviewProps> = ({
  title,
  url,
  content,
  published_on,
  updated_on,
  type,
}) => {
  const { preview, isTruncated } = getFirst5Lines(content);
  return (
    <div
      className="border rounded-lg p-4 flex flex-col gap-2 h-full"
      style={{
        background: 'var(--card-bg)',
        borderColor: 'var(--border)',
        boxShadow: '0 1px 3px 0 var(--border)'
      }}
    >
      <a
        href={url || "#"}
        target="_blank"
        rel="noopener noreferrer"
        className="text-lg font-semibold hover:underline break-words"
        style={{ color: 'var(--primary)' }}
      >
        {title}
      </a>
      {type && (
        <div className="text-xs font-semibold mb-1" style={{ color: 'var(--primary)' }}>
          {type}
        </div>
      )}
      <div className="text-xs mb-1" style={{ color: '#7ca982' }}>
        <span>
          Published: {published_on ? new Date(published_on).toLocaleDateString() : "-"}
        </span>
        <span className="mx-2">|</span>
        <span>
          Updated: {updated_on ? new Date(updated_on).toLocaleDateString() : "-"}
        </span>
      </div>
      <div
        className="text-sm text-[#234e23] whitespace-pre-line max-h-32 min-h-24 relative overflow-hidden"
        style={{}}
      >
        {preview}
        {isTruncated && "..."}
      </div>
      {isTruncated && (
        <a
          href={url || "#"}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs self-end mt-1 hover:underline"
          style={{ color: 'var(--primary)' }}
        >
          Read more
        </a>
      )}
    </div>
  );
};

export default SourcePreview;
