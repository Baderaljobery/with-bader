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

**Use the Thmanyah type system** (added 2026-09-03, replacing the earlier
IBM Plex Sans Arabic direction, which itself replaced the original
Alexandria/Tajawal pairing). All three families are self-hosted via
`next/font/local` (WOFF2, project-local files under
`frontend/public/fonts/thmanyah/`) — no dependency on a font being
installed on any developer's machine, and no external font request at
runtime. See `frontend/lib/fonts.ts` for the loader definitions.

### Thmanyah Sans — primary application/UI font

The default font for everything: headings, body, labels, buttons, forms,
cards, navigation. Covers Arabic + Latin in one consistent family so mixed
Arabic/English strings (e.g. a guest's English job title) don't clash —
same rationale as the earlier IBM Plex Sans Arabic choice, now with the
brand's own type family.

- CSS variable: `--font-thmanyah-sans` (also aliased as Tailwind's
  canonical `--font-sans`, so the existing `font-sans` utility and
  `--font-heading` — which aliases `--font-sans` — automatically use it;
  no per-component migration needed).
- Files: `frontend/public/fonts/thmanyah/sans/thmanyahsans-*.woff2`.
- Available weights: Light (300), Regular (400), Medium (500), Bold (700),
  Black (900). Weight pairing inspired by the logo still applies: a
  **light/regular** weight for supporting words and a **bold/black** weight
  for the emphasized word in a heading, mirroring "With **Bader**."

### Thmanyah Serif Display — editorial/display headline font

Not part of the default UI. Reserved for large visual headlines: Design
Engine template headlines, editorial poster-style titles, and selected
premium content designs (see `frontend/services/design/`). Do not use it
for ordinary app UI.

- CSS variable: `--font-thmanyah-serif-display`.
- Files: `frontend/public/fonts/thmanyah/serif-display/thmanyahserifdisplay-*.woff2`.
- Available weights: Light (300), Regular (400), Medium (500), Bold (700),
  Black (900).

### Thmanyah Serif Text — editorial reading font

Not the default UI body font. Reserved for longer editorial copy in
selected Design Engine layouts — article-like or storytelling visual
treatments where a text-optimized serif reads better than the UI sans.

- CSS variable: `--font-thmanyah-serif-text`.
- Files: `frontend/public/fonts/thmanyah/serif-text/thmanyahseriftext-*.woff2`.
- Available weights: Light (300), Regular (400), Medium (500), Bold (700),
  Black (900).

### Font licensing

The delivered Thmanyah font package did not include a license/EULA/readme
file of any kind — only the font binaries themselves (OTF + WOFF2 per
weight). Nothing was omitted or discarded; there was simply nothing to
preserve. If a license document becomes available later, it belongs at
`frontend/public/fonts/thmanyah/LICENSE` (or similar) alongside the font
files it covers.

## Layout direction

- **Arabic-first, RTL by default.** Build every layout mirrored
  (`dir="rtl"`), not as an afterthought bolted onto an LTR build. The main
  sidebar sits on the **right**.
- **Premium atmosphere, not flat white-on-gray.** (Revised 2026-09-03 — see
  below.) Generous padding stays, but surfaces now carry real depth: soft
  ambient gradient glows, gently tinted panels, layered shadows. Prefer
  whitespace over dividers where possible.
- **Clean SaaS aesthetic** — rounded corners, now 12–20px (`rounded-xl`
  to `rounded-3xl`) for a softer, calmer feel than the earlier 8–12px.
  Borders stay a subtle 1px in `#E6EAF0`. Shadows are layered/soft, not
  heavy.

## Atmosphere system (added 2026-09-03)

The brand gradient rule ("sparingly, not a paint bucket") still holds for
*solid fills* — buttons, active states, avatars. But the app now also uses
the same teal/blue pair as **soft ambient glow**, at very low opacity
(6–14%), heavily blurred, as a background atmosphere layer:

- `components/shared/ambient-background.tsx` renders 2–3 large blurred
  radial-gradient blobs (teal + blue) fixed behind the content area. Mounted
  once in `AppShell` so every page gets it for free — never re-implement
  per page.
- Surfaces get a very subtle top-to-bottom tint (`--surface-tint`,
  white → `#F7F8FA`) instead of flat white, for a sense of depth without
  a visible gradient edge.
- This is still restrained: glows sit *behind* content at low opacity, never
  compete with text/data for attention, and never appear as a hard-edged
  gradient wash on a large surface (that rule is unchanged).

## Design Engine templates (reworked 2026-09-03: deterministic renderers)

The Design Engine is a **template renderer**, not an AI image generator.
Each of the 4 templates under `frontend/services/design/templates/<id>/`
(`config.ts` + `Renderer.tsx`) is real frontend code that reproduces its
original reference image's composition/palette/typography by hand — fixed
background/text colors, fixed Thmanyah font, fixed spacing, one
`Renderer` component per template with a distinct layout per slide role
(cover/main_content/continuation/quote/quick_points/closing). The same
template + same text always renders the same pixels (no AI in this path).

- `frontend/services/design/templates/registry.ts` is the single
  authoritative template list (picker metadata + the real `Renderer` +
  `fontFamily` + `supportedAspectRatios` + per-role `contentLimits`) — the
  old split between a picker-only registry and a separate generation-time
  definition is gone.
- The original reference images (`frontend/public/design-references/<id>/`)
  are now **implementation blueprints only**: still shown in the template
  picker so the user knows what they're choosing, but never sent to any
  model at runtime.
- Type scale uses CSS container-query units (`cqw`) inside each
  `TemplateFrame` (`templates/shared.tsx`), so one Renderer produces an
  identical, proportionally-scaled result as a thumbnail, the live editor
  preview, or a full-resolution PNG export.
- AI (Groq, via `backend/app/design_planning/`) only ever writes the
  slide *text*, constrained by that template/role's `contentLimits` (also
  mirrored backend-side in `app/design_planning/content_limits.py` so the
  planner's prompt gets the real per-slide character budget). The original
  Design Engine v1's OpenRouter/Gemini full-slide image generator has been
  removed (2026-09-06 cleanup) — it was already dormant/unreachable from
  the normal template flow. `backend/app/design_generation/storage.py`
  still exists in a trimmed form purely to serve/clean up any pre-existing
  `design_slides.image_path` from before this rework; no code writes a new
  one anymore.
- There is no automatic/AI template, slide-count, or role selection
  anywhere in this flow — all three are always an explicit user choice.

## Statistics card tones (added 2026-09-05)

The Statistics dashboard (`frontend/services/statistics/`) introduces a
small, reusable 4-tone card system for KPI cards - all four derived only
from colors already in the palette table above, never a new hue:

- `navy` — solid `#0B1F3A` (the wordmark navy), white text, teal accent.
  Reserved for exactly one "hero" card per screen (the single most
  important number) - do not use it for more than one card at a time, or
  it stops reading as an accent.
- `teal` — a light tint of the gradient's teal end (`#EAFBFA` bg, `#0F766E`
  text) for one KPI group.
- `blue` — a light tint of the gradient's blue end (`#EAF4FE` bg, `#155E9E`
  text) for another KPI group.
- `neutral` — the standard `#F7F8FA` secondary background, for anything
  that shouldn't visually compete with the tinted cards.

See `frontend/services/statistics/lib/theme.ts` for the exact values. Use
this same 4-tone set (not new colors) if another feature ever needs
several coordinated "stat card" treatments on one screen.

## Quick checklist before shipping any new screen

- [ ] `dir="rtl"` set, sidebar/nav on the right
- [ ] Thmanyah Sans loaded and applied (not a default system font)
- [ ] Gradient used as a solid fill only as an accent (button, active state,
      icon); ambient glow use is fine at low opacity per the atmosphere
      system above — neither should ever read as a background wash
- [ ] Text colors from the table above — no arbitrary grays
- [ ] Borders at `#E6EAF0`, not a random gray
- [ ] Matches "premium SaaS product," not "AI-generated demo site"
