# With Bader — Product Reference Document

## 1. Project Overview

**With Bader** is an AI-powered interview content workspace designed to manage the full lifecycle of guest-based content production.

The platform follows this high-level workflow:

**Research → Prepare → Interview → Extract → Create → Design → Publish**

Its purpose is to replace a fragmented process that would otherwise require separate tools for guest research, note-taking, question preparation, transcription, AI writing, design, and export.

With Bader is not a generic chatbot, a basic note-taking app, a transcription-only service, or a generic design generator. It is a specialized workspace for turning guest conversations into structured, reusable, branded content.

---

## 2. Core Product Philosophy

The central entity in the product is the **Guest**.

Each guest can have:

- Profile information
- Public research
- Social links
- Interview details
- Notebook pages
- Questions
- Audio/video recordings
- Transcript data
- Extracted answers
- AI-generated content
- Designs
- Files
- Published content

The product should feel like one continuous guest workspace rather than a set of disconnected tools.

---

## 3. End-to-End User Flow

```text
Create Guest
    ↓
Add Guest Information
    ↓
Research Guest
    ↓
Prepare Interview
    ↓
Create / Improve Questions
    ↓
Conduct Interview
    ↓
Upload or Record Audio
    ↓
Speech-to-Text
    ↓
Detect Speakers
    ↓
Match Spoken Questions with Prepared Questions
    ↓
Extract Guest Answers
    ↓
Save Answers under the Correct Questions
    ↓
Review Notebook and Q&A
    ↓
Select Valuable Content
    ↓
Generate Structured Content with AI
    ↓
Review and Edit
    ↓
Create Branded Design
    ↓
Preview
    ↓
Export
    ↓
Publish
```

---

## 4. Main Navigation

The global sidebar should remain simple:

```text
With Bader

Home
Text Extract
Calendar
Statistics

────────────

Settings
```

Guest-specific functions such as Notebook, Questions, Profile, Content, Design, and Files belong inside the guest workspace.

---

## 5. Home

Home is the main guest-management page.

Suggested elements:

- Guest search
- Guest filters
- Guest cards
- Add Guest button
- Interview date
- Preparation status
- Content status
- Recent activity

Example:

```text
Guests

[ Guest A ]   [ Guest B ]   [ Guest C ]   [ + Add Guest ]
```

A guest card may show:

- Photo
- Name
- Role
- Company
- Interview date
- Preparation status
- Content status

---

## 6. Guest Workspace

Selecting a guest opens a dedicated workspace.

Recommended sections:

```text
Overview
Notebook
Questions
Profile
Content
Design
Files
```

These can be implemented as tabs, contextual panels, or sections within one page.

---

## 7. Guest Profile

Suggested guest fields:

```text
Name
Job Title
Company
Photo
Biography
Interview Date
Interview Time
Interview Location
LinkedIn URL
Website
Other Social Links
Personal Notes
Research Summary
```

Future data may include:

- Previous companies
- Education
- Public speaking topics
- Previous interviews
- Career milestones
- Areas of expertise
- Public content themes

---

## 8. Guest Research

### Purpose

Guest Research helps the AI understand the guest before questions are generated.

The user may provide:

- Name
- Company
- Job title
- LinkedIn URL
- Personal website
- Company website
- Other public links
- Uploaded biography
- CV
- PDF
- Existing notes

The system may also use approved public web research.

### Recommended Flow

```text
Guest Information
      ↓
Provided Links
      ↓
Public Web Sources
      ↓
Source Extraction
      ↓
Normalize Information
      ↓
Build Structured Guest Profile
      ↓
Identify Interesting Topics
      ↓
Generate Interview Angles
```

### Structured Research Output

```json
{
  "name": "Guest Name",
  "current_role": "CEO",
  "company": "Company Name",
  "career_history": [],
  "education": [],
  "achievements": [],
  "projects": [],
  "topics": [],
  "interesting_events": [],
  "potential_interview_angles": [],
  "sources": []
}
```

### Architectural Principle

Research and question generation should remain separate logical steps:

