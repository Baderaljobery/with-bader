-- ============================================================================
-- With Bader
-- Database Schema - Version 8 / Authentication & Data Ownership
-- PostgreSQL 16+
-- ============================================================================
--
-- Additive/adjusting only - does not touch 001-007's table definitions
-- beyond this one foreign key.
--
-- guests.created_by already exists (001_foundation.sql) but was never
-- populated by any code path and was defined as ON DELETE SET NULL. Two
-- changes:
--
-- 1. ON DELETE SET NULL -> ON DELETE CASCADE: deleting a user must delete
--    every Guest they own (and, via each Guest's own existing cascades,
--    everything beneath it) - see app/services/user_service.py's
--    delete_user_account(). SET NULL would instead silently orphan their
--    data as "ownerless," which is the opposite of a real account
--    deletion.
--
-- 2. An index on created_by, since every guest list/scoping query now
--    filters by it.
--
-- created_by deliberately STAYS NULLABLE here. As of this migration the
-- live dev database has 0 users and 17 existing guests, all with
-- created_by = NULL - there is no existing user to safely backfill them
-- to, and guessing one is explicitly the wrong move (see the task's own
-- Part 55/21: "do NOT invent credentials silently... do not guess
-- ownership"). Those 17 guests are preserved as-is; they simply become
-- inaccessible through the now-scoped API until a human decides which
-- real account should own them and either runs the one-line backfill
-- below or asks for it to be run:
--
--   UPDATE guests SET created_by = '<real-user-id>' WHERE created_by IS NULL;
--
-- Once every guest has a real owner, a follow-up migration can safely add
-- `NOT NULL` to this column.

ALTER TABLE guests DROP CONSTRAINT guests_created_by_fkey;

ALTER TABLE guests
    ADD CONSTRAINT guests_created_by_fkey
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_guests_created_by ON guests (created_by);
