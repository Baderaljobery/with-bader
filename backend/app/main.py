from fastapi import FastAPI

from app.api.assets import router as assets_router
from app.api.blocks import detail_router as blocks_detail_router
from app.api.blocks import router as blocks_router
from app.api.guest_links import detail_router as guest_link_detail_router
from app.api.guest_links import router as guest_links_router
from app.api.guest_research import detail_router as guest_research_detail_router
from app.api.guest_research import router as guest_research_router
from app.api.guests import router as guests_router
from app.api.notebook_pages import detail_router as notebook_pages_detail_router
from app.api.notebook_pages import router as notebook_pages_router
from app.api.notebooks import detail_router as notebooks_detail_router
from app.api.notebooks import router as notebooks_router
from app.api.question_versions import detail_router as question_version_detail_router
from app.api.question_versions import router as question_versions_router
from app.api.questions import detail_router as questions_detail_router
from app.api.questions import router as questions_router

app = FastAPI(title="With Bader API")

app.include_router(guests_router)
app.include_router(guest_links_router)
app.include_router(guest_link_detail_router)
app.include_router(guest_research_router)
app.include_router(guest_research_detail_router)
app.include_router(questions_router)
app.include_router(questions_detail_router)
app.include_router(question_versions_router)
app.include_router(question_version_detail_router)
app.include_router(assets_router)
app.include_router(notebooks_router)
app.include_router(notebooks_detail_router)
app.include_router(notebook_pages_router)
app.include_router(notebook_pages_detail_router)
app.include_router(blocks_router)
app.include_router(blocks_detail_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
