# With Bader — Last Update (2026-09-01)

Summary of everything implemented in today's session, in order. Two phases, both on the **frontend** (new — this is the first frontend work in the project), plus one backend touch (CORS) needed to connect them. See `last-update.md` for the prior session's backend-only work.

---

## 1. Frontend foundation

**Goal:** stand up a real, working Next.js frontend connected to the existing FastAPI backend — App Shell, routing, API layer, and a fully functional Guest CRUD flow. No Research/Questions/Interview UI yet (out of scope for this pass).

**Stack** (`frontend/`): Next.js 16 (App Router, Turbopack) + React 19 + TypeScript, Tailwind CSS v4, shadcn/ui (this shadcn generation runs on **Base UI**, not Radix, under the hood), TanStack Query, React Hook Form + Zod, lucide-react. No Redux, no CRA, no Pages Router.

**Structure**
- `app/` — routes; `components/ui/` — shadcn primitives; `components/app-shell/` — sidebar/topbar/nav; `components/shared/` — PageHeader/EmptyState/ErrorState/PlaceholderPage; `features/guests/` — api/hooks/schemas/types/components for the one fully-implemented feature; `lib/api/` — typed fetch client + `ApiError` normalizing FastAPI's two error shapes; `providers/query-provider.tsx`.

**App Shell**
- Sidebar fixed on the **physical right**, regardless of text direction: the shell's outer row is pinned `dir="ltr"` so the sidebar (last flex child) always lands on the right, while the inner content wrapper is `dir="rtl"` for correct Arabic text — a deliberate structural choice, not an accident.
- Desktop: fixed `w-64` sidebar. Mobile (`<md`): hamburger-triggered `Sheet` drawer sliding from the right, same nav component reused.
- Routes: `/`, `/text-extract`, `/calendar`, `/statistics`, `/settings` (all placeholders except Home), `/guests/[guestId]` + 6 nested placeholder tabs (`research`, `questions`, `interview`, `notebook`, `content`, `design`).

**Guest CRUD** (the one real feature)
- Home page: real guest list from `GET /api/guests`, skeleton/error/empty states, Add Guest dialog.
- `GuestFormDialog` (React Hook Form + Zod) handles both add and edit; only `name`/`job_title`/`company`/`biography` exposed (the rest of the backend's `Guest` schema — `slug`, `personal_notes`, `research_summary`, statuses — is workspace-managed, not part of this quick form).
- Delete via `AlertDialog` confirmation.
- Guest workspace: fetches the real guest, shows a header + tabs, 404 state for a deleted/bad guest id, Overview tab shows real fields only (no fabricated research/interview/question-count data).
- TanStack Query owns all server state — no manual `useEffect`/`useState` fetch loops.

**Backend change** — added `CORSMiddleware` to `backend/app/main.py`, allowing exactly `http://localhost:3000` and `http://127.0.0.1:3000`. The only backend file touched this session.

**Verified**: `npm run lint` and `npm run typecheck` clean; live in a real headless-Edge browser (via Playwright, since no browser tooling is preinstalled here) against the real backend — add/edit/delete guest all round-tripped through the real API, tab navigation and direct nested-route loads (refresh simulation) all worked, zero console errors.

---

## 2. Arabic-first / RTL design refinement

**Goal:** restyle the working frontend into a polished Arabic SaaS look, using a real logo and concept references the user provided mid-session — without touching the CRUD logic, API layer, or routing underneath.

**Fonts** — Alexandria for headings/titles (`--font-heading`, feeds shadcn's own `CardTitle`/`DialogTitle`/etc. automatically), Tajawal stays for body text. Both via `next/font/google`.

**Language/direction** — every visible string translated to Arabic (nav, forms, dialogs, toasts, empty/error states, placeholders); `lang="ar" dir="rtl"` stays the default; architecture kept ready for a future English toggle (see the shell's ltr/rtl split above).

**Routing restructure** — moved every existing route into an `app/(app)/` route group (URLs unchanged) with its own shell-wrapping layout, and added `/login` as a sibling with **no** sidebar — needed so the new login page could render standalone.

**Real logo integration** — the user's uploaded reference (`Gemini_Generated_Image_without backgraound.jpg`) turned out to be a JPEG with the transparency-editor's checkerboard baked in as real pixels. Wrote a small Python/Pillow cleanup pass: classified pixels by color "spread" to separate the neutral checker background from the saturated teal/blue/navy logo, built a hard alpha mask, despeckled it, then eroded it slightly to remove a checker-tinted fringe that survived the first pass. Produced two clean assets in `frontend/public/`: `logo-icon.png` (mark only) and `logo-full.png` (full "With Bader" lockup), wired through a new `components/brand/logo.tsx` using `next/image`. The original JPG was removed after extraction (not usable as-is, content preserved in the PNGs).

**Pages restyled** — Home (Arabic welcome header, working client-side guest search, dashed "add guest" card), Guest Workspace (back link, Arabic tabs, Overview rebuilt as real-data info chips instead of a plain list), all placeholder pages, and a new static Login page (centered card, real logo, icon-prefixed inputs, gradient CTA — submitting shows an honest "not enabled yet" toast rather than faking a login, since there's no real auth backend).

**Shared component polish** — `Card` switched from a black-tinted ring to a literal `#E6EAF0` border + soft shadow; the brand gradient now flows through one `--gradient-primary` CSS var everywhere (button, active nav, avatars, hover accents) instead of drifting ad hoc Tailwind gradients; added the `Checkbox` component (needed for login, wasn't installed before).

**Bugs found and fixed**
- RTL bidi artifact: plain text inside the `dir="rtl"` shell had trailing punctuation visually shoved to the front (e.g. a period jumping in front of a sentence). Fixed with a scoped `unicode-bidi: plaintext` base rule.
- Date formatting used the browser's locale, which under Arabic locales rendered Arabic-Indic digits colliding with the surrounding text. Fixed by pinning `toLocaleDateString("en-GB", …)`.
- The destructive "Delete guest" button rendered with a gradient background (from `Button`'s default variant) instead of the destructive style, because a `className` override only touched `background-color`, not the gradient's `background-image`. Fixed by passing `variant="destructive"` instead.
- Two Base UI API mismatches from Radix muscle memory (`SheetTrigger`/`DialogTrigger`/`SheetTitle` needed the `render` prop, not `asChild`) — caught by `tsc` before first run.

**Verified**: `npm run lint` and `npm run typecheck` clean after every round of changes; re-verified live in the browser (Home, Login, Guest Workspace + tabs, search filtering, add/edit/delete, mobile drawer, the real logo in every context) with zero console errors.

---

## Net result

The frontend now has a real, working, Arabic-first RTL shell wired to the live FastAPI backend: Guest CRUD is fully functional end-to-end, the app shell/sidebar/login page use the actual With Bader brand mark, and every other product area (Research, Questions, Interview, Notebook, Content, Design, Text Extract, Calendar, Statistics, Settings) is a polished, honest placeholder — no fake data, no faked functionality anywhere.

**Still not implemented (by design, out of scope today):** Research/Questions/Interview UI integration, Notebook, Content Creation, Design Engine, real authentication, Text Extract's actual STT integration.

**Known but untouched:** 7 leftover test guests from earlier backend-testing sessions still sit in the database (`Sam Altman` ×2, `Grace Hopper` ×2, `Guest B`, `Bader Alharbi`, `Temp Guest For Key Test`) — left alone since deleting data wasn't asked for; say the word if you want them cleared.
