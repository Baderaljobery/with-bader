from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.assets import router as assets_router
from app.api.auth import router as auth_router
from app.api.blocks import detail_router as blocks_detail_router
from app.api.blocks import guest_blocks_router
from app.api.blocks import router as blocks_router
from app.api.calendar import router as calendar_router
from app.api.content import detail_router as content_detail_router
from app.api.content import router as content_router
from app.api.design import detail_router as design_detail_router
from app.api.design import router as design_router
from app.api.guest_interview import router as guest_interview_router
from app.api.guest_links import detail_router as guest_link_detail_router
from app.api.guest_links import router as guest_links_router
from app.api.guest_research import detail_router as guest_research_detail_router
from app.api.guest_research import router as guest_research_router
from app.api.guest_research_engine import router as guest_research_engine_router
from app.api.guests import router as guests_router
from app.api.notebook_pages import detail_router as notebook_pages_detail_router
from app.api.notebook_pages import router as notebook_pages_router
from app.api.notebooks import detail_router as notebooks_detail_router
from app.api.notebooks import router as notebooks_router
from app.api.question_generation import router as question_generation_router
from app.api.question_improvement import router as question_improvement_router
from app.api.question_versions import detail_router as question_version_detail_router
from app.api.question_versions import router as question_versions_router
from app.api.questions import detail_router as questions_detail_router
from app.api.questions import router as questions_router
from app.api.statistics import router as statistics_router
from app.api.text_extract import router as text_extract_router
from app.core.config import settings
from app.design_generation.storage import MEDIA_URL_PREFIX, STORAGE_DIR

app = FastAPI(title="With Bader API")

# The frontend (Next.js) runs on a different origin than the backend, so
# browser requests need this to succeed. Explicit origin allowlist, never
# "*" - required anyway since allow_credentials=True (the session cookie)
# is not permitted alongside a wildcard origin by the CORS spec.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(guests_router)
app.include_router(calendar_router)
app.include_router(guest_interview_router)
app.include_router(guest_links_router)
app.include_router(guest_link_detail_router)
app.include_router(guest_research_router)
app.include_router(guest_research_detail_router)
app.include_router(guest_research_engine_router)
app.include_router(questions_router)
app.include_router(questions_detail_router)
app.include_router(question_generation_router)
app.include_router(question_improvement_router)
app.include_router(question_versions_router)
app.include_router(question_version_detail_router)
app.include_router(assets_router)
app.include_router(notebooks_router)
app.include_router(notebooks_detail_router)
app.include_router(notebook_pages_router)
app.include_router(notebook_pages_detail_router)
app.include_router(blocks_router)
app.include_router(blocks_detail_router)
app.include_router(guest_blocks_router)
app.include_router(text_extract_router)
app.include_router(content_router)
app.include_router(content_detail_router)
app.include_router(design_router)
app.include_router(design_detail_router)
app.include_router(statistics_router)

# Serves generated design images back out from local disk (see
# app/design_generation/storage.py) - the directory must exist before
# StaticFiles mounts it.
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
app.mount(MEDIA_URL_PREFIX, StaticFiles(directory=STORAGE_DIR), name="design-drafts-media")


@app.get("/health")
def health_check():
    return {"status": "ok"}
