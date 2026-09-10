"use client";

import { useEffect, useId, useRef, useState } from "react";

import { cn } from "@/lib/utils";

// Geometry extracted from the exported Claude Design canvas at
// "Logo animation sequence/" (logo-animation.jsx + the OM_SCENES cue list
// declared in "With Bader Logo Animation.dc.html"). Paths, gradient, and
// per-element choreography are copied verbatim from that source - do not
// hand-tune them without updating the source export too.
//
// The source's own OM_SCENES durations were Draw 1.8s, Lines 1.2s,
// Wordmark 1.6s, Hold 2.4s, Reset 1.1s (8.1s total), authored as a single
// narrative play-through. This component is a *persistent* UI element
// (a login-page brand mark, a loading indicator) rather than a one-time
// intro, so only the idle "Hold" beat - which has no drawing choreography
// tied to its length, just a static dwell before the loop resets - is
// shortened (2.4s -> 0.6s) to keep the loop feeling alive. Draw/Lines/
// Wordmark/Reset keep their exact original durations and handoff timings.
const CUES = { Draw: 0, Lines: 1.8, Wordmark: 3, Hold: 4.6, Reset: 5.2 };
// The choreography below (Mark/Wordmark/the scale+fade+drift math) is all
// keyed to these "authored" seconds, unchanged from the source export's
// own pacing/handoffs. It's played back sped up so one real loop takes
// LOOP_DURATION seconds instead of AUTHORED_DURATION - a single playback
// rate multiplier, rather than rewriting every offset by hand, so every
// handoff (e.g. the wedge popping in exactly as the bubble finishes
// drawing) stays exactly as authored, just faster.
const AUTHORED_DURATION = 6.3;
const DEFAULT_LOOP_DURATION = 2; // real seconds per visible loop - the UI-facing cycle time

// A settled, fully-drawn frame (just past the wordmark reveal) used as the
// static image for prefers-reduced-motion - no timers, no motion.
const SETTLED_T = CUES.Wordmark + 0.8;

const BUBBLE =
  "M118 75H316C377 75 421 119 421 177c0 57-44 101-105 101H171l-91 67 11-98c-32-19-51-54-51-94C40 109 73 75 118 75Z";
const WEDGE = "M300 278h121v-64Z";

const BARS = [
  { x: 118, y: 302, w: 304, h: 46 },
  { x: 118, y: 370, w: 304, h: 46 },
  { x: 118, y: 438, w: 236, h: 35 },
];

const WITH_GLYPHS = [
  "m 624.992,238 31.08,-122.472 H 638.6 L 616.088,214.984 588.2,115.528 h -16.8 l -27.216,99.456 -23.016,-99.456 H 503.696 L 535.112,238 h 17.136 L 579.632,137.368 607.856,238 Z",
  "m 676.45591,149.968 h -13.944 V 238 h 13.944 z m 0,-34.44 h -14.112 v 17.64 h 14.112 z",
  "m 724.22393,149.968 h -14.448 v -24.192 h -13.944 v 24.192 h -11.928 v 11.424 h 11.928 v 66.528 c 0,9.072 6.048,13.944 16.968,13.944 3.696,0 6.72,-0.336 11.424,-1.176 v -11.76 c -2.016,0.504 -3.864,0.672 -6.72,0.672 -6.048,0 -7.728,-1.68 -7.728,-7.896 v -60.312 h 14.448 z",
  "M 732.00782,115.528 V 238 h 13.944 v -48.552 c 0,-17.976 9.408,-29.736 23.856,-29.736 4.704,0 9.072,1.344 12.432,3.864 4.032,3.024 5.712,7.224 5.712,13.44 V 238 h 13.944 v -66.528 c 0,-14.784 -10.584,-24.024 -27.72,-24.024 -12.432,0 -19.992,3.864 -28.224,14.616 v -46.536 z",
];

