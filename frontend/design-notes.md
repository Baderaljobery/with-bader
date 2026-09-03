# With Bader — Design Notes

Reference this file whenever building or styling any frontend component.
Use it together with the `frontend-design` skill (`.claude/skills/frontend-design`).

## Brand

**With Bader** (ويذ بدر) — an Arabic-first interview preparation and content
platform. The tone is professional, clean, and modern SaaS — not playful, not
corporate-cold. Think "a serious tool a podcaster/interviewer trusts daily,"
not a marketing landing page.

## Logo

- Icon: a speech-bubble mark (two overlapping chat bubbles suggesting
  conversation/dialogue) in a teal → blue gradient, paired with three
  horizontal bars underneath (representing notes/transcript lines) in the
  same gradient.
- Wordmark: "With" in a thin/light weight, "Bader" in a bold weight, both in
  dark navy — the weight contrast (thin + bold) is a deliberate brand device.
  Reuse this thin/bold pairing in UI headings where it fits (e.g. a page
  title like "بحث **بدر**").

## Color palette

| Role | Hex | Usage |
|---|---|---|
| Primary gradient start | `#1FCFC3` | Teal end of gradient — icons, accents, chart highlights |
| Primary gradient end | `#1B8FEA` | Blue end of gradient — buttons, links, active states |
| Primary gradient | `linear-gradient(135deg, #1FCFC3, #1B8FEA)` | Logo, primary CTAs, active nav indicator, key accents — use sparingly, not as a background wash |
| Main text | `#161616` | Body copy, primary headings |
| Secondary text | `#5F6368` | Captions, muted labels, timestamps |
| Background | `#FFFFFF` | Page background |
| Secondary background | `#F7F8FA` | Cards, sidebars, subtle section separation |
| Borders | `#E6EAF0` | Dividers, input borders, card outlines |
| Wordmark navy | `#0B1F3A` | Logo text color — reuse for high-contrast dark text on light backgrounds where `#161616` feels too flat next to the brand mark |

**Rule of thumb:** the gradient is a signature accent, not a paint bucket.
Use it on the logo, primary action buttons, active tab/nav indicators, and
maybe one hero highlight per screen. Everything else stays neutral
(white / `#F7F8FA` / `#E6EAF0` / grays) so the gradient keeps its impact.

## Typography

**Use the IBM Plex family** (replacing the earlier Alexandria/Tajawal
direction):

- **IBM Plex Sans Arabic** — for all Arabic UI text: headings, body, labels,
  buttons. Covers Arabic + Latin in one consistent family so mixed
  Arabic/English strings (e.g. a guest's English job title) don't clash.
- **IBM Plex Sans** — for any pure-Latin content (code snippets, English
  API/debug text, numeric-heavy dashboards) where you want tighter Latin
  metrics than the Arabic-optimized cut provides.
- **IBM Plex Mono** — for anything code- or ID-like (API keys, UUIDs,
  timestamps in dev/debug views).

Load via Google Fonts or self-hosted `@font-face`:
```
https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap
```

Weight pairing inspired by the logo: use a **light/regular (300–400)** weight
for supporting words and a **bold/semibold (600–700)** weight for the
emphasized word in a heading, mirroring "With **Bader**."

## Layout direction

- **Arabic-first, RTL by default.** Build every layout mirrored
  (`dir="rtl"`), not as an afterthought bolted onto an LTR build. The main
  sidebar sits on the **right**.
- **Minimal, spacious, white.** Generous padding, light borders instead of
  heavy shadows, no dense corporate dashboards. Prefer whitespace over
  dividers where possible.
- **Clean SaaS aesthetic** — rounded corners (8–12px), subtle 1px borders in
  `#E6EAF0`, no gradients on large surfaces (reserve gradients for accents
  per the color rule above), no drop shadows beyond a very soft elevation on
  modals/popovers.

## Quick checklist before shipping any new screen

- [ ] `dir="rtl"` set, sidebar/nav on the right
- [ ] IBM Plex Sans Arabic loaded and applied (not a default system font)
- [ ] Gradient used only as an accent (button, active state, icon) — not a background wash
- [ ] Text colors from the table above — no arbitrary grays
- [ ] Borders at `#E6EAF0`, not a random gray
- [ ] Matches "professional SaaS tool," not "AI-generated demo site"