```text
Research
   ↓
Structured Guest Profile
   ↓
Question Strategy
   ↓
Question Generation
```

---

## 9. Questions

The Questions module supports three main workflows.

### 9.1 Manual Questions

The user writes and saves questions manually.

Example:

```text
How did the company begin?
```

### 9.2 AI-Generated Questions

The AI generates questions after understanding the guest.

The model should consider:

- Guest role
- Career history
- Company
- Achievements
- Public interviews
- Articles
- Public posts
- Important events
- Existing notebook content
- Previous questions
- User-defined interview theme

The goal is to generate personalized questions, not generic prompts.

### 9.3 Manual + AI Improvement

The user writes a question, then asks AI to improve it.

Example:

```text
Original:
How did the company start?

AI Suggestion:
When did the idea first move from being a concept into a real company, and what convinced you that it was worth pursuing?
```

The original should not be overwritten automatically.

Recommended UX:

```text
Original Question
[ Keep Original ]

AI Suggestion
[ Use Suggestion ]
```

### Additional Question Features

- Generate follow-up questions
- Rephrase
- Make deeper
- Make shorter
- Make more conversational
- Avoid duplicate questions
- Group by topic
- Reorder questions
- Mark important
- Mark optional
- Add notes
- Link questions to extracted answers

---

## 10. Notebook

### Purpose

The Notebook is a flexible writing and interview workspace.

Core principle:

**The user defines the notebook structure, not the system.**

### Block Types

- Heading
- Paragraph
- Question
- Answer
- Quote
- Highlight
- Bullet list
- Numbered list
- Checklist
- Divider
- Image
- Callout
- Table
- Guest information block
- Content idea block
- Personal note block

Future:

- Audio note
- Voice transcription
- Attachment
- Link preview
- Reference card

### Block Actions

Each block may support:

- Edit
- Move
- Duplicate
- Delete
- Mark Important
- Mark as Potential Content
- Send to AI
- Rewrite
- Summarize
- Turn into quote
- Turn into LinkedIn post
- Turn into carousel
- Generate follow-up question

---

## 11. Text Extract / Interview Intelligence

The current UI label may remain **Text Extract**, but the long-term functionality is broader.

A more accurate technical name is:

**Interview Transcription & Intelligence**

### Main Responsibilities

- Convert audio to text
- Identify speakers
- Create timestamped transcript
- Match spoken questions with prepared questions
- Extract the guest answer
- Save the answer under the correct question
- Handle paraphrased spoken questions
- Produce a clean interview transcript
- Allow manual correction

### Recommended Flow

```text
Interview Audio
      ↓
Speech-to-Text
      ↓
Speaker Detection / Diarization
      ↓
Timestamped Transcript
      ↓
Question Detection
      ↓
Semantic Question Matching
      ↓
Answer Boundary Detection
      ↓
Extract Guest Answer
      ↓
Attach Answer to Prepared Question
      ↓
Save to Notebook / Questions
```

### Semantic Matching

Matching must not depend on exact wording.

Prepared question:

```text
What was your biggest challenge?
```

Actual spoken wording:

```text
What was the hardest thing you faced when the company was starting?
```

The system should recognize that these represent the same question.

### Human Review

The user should be able to:

- Correct speaker labels
- Correct question matches
- Edit transcript
- Move an answer
- Merge answers
- Split answers
- Ignore irrelevant sections

---

## 12. AI Architecture

### Provider Strategy

The architecture should not be tightly coupled to Claude or any single model provider.

The product should expose an internal:

**AI Service**

The provider can later be selected based on:

- Cost
- Accuracy
- Arabic quality
- Speed
- Structured-output reliability
- Context window
- Research quality
- Content-generation quality

### AI Service Responsibilities

```text
AI Service
    │
    ├── Question Generation
    ├── Question Improvement
    ├── Guest Understanding
    ├── Transcript Analysis
    ├── Content Generation
    ├── Summarization
    └── Structured Output
```

Conceptual provider interface:

```python
class AIProvider:
    generate()
    summarize()
    improve_question()
    generate_questions()
    analyze_transcript()
    structure_content()
```

