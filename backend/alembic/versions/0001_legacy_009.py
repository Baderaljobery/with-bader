"""Baseline the historical SQL migrations 001 through 009.

Revision ID: 0001_legacy_009
Revises:
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from alembic import op

revision = "0001_legacy_009"
down_revision = None
branch_labels = None
depends_on = None

_LEGACY_MIGRATIONS = {
    "001_foundation.sql": "f24ccbd000122ce42912515dcb3e3e122b8a2322114a8b958f3727d2383774ec",
    "002_guest_research.sql": "cc09289555c864a1bda493044c4e31e3fabe450b94d311413a9237d38cc7a21c",
    "003_guest_transcripts_and_answers.sql": "a0d3fa30f2dd4d477e61554abf9ccb01121bb6f1f460f85140ebb470d7375ce4",
    "004_content_creation.sql": "eb220e39bf394b2ce3f21544d7dfaf408d5e8c551a57992aa33a75ca7f839400",
    "005_design_generation.sql": "354b2a8f978dc0f8f3951a50833eb608e449468d6323028922b0ba7eb046b810",
    "006_design_slides.sql": "404ade3ef89338c935f6bc3789b213552a097fc432f9236b3ae5170b583e60df",
    "007_guest_interview_schedule.sql": "ded9248c273e18ecc43b72bffe8eba9f1c81d2aec3ba0b6d21ed6ec4ca8e9637",
    "008_authentication.sql": "4d62f18ba21ce5b5222b152357670bfe8631bdc4c3eb69024e81402e0c3d5778",
    "009_content_status_manual_override.sql": "06e348ecb3ada718ed00ad924db844a5c2389a219411b574cdac961a8638b0db",
}


def upgrade() -> None:
    database_dir = Path(__file__).resolve().parents[3] / "database"
    connection = op.get_bind()
    for filename, expected_hash in _LEGACY_MIGRATIONS.items():
        path = database_dir / filename
        script = path.read_bytes()
        actual_hash = hashlib.sha256(script).hexdigest()
        if actual_hash != expected_hash:
            raise RuntimeError(
                f"Historical migration {filename} changed; expected {expected_hash}, got {actual_hash}"
            )
        connection.exec_driver_sql(script.decode("utf-8-sig"))


def downgrade() -> None:
    raise RuntimeError(
        "The legacy baseline cannot be downgraded safely; restore from a database backup instead"
    )
