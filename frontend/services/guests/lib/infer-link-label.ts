/**
 * Infers a trusted link's type from its URL/domain, so the user never has
 * to classify it manually. The returned strings are the exact canonical
 * values backend/app/research/collectors/guest_link_collector.py's
 * `_infer_source_type` keyword-matches (case-insensitively) - keep both in
 * sync if either changes.
 */
export function inferLinkLabel(url: string): string {
  let host = "";
  try {
    host = new URL(url).hostname.toLowerCase().replace(/^www\./, "");
  } catch {
    return "Website";
  }

  if (host.includes("linkedin.com")) return "LinkedIn";
  if (host.includes("youtube.com") || host.includes("youtu.be")) return "YouTube";
  if (host.includes("x.com") || host.includes("twitter.com")) return "X (Twitter)";
  if (host.includes("instagram.com")) return "Instagram";
  if (host.includes("facebook.com")) return "Facebook";
  return "Website";
}
