import type { ReactNode } from "react";

import { AnimatedLogo } from "@/components/brand/animated-logo";
import { BackgroundPattern } from "@/components/brand/background-pattern";
import { Logo } from "@/components/brand/logo";

/**
 * Split-card composition for the login/register screen: one large rounded
 * container, a branded gradient panel on one side and the auth form on the
 * other - loosely inspired by a reference split-login layout (large card,
 * logo on the branded side, generous whitespace), but built entirely from
 * the existing With Bader gradient/typography/RTL system, not the
 * reference's own colors or content.
 *
 * The brand panel renders first in the RTL flow so it lands on the
 * physical right edge, mirroring the app shell's own sidebar-on-the-right
 * convention (components/app-shell/sidebar.tsx).
 */
export function AuthShell({ children }: { children: ReactNode }) {
  return (
    <div
      dir="rtl"
      className="relative isolate flex min-h-dvh items-center justify-center overflow-hidden bg-[#F7F8FA] px-4 py-10"
    >
      <BackgroundPattern />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-24 start-1/4 z-0 size-96 rounded-full opacity-70 blur-3xl"
        style={{ backgroundImage: "var(--glow-teal)" }}
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -bottom-32 end-1/4 z-0 size-96 rounded-full opacity-70 blur-3xl"
        style={{ backgroundImage: "var(--glow-blue)" }}
      />

      <div className="relative z-10 grid w-full max-w-4xl overflow-hidden rounded-3xl border border-[#E6EAF0] bg-white shadow-[var(--shadow-elevated)] md:grid-cols-2">
        <div
          className="relative hidden flex-col justify-between overflow-hidden p-10 text-white md:flex"
          style={{ backgroundImage: "var(--gradient-primary)" }}
        >
          <div
            aria-hidden="true"
            className="pointer-events-none absolute -end-16 -top-16 size-64 rounded-full bg-white/10 blur-2xl"
          />
          <div
            aria-hidden="true"
            className="pointer-events-none absolute -start-20 bottom-0 size-72 rounded-full bg-white/10 blur-2xl"
          />

          <div className="relative mt-10 w-fit self-center">
            {/* Continuous brand animation, not a loading state - loops for
                as long as the login screen is open (AnimatedLogo). */}
            <AnimatedLogo loopSeconds={4} className="h-25 w-auto brightness-0 invert" />
          </div>

          <div className="relative space-y-3">
            <h2 className="font-heading text-2xl font-bold leading-snug">
              منصتك الكاملة لإدارة المقابلات
            </h2>
            <p className="text-sm leading-relaxed text-white/85">
              نظّم ضيوفك، أعدّ أسئلتك، ووثّق محتواك في مكان واحد مصمم
              للمحاورين المحترفين.
            </p>
          </div>
        </div>

        <div className="flex flex-col justify-center p-8 sm:p-10">
          <div className="mb-6 flex justify-center md:hidden">
            <Logo size="md" />
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}
