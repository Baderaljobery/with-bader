# With Bader — Last Update (2026-09-02)

Summary of everything implemented in today's session, in order. Three frontend features plus one small backend observability addition, plus a runtime bug found and fixed in the last of the three. See `last-update-2026-09-01.md` for the prior session's frontend-foundation and RTL-redesign work.

---

## 1. Guest Interview matcher observability (backend)

**Goal:** expose which AI provider/model actually processed a given interview-matching request, without changing any matching, persistence, or STT behavior.

- `GuestInterviewMatchResponse` (`backend/app/schemas/guest_interview.py`) gained `matcher_provider: str` and `matcher_model: str | None`.
- `InterviewIntelligenceService` (`backend/app/interview_intelligence/service.py`) gained two read-only properties, `matcher_provider`/`matcher_model`, sourced directly from the concrete matcher instance in use (`self._matcher.provider_name`/`.model_name`) — never inferred from `INTERVIEW_MATCHER_PROVIDER` env var directly, so it always reflects what actually ran.
- Both `POST /transcribe-interview` and `POST /match-answers` in `backend/app/api/guest_interview.py` now populate the new fields.
- `MockQuestionAnswerMatcher`/`GroqQuestionAnswerMatcher` already exposed `provider_name`/`model_name` correctly — no changes needed there.
- Added 6 new backend tests (mock/groq metadata on both endpoints, plus an explicit "never leaks API key or raw response" test). Full suite: **257/257 passing**.
- No database, matching-logic, or persistence changes.

---

## 2. General Text Extract frontend

**Goal:** wire the standalone `/text-extract` utility page to the real `POST /api/text-extract/audio` endpoint — upload an audio file, get back plain text, nothing persisted.

