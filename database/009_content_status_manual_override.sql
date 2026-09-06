-- ============================================================================
-- With Bader
-- Database Schema - Version 9 / Guest Content Status: auto vs. manual
-- PostgreSQL 16+
-- ============================================================================
--
-- Additive only - does not touch 001-008. Simplifies guests.content_status
-- to exactly 3 states (not_started / in_progress / published) and adds
-- content_status_manual to record whether the current value was explicitly
-- chosen by the user, as opposed to derived automatically from whether the
-- guest has a scheduled interview (guests.interview_scheduled_at). See
-- backend/app/services/guest_service.py for the automatic rule.
--
-- 'review' is dropped - there was never a workflow that set it, and it does
-- not map to the new automatic/manual model.

-- Fold the old 'review' value into 'in_progress' before tightening the
-- CHECK constraint below.
UPDATE guests SET content_status = 'in_progress' WHERE content_status = 'review';

ALTER TABLE guests
    ADD COLUMN content_status_manual BOOLEAN NOT NULL DEFAULT FALSE;

-- Existing non-default values were set under the old model, which had no
-- automatic/manual distinction. Treat them as manual so this migration
-- doesn't silently revert anyone's already-chosen status via the new
-- Calendar-driven automatic rule the first time their guest is touched.
UPDATE guests SET content_status_manual = TRUE WHERE content_status <> 'not_started';

ALTER TABLE guests DROP CONSTRAINT guests_content_status_check;

ALTER TABLE guests
    ADD CONSTRAINT guests_content_status_check
    CHECK (content_status IN ('not_started', 'in_progress', 'published'));
