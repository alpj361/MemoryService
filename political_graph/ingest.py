import json
import logging
from typing import Dict, Any

from memory import _get_zep_client

logger = logging.getLogger(__name__)
GROUP_ID = "pulse-politics"


def ingest_batch(batch: Dict[str, Any]) -> None:
    """Add a batch of data (JSON) to the PulsePolitics group graph."""
    client = _get_zep_client()
    try:
        client.graph.add(group_id=GROUP_ID, type="json", data=json.dumps(batch))
        logger.info("📌 Ingested batch into '%s' (keys=%d)", GROUP_ID, len(batch))
    except Exception as e:
        logger.error("❌ Error ingesting batch: %s", e)
        raise


if __name__ == "__main__":
    import argparse, sys
    parser = argparse.ArgumentParser(description="Ingest a JSON batch into PulsePolitics group graph")
    parser.add_argument("file", help="Path to JSON file with batch data")
    args = parser.parse_args()

    try:
        with open(args.file, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        ingest_batch(data)
    except Exception as exc:
        logger.error("❌ %s", exc)
        sys.exit(1) 