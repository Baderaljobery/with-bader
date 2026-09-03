// Fixed locale (not `undefined`/browser locale) so dates render with stable
// Latin numerals regardless of the viewer's OS/browser language - matches
// the same fix already applied on the guest overview page.
export function formatDate(value: string) {
  return new Date(value).toLocaleDateString("en-GB", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}