const BADER_GLYPHS = [
  "m 514.268,418 h 57.072 c 14.616,0 24.36,-2.784 32.016,-9.222 7.656,-6.438 12.528,-17.052 12.528,-27.318 0,-12.528 -6.612,-22.446 -21.054,-30.798 12.528,-8.004 17.4,-15.312 17.4,-26.1 0,-8.874 -4.35,-17.922 -11.484,-24.186 -7.482,-6.438 -16.356,-9.222 -29.928,-9.222 h -56.55 z m 26.1,-105.096 h 28.362 c 12.18,0 18.444,4.872 18.444,14.268 0,9.57 -6.264,14.442 -18.444,14.442 h -28.362 z m 0,50.46 h 31.146 c 12.702,0 19.314,5.568 19.314,16.53 0,10.788 -6.612,16.356 -19.314,16.356 h -31.146 z",
  "m 709.80402,415.042 c -4.176,-4.002 -5.568,-6.786 -5.568,-11.484 v -52.2 c 0,-19.14 -13.05,-28.884 -38.454,-28.884 -25.404,0 -38.628,10.788 -40.194,32.538 h 23.49 c 1.218,-9.744 5.22,-12.876 17.226,-12.876 9.396,0 14.094,3.132 14.094,9.396 0,3.132 -1.566,5.742 -4.176,7.308 -3.306,1.74 -3.306,1.74 -15.312,3.654 l -9.744,1.74 c -18.618,3.132 -27.666,12.702 -27.666,29.58 0,16.878 11.31,28.188 28.536,28.188 10.44,0 19.836,-4.35 28.536,-13.398 0,4.872 0.522,6.612 2.784,9.396 h 26.448 z m -29.406,-34.8 c 0,14.094 -6.96,22.098 -19.314,22.098 -8.178,0 -13.224,-4.35 -13.224,-11.31 0,-7.308 3.828,-10.788 13.92,-12.876 l 8.352,-1.566 c 6.438,-1.218 7.482,-1.566 10.266,-2.958 z",
  "m 778.84198,418 h 24.36 V 291.154 h -24.36 v 45.066 c -6.09,-9.396 -14.094,-13.746 -25.926,-13.746 -22.446,0 -39.498,21.576 -39.498,49.938 0,12.702 3.828,25.578 10.092,34.626 6.438,9.222 17.922,14.964 29.406,14.964 11.832,0 19.836,-4.176 25.926,-13.572 z m -20.532,-75.168 c 12.354,0 20.532,11.832 20.532,29.928 0,17.052 -8.352,28.884 -20.532,28.884 -12.18,0 -20.532,-12.006 -20.532,-29.232 0,-17.574 8.352,-29.58 20.532,-29.58 z",
  "m 898.86197,378.676 c 0.174,-2.088 0.174,-2.958 0.174,-4.176 0,-9.396 -1.392,-18.096 -3.654,-24.708 -6.264,-17.052 -21.402,-27.318 -40.368,-27.318 -26.97,0 -43.5,19.488 -43.5,50.982 0,30.102 16.356,48.546 42.978,48.546 21.054,0 38.106,-11.832 43.5,-30.45 h -24.012 c -2.958,7.482 -9.744,11.832 -18.618,11.832 -6.96,0 -12.528,-2.958 -16.008,-8.178 -2.262,-3.48 -3.132,-7.656 -3.48,-16.53 z m -62.64,-16.182 c 1.566,-14.442 7.656,-21.402 18.444,-21.402 11.136,0 17.748,7.482 18.966,21.402 z",
  "M 908.39193,324.04 V 418 h 24.36 v -49.938 c 0,-14.268 7.134,-21.402 21.402,-21.402 2.61,0 4.35,0.174 7.656,0.696 v -24.708 c -1.392,-0.174 -1.914,-0.174 -2.958,-0.174 -11.136,0 -20.706,7.308 -26.1,20.01 V 324.04 Z",
];

// Easing + animate() are the exact functions the exported composition
// engine used (easeOutCubic/easeInOutQuad/easeOutBack via
// animate({from,to,start,end,ease})), reduced to just what this animation
// calls - the exported engine also carried a full timeline editor, video
// exporter, and watercolor kit that this app has no use for.
function easeOutCubic(t: number) {
  const p = t - 1;
  return p * p * p + 1;
}
function easeInOutQuad(t: number) {
  return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
}
function easeOutBack(t: number) {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
}

type Ease = (t: number) => number;

function animate(from: number, to: number, start: number, end: number, ease: Ease) {
  return (t: number) => {
    if (t <= start) return from;
    if (t >= end) return to;
    const local = (t - start) / (end - start);
    return from + (to - from) * ease(local);
  };
}

const enter = (from: number, to: number, start: number, end: number) =>
  animate(from, to, start, end, easeOutCubic);
const draw = (from: number, to: number, start: number, end: number) =>
  animate(from, to, start, end, easeInOutQuad);
const pop = (from: number, to: number, start: number, end: number) =>
  animate(from, to, start, end, easeOutBack);

function Mark({ t, gradientId }: { t: number; gradientId: string }) {
  const dash = draw(1, 0, CUES.Draw + 0.15, CUES.Draw + 1.6)(t);
  const wedge = pop(0, 1, CUES.Lines - 0.2, CUES.Lines + 0.45)(t);
  const fill = `url(#${gradientId})`;
  return (
    <g>
      <path
        d={BUBBLE}
        pathLength={1}
        fill="none"
        stroke={fill}
        strokeWidth={39}
        strokeLinejoin="round"
        strokeLinecap="round"
        strokeDasharray="1 1"
        strokeDashoffset={dash}
      />
      <path
        d={WEDGE}
        fill={fill}
        opacity={wedge > 0.02 ? 1 : 0}
        transform={`translate(421,278) scale(${Math.max(wedge, 0.001)}) translate(-421,-278)`}
      />
      {BARS.map((b, i) => {
        const s = CUES.Lines + 0.1 + i * 0.2;
        const w = enter(0, b.w, s, s + 0.55)(t);
        const o = enter(0, 1, s, s + 0.2)(t);
        return (
          <rect
            key={i}
            x={b.x}
            y={b.y}
            width={Math.max(w, 0.01)}
            height={b.h}
            rx={2}
            fill={fill}
            opacity={o}
          />
        );
      })}
    </g>
  );
}

