# With Bader — Last Update (2026-08-31)

Summary of everything implemented in today's session, in order. Three phases, all on the FastAPI/SQLAlchemy/PostgreSQL backend.

---

## 1. Guest Research — storage & versioning

**Goal:** store structured research snapshots about a guest, versioned and immutable, before any real research/AI existed yet.

**Database**
- `guest_research` table did **not** exist yet in `database/001_foundation.sql` or the live Postgres container — this was discovered before coding, not assumed.
- Added `database/002_guest_research.sql` (additive migration, nothing existing altered) and applied it to the running `with_bader_postgres` container:
  - `id`, `guest_id` (FK → `guests`, `ON DELETE CASCADE`), `version` (`UNIQUE(guest_id, version)`)
  - `role_title`, `company`
  - JSONB fields: `career_history`, `education`, `achievements`, `projects`, `topics`, `interesting_events`, `potential_interview_angles`, `sources` (all default `[]`)
  - `raw_ai_response` (nullable JSONB, reserved for later)
  - `created_at`

**Backend code**
- `app/models/guest_research.py` — SQLAlchemy model, `Guest.research_versions` relationship added.
- `app/schemas/guest_research.py` — `GuestResearchCreate`, `GuestResearchResponse`, `ResearchSource`. `version` is never client-controlled.
- `app/services/guest_research_service.py` — `create_guest_research` (auto-increments version = `max(version)+1`, never updates old rows), `get_guest_research_history`, `get_latest_guest_research`, `get_guest_research_by_id`.
- `app/api/guest_research.py`:
  - `POST /api/guests/{guest_id}/research` → 201, new version
  - `GET /api/guests/{guest_id}/research` → version history, ascending
  - `GET /api/guests/{guest_id}/research/latest` → 404 if none yet (chosen over 204, for consistency with the rest of the API)
  - `GET /api/guest-research/{research_id}` → single version
  - No PATCH/DELETE — versions are immutable historical snapshots.

**Tested live** against the real database: versioning (1→2→...), full history, latest, byte-for-byte-unchanged old versions, cascade delete on guest removal, 404s on unknown guest/research id, 422 on malformed input, client-supplied `version` ignored.

---

## 2. Guest Research Engine — orchestration infrastructure (still mocked)

**Goal:** build the pipeline architecture connecting Guest → sources → structured research, using swappable abstractions, with mock search/extraction so no real API costs money yet.

**New package `app/research/`**
- `models.py` — internal (non-DB) Pydantic models: `ResearchQuery`, `RawResearchSource`, `NormalizedResearchSource`, `ResearchExtractionResult`.
- `providers/base.py` — `ResearchSearchProvider` ABC (`async search(query, limit)`), `ResearchProviderError`.
- `providers/mock.py` — `MockResearchSearchProvider`: deterministic fake sources (company profile / news / personal site / interview), zero network calls.
- `collectors/guest_link_collector.py` — turns a guest's existing `guest_links` rows into source candidates (label → source type, e.g. "LinkedIn" → `linkedin`). Does **not** fetch link contents.
- `collectors/query_builder.py` — deterministic, rule-based search queries from `guest.name` / `job_title` / `company` (no AI). Dedupes, skips blank fields, configurable max (default 8).
- `normalization/source_normalizer.py` — trims strings, maps `source_type` into a fixed known-set (`linkedin`, `website`, `company_website`, `article`, `interview`, `youtube`, `x`, `news`, `uploaded_document`, `other`), computes a `canonical_url`.
- `normalization/deduplicator.py` — collapses duplicates by canonical URL → URL → title+publisher, keeping the richest record.
- `extraction/base.py` — `ResearchExtractor` ABC (`async extract(guest, sources)`), `ResearchExtractionError`.
- `extraction/mock.py` — `MockResearchExtractor`: only derives from fields the guest already has (`job_title`, `company`); never invents facts about a real person. `career_history`/`education`/`achievements`/`projects` always `[]`.
- `profile_builder.py` — converts extraction result + sources into the existing `GuestResearchCreate` shape.
- `research_engine.py` — `ResearchEngine` orchestrator: guest exists → collect link sources → build queries → run searches concurrently (`asyncio.gather` + semaphore) → normalize → dedupe → extract → build payload → **save via the existing `guest_research_service.create_guest_research`** (no duplicated versioning logic). `get_research_engine()` is the single wiring point for provider/extractor implementations.

