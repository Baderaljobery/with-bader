-- ============================================================================
-- With Bader
-- Database Schema - Version 3 / Guest Transcripts & Question Answers
-- PostgreSQL 16+
-- ============================================================================


-- ============================================================================
-- 11. GUEST TRANSCRIPTS
-- ============================================================================
-- Each Guest has exactly one interview, so exactly one transcript
-- (guest_id UNIQUE). No separate Interview entity is introduced.

CREATE TABLE guest_transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    guest_id UUID NOT NULL UNIQUE
        REFERENCES guests(id)
        ON DELETE CASCADE,

    text TEXT NOT NULL,

    stt_provider TEXT,

    stt_model TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TRIGGER trg_guest_transcripts_updated_at
BEFORE UPDATE ON guest_transcripts
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE INDEX idx_guest_transcripts_guest_id
ON guest_transcripts(guest_id);


-- ============================================================================
-- 12. QUESTION ANSWER FIELDS
-- ============================================================================
-- Additive columns on the existing questions table. One answer belongs to
-- one question - no separate answers table.

ALTER TABLE questions
    ADD COLUMN spoken_question TEXT,
    ADD COLUMN answer TEXT,
    ADD COLUMN answer_status TEXT NOT NULL DEFAULT 'not_answered'
        CHECK (
            answer_status IN (
                'not_answered',
                'answered',
                'uncertain'
            )
        ),
    ADD COLUMN answer_source TEXT
        CHECK (
            answer_source IS NULL
            OR answer_source IN ('manual', 'ai_extracted')
        ),
    ADD COLUMN answer_updated_at TIMESTAMPTZ;


-- ============================================================================
-- END OF VERSION 3
-- ============================================================================
