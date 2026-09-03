"use client";

import { Copy, Pencil, RefreshCw, Upload } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate } from "@/lib/format-date";
import type { GuestTranscript } from "../types/interview";
import { TranscriptEditDialog } from "./transcript-edit-dialog";

type TranscriptCardProps = {
  guestId: string;
  transcript: GuestTranscript;
  onRematch: () => void;
  isRematching: boolean;
  onReplace: () => void;
};

export function TranscriptCard({ guestId, transcript, onRematch, isRematching, onReplace }: TranscriptCardProps) {
  const [editOpen, setEditOpen] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(transcript.text);
      toast.success("تم نسخ النص");
    } catch {
      toast.error("تعذر نسخ النص");
    }
  }

  return (
    <>
      <Card>
        <CardHeader className="flex-row items-start justify-between gap-3 space-y-0">
          <div className="space-y-1">
            <CardTitle>نص المقابلة</CardTitle>
            <p className="text-xs text-[#5F6368]">
              آخر تحديث: {formatDate(transcript.updated_at)}
              {transcript.stt_provider ? ` · ${transcript.stt_provider}` : ""}
            </p>
          </div>
          <div className="flex flex-wrap items-center justify-end gap-2">
            <Button variant="outline" size="sm" onClick={handleCopy}>
              <Copy className="size-4" />
              نسخ النص
            </Button>
            <Button variant="outline" size="sm" onClick={() => setEditOpen(true)}>
              <Pencil className="size-4" />
              تعديل النص
            </Button>
            <Button variant="outline" size="sm" onClick={onReplace}>
              <Upload className="size-4" />
              استبدال المقابلة
            </Button>
            <Button size="sm" onClick={onRematch} disabled={isRematching}>
              <RefreshCw className="size-4" />
              {isRematching ? "جارٍ إعادة المطابقة..." : "إعادة مطابقة الإجابات"}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="max-h-80 overflow-y-auto rounded-lg bg-[#F7F8FA] p-3">
            <p className="whitespace-pre-wrap text-sm leading-7 text-[#161616]">{transcript.text}</p>
          </div>
        </CardContent>
      </Card>

      <TranscriptEditDialog
        guestId={guestId}
        open={editOpen}
        onOpenChange={setEditOpen}
        currentText={transcript.text}
      />
    </>
  );
}
