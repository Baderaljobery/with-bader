-- ============================================================================
-- With Bader
-- Database Schema - Version 1 / Foundation
-- PostgreSQL 16+
-- ============================================================================


-- ============================================================================
-- EXTENSIONS
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";


-- ============================================================================
-- UPDATED_AT HELPER
-- ============================================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- 1. USERS
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name TEXT NOT NULL,

    email TEXT NOT NULL UNIQUE,

    password_hash TEXT NOT NULL,

    role TEXT NOT NULL DEFAULT 'owner'
        CHECK (role IN ('owner', 'editor')),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================================
-- 2. ASSETS
-- ============================================================================

CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    uploaded_by UUID
        REFERENCES users(id)
        ON DELETE SET NULL,

    type TEXT NOT NULL
        CHECK (
            type IN (
                'guest_photo',
                'pdf_upload',
                'image',
                'document',
                'other'
            )
        ),

    file_name TEXT NOT NULL,

    file_path TEXT NOT NULL,

    mime_type TEXT,

    size_bytes BIGINT
        CHECK (size_bytes IS NULL OR size_bytes >= 0),

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE INDEX idx_assets_uploaded_by
ON assets(uploaded_by);

CREATE INDEX idx_assets_type
ON assets(type);


-- ============================================================================
-- Add profile image to users after assets exists
-- ============================================================================

ALTER TABLE users
ADD COLUMN profile_image_id UUID
REFERENCES assets(id)
ON DELETE SET NULL;


-- ============================================================================
-- 3. GUESTS
-- ============================================================================

CREATE TABLE guests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    created_by UUID
        REFERENCES users(id)
        ON DELETE SET NULL,

    name TEXT NOT NULL,

    slug TEXT UNIQUE,

    job_title TEXT,

    company TEXT,

    photo_id UUID
        REFERENCES assets(id)
        ON DELETE SET NULL,

    biography TEXT,

    personal_notes TEXT,

    research_summary TEXT,

    preparation_status TEXT NOT NULL DEFAULT 'not_started'
        CHECK (
            preparation_status IN (
                'not_started',
                'researching',
                'questions_ready',
                'interview_scheduled',
                'interview_completed'
            )
        ),

    content_status TEXT NOT NULL DEFAULT 'not_started'
        CHECK (
            content_status IN (
                'not_started',
                'in_progress',
                'review',
                'published'
            )
        ),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TRIGGER trg_guests_updated_at
BEFORE UPDATE ON guests
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE INDEX idx_guests_created_by
ON guests(created_by);

CREATE INDEX idx_guests_preparation_status
ON guests(preparation_status);

CREATE INDEX idx_guests_content_status
ON guests(content_status);

CREATE INDEX idx_guests_name
ON guests(name);


-- ============================================================================
-- 4. GUEST LINKS
-- ============================================================================

CREATE TABLE guest_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    guest_id UUID NOT NULL
        REFERENCES guests(id)
        ON DELETE CASCADE,

    label TEXT NOT NULL,

    url TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE INDEX idx_guest_links_guest_id
ON guest_links(guest_id);


-- ============================================================================
-- 5. NOTEBOOKS
-- ============================================================================

CREATE TABLE notebooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    guest_id UUID NOT NULL
        REFERENCES guests(id)
        ON DELETE CASCADE,

    title TEXT NOT NULL DEFAULT 'Notebook',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TRIGGER trg_notebooks_updated_at
BEFORE UPDATE ON notebooks
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE INDEX idx_notebooks_guest_id
ON notebooks(guest_id);


-- ============================================================================
-- 6. NOTEBOOK PAGES
-- ============================================================================

CREATE TABLE notebook_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    notebook_id UUID NOT NULL
        REFERENCES notebooks(id)
        ON DELETE CASCADE,

    title TEXT NOT NULL DEFAULT 'Untitled Page',

    position INTEGER NOT NULL DEFAULT 0
        CHECK (position >= 0),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TRIGGER trg_notebook_pages_updated_at
BEFORE UPDATE ON notebook_pages
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE INDEX idx_notebook_pages_notebook
ON notebook_pages(notebook_id);

CREATE INDEX idx_notebook_pages_position
ON notebook_pages(notebook_id, position);


-- ============================================================================
-- 7. QUESTIONS
-- ============================================================================

CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    guest_id UUID NOT NULL
        REFERENCES guests(id)
        ON DELETE CASCADE,

    text TEXT NOT NULL,

    source TEXT NOT NULL DEFAULT 'manual'
        CHECK (
            source IN (
                'manual',
                'ai_generated',
                'ai_improved'
            )
        ),

    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (
            status IN (
                'draft',
                'approved',
                'asked',
                'answered'
            )
        ),

    topic TEXT,

    position INTEGER NOT NULL DEFAULT 0
        CHECK (position >= 0),

    is_important BOOLEAN NOT NULL DEFAULT FALSE,

    is_optional BOOLEAN NOT NULL DEFAULT FALSE,

    notes TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TRIGGER trg_questions_updated_at
BEFORE UPDATE ON questions
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE INDEX idx_questions_guest_id
ON questions(guest_id);

CREATE INDEX idx_questions_guest_position
ON questions(guest_id, position);

CREATE INDEX idx_questions_status
ON questions(status);


-- ============================================================================
-- 8. QUESTION VERSIONS
-- ============================================================================

CREATE TABLE question_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    question_id UUID NOT NULL
        REFERENCES questions(id)
        ON DELETE CASCADE,

    version INTEGER NOT NULL
        CHECK (version > 0),

    text TEXT NOT NULL,

    source TEXT NOT NULL
        CHECK (
            source IN (
                'manual',
                'ai_generated',
                'ai_improved'
            )
        ),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(question_id, version)
);


CREATE INDEX idx_question_versions_question_id
ON question_versions(question_id);


-- ============================================================================
-- 9. BLOCKS
-- ============================================================================

CREATE TABLE blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    page_id UUID NOT NULL
        REFERENCES notebook_pages(id)
        ON DELETE CASCADE,

    type TEXT NOT NULL
        CHECK (
            type IN (
                'heading',
                'paragraph',
                'question',
                'answer',
                'quote',
                'highlight',
                'bullet_list',
                'numbered_list',
                'checklist',
                'divider',
                'image',
                'callout',
                'table',
                'guest_info',
                'content_idea',
                'personal_note'
            )
        ),

    content JSONB NOT NULL DEFAULT '{}'::jsonb,

    position DOUBLE PRECISION NOT NULL DEFAULT 0,

    is_important BOOLEAN NOT NULL DEFAULT FALSE,

    is_potential_content BOOLEAN NOT NULL DEFAULT FALSE,

    linked_question_id UUID
        REFERENCES questions(id)
        ON DELETE SET NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TRIGGER trg_blocks_updated_at
BEFORE UPDATE ON blocks
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE INDEX idx_blocks_page_id
ON blocks(page_id);

CREATE INDEX idx_blocks_page_position
ON blocks(page_id, position);

CREATE INDEX idx_blocks_linked_question
ON blocks(linked_question_id);


-- ============================================================================
-- OPTIONAL: Link an asset directly to a guest
-- ============================================================================

ALTER TABLE assets
ADD COLUMN guest_id UUID
REFERENCES guests(id)
ON DELETE CASCADE;


CREATE INDEX idx_assets_guest_id
ON assets(guest_id);


-- ============================================================================
-- END OF VERSION 1
-- ============================================================================