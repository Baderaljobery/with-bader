-- ============================================================================
-- With Bader
-- Database Schema - Version 2 / Guest Research
-- PostgreSQL 16+
-- ============================================================================


-- ============================================================================
-- 10. GUEST RESEARCH
-- ============================================================================

CREATE TABLE guest_research (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    guest_id UUID NOT NULL
        REFERENCES guests(id)
        ON DELETE CASCADE,

    version INTEGER NOT NULL
        CHECK (version > 0),

    role_title TEXT,

    company TEXT,

    career_history JSONB NOT NULL DEFAULT '[]'::jsonb,

    education JSONB NOT NULL DEFAULT '[]'::jsonb,

    achievements JSONB NOT NULL DEFAULT '[]'::jsonb,

    projects JSONB NOT NULL DEFAULT '[]'::jsonb,

    topics JSONB NOT NULL DEFAULT '[]'::jsonb,

    interesting_events JSONB NOT NULL DEFAULT '[]'::jsonb,

    potential_interview_angles JSONB NOT NULL DEFAULT '[]'::jsonb,

    sources JSONB NOT NULL DEFAULT '[]'::jsonb,

    raw_ai_response JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(guest_id, version)
);


CREATE INDEX idx_guest_research_guest_id
ON guest_research(guest_id);

CREATE INDEX idx_guest_research_guest_version
ON guest_research(guest_id, version);


-- ============================================================================
-- END OF VERSION 2
-- ============================================================================
