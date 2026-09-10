# With Bader — Last Update (2026-09-10)

Rewritten against the actual `git diff`, not just conversation memory — every item below is backed by a real diff hunk read from the working tree. Six pieces of work, in dependency order: brand/loading system, bilingual guest identity, a substantially rebuilt research pipeline (Phases 8–17), a substantially rebuilt question-generation pipeline, the Trusted Links simplification, and the guest-links infrastructure that backs the last two. See `last-update-2026-09-03.md` for the prior session.

---

## 1. Brand system — animated logo, background pattern, unified loading

- `frontend/components/brand/animated-logo.tsx` (new) — persistent/loopable version of the Claude Design canvas export in `Logo animation sequence/`; geometry/gradient/choreography copied verbatim, only the idle "Hold" beat shortened (2.4s → 0.6s) for a looping UI element.
- `frontend/components/brand/background-pattern.tsx` (new) — static Server Component, two brand-gradient line clusters, removed from a11y/pointer trees.
- `frontend/components/brand/brand-loader.tsx` (new) — shared loading indicator driven by a real `loading` boolean (never invents its own timing), `"fullscreen"` vs `"section"` variants with a short fade-out.
- Wired into `frontend/app/loading.tsx`, `frontend/app/(app)/loading.tsx`, `app-shell.tsx`, `auth-shell.tsx`, `ambient-background.tsx`, and the Content/Design/Interview/Transcription/Research loading states.

---

## 2. Bilingual guest identity — name only

- `backend/alembic/versions/0003_bilingual_guest_identity.py` — additive migration: `guests.name_ar`/`name_en` (nullable, no backfill) + `guest_research.public_appearances`/`identity_confidence`.
- `backend/app/models/guest.py` — `name_ar`/`name_en` columns, plus a `display_name` property (`name_ar or name`, Arabic-first, falls back only for legacy rows).
- `backend/app/schemas/guest.py` — `GuestCreate` now requires both `name_ar` and `name_en` (whitespace-only rejected via validator); `name` becomes optional and is auto-set to `name_ar`. `GuestUpdate` allows partial edits. `GuestResponse` now returns `display_name`.
- `backend/app/services/guest_service.py` — new `has_complete_bilingual_identity()` and `IncompleteBilingualIdentityError`: editing a legacy guest into having *one* of `name_ar`/`name_en` without the other is rejected (rolled back) — half a bilingual identity is treated as worse than none, since the research/question pipelines below depend on it.
- `job_title`/`company`/`biography` deliberately stay single-value (an earlier draft that also bilingual-ized these was corrected before merge).

---

## 3. Research pipeline — rebuilt across Phases 8–17

This is the largest single piece of backend work today (`research_engine.py`, `query_builder.py`, `source_selector.py`, `identity_resolution.py`, `research_planner.py`, `link_content_fetcher.py`, plus schema/model/config changes): ~1,400 insertions across 22 backend files.