function Wordmark({ t }: { t: number }) {
  const glyph = (d: string, key: string, start: number) => {
    const y = enter(34, 0, start, start + 0.7)(t);
    const o = enter(0, 1, start, start + 0.45)(t);
    return <path key={key} d={d} opacity={o} transform={`translate(0,${y})`} />;
  };
  return (
    <g fill="#113b69">
      {WITH_GLYPHS.map((d, i) => glyph(d, `w${i}`, CUES.Wordmark + i * 0.075))}
      {BADER_GLYPHS.map((d, i) => glyph(d, `b${i}`, CUES.Wordmark + 0.28 + i * 0.075))}
    </g>
  );
}

export type AnimatedLogoProps = {
  className?: string;
  /** Render just the speech-bubble mark (no wordmark) - for compact/inline
   * loading badges where the full lockup would be too small to read. */
  markOnly?: boolean;
  /** Real seconds per visible loop. Defaults to the standard ~2s loading
   * cadence; the login page's persistent brand mark asks for a slower,
   * calmer ~4s loop via this prop - the authored choreography (CUES,
   * every handoff) is identical either way, only the playback speed
   * changes. */
  loopSeconds?: number;
};

/**
 * The animated "With Bader" mark + wordmark, looping continuously for as
 * long as it stays mounted. Purely visual - it owns no loading state and
 * no fixed duration; callers control how long it's on screen simply by
 * mounting/unmounting it (see BrandLoader for the loading-state wrapper,
 * and services/auth/components/auth-shell.tsx for the persistent
 * login-panel usage). Safe to unmount at any point mid-cycle: the only
 * cleanup required is cancelling its own requestAnimationFrame, which the
 * effect below always does.
 */
export function AnimatedLogo({ className, markOnly = false, loopSeconds = DEFAULT_LOOP_DURATION }: AnimatedLogoProps) {
  const gradientId = useId();
  const [t, setT] = useState(0);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    const reduced =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (reduced) {
      const raf = requestAnimationFrame(() => setT(SETTLED_T));
      return () => cancelAnimationFrame(raf);
    }

    const playbackRate = AUTHORED_DURATION / loopSeconds;
    let start: number | null = null;
    const tick = (ts: number) => {
      if (start === null) start = ts;
      const elapsedReal = (ts - start) / 1000;
      const authoredT = (elapsedReal * playbackRate) % AUTHORED_DURATION;
      setT(authoredT);
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);

    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    };
  }, [loopSeconds]);

  const settle = enter(1.07, 1, CUES.Draw, CUES.Wordmark + 0.8)(t);
  const drift = 1 + 0.012 * Math.sin(((t - CUES.Hold) / 3.4) * Math.PI * 2) * (t > CUES.Hold ? 1 : 0);
  const out = draw(1, 1.035, CUES.Reset + 0.15, AUTHORED_DURATION)(t);
  const scale = settle * drift * out;
  const fade = draw(1, 0, CUES.Reset + 0.3, AUTHORED_DURATION - 0.05)(t);
  const sheen = 70 * Math.sin((t / 4.6) * Math.PI * 2);

  return (
    <svg
      aria-hidden="true"
      className={cn("h-full w-full", className)}
      // markOnly's viewBox deliberately frames the mark's true bounding box
      // (x:40-422, y:75-473, including the tail and bars) with ~85px of
      // margin on every side - not a tight crop. The entrance/exit
      // choreography above briefly scales the whole <svg> up to ~1.07x via
      // a CSS transform, which paints outside the element's own box
      // whenever a container doesn't clip it (e.g. a small icon badge).
      // Baking the margin into the viewBox (rather than clipping with
      // overflow-hidden, which would just crop the overshoot off instead
      // of preventing it) keeps the drawn mark's edges inside the box at
      // every scale this animation ever reaches, in any container.
      viewBox={markOnly ? "-50 -10 560 570" : "20 45 970 460"}
      style={{ transform: `scale(${scale})`, opacity: fade }}
    >
      <defs>
        <linearGradient
          id={gradientId}
          x1={60 + sheen}
          y1="70"
          x2={430 + sheen}
          y2="420"
          gradientUnits="userSpaceOnUse"
        >
          <stop offset="0" stopColor="#25D7B9" />
          <stop offset="0.52" stopColor="#20BCCE" />
          <stop offset="1" stopColor="#2585F2" />
        </linearGradient>
      </defs>
      <Mark t={t} gradientId={gradientId} />
      {!markOnly && <Wordmark t={t} />}
    </svg>
  );
}
