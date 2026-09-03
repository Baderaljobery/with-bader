"use client";

import { ChevronDown, ExternalLink } from "lucide-react";
import { useState } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/format-date";
import type { ResearchSource } from "../../types/research";

function SourceItem({ source }: { source: ResearchSource }) {
  // Plain-text rendering only (title/publisher/snippet) - never
  // dangerouslySetInnerHTML, and `content` (the longer raw blob) is
  // intentionally never rendered here.
  const heading = source.title || source.publisher || source.url || "مصدر بدون عنوان";

  return (
    <div className="rounded-lg border border-[#E6EAF0] p-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <p className="min-w-0 truncate text-sm font-medium text-[#161616]">{heading}</p>
        {source.published_at ? (
          <p className="shrink-0 text-xs text-[#5F6368]">{formatDate(source.published_at)}</p>
        ) : null}
      </div>
      {source.publisher && source.title ? (
        <p className="text-xs text-[#5F6368]">{source.publisher}</p>
      ) : null}
      {source.snippet ? (
        <p className="mt-1 line-clamp-3 text-sm text-[#5F6368]">{source.snippet}</p>
      ) : null}
      <div className="mt-2 flex flex-wrap items-center gap-3">
        {source.url ? (
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs font-medium text-[#1B8FEA] hover:underline"
          >
            <ExternalLink className="size-3" aria-hidden="true" />
            فتح المصدر
          </a>
        ) : null}
        {source.provider ? (
          <span className="text-xs text-muted-foreground">{source.provider}</span>
        ) : null}
      </div>
    </div>
  );
}

export function SourcesSection({ sources }: { sources: ResearchSource[] }) {
  const [open, setOpen] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <button
          type="button"
          onClick={() => setOpen((value) => !value)}
          aria-expanded={open}
          className="flex w-full items-center justify-between gap-2 text-start"
        >
          <CardTitle>المصادر ({sources.length})</CardTitle>
          <ChevronDown
            className={cn("size-4 text-[#5F6368] transition-transform", open && "rotate-180")}
            aria-hidden="true"
          />
        </button>
      </CardHeader>
      {open ? (
        <CardContent className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {sources.map((source, index) => (
            <SourceItem key={`${source.url ?? "source"}-${index}`} source={source} />
          ))}
        </CardContent>
      ) : null}
    </Card>
  );
}
