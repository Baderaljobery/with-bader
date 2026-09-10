/**
 * With Bader's shared decorative background: two restrained clusters of
 * flowing lines in the brand teal-to-blue gradient. The pattern is mounted by
 * the app and auth shells so route content never needs to know about it.
 *
 * This is a static Server Component. It is removed from the accessibility and
 * pointer-event trees and is sized by its containing shell, so it neither
 * affects layout nor creates overflow.
 */

const LINE_COUNT = 9;
const CLUSTER_SPAN = 820; // Local x span in the 1600x900 viewBox below.
const FREQUENCY = 1.15; // Sine cycles across the span.
const PHASE = 0.35;
const STEPS = 40;

function wavePath(index: number) {
  const baseline = 20 + index * 58;
  const amplitude = 44 + index * 2;
  const points: string[] = [];

  for (let i = 0; i <= STEPS; i++) {
    const t = i / STEPS;
    const x = -60 + t * (CLUSTER_SPAN + 60);
    const y = baseline + Math.sin(t * FREQUENCY * Math.PI * 2 + PHASE) * amplitude;
    points.push(`${x.toFixed(1)},${y.toFixed(1)}`);
  }

  return `M${points.join("L")}`;
}

const LINES = Array.from({ length: LINE_COUNT }, (_, i) => ({
  d: wavePath(i),
  opacity: Math.max(0.34 - i * 0.032, 0.05),
}));

export function BackgroundPattern() {
  return (
    <svg
      aria-hidden="true"
      className="pointer-events-none absolute inset-0 z-[1] h-full w-full opacity-55 sm:opacity-75 lg:opacity-100"
      viewBox="0 0 1600 900"
      preserveAspectRatio="xMidYMid slice"
    >
      <defs>
        <linearGradient id="withBaderWaveGradient" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#1FCFC3" />
          <stop offset="1" stopColor="#1B8FEA" />
        </linearGradient>
      </defs>
      <g
        stroke="url(#withBaderWaveGradient)"
        strokeWidth="1.4"
        fill="none"
        strokeLinecap="round"
      >
        {LINES.map((line, i) => (
          <path key={`tl-${i}`} d={line.d} opacity={line.opacity} />
        ))}
      </g>
      <g
        stroke="url(#withBaderWaveGradient)"
        strokeWidth="1.4"
        fill="none"
        strokeLinecap="round"
        transform="translate(1600,900) rotate(180)"
      >
        {LINES.map((line, i) => (
          <path key={`br-${i}`} d={line.d} opacity={line.opacity} />
        ))}
      </g>
    </svg>
  );
}