**API**
- `app/api/guest_research_engine.py`: `POST /api/guests/{guest_id}/research/run` → runs the full pipeline, saves a new research version, returns `queries_executed`, `total_sources_found`, `total_sources_after_deduplication`, plus the created research.
- `app/core/config.py`: added `research_max_queries` (default 8), `research_results_per_query` (default 5).

**Tests** — 13 new `unittest` tests (query builder, normalizer, deduplicator, and an async engine test using spy wrappers around the mocks) — all passing, no new test framework introduced (project had none).

**Tested live**: full 16-step sequence — two research runs (v1, v2) via `/research/run`, history, latest, unchanged old versions, minimal guest (name-only) still worked with fewer queries, unknown guest → 404, no regressions on any existing endpoint.

---

## 3. Real search provider — Tavily integration (extractor still mock)

**Goal:** replace the mock *search* provider with one real one (Tavily), proving real queries leave the app and real results come back — while keeping the extractor mock (no LLM yet).

**New/changed**
- `app/research/providers/tavily.py` — `TavilyResearchSearchProvider`, async, using `httpx.AsyncClient` (added to `requirements.txt`). Converts Tavily's response into `RawResearchSource` only — no Tavily-specific object ever reaches `ResearchEngine`. Does **not** fetch page contents — only uses the `title`/`url`/`content`(→snippet) Tavily returns directly. LinkedIn results are kept as returned, never scraped.
- `providers/base.py` — added `ResearchProviderConfigurationError`, `ResearchProviderTimeoutError`, and a `provider_name` attribute on the provider interface.
- `normalization/source_normalizer.py` — added `infer_source_type_from_url()` (small fixed domain table: linkedin/youtube/x, plus a coarse news-domain hint list, else `website`).
- `research_engine.py` — added `build_search_provider()` factory (`RESEARCH_SEARCH_PROVIDER=mock|tavily`); partial-query-failure handling (some queries can fail without aborting the run — only a *total* wipeout raises, distinguishing an all-timeout case → 504 from other failures → 502); `ResearchRunResult` now also carries `search_provider` and `queries_failed`.
- `app/core/config.py` — added `tavily_api_key`, `research_search_provider` (default `"mock"`), `research_search_timeout_seconds` (default 15).
- `app/api/guest_research_engine.py` — missing API key fails clearly with a clean `500` (never a silent fallback to mock); timeout → `504`; other provider failures → `502`.
- `.env.example` — documented the three new variables (no real secret committed).

**Tests** — 8 new `test_tavily_provider.py` tests (success mapping, domain-based type inference, empty results, HTTP error, timeout, missing key, missing optional fields, limit respected) — all mocked, zero real network calls in the test suite. Fixed one pre-existing test fixture that needed a `provider_name` attribute after the interface grew. **21/21 tests passing overall.**

**Live integration test** (your `TAVILY_API_KEY` was already in `.env`; tested via a one-off env override, not a permanent default change): guest `Sam Altman / CEO / OpenAI` → real run returned `search_provider: "tavily"`, 8 queries, 0 failed, 40 sources found → 25 after dedup, all real `https://` URLs (Wikipedia, Forbes, Business Insider, LinkedIn, YouTube, X, NYTimes, etc.), and the mock extractor still left `achievements`/`career_history`/`education` empty — no fabricated facts. Also verified: missing-key path → clean 500, no key leaked; mock-provider path still works unchanged and remains the **default** (`RESEARCH_SEARCH_PROVIDER` is not set in your `.env`, so nothing runs against the real API unless you opt in).

---

## Net result

The guest research pipeline now runs end-to-end against a real search API (Tavily) with a mock extraction step, fully swappable via `RESEARCH_SEARCH_PROVIDER`, with no changes to the database schema beyond the one additive `guest_research` table, and no regressions to any previously working endpoint (guests, guest links, questions/versions, assets, notebooks/pages/blocks).

**Still mock / not yet implemented:** real LLM extraction, question generation, transcription, content generation, design, LinkedIn scraping, page-content fetching.

**To turn Tavily on by default:** add `RESEARCH_SEARCH_PROVIDER=tavily` to `backend/.env` (the API key is already there).
