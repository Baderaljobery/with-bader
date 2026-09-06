"use client";

import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api/client";
import { useUpdateGuestTranscript } from "../hooks/use-update-transcript";

type TranscriptEditDialogProps = {
  guestId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  currentText: string;
};

export function TranscriptEditDialog({ guestId, open, onOpenChange, currentText }: TranscriptEditDialogProps) {
  const updateTranscript = useUpdateGuestTranscript(guestId);
  const [text, setText] = useState(currentText);
  // Re-sync the draft to the latest saved text whenever the dialog
  // transitions closed -> open, using React's "adjust state during render"
  // pattern instead of an effect (avoids an extra render + the
  // set-state-in-effect pitfall).
  const [wasOpen, setWasOpen] = useState(open);
  if (open !== wasOpen) {
    setWasOpen(open);
    if (open) setText(currentText);
  }

  async function handleSave() {
    if (!text.trim() || text === currentText) return;
    try {
      await updateTranscript.mutateAsync(text);
      toast.success("تم تحديث النص. يمكنك إعادة مطابقة الإجابات لتطبيق التعديلات.");
      onOpenChange(false);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "تعذر حفظ النص، حاول مرة أخرى";
      toast.error(message);
    }
  }

  const unchanged = text === currentText || !text.trim();

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>تعديل نص المقابلة</DialogTitle>
          <DialogDescription>
            صحّح أي أخطاء في تفريغ النص. لن تتم إعادة مطابقة الإجابات تلقائيًا بعد الحفظ.
          </DialogDescription>
        </DialogHeader>

        <Textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          rows={14}
          className="max-h-[50vh] min-h-48 resize-y"
        />

        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            إلغاء
          </Button>
          <Button onClick={handleSave} disabled={unchanged || updateTranscript.isPending}>
            {updateTranscript.isPending ? "جارٍ الحفظ..." : "حفظ النص"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
