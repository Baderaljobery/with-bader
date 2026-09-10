"use client";

import { toast } from "sonner";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { ApiError } from "@/lib/api/client";
import { useDeleteGuest } from "../hooks/use-guest-mutations";
import type { Guest } from "../types/guest";

type DeleteGuestDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  guest: Guest;
  onDeleted?: () => void;
};

export function DeleteGuestDialog({ open, onOpenChange, guest, onDeleted }: DeleteGuestDialogProps) {
  const deleteGuest = useDeleteGuest();

  async function handleDelete() {
    try {
      await deleteGuest.mutateAsync(guest.id);
      toast.success("تم حذف الضيف");
      onOpenChange(false);
      onDeleted?.();
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "حدث خطأ ما.";
      toast.error(message);
    }
  }

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>حذف {guest.display_name}؟</AlertDialogTitle>
          <AlertDialogDescription>
            سيتم حذف هذا الضيف نهائيًا مع كل ما يرتبط به (البحث، الأسئلة، وبيانات المقابلة).
            لا يمكن التراجع عن هذا الإجراء.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>إلغاء</AlertDialogCancel>
          <AlertDialogAction
            variant="destructive"
            disabled={deleteGuest.isPending}
            onClick={handleDelete}
          >
            {deleteGuest.isPending ? "جارٍ الحذف..." : "حذف الضيف"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