- New `frontend/features/text-extract/` (api, hooks, types, lib, components) following the same conventions as the earlier Interview feature — reused the existing FormData-capable `apiClient`, no second HTTP client.
- Upload card: drag-and-drop + click-to-choose, client-side extension/size validation (mirrors the backend's `.mp3/.wav/.flac/.ogg/.m4a`, 25MB limit) — backend stays the source of truth.
- Result card: large readable transcript, copy-to-clipboard, provider/model/language/duration shown as small muted metadata (never prominent), "رفع ملف آخر" resets cleanly.
- Full Arabic error-code mapping (413/415/422/500/502/504) — never surfaces raw backend/provider errors.
- Audio is never persisted client-side: the `File` object is dropped from state immediately after the request settles; verified live that `localStorage`/`sessionStorage`/IndexedDB stay empty after a real transcription.
- **Live-tested against the real backend + Cohere**: a real Arabic interview clip transcribed correctly end-to-end, copy/clipboard verified, unsupported-format and oversized-file client-side rejections verified, empty-file backend 422 verified with the correct Arabic message.
- `npm run lint` / `npm run typecheck`: clean.

---

## 3. Notebook frontend — the big one

**Goal:** a real, flexible, block-based notebook workspace per guest (Notion-ish, not a form) — notebooks → pages → blocks, wired to the existing backend (`/api/guests/{id}/notebooks`, `/api/notebooks/{id}/pages`, `/api/notebook-pages/{id}/blocks`, `/api/blocks/{id}`).

**Scope:** replaced the `/guests/[guestId]/notebook` placeholder with `frontend/features/notebook/` (types, api, 9 hooks, 5 lib files, 20 components). Added `@dnd-kit/{core,sortable,utilities}` as the only new dependency.

**Block types implemented (14, all real backend types with a genuine editing UI):** paragraph, heading, question, answer, quote, highlight, callout, bullet_list, numbered_list, checklist, divider, guest_info, content_idea, personal_note.

**Deliberately deferred:** `image` and `table` — both exist in the backend's type enum but have no upload pipeline or structured table editor behind them anywhere in the product; shipping them would mean a block users could create but never fill in, so they're excluded from the insertion menu and documented instead of faked.

**Key design decisions**
- No Tiptap — every block's content is plain text (`{ text: string }` for text-like blocks, `{ items: [...] }` for lists/checklists), so a rich-text editor library would add real complexity for zero requested benefit. Text blocks reuse the existing `Textarea` component's built-in `field-sizing-content` auto-grow.
- Fractional block positioning (backend supports float positions) — appends use `+1000` gaps, inserts/reorders use neighbor midpoints, never renumber the whole page.
- `dnd-kit` for drag-and-drop reorder (pointer + keyboard sensors), optimistic reorder in the TanStack Query cache with rollback on failure.
- Debounced autosave (600ms, flush-on-blur) via a `useLocalDraft` hook that protects in-progress typing from being clobbered by background refetches — the local value is never overwritten by an incoming server value while an edit is pending.
- Selection (`?notebook=<id>&page=<id>`) lives in the URL, so refresh/deep-links land back on the same page.
- Question blocks can optionally link to a real saved Guest Question (`linked_question_id`); unlink degrades cleanly; a deleted linked question is already nulled server-side (`ON DELETE SET NULL`).
- Mobile: notebook/page nav becomes a `Sheet` drawer instead of squeezing a two-column layout.
- No AI features, no auto-linking of interview answers into blocks, no Content Creation integration — kept strictly to the editor itself, per scope.

**Bug found and fixed during delete-flow testing:** `useDeleteNotebook`/`useDeletePage`'s `onSuccess` originally called `queryClient.removeQueries()` on the child cache (pages/blocks) synchronously — this evicted an *actively observed* query, causing TanStack Query to immediately refetch the just-deleted resource and 404 in the console. Fixed by simply not evicting (the stale entry gets garbage-collected later; nothing reads it again once selection moves on). Verified via live network logging for both "delete a background notebook" and "delete the currently-open page" — zero console errors afterward.

**Live-tested end-to-end** against a real guest (Sam Altman, 4 saved questions): create/rename/delete notebook and page, create/edit/convert/reorder/delete blocks, question linking + unlinking, all verified to **actually persist** via direct backend curl checks (not just the UI) — correct content, types, fractional positions, and FK links. Responsive-tested at 1440/1024/390px with zero horizontal overflow. `npm run lint` / `npm run typecheck`: clean.

---

## 4. Notebook infinite re-render bug (found after initial delivery)

**Report:** clicking a block's three-dot menu crashed React with "Too many re-renders," overlay pointing at `ListBlock`.

**Root cause:** `ListBlock`/`ChecklistBlock` passed `useLocalDraft` a **freshly-allocated array every render** (`getBlockItems(block.content).filter(...)` plus a `[""]` fallback), while `useLocalDraft`'s render-time sync guard compares by reference (`!==`) — correct for the primitive strings used everywhere else, but always "different" for a new array literal. Once *any* second render of that component happened for *any* reason, the guard fired unconditionally forever. Reproduced directly: even just **loading a page containing a bullet_list block crashed immediately**, no click required — the menu click in the original report was simply one of many ways to trigger a second render (it blurs the focused input, flushing an autosave that legitimately updates `block.content`'s reference).

**Fix:** wrapped the derived array in `useMemo(() => ..., [block.content])` in both `list-block.tsx` and `checklist-block.tsx`, so the reference is only replaced when `block.content` itself actually changes. Two-line-shaped fix, no changes needed to `useLocalDraft`, `block-editor.tsx`, or any other file — the primitive-valued blocks (paragraph, heading, question, etc.) were never affected since JS strings compare by value.

**Regression-tested** after the fix: three-dot menu opens cleanly on all 7 block types present on one page, text-like↔text-like conversion preserves text (heading→paragraph), cross-family conversion (paragraph→bullet_list) still correctly resets content by design, exactly 1 autosave PATCH per debounced edit, refresh-persistence, keyboard drag reorder, and question link/unlink — all with **zero console errors and zero network errors**. `npm run lint` / `npm run typecheck`: clean. Backend suite re-confirmed at 257/257 (untouched).

---

## Net result

Four more real, working pieces wired to the live backend: interview-matcher observability metadata, the General Text Extract utility, and the full Notebook workspace (block-based, drag-reorderable, autosaved, question-linkable) — plus one genuine runtime bug in the Notebook found and fixed with a verified root cause, not a guess. Every claim above (persistence, autosave debounce, error mapping, no-console-errors) was checked against the real running backend and a real browser, not assumed.

**Still not implemented (by design, out of scope today):** Notebook AI features, Content Creation, Design Engine, image/table blocks, Calendar, Statistics, Settings functionality.
