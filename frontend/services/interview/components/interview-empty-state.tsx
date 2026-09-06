import { Mic } from "lucide-react";

import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";

type InterviewEmptyStateProps = {
  onUpload: () => void;
};

export function InterviewEmptyState({ onUpload }: InterviewEmptyStateProps) {
  return (
    <EmptyState
      icon={Mic}
      title="لم تتم إضافة مقابلة لهذا الضيف بعد"
      description="ارفع ملف المقابلة لاستخراج النص وربط الإجابات بالأسئلة المحفوظة."
      action={<Button onClick={onUpload}>رفع ملف المقابلة</Button>}
    />
  );
}
