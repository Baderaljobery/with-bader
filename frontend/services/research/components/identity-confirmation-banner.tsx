import { AlertTriangle } from "lucide-react";

// Mirrors the backend default (settings.research_identity_confirmation_threshold,
// app/core/config.py) - used only to decide when to show this banner, not
// to re-derive the actual confidence score.
const IDENTITY_CONFIRMATION_THRESHOLD = 0.35;

/**
 * Phase 11 - "do NOT silently generate a confident-looking research
 * profile" when little of the evidence is confidently tied to this guest.
 * Shown whenever the run's aggregate identity relevance is low, whatever is
 * displayed below it.
 */
export function IdentityConfirmationBanner({
  identityConfidence,
}: {
  identityConfidence?: number | null;
}) {
  if (identityConfidence == null || identityConfidence >= IDENTITY_CONFIRMATION_THRESHOLD) {
    return null;
  }

  return (
    <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4">
      <AlertTriangle className="mt-0.5 size-4.5 shrink-0 text-amber-600" aria-hidden="true" />
      <div className="space-y-0.5">
        <p className="text-sm font-medium text-amber-900">قد يحتاج تأكيد هوية الضيف</p>
        <p className="text-sm text-amber-800">
          لم يجد البحث أدلة كافية مرتبطة بثقة بهذا الضيف تحديدًا. راجع بيانات الضيف (الاسم، الشركة،
          الدولة، الروابط الموثوقة) وأعد البحث، أو تحقق يدويًا من النتائج أدناه.
        </p>
      </div>
    </div>
  );
}
