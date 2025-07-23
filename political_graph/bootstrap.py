import json
import logging
from pathlib import Path

from settings import settings
from memory import _get_zep_client

logger = logging.getLogger(__name__)

GROUP_ID = "pulse-politics"
SEED_PATH = Path(__file__).with_suffix("").parent / "seed.json"


def ensure_group_exists() -> None:
    """Ensure the PulsePolitics group graph exists in Zep."""
    client = _get_zep_client()
    try:
        client.group.add(
            group_id=GROUP_ID,
            name="Pulse Politics",
            description="Shared political knowledge graph for all agents."
        )
        logger.info("✅ Group graph '%s' created", GROUP_ID)
    except Exception as e:
        # Zep raises 400 if group already exists
        if "already" in str(e).lower():
            logger.info("Group graph '%s' already exists", GROUP_ID)
        else:
            logger.error("❌ Error ensuring group graph: %s", e)
            raise


def _load_seed() -> dict:
    if SEED_PATH.exists():
        try:
            with open(SEED_PATH, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception as e:
            logger.error("❌ Error loading seed.json: %s", e)
    return {}


def populate_seed() -> None:
    """Populate the group graph with initial seed data if provided."""
    seed = _load_seed()
    if not seed:
        logger.warning("⚠️ No seed data found – skipping initial population")
        return

    client = _get_zep_client()
    try:
        client.graph.add(
            group_id=GROUP_ID,
            type="json",
            data=json.dumps(seed)
        )
        logger.info("🌱 Seed data inserted into '%s' (%d top-level keys)", GROUP_ID, len(seed))
    except Exception as e:
        logger.error("❌ Error adding seed data: %s", e) 