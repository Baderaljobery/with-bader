-- ============================================================================
-- With Bader
-- Database Schema - Version 5 / Design Generation
-- PostgreSQL 16+
-- ============================================================================


-- ============================================================================
-- 14. DESIGN DRAFTS
-- ============================================================================
-- One row per AI-generated social-media visual design for a guest. The AI
-- image (Gemini) provides only the visual background/composition; the actual
-- Arabic headline/body/CTA text is rendered by the frontend as an HTML/CSS
-- overlay on top of it (see app/design_generation/). `platform` only
-- describes the intended publishing destination - no publishing integration
-- exists.

CREATE TABLE design_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    guest_id UUID NOT NULL
        REFERENCES guests(id)
        ON DELETE CASCADE,

    -- The saved content draft this design was generated from, if any. Kept
    -- nullable and ON DELETE SET NULL: deleting the source content draft
    -- later should not destroy an already-generated design.
    content_draft_id UUID
        REFERENCES content_drafts(id)
        ON DELETE SET NULL,

    title TEXT,

    platform TEXT NOT NULL
        CHECK (
            platform IN (
                'linkedin',
                'x',
                'instagram',
                'general'
            )
        ),

    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (
            status IN (
                'draft',
                'approved'
            )
        ),

    layout_type TEXT NOT NULL
        CHECK (
            layout_type IN (
                'text_focus',
                'quote_highlight',
                'split_visual',
                'minimal_card'
            )
        ),

    aspect_ratio TEXT NOT NULL
        CHECK (
            aspect_ratio IN (
                '1:1',
                '4:5',
                '16:9',
                '9:16'
            )
        ),

    background_color TEXT NOT NULL,
    accent_color TEXT NOT NULL,

    -- Frontend-rendered overlay text (never baked into the AI image).
    headline TEXT NOT NULL DEFAULT '',
    body_text TEXT NOT NULL DEFAULT '',
    cta_text TEXT,

    -- The exact image-generation prompt sent to Gemini, kept for
    -- regeneration/debugging - never shown to end users as-is.
    prompt TEXT NOT NULL,

    -- Compact record of the generation options used (content_draft_id,
    -- question_ids, length/density, custom_instructions, etc.) for
    -- traceability and to power "regenerate with the same options".
    customizations JSONB NOT NULL DEFAULT '{}'::jsonb,

    ai_provider TEXT,
    ai_model TEXT,

    -- Server-relative URL path to the generated image file on local disk,
    -- e.g. "/media/design-drafts/<uuid>.png" (see
    -- app/design_generation/storage.py). Nullable only because a row is
    -- never created until generation succeeds - kept nullable rather than
    -- NOT NULL purely for forward compatibility.
    image_path TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TRIGGER trg_design_drafts_updated_at
BEFORE UPDATE ON design_drafts
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE INDEX idx_design_drafts_guest_id
ON design_drafts(guest_id);

CREATE INDEX idx_design_drafts_content_draft_id
ON design_drafts(content_draft_id);

CREATE INDEX idx_design_drafts_status
ON design_drafts(status);


-- ============================================================================
-- END OF VERSION 5
-- ============================================================================