This abstraction allows the AI provider to change without rewriting the rest of the platform.

---

## 13. Content Creation

Content creation should be a contextual action inside the guest workflow rather than a disconnected standalone tool.

Recommended flow:

```text
Notebook / Answer
      ↓
Select Content
      ↓
Create with AI
      ↓
Choose Content Type
      ↓
Review
      ↓
Approve
      ↓
Create Design
```

### Supported Content Types

- Interview Carousel
- Quote Post
- Q&A Post
- Story Post
- Lessons Learned
- Key Insight
- Personal Reflection
- Short LinkedIn Post
- Educational Carousel
- LinkedIn Caption

---

## 14. Structured AI Output

AI-generated content should use structured JSON whenever possible.

Example:

```json
{
  "title": "Why Growth Can Become a Problem",
  "content_type": "interview_carousel",
  "slides": [
    {
      "type": "hook",
      "text": "Fast growth is not always a sign of success."
    },
    {
      "type": "question",
      "text": "What was the biggest mistake you made early on?"
    },
    {
      "type": "answer",
      "text": "We expanded before our internal operations were ready."
    },
    {
      "type": "quote",
      "text": "Growth without structure creates new problems faster than it solves old ones."
    }
  ]
}
```

Benefits:

- Easier validation
- Better UI rendering
- Easier editing
- Better template mapping
- Predictable behavior
- Easier export
- Better scalability
- Easier testing

---

## 15. Design Studio

### Purpose

The Design Studio turns approved content into branded publication-ready visuals.

The first target platform is LinkedIn.

### Design Philosophy

The MVP should use **template-based rendering** instead of unrestricted generative design.

Benefits:

- Brand consistency
- Better Arabic typography
- Predictable layout
- Reliable RTL support
- Easier quality control
- Faster rendering
- Higher-resolution output
- Reusable templates

### Main Features

- Select template
- Map structured content to template
- Add guest image
- Crop image
- Reposition image
- Zoom image
- Edit text
- Preview
- Export slide
- Export carousel
- Export ZIP
- Export PDF

### Suggested Layout

```text
┌───────────────┬──────────────────┬───────────────┐
│ Content       │ Live Preview     │ Design        │
│               │                  │               │
│ Headline      │                  │ Template      │
│ Question      │      Slide       │ Typography    │
│ Answer        │                  │ Image         │
│ Quote         │                  │ Alignment     │
│ Guest         │                  │ Export        │
└───────────────┴──────────────────┴───────────────┘
```

---

## 16. Rendering Engine

Recommended flow:

```text
Template
   ↓
HTML + CSS
   ↓
Insert Structured Content
   ↓
Render with Headless Browser
   ↓
Export PNG / JPG / PDF
```

Recommended technology:

- Chromium
- Playwright

Example:

```text
AI JSON
   ↓
Template Mapper
   ↓
HTML / React Template
   ↓
Playwright
   ↓
1080 × 1350 PNG
```

---

## 17. LinkedIn Formats

### Portrait

```text
1080 × 1350 px
```

Suitable for:

- Carousel slides
- Quote cards
- Insight posts

### Square

```text
1080 × 1080 px
```

Suitable for:

- Single-image posts
- Quotes
- Simple branded content

### PDF Carousel

Future capability:

- Combine slides into a PDF carousel

---

## 18. Calendar

Possible events:

- Interview date
- Interview preparation deadline
- Guest follow-up
- Design deadline
- Publishing date

Future functionality:

- Reminders
- Content calendar
- Scheduled publishing
- Recurring interview series

---

## 19. Statistics

Initial metrics may include:

- Total guests
- Interviews completed
- Upcoming interviews
- Questions created
- AI-generated questions
- Audio processed
- Total transcript minutes
- Content drafts
- Approved content
- Designs generated
- Exported carousels

Future metrics:

- LinkedIn performance
- Impressions
- Engagement
- Saves
- Comments
- Best-performing guest
- Best-performing content type

---

## 20. Settings

Possible sections:

### Account
- Name
- Email
- Password
- Profile image

### Brand
- Logo
- Brand colors
- Typography
- Default templates

### AI
- Provider
- Model
- API credentials where applicable
- Language
- Prompt settings

### Interview
- Default language
- Default question style
- Transcription options

### Export
- Default dimensions
- Default file format
- Compression settings

---

## 21. Visual Identity

The UI should feel:

- Minimal
- Modern
- Technology-oriented
- Professional
- Spacious
- Clean
- Calm
- Premium

### Primary Gradient

```css
linear-gradient(135deg, #1FCFC3 0%, #1B8FEA 100%);
```

### Main Text

```text
#161616
```

### Secondary Text

```text
#5F6368
```

### Primary Background

```text
#FFFFFF
```

### Secondary Background

```text
#F7F8FA
```

### Border

```text
#E6EAF0
```

### Typography

Recommended English:

- Inter
- Manrope
- Plus Jakarta Sans
- DM Sans

Recommended Arabic:

- IBM Plex Sans Arabic
- Noto Sans Arabic
- Alexandria
- Tajawal

---

## 22. Logo Direction

The preferred logo concept combines:

- Conversation
- Notes
- Content
- Interview identity

The selected direction uses:

- Speech bubble
- Content/note lines
- Turquoise-to-blue gradient
- "With Bader" wordmark

---

## 23. Frontend Architecture

### Technology

- Next.js
- React
- TypeScript
- Tailwind CSS or CSS Modules
- Tiptap or Lexical for the notebook editor

### Recommended Structure

```text
frontend/
│
├── public/
│   ├── images/
│   ├── icons/
│   └── assets/
│
├── src/
│   │
│   ├── app/
│   │   ├── login/
│   │   ├── dashboard/
│   │   ├── guests/
│   │   ├── text-extract/
│   │   ├── calendar/
│   │   ├── statistics/
│   │   └── settings/
│   │
│   ├── components/
│   │   ├── ui/
│   │   ├── layout/
│   │   ├── sidebar/
│   │   ├── guest/
│   │   ├── notebook/
│   │   ├── questions/
│   │   ├── transcription/
│   │   └── design/
│   │
│   ├── features/
│   │   ├── authentication/
│   │   ├── guests/
│   │   ├── notebook/
│   │   ├── questions/
│   │   ├── research/
│   │   ├── transcription/
│   │   ├── content/
│   │   └── design/
│   │
│   ├── services/
│   │   └── api/
│   │
│   ├── hooks/
│   ├── types/
│   ├── utils/
│   └── styles/
│
├── Dockerfile
├── package.json
├── next.config.ts
├── tsconfig.json
└── .env.example
```

---

## 24. Backend Architecture

### Technology

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL

### Recommended Structure

```text
backend/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── api/
│   │   ├── auth.py
│   │   ├── guests.py
│   │   ├── notebooks.py
│   │   ├── questions.py
│   │   ├── research.py
│   │   ├── transcription.py
│   │   ├── content.py
│   │   ├── designs.py
│   │   ├── calendar.py
│   │   └── statistics.py
│   │
│   ├── models/
│   ├── schemas/
│   │
│   ├── services/
│   │   ├── guest_service.py
│   │   ├── notebook_service.py
│   │   ├── question_service.py
│   │   ├── research_service.py
│   │   ├── transcription_service.py
│   │   ├── content_service.py
│   │   └── design_service.py
│   │
│   ├── ai/
│   │   ├── provider.py
│   │   ├── prompts/
│   │   ├── question_generator.py
│   │   ├── question_improver.py
│   │   ├── content_generator.py
│   │   └── transcript_analyzer.py
│   │
│   ├── research/
│   │   ├── guest_research.py
│   │   ├── web_search.py
│   │   ├── source_parser.py
│   │   └── profile_builder.py
│   │
│   ├── transcription/
│   │   ├── speech_to_text.py
│   │   ├── speaker_detection.py
│   │   ├── question_matcher.py
│   │   └── answer_extractor.py
│   │
│   ├── design/
│   │   ├── templates/
│   │   ├── renderer.py
│   │   └── exporter.py
│   │
│   ├── database/
│   │   ├── session.py
│   │   ├── base.py
│   │   └── migrations/
│   │
│   ├── repositories/
│   ├── storage/
│   └── core/
│       ├── config.py
│       ├── security.py
│       └── logging.py
│
├── tests/
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## 25. Repository Structure

Use one repository with clear top-level separation:

```text
with-bader/
│
├── frontend/
├── backend/
├── infrastructure/
├── docs/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

This is intentionally clear and professional. The top-level names immediately communicate responsibility.

---

## 26. Infrastructure

```text
infrastructure/
│
├── nginx/
│   └── nginx.conf
│
├── postgres/
│
└── scripts/
    ├── deploy.sh
    └── backup.sh
```

---

## 27. Deployment Strategy

The first deployment should optimize for low cost and simplicity.

Recommended:

**One VPS + Docker Compose**

Services:

```text
nginx
frontend
backend
postgres
```

External services may include:

- AI provider
- Speech-to-text provider
- Public research APIs
- Future object storage

### High-Level Deployment

```text
                         Internet
                            │
                            ▼
                          Nginx
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
              Next.js               FastAPI
                 │                     │
                 └────── REST API ─────┘
                                       │
                        ┌──────────────┼──────────────┐
                        │              │              │
                        ▼              ▼              ▼
                   PostgreSQL     File Storage     AI Service
```

### Routing

```text
withbader.com/
        ↓
     Next.js

withbader.com/api/*
        ↓
     FastAPI
```

Benefits:

- Lower cost
- Simpler deployment
- Easier monitoring
- One domain
- Cleaner CORS behavior
- Logical service separation
- Easy future migration to multiple servers

---

## 28. Data Layer

Primary database:

**PostgreSQL**

File storage remains separate.

### PostgreSQL Stores

- Users
- Guests
- Guest research
- Notebooks
- Notebook pages
- Blocks
- Questions
- Question versions
- Interviews
- Transcript metadata
- Answer mappings
- Content projects
- AI outputs
- Templates
- Designs
- Asset metadata
- Calendar events
- Statistics metadata

### File Storage Stores

- Guest photos
- Uploaded PDFs
- Audio files
- Video files
- Transcript source files
- Generated images
- Carousel slides
- PDF exports
- Other assets

Initial implementation may use local disk storage.

Future options:

- Amazon S3
- Cloudflare R2
- Supabase Storage

---

## 29. Suggested Database Entities

```text
users
guests
guest_links
guest_research
notebooks
notebook_pages
blocks
questions
question_versions
interviews
recordings
transcripts
transcript_segments
question_answer_matches
content_projects
generated_content
templates
designs
assets
calendar_events
```

### questions

```text
id
guest_id
text
source
status
topic
position
is_important
created_at
updated_at
```

Possible source values:

```text
manual
ai_generated
ai_improved
```

### transcript_segments

```text
id
transcript_id
speaker
start_time
end_time
text
confidence
```

### question_answer_matches

```text
id
question_id
transcript_id
question_segment_id
answer_start_segment_id
answer_end_segment_id
match_score
review_status
created_at
```

---

## 30. API Direction

Example routes:

```text
POST   /api/guests
GET    /api/guests
GET    /api/guests/{id}
PATCH  /api/guests/{id}

POST   /api/guests/{id}/research
GET    /api/guests/{id}/research

POST   /api/guests/{id}/questions
GET    /api/guests/{id}/questions
POST   /api/questions/{id}/improve
POST   /api/guests/{id}/questions/generate

POST   /api/notebooks
GET    /api/notebooks/{id}
POST   /api/notebooks/{id}/pages
POST   /api/pages/{id}/blocks
PATCH  /api/blocks/{id}
DELETE /api/blocks/{id}

POST   /api/interviews
POST   /api/interviews/{id}/recordings
POST   /api/interviews/{id}/transcribe
GET    /api/interviews/{id}/transcript
POST   /api/interviews/{id}/match-questions

POST   /api/content/generate
POST   /api/content/rewrite
POST   /api/content/summarize
POST   /api/content/generate-caption

GET    /api/templates
POST   /api/designs
GET    /api/designs/{id}
POST   /api/designs/{id}/render
POST   /api/designs/{id}/export

POST   /api/assets/upload
```

---

## 31. Four Core AI Capability Groups

### 31.1 Guest Intelligence

- Understand the guest
- Research public background
- Identify interesting topics
- Identify unique interview angles
- Generate personalized questions

### 31.2 Interview Intelligence

- Convert speech to text
- Identify speakers
- Detect questions
- Match spoken questions
- Extract answers
- Clean transcript
- Link Q&A automatically

### 31.3 Content Intelligence

- Extract insights
- Find strong quotes
- Summarize
- Rewrite
- Generate hooks
- Create LinkedIn content
- Build carousel structure

### 31.4 Design Intelligence

- Map content to templates
- Select suitable layouts
- Keep typography within limits
- Handle guest image placement
- Prepare export-ready visuals

The initial Design Intelligence should remain template-driven rather than generative.

---

## 32. Development Phases

### Phase 1 — Foundation

- Authentication
- Guest management
- Guest profile
- Notebook
- Block editor
- Manual questions
- PostgreSQL
- Basic file upload

### Phase 2 — Guest & Question Intelligence

- Guest research
- Public source collection
- Structured guest profile
- AI question generation
- AI question improvement
- Question categories
- Source attribution

### Phase 3 — Interview Intelligence

- Audio upload
- Speech-to-text
- Speaker detection
- Transcript viewer
- Question detection
- Semantic question matching
- Answer extraction
- Manual review

### Phase 4 — Content Intelligence

- AI provider abstraction
- Structured JSON output
- Quote generation
- Rewrite
- Summarization
- Carousel generation
- LinkedIn caption generation

### Phase 5 — Design Engine

- Branded templates
- Guest image placement
- Live preview
- HTML/CSS rendering
- PNG export
- PDF export

### Phase 6 — Product Polish

- Better dashboard
- Calendar improvements
- Statistics
- Better workflows
- Better search
- Better file management

### Future

- Automatic LinkedIn publishing
- LinkedIn analytics
- Instagram export
- X/Twitter support
- Newsletter generation
- Scheduling
- Content calendar
- Team collaboration
- Approval workflows
- Voice recording inside the platform
- Automatic background removal
- More AI providers

---

## 33. Product Success Criteria

The product succeeds when one complete interview can be managed without depending on several disconnected external tools.

The user should be able to:

1. Create a guest.
2. Add public links.
3. Research the guest.
4. Generate personalized questions.
5. Improve manual questions.
6. Prepare interview notes.
7. Conduct the interview.
8. Upload the recording.
9. Transcribe the interview.
10. Match answers with prepared questions.
11. Review the resulting Q&A.
12. Select valuable content.
13. Generate structured content.
14. Edit it.
15. Choose a branded template.
16. Add guest imagery.
17. Preview the result.
18. Export publication-ready content.

---

## 34. Product Positioning

With Bader is not:

- A chatbot
- A generic AI writer
- A transcription-only tool
- A note-taking app
- A design app
- A generic interview question generator

Instead:

> **With Bader is an AI-powered interview content workspace that helps research guests, prepare questions, capture conversations, understand interviews, create structured content, and turn that content into branded publication-ready visuals.**

---

## 35. Short Product Description

> **With Bader is an AI-powered workspace for managing interview-based content from guest research to publication. It combines guest research, intelligent question preparation, a flexible notebook, speech-to-text interview analysis, automatic question-and-answer matching, AI-assisted content creation, and a branded design engine in one connected workflow.**

---

## 36. Product Formula

```text
Guest Research
      +
Interview Preparation
      +
Interview Intelligence
      +
Content Intelligence
      +
Branded Design Engine
      =
With Bader
```

User-facing alternatives:

> **Turn conversations into content.**

> **Research the guest. Capture the conversation. Shape the story.**
