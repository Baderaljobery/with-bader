"""Safe content retrieval for user-provided trusted guest links (Phase 12).

A trusted link stored with no content at all ranks WORSE than a random
search result in the existing selection logic (which prefers sources that
have real content/snippet) - the opposite of "high identity confidence".
This module fetches a bounded amount of visible text from the link so it
can actually be used as evidence, with the safety constraints the task
requires: public http/https only, no localhost/private-network targets,
bounded redirects, timeout, response-size cap, content-type validation, no
JS execution, no auth/paywall bypass. Stdlib-only HTML-to-text (no new
dependency) - good enough for evidence text, not meant to be a full reader.

Auth-walled platforms (LinkedIn, YouTube, X/Twitter, Facebook, Instagram)
are deliberately skipped rather than faked - they block or require
authentication for server-side fetches, and Phase 12 explicitly forbids
pretending to support what isn't actually supported. The link is still
used as a first-class identity anchor (app/research/identity_resolution.py
gives any guest_link-origin source a high base score) even without body
text.
"""

import ipaddress
import socket
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

import httpx

_SKIP_DEEP_FETCH_HOST_HINTS = (
    "linkedin.com",
    "youtube.com",
    "youtu.be",
    "twitter.com",
    "x.com",
    "facebook.com",
    "instagram.com",
)

_USER_AGENT = "WithBaderResearchBot/1.0 (+trusted-link-evidence-fetch)"


class _HTMLTextExtractor(HTMLParser):
    """Strips tags and script/style content, keeping only visible text."""

    _SKIP_TAGS = {"script", "style", "noscript", "template"}

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self.chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            stripped = " ".join(data.split())
            if stripped:
                self.chunks.append(stripped)


def _extract_html_text(html: str) -> str:
    parser = _HTMLTextExtractor()
    try:
        parser.feed(html)
    except Exception:  # malformed markup is data, not our problem to raise on
        return ""
    return " ".join(parser.chunks)


def _is_disallowed_host(hostname: str) -> bool:
    """SSRF guard: reject anything that resolves to a private/loopback/
    link-local/reserved address, and localhost by name."""
    hostname = hostname.lower()
    if hostname in ("localhost", "localhost.localdomain"):
        return True
    try:
        ip = ipaddress.ip_address(hostname)
        return _is_disallowed_ip(ip)
    except ValueError:
        pass  # not a literal IP - resolve it
    try:
        infos = socket.getaddrinfo(hostname, None)
    except OSError:
        return True  # can't resolve -> treat as unsafe, never silently proceed
    for info in infos:
        sockaddr = info[4]
        try:
            ip = ipaddress.ip_address(sockaddr[0])
        except ValueError:
            return True
        if _is_disallowed_ip(ip):
            return True
    return False


def _is_disallowed_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _is_safe_public_url(url: str) -> bool:
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https"):
        return False
    hostname = parts.hostname
    if not hostname:
        return False
    return not _is_disallowed_host(hostname)


def should_skip_deep_fetch(url: str) -> bool:
    host = (urlsplit(url).hostname or "").lower()
    return any(hint in host for hint in _SKIP_DEEP_FETCH_HOST_HINTS)


async def fetch_trusted_link_text(
    url: str,
    *,
    timeout_seconds: float,
    max_bytes: int,
    max_redirects: int,
    max_text_chars: int,
) -> str | None:
    """Best-effort: returns None on anything unsafe, disallowed, or failed -
    never raises, so one bad trusted link never breaks the research run."""
    if should_skip_deep_fetch(url):
        return None

    current_url = url
    async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=False) as client:
        for _ in range(max_redirects + 1):
            if not _is_safe_public_url(current_url):
                return None
            try:
                async with client.stream(
                    "GET", current_url, headers={"User-Agent": _USER_AGENT}
                ) as response:
                    if response.status_code in (301, 302, 303, 307, 308):
                        location = response.headers.get("location")
                        if not location:
                            return None
                        current_url = urljoin(current_url, location)
                        continue

                    if response.status_code >= 400:
                        return None

                    content_type = response.headers.get("content-type", "").lower()
                    if "text/html" not in content_type and "text/plain" not in content_type:
                        return None  # no binaries, no PDFs, no JS execution - text only

                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        body.extend(chunk)
                        if len(body) > max_bytes:
                            break

                    charset = response.encoding or "utf-8"
                    try:
                        text = bytes(body).decode(charset, errors="ignore")
                    except LookupError:
                        text = bytes(body).decode("utf-8", errors="ignore")
            except (httpx.TimeoutException, httpx.RequestError):
                return None

            extracted = text if "text/plain" in content_type else _extract_html_text(text)
            extracted = extracted.strip()
            return extracted[:max_text_chars] if extracted else None

    return None  # exhausted max_redirects without landing on a final page
