import logging
from typing import List

from memory import _get_zep_client

GROUP_ID = "pulse-politics"
logger = logging.getLogger(__name__)


def search_political_context(query: str, limit: int = 5) -> List[str]:
    """Search PulsePolitics group graph for relevant edges or facts."""
    if not query or not query.strip():
        return []

    client = _get_zep_client()

    try:
        results = client.graph.search(
            group_id=GROUP_ID,
            query=query,
            scope="edges",
            limit=limit
        )
        facts: List[str] = []
        for edge in getattr(results, "results", []):
            # Edge objects differ per SDK; use generic casting
            try:
                facts.append(str(edge.content if hasattr(edge, "content") else edge))
            except Exception:
                facts.append(str(edge))
        logger.info("🔍 Political graph search '%s' → %d results", query, len(facts))
        return facts
    except Exception as e:
        logger.error("❌ Error searching political graph: %s", e)
        return [] 