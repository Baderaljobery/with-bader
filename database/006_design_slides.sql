-- ============================================================================
-- With Bader
-- Database Schema - Version 6 / Multi-Slide Design Engine
-- PostgreSQL 16+
-- ============================================================================
--
-- Reworks the single-image Design Engine (version 5) into a user-controlled,
-- template-based, multi-slide system. `design_drafts` becomes the SHARED
-- configuration for a design set (template, slide count, colors, aspect
-- ratio); per-slide content/image state moves to a new `design_slides`
-- table. This is additive to the schema as a whole (no version-5 table is
-- dropped) but does alter `design_drafts` itself, since the single-slide
-- shape it had is being replaced by the shared-config shape - there is no
-- production data depending on the old shape yet.


-- ============================================================================
-- 14. DESIGN DRAFTS (altered)
-- ============================================================================
-- Drop the old single-slide fields - they move to design_slides below.

ALTER TABLE design_drafts DROP CONSTRAINT IF EXISTS design_drafts_layout_type_check;

ALTER TABLE design_drafts
    DROP COLUMN IF EXISTS layout_type,
    DROP COLUMN IF EXISTS headline,
    DROP COLUMN IF EXISTS body_text,
    DROP COLUMN IF EXISTS cta_text,
    DROP COLUMN IF EXISTS prompt,
    DROP COLUMN IF EXISTS image_path;

-- The manually-selected template (frontend/features/design/lib/
-- template-registry.ts) and the manually-selected slide count (1-5). Both
-- are always chosen by the user - never inferred.
ALTER TABLE design_drafts
    ADD COLUMN template_id TEXT NOT NULL DEFAULT 'template-01',
    ADD COLUMN slide_count INTEGER NOT NULL DEFAULT 1
        CHECK (slide_count >= 1 AND slide_count <= 5);

ALTER TABLE design_drafts ALTER COLUMN template_id DROP DEFAULT;
ALTER TABLE design_drafts ALTER COLUMN slide_count DROP DEFAULT;


-- ============================================================================
-- 15. DESIGN SLIDES
-- ============================================================================
-- One row per slide within a design_drafts set. Role/text are produced by
-- DesignContentPlanner (Groq, structured output) and are user-editable
-- before and after image generation; image_path/prompt are filled in only
-- once that specific slide's Gemini (via OpenRouter) call succeeds - a
-- slide can exist with real approved text and no image yet (preview-first
-- flow), and slides are generated/regenerated independently of each other.

CREATE TABLE design_slides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    design_draft_id UUID NOT NULL
        REFERENCES design_drafts(id)
        ON DELETE CASCADE,

    -- 1-based position within the set, stable identity for "regenerate
    -- slide 2" style operations - never reordered automatically.
    slide_index INTEGER NOT NULL
        CHECK (slide_index >= 1 AND slide_index <= 5),

    role TEXT NOT NULL
        CHECK (
            role IN (
                'cover',
                'main_content',
                'continuation',
                'quote',
                'quick_points',
                'closing'
            )
        ),

    -- Frontend-rendered overlay text (never baked into the AI image). For
    -- role='quick_points', body_text holds newline-separated short points
    -- rather than a new column - see app/design_planning/.
    headline TEXT NOT NULL DEFAULT '',
    body_text TEXT NOT NULL DEFAULT '',
    cta_text TEXT,

    -- Null until this slide's image has actually been generated.
    image_path TEXT,

    -- The exact per-slide image-generation prompt sent to Gemini via
    -- OpenRouter, kept for regeneration/debugging - never shown to end
    -- users as-is. Null until first generated.
    prompt TEXT,

    -- Compact record of per-slide generation options/overrides (e.g. a
    -- one-off custom_instructions override used only for this slide's most
    -- recent regenerate).
    customizations JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (design_draft_id, slide_index)
);


CREATE TRIGGER trg_design_slides_updated_at
BEFORE UPDATE ON design_slides
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE INDEX idx_design_slides_design_draft_id
ON design_slides(design_draft_id);


-- ============================================================================
-- END OF VERSION 6
-- ============================================================================
