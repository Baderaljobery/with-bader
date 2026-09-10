import { BrandLoader } from "@/components/brand/brand-loader";

/**
 * Scoped to the authenticated app-shell route group: Next.js swaps this in
 * for the routed page content while a segment under (app) is genuinely
 * suspended (a real route transition, not a component-level data fetch
 * inside an already-rendered page - those use BrandLoader's "section"
 * variant directly, e.g. the guest overview page). Full-viewport per the
 * app's global/page-loading contract - Next.js alone decides when this
 * unmounts, so there's no fixed duration here either.
 */
export default function AppGroupLoading() {
  return <BrandLoader loading variant="fullscreen" />;
}
