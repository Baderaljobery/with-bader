import { ExternalLink } from "lucide-react";

export function SourceLinksRow({ urls }: { urls?: string[] }) {
  if (!urls || urls.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-2 pt-1">
      {urls.map((url) => (
        <a
          key={url}
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-xs text-[#1B8FEA] hover:underline"
        >
          <ExternalLink className="size-3" aria-hidden="true" />
          مصدر
        </a>
      ))}
    </div>
  );
}

export function ConfidenceNote({ confidence }: { confidence?: number | null }) {
  if (confidence === null || confidence === undefined) return null;

  return (
    <p className="text-xs text-muted-foreground">ثقة النموذج: {Math.round(confidence * 100)}%</p>
  );
}
