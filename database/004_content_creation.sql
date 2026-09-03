-- ============================================================================
-- With Bader
-- Database Schema - Version 4 / Content Creation
-- PostgreSQL 16+
-- ============================================================================


-- ============================================================================
-- 13. CONTENT DRAFTS
-- ============================================================================
-- One row per generated-or-manual piece of social content for a guest.
-- `platform` only describes the intended publishing destination - no
-- publishing integration exists yet (see app/content/generation/).

CREATE TABLE content_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    guest_id UUID NOT NULL
        REFERENCES guests(id)
        ON DELETE CASCADE,

    platform TEXT NOT NULL
        CHECK (
            platform IN (
                'linkedin',
                'x',
                'instagram',
                'general'
            )
        ),

    length TEXT NOT NULL
        CHECK (
            length IN (
                'short',
                'medium',
                'detailed'
            )
        ),

    title TEXT,

    content TEXT NOT NULL,

    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (
            status IN (
                'draft',
                'approved'
            )
        ),

    -- Compact, machine-readable record of which context categories informed
    -- this draft (e.g. ["answers", "notebook", "research"]) - shown to the
    -- user as subtle source transparency. Never the raw prompt or model
    -- response.
    source_context JSONB NOT NULL DEFAULT '[]'::jsonb,

    ai_provider TEXT,
    ai_model TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TRIGGER trg_content_drafts_updated_at
BEFORE UPDATE ON content_drafts
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE INDEX idx_content_drafts_guest_id
ON content_drafts(guest_id);

CREATE INDEX idx_content_drafts_status
ON content_drafts(status);


-- ============================================================================
-- END OF VERSION 4
-- ============================================================================
