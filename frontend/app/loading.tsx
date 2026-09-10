import { BrandLoader } from "@/components/brand/brand-loader";

/**
 * Next.js route-segment fallback: rendered only while the root segment is
 * genuinely suspended (e.g. a route's code/RSC payload is still being
 * fetched), and swapped out for the real page the instant Next.js decides
 * it's ready - no fixed duration, no artificial delay.
 */
export default function RootLoading() {
  return <BrandLoader loading variant="fullscreen" />;
}
