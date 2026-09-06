import { Check, Palette } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type AppearanceOption = {
  id: "default" | "dark" | "custom";
  label: string;
  preview: React.ReactNode;
};

function PreviewLines({ tone }: { tone: "light" | "dark" }) {
  const barClass = tone === "light" ? "bg-[#E6EAF0]" : "bg-white/25";
  return (
    <div className="flex flex-col gap-1.5">
      <div className={cn("h-1.5 w-3/4 rounded-full", barClass)} />
      <div className={cn("h-1.5 w-1/2 rounded-full", barClass)} />
    </div>
  );
}

const OPTIONS: AppearanceOption[] = [
  {
    id: "default",
    label: "افتراضي",
    preview: (
      <div className="flex h-16 flex-col justify-between rounded-lg border border-[#E6EAF0] bg-white p-2.5">
        <span
          aria-hidden="true"
          className="h-1.5 w-6 rounded-full"
          style={{ backgroundImage: "var(--gradient-primary)" }}
        />
        <PreviewLines tone="light" />
      </div>
    ),
  },
  {
    id: "dark",
    label: "داكن",
    preview: (
      <div className="flex h-16 flex-col justify-between rounded-lg border border-white/10 bg-[#0B1F3A] p-2.5">
        <span aria-hidden="true" className="h-1.5 w-6 rounded-full bg-[#1FCFC3]" />
        <PreviewLines tone="dark" />
      </div>
    ),
  },
  {
    id: "custom",
    label: "مخصص",
    preview: (
      <div
        className="flex h-16 flex-col justify-between rounded-lg border border-white/10 p-2.5"
        style={{ backgroundImage: "linear-gradient(135deg, #1FCFC3 0%, #1B8FEA 100%)" }}
      >
        <Palette className="size-3.5 text-white/90" aria-hidden="true" />
        <PreviewLines tone="dark" />
      </div>
    ),
  },
];

/** Visual-only preview of a future appearance/theme feature - no real
 * switching, no persistence, no backend. Every control here is disabled;
 * "قريبًا" makes that unmistakable rather than letting the cards look
 * broken or accidentally interactive. */
export function AppearanceCard() {
  return (
    <Card className="relative overflow-hidden">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>المظهر</CardTitle>
          <Badge>قريبًا</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="mb-4 text-sm text-muted-foreground">اختر شكل الواجهة المفضّل لديك.</p>

        <div
          aria-disabled="true"
          className="grid grid-cols-1 gap-3 opacity-70 grayscale-[8%] select-none sm:grid-cols-3"
        >
          {OPTIONS.map((option) => (
            <div
              key={option.id}
              role="radio"
              aria-checked={option.id === "default"}
              aria-disabled="true"
              tabIndex={-1}
              className={cn(
                "pointer-events-none flex flex-col gap-2 rounded-xl border p-2.5",
                option.id === "default" ? "border-[#1B8FEA]/40" : "border-border",
              )}
            >
              <div className="relative">
                {option.preview}
                {option.id === "default" ? (
                  <span
                    className="absolute -top-1 -end-1 flex size-4 items-center justify-center rounded-full text-white"
                    style={{ backgroundImage: "var(--gradient-primary)" }}
                    aria-hidden="true"
                  >
                    <Check className="size-2.5" />
                  </span>
                ) : null}
              </div>
              <span className="text-center text-xs font-medium text-foreground">{option.label}</span>
            </div>
          ))}
        </div>

        <p className="mt-4 text-center text-xs text-muted-foreground">
          هذه الميزة قيد التطوير وستكون متاحة قريبًا.
        </p>
      </CardContent>
    </Card>
  );
}
