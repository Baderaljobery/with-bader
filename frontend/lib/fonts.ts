import localFont from "next/font/local";

/**
 * Self-hosted Thmanyah type system (see design-notes.md > Typography).
 * WOFF2-only, project-local files under public/fonts/thmanyah/ - no
 * dependency on any font being installed on a developer's machine, and no
 * external font request at runtime (unlike next/font/google).
 *
 * Weights match exactly what shipped in the delivered font package (Light/
 * Regular/Medium/Bold/Black) - no invented weights.
 *
 * next/font/local's build-time plugin statically parses each `localFont()`
 * call, so the `src` array must be a literal here - it cannot be built via
 * a shared helper function (that fails with a cryptic "missing field
 * `src`" resolve error since the plugin never actually evaluates the JS).
 */

/** Primary application/UI font - see app/layout.tsx and globals.css
 * (--font-sans / --font-thmanyah-sans). */
export const thmanyahSans = localFont({
  variable: "--font-thmanyah-sans",
  display: "swap",
  src: [
    { path: "../public/fonts/thmanyah/sans/thmanyahsans-Light.woff2", weight: "300", style: "normal" },
    { path: "../public/fonts/thmanyah/sans/thmanyahsans-Regular.woff2", weight: "400", style: "normal" },
    { path: "../public/fonts/thmanyah/sans/thmanyahsans-Medium.woff2", weight: "500", style: "normal" },
    { path: "../public/fonts/thmanyah/sans/thmanyahsans-Bold.woff2", weight: "700", style: "normal" },
    { path: "../public/fonts/thmanyah/sans/thmanyahsans-Black.woff2", weight: "900", style: "normal" },
  ],
});

/** Editorial/display headline font - reserved for Design Engine template
 * headlines and premium poster-style treatments, not the default UI font. */
export const thmanyahSerifDisplay = localFont({
  variable: "--font-thmanyah-serif-display",
  display: "swap",
  src: [
    {
      path: "../public/fonts/thmanyah/serif-display/thmanyahserifdisplay-Light.woff2",
      weight: "300",
      style: "normal",
    },
    {
      path: "../public/fonts/thmanyah/serif-display/thmanyahserifdisplay-Regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../public/fonts/thmanyah/serif-display/thmanyahserifdisplay-Medium.woff2",
      weight: "500",
      style: "normal",
    },
    {
      path: "../public/fonts/thmanyah/serif-display/thmanyahserifdisplay-Bold.woff2",
      weight: "700",
      style: "normal",
    },
    {
      path: "../public/fonts/thmanyah/serif-display/thmanyahserifdisplay-Black.woff2",
      weight: "900",
      style: "normal",
    },
  ],
});

/** Editorial reading font - reserved for longer editorial copy in selected
 * Design Engine layouts, not the default UI body font. */
export const thmanyahSerifText = localFont({
  variable: "--font-thmanyah-serif-text",
  display: "swap",
  src: [
    { path: "../public/fonts/thmanyah/serif-text/thmanyahseriftext-Light.woff2", weight: "300", style: "normal" },
    { path: "../public/fonts/thmanyah/serif-text/thmanyahseriftext-Regular.woff2", weight: "400", style: "normal" },
    { path: "../public/fonts/thmanyah/serif-text/thmanyahseriftext-Medium.woff2", weight: "500", style: "normal" },
    { path: "../public/fonts/thmanyah/serif-text/thmanyahseriftext-Bold.woff2", weight: "700", style: "normal" },
    { path: "../public/fonts/thmanyah/serif-text/thmanyahseriftext-Black.woff2", weight: "900", style: "normal" },
  ],
});