- **Phase 8 — hybrid query planner** (`research_planner.py`, new): the existing deterministic `query_builder.py` queries always run; on top of them, a bounded Groq-assisted expansion step may add *more* queries, but only from the fixed `RESEARCH_OBJECTIVES` set (`identity`, `career`, `education`, `achievements`, `projects`, `public_appearances`, `recent`) — every AI-suggested query is validated (non-blank, non-duplicate, has a guest-identity anchor, on-objective) before use. If Groq is unavailable/misconfigured/fails, this degrades silently to "no additional queries" — the deterministic half never depends on it. Toggle: `research_planner_enabled`.
- **Phase 9 — bilingual queries** (`query_builder.py`): queries are now built from `name_ar`/`name_en` directly instead of bolting English suffixes ("interview", "biography") onto a possibly-Arabic name — an Arabic guest now gets Arabic-phrased queries (gender-neutral noun phrasing, e.g. "المسيرة المهنية" not "مسيرته") and an English guest gets English ones, each concept (career/achievements/projects/public_appearances/recent) queried once per available language.
- **Phase 10 — adaptive query budget** (`query_builder.estimate_query_budget`): the flat 8-query cap is gone. Budget now scales with a "richness" score (bilingual name present, company, job_title, biography, up to 3 trusted links) into three tiers — thin profile 6–8, normal 8–12, high-profile 12–16 — always clamped to `[research_min_queries=6, research_max_queries=16]` (raised from the old flat 8).
- **Phase 11 — identity resolution** (`identity_resolution.py`, new): deterministic, no-AI scoring of how likely a source is actually about *this* guest vs. a same-named stranger. `source_selector.py` now drops any source below `research_identity_min_relevance` (0.2) *before* ranking/extraction — if nothing clears the bar, extraction runs on nothing rather than on likely-wrong-person sources. The run's aggregate identity confidence is stored on `guest_research.identity_confidence` and surfaced via `IdentityConfirmationBanner` (frontend) whenever it falls below `research_identity_confirmation_threshold` (0.35). A trusted `guest_link` source is treated as high-confidence by construction (score 3/3 tier) since the user vouched for it directly.
- **Phase 12 — trusted-link content fetching** (`link_content_fetcher.py`, new): `guest_link_collector.py` now fetches a bounded amount of real visible text from each trusted link (previously only the bare URL/label was used, which ranked *worse* than an ordinary search result). Public http/https only, no localhost/private-network targets, ≤3 redirects, 8s timeout, 1.5MB size cap, 4000-char text cap, content-type validated, no JS execution. Auth-walled platforms (LinkedIn/YouTube/X/Facebook/Instagram) are deliberately skipped rather than faked — the link still counts as high-confidence identity evidence even without body text. Toggle: `research_link_fetch_enabled`.
- **Phase 14 — quality-based fallback backfill** (`research_engine._needs_quality_fallback`): distinct from the existing exception-triggered per-query fallback. If the primary provider's aggregate results look weak (too few sources, or too little domain diversity — `research_quality_fallback_min_sources`/`_min_domains`), the engine issues a small, bounded (`research_quality_fallback_max_queries=4`) supplementary batch of the highest-priority queries directly to the fallback provider.
- **Phase 15/16 — identity-led, tiered source ranking** (`source_selector.py`): ranking key is now `(identity_relevance, has_content, has_snippet, tier, provider_score, has_title)` — identity relevance leads, so a domain that merely "looks authoritative" (Wikipedia, a news outlet) can no longer outrank a well-matched source about the actual guest. Domain tiers: A = `.gov`/`.edu`, B = named business/news outlets (Reuters, Bloomberg, FT, WSJ, Forbes, Al Jazeera, BBC, CNBC, Arabian Business, The National), C = Wikipedia/Britannica/LinkedIn/Crunchbase; a trusted guest link is always tier 3 (top).
- **New `public_appearances` research field**: prior public activity (interviews, podcasts, panels, keynotes, articles quoting the guest) — explicitly scoped to *before* this run, never the upcoming With Bader interview — extracted end-to-end (`groq_models.PublicAppearanceItem` → `groq_postprocess` → `profile_builder` → `guest_research` model/schema → `research_context.py` → frontend `public-appearances-section.tsx`).
- **`research_context.py` rewritten**: candidates are now built round-robin across all fact types (so one long field can't crowd out the others) and then clustered — near-duplicate facts/angles describing the "same underlying story" are merged (using shared source URLs + token-overlap heuristics) instead of appearing as separate context items, while same-type career/project/education/topic items are deliberately *never* auto-merged so distinct roles survive.
- **`extraction/prompts.py`**: guest metadata block now includes both `name_ar`/`name_en` and biography (for identity matching, per rule 10/15), and `potential_interview_angles` now has an explicit rule that an angle must be an *observation* ("their move from Company A to Company B may be worth exploring"), never a literal question — that's the question-generation pipeline's job, not research's.

---

## 4. Question generation — rebuilt into a candidate-pool + dedup pipeline

You called this out specifically — it's a real rebuild (~1,440 insertions across 15 backend files + matching frontend wiring), not a tweak.

**Old model:** ask the generator for exactly N questions once, save whatever came back with only `text`/`topic`/`source`/`status`/`position` persisted.

**New model** (`questions/generation/engine.py`, `deduplication.py` + `similarity.py` new, `services/question_generation_service.py`):
- **Over-generate, then filter, then top up.** The engine requests a candidate pool larger than what's needed (`requested_count × question_generation_candidate_multiplier`, capped at `question_generation_max_candidates=30`), filters out duplicates, and — if that leaves fewer than requested — runs up to `question_generation_max_refill_attempts` (default 1) additional bounded generation rounds explicitly avoiding everything seen so far, before selecting the final diverse set.
- **Three-layer duplicate filtering** (`deduplication.filter_unique_candidates`), checked against both the guest's saved questions (up to `question_generation_max_existing_questions=500`) and the rest of the current batch:
  1. **Exact** — Arabic/Latin-normalized text match (diacritics/alef-forms/tatweel/punctuation stripped, via `similarity.normalize_question_text`).
  2. **Lexical/intent** — Jaccard + containment token similarity (`question_generation_lexical_duplicate_threshold=0.88`) on question text, and separately on each candidate's new `intent_summary` field (`question_generation_intent_duplicate_threshold=0.82`) combined with topic match.
  3. **Semantic (Groq-judged)** — only for *plausible* overlaps that survive layers 1–2 (score ≥ `question_generation_semantic_candidate_threshold=0.12`), capped at `question_generation_max_semantic_pairs=80` pairs, round-robined per candidate so one heavily-covered topic can't consume the whole budget, sent to Groq in **one batched call** (`GroqQuestionGenerator.classify_duplicate_pairs`, structured-output `DUPLICATE`/`SAME_TOPIC_DIFFERENT_ANGLE`/`DIFFERENT`). If Groq is unavailable, this layer degrades gracefully — generation still works using layers 1–2 alone.
- **Diverse final selection** (`deduplication.select_diverse_questions`) — stable round-robin by topic/category so the final N aren't all from the richest single research bucket.
- **New provenance persisted with every question** (previously discarded after generation): `Question` gained `category`, `priority`, `intent_summary`, `research_id`/`research_version`/`research_item_ids`, `source_urls`, `follow_up_questions`, `generation_reason`, `generation_run_id`, `generation_candidate_id`, `ai_normalized_text_hash` (migration `0004_question_generation_dedup.py`).
- **Save-time idempotency and race safety** (`question_generation_service.save_generated_questions`): re-checks exact/semantic duplicates against the guest's *current* saved set at save time (not just generation time), locks the guest row (`SELECT ... FOR UPDATE`), and two new **partial unique DB indexes** (`uq_questions_guest_ai_text_hash`, `uq_questions_generation_candidate_id`) catch any remaining race under concurrent saves — caught via `IntegrityError` inside a nested transaction and reported back as `concurrent_duplicate` rather than crashing the request. Each skipped question now comes back to the frontend with a typed reason (`already_saved` / `exact_duplicate` / `semantic_duplicate` / `concurrent_duplicate`) instead of silently vanishing.
- **Research-version consistency guard**: saving now validates the referenced `research_id` actually belongs to the guest and (if provided) matches the research version the questions were generated against — mismatches raise a `409` instead of silently attaching a question to the wrong research snapshot.
- **API contract** (`api/question_generation.py`, `schemas/question_generation.py`): `POST .../questions/generate` now returns `generation_run_id`, `candidate_count`, `duplicates_filtered_count`, `refill_attempts` alongside the questions; `POST .../questions/generated/save` now takes `{generation_run_id, research_id, research_version, questions}` and returns `{saved_count, skipped_count, questions, skipped}`.
- **Frontend** (`generation-preview-sheet.tsx`, `use-save-generated-questions.ts`, `questions-api.ts`, `types/question.ts`): save call now round-trips the full generation-run context; the preview banner shows "N of M shown after removing duplicates/similar questions" when the pool was filtered, and the save toast distinguishes "saved N" vs "saved N, skipped M duplicates" vs "nothing new to save."

---

## 5. Trusted Links — remove manual type picker, infer from URL

- **New `frontend/services/guests/lib/infer-link-label.ts`** — maps hostname → canonical label: `linkedin.com`→LinkedIn, `youtube.com`/`youtu.be`→YouTube, `x.com`/`twitter.com`→X (Twitter), `instagram.com`→Instagram, `facebook.com`→Facebook, else→Website.
- `guest_link_collector.py`'s `_LABEL_KEYWORDS` extended with `instagram`/`facebook` (previously fell through to generic `"other"`).
- `trusted-links-field.tsx` rewritten: dropdown removed entirely — URL input + delete button per row, "Add another link" unchanged.
- `guest-form-dialog.tsx`: label is now always computed via `inferLinkLabel(url)`. New links → always freshly inferred. Existing links → only re-inferred/PATCHed if the user actually edited that link's URL this session; an untouched link (including one with an old manually-picked label like "Podcast") keeps its saved label exactly as-is.
- `guest-schema.ts`: `trustedLinkSchema.label` no longer user-validated.
- Verified: reconcile-logic trace confirms untouched links produce zero API calls; backend keyword matcher tested against all 6 canonical labels; lint/typecheck/build clean.

---

## 6. Supporting guest-links infrastructure

New dedicated modules backing items 3 and 5: `frontend/services/guests/api/guest-links-api.ts`, `hooks/use-guest-links.ts`, `hooks/use-guest-link-mutations.ts`, `types/guest-link.ts`.

---

## Net result

The research pipeline no longer trusts a flat query budget, an English-only query set, or "looks authoritative" domain ranking — it adapts to guest richness, searches bilingually, actively screens out same-named strangers, reads real text from trusted links, and backfills weak result sets. The question-generation pipeline no longer asks for exactly N and saves whatever comes back — it over-generates, filters duplicates through three escalating layers (exact → lexical/intent → Groq-judged semantic), tops up on deficit, and persists full provenance with database-level race protection against double-saving. Guest identity bilinguality is correctly scoped to the name only. Adding a trusted link is a single URL field with type inferred automatically. One consistent brand loading/visual system replaces the old ad-hoc spinners.

**Still not implemented (out of scope today):** social publishing, OAuth, freeform canvas, template marketplace, automatic Design template/slide-count/role selection, video/animation, scheduling, Calendar, Statistics, Settings functionality.
