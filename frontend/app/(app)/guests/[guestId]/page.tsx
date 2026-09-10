"use client";

import { Building2, CalendarPlus, ExternalLink, RefreshCw, Search } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import type { LucideIcon } from "lucide-react";

import { BrandLoader } from "@/components/brand/brand-loader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ContentStatusSelect } from "@/services/guests/components/content-status-select";
import { useGuest } from "@/services/guests/hooks/use-guest";
import { useGuestLinks } from "@/services/guests/hooks/use-guest-links";
import { useLatestGuestResearch } from "@/services/research/hooks/use-latest-guest-research";

function formatDate(value: string) {
  // Fixed locale (not `undefined`/browser locale) so dates render with
  // stable Latin numerals regardless of the viewer's OS/browser language -
  // ar locales format Gregorian dates with Arabic-Indic digits, which
  // collide visually next to the surrounding Arabic copy.
  return new Date(value).toLocaleDateString("en-GB", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function InfoChip({ icon: Icon, label, value }: { icon: LucideIcon; label: string; value: string }) {
  return (
    <Card size="sm">
      <CardContent className="flex items-center gap-3">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-[image:var(--gradient-primary)] text-white shadow-[0_6px_14px_-4px_rgba(27,143,234,0.4)]">
          <Icon className="size-4.5" aria-hidden="true" />
        </span>
        <div className="min-w-0">
          <p className="text-xs text-[#5F6368]">{label}</p>
          <p className="truncate text-sm font-medium text-[#161616]">{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}

/** The guest's name shown paired: Arabic first (primary), English second
 * (secondary/muted) - the only bilingual identity field. */
function NameRow({ ar, en }: { ar: string | null; en: string | null }) {
  return (
    <div className="flex items-baseline justify-between gap-3 border-b border-[#E6EAF0] py-2.5">
      <p className="shrink-0 text-xs text-[#5F6368]">الاسم</p>
      <div className="min-w-0 text-end">
        <p className="truncate text-sm font-medium text-[#161616]">{ar || "—"}</p>
        {en && en !== ar ? (
          <p dir="ltr" className="truncate text-xs text-[#5F6368]">
            {en}
          </p>
        ) : null}
      </div>
    </div>
  );
}

function IdentityRow({ label, value }: { label: string; value: string | null }) {
  if (!value) return null;
  return (
    <div className="flex items-baseline justify-between gap-3 border-b border-[#E6EAF0] py-2.5 last:border-0">
      <p className="shrink-0 text-xs text-[#5F6368]">{label}</p>
      <p className="min-w-0 truncate text-end text-sm font-medium text-[#161616]">{value}</p>
    </div>
  );
}

export default function GuestOverviewPage() {
  const { guestId } = useParams<{ guestId: string }>();
  const { data: guest, isPending } = useGuest(guestId);
  const { data: latestResearch, isError: hasNoResearch } = useLatestGuestResearch(guestId);
  const { data: links } = useGuestLinks(guestId);

  if (isPending || !guest) {
    return <BrandLoader loading variant="section" />;
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <InfoChip icon={Building2} label="الشركة" value={guest.company ?? "—"} />
        <ContentStatusSelect guest={guest} />
        <InfoChip icon={CalendarPlus} label="تاريخ الإضافة" value={formatDate(guest.created_at)} />
        <InfoChip icon={RefreshCw} label="آخر تحديث" value={formatDate(guest.updated_at)} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>الهوية الأساسية</CardTitle>
          </CardHeader>
          <CardContent className="space-y-0">
            <NameRow ar={guest.name_ar} en={guest.name_en} />
            <IdentityRow label="المسمى الوظيفي" value={guest.job_title} />
            <IdentityRow label="الشركة" value={guest.company} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>حالة البحث</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {latestResearch ? (
              <div className="space-y-1">
                <p className="text-sm font-medium text-[#161616]">
                  آخر بحث: الإصدار {latestResearch.version}
                </p>
                <p className="text-xs text-[#5F6368]">{formatDate(latestResearch.created_at)}</p>
              </div>
            ) : hasNoResearch ? (
              <p className="text-sm text-[#5F6368]">لم يُجرَ بحث لهذا الضيف بعد.</p>
            ) : null}
            <Link
              href={`/guests/${guestId}/research`}
              className="inline-flex items-center gap-1.5 text-sm font-medium text-[#1B8FEA] hover:underline"
            >
              <Search className="size-4" aria-hidden="true" />
              فتح صفحة البحث
            </Link>

            {links && links.length > 0 ? (
              <div className="space-y-1.5 border-t border-[#E6EAF0] pt-3">
                <p className="text-xs text-[#5F6368]">روابط موثوقة</p>
                <ul className="space-y-1">
                  {links.map((link) => (
                    <li key={link.id}>
                      <a
                        href={link.url}
                        target="_blank"
                        rel="noreferrer noopener"
                        className="inline-flex items-center gap-1.5 text-sm text-[#161616] hover:text-[#1B8FEA] hover:underline"
                      >
                        <ExternalLink className="size-3.5 shrink-0" aria-hidden="true" />
                        <span className="truncate">{link.label}</span>
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>نبذة تعريفية</CardTitle>
          </CardHeader>
          <CardContent>
            {guest.biography ? (
              <p className="whitespace-pre-wrap text-sm text-[#161616]">{guest.biography}</p>
            ) : (
              <p className="text-sm text-[#5F6368]">لا توجد نبذة تعريفية بعد.</p>
            )}
          </CardContent>
        </Card>

        {guest.research_summary ? (
          <Card>
            <CardHeader>
              <CardTitle>ملخص البحث</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="whitespace-pre-wrap text-sm text-[#161616]">{guest.research_summary}</p>
            </CardContent>
          </Card>
        ) : null}
      </div>
    </div>
  );
}
