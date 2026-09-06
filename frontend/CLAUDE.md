@AGENTS.md
# With Bader — Frontend Agent Instructions

## Design system
Before building or styling any UI component or page, read `design-notes.md`
in this directory for the With Bader brand colors, typography (IBM Plex
Sans Arabic), gradient usage rules, and RTL layout requirements.

Use it together with the `frontend-design` skill
(`.claude/skills/frontend-design`) — the skill defines *how* to make bold,
non-templated design choices; `design-notes.md` defines *which* choices are
correct for this specific brand.

## Layout
- RTL by default (`dir="rtl"`), sidebar on the right.
- Match existing patterns in `app/`, `components/`, and `services/` before
  introducing new conventions.