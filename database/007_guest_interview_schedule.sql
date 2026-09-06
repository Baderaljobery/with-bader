-- ============================================================================
-- With Bader
-- Database Schema - Version 7 / Guest Interview Schedule (Calendar)
-- PostgreSQL 16+
-- ============================================================================
--
-- Additive only - does not touch 001-006. Adds the minimum data needed for
-- the Calendar feature: each guest can have at most one scheduled interview
-- (date/time + a short location string). No separate events table - a
-- calendar "event" is just a guest with a non-null interview_scheduled_at.
--
-- interview_scheduled_at is intentionally a naive TIMESTAMP (no timezone) -
-- this product has no multi-timezone concept, so it stores the interview's
-- plain wall-clock date/time exactly as entered, with no UTC conversion in
-- either direction (see backend/app/models/guest.py).

ALTER TABLE guests
    ADD COLUMN interview_scheduled_at TIMESTAMP NULL,
    ADD COLUMN interview_location TEXT NULL;

-- Speeds up the Calendar's "events within this visible date range" query -
-- partial index since most guests will never have a scheduled interview.
CREATE INDEX idx_guests_interview_scheduled_at
    ON guests (interview_scheduled_at)
    WHERE interview_scheduled_at IS NOT NULL;
