import os
from pathlib import Path

import psycopg
from pydantic import TypeAdapter

from campaign_ai.modules.knowledge.models import Evidence


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    seed_path = project_root / "data" / "knowledge_seed.json"

    if not seed_path.is_file():
        raise SystemExit(f"Seed file missing: {seed_path}")

    records = TypeAdapter(list[Evidence]).validate_json(seed_path.read_bytes())
    inserted = 0

    with psycopg.connect(os.environ["KNOWLEDGE_DATABASE_URL"]) as conn:
        for record in records:
            source = record.source
            source_row = conn.execute(
                """
                INSERT INTO knowledge.sources
                    (url, title, kind, collected_on, published_on, doi)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO UPDATE SET title = EXCLUDED.title
                RETURNING id
                """,
                (
                    str(source.url),
                    source.title,
                    source.kind,
                    source.collected_on,
                    source.published_on,
                    source.doi,
                ),
            ).fetchone()

            assert source_row is not None
            source_id = source_row[0]

            result = conn.execute(
                """
                INSERT INTO knowledge.evidence
                    (source_id, finding, locator, limitation, markets,
                     audience, category, channel, topics)
                SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM knowledge.evidence
                    WHERE source_id = %s AND finding = %s AND locator = %s
                )
                """,
                (
                    source_id,
                    record.finding,
                    record.locator,
                    record.limitation,
                    record.markets,
                    record.audience,
                    record.category,
                    record.channel,
                    record.topics,
                    source_id,
                    record.finding,
                    record.locator,
                ),
            )
            inserted += result.rowcount

    print(f"Validated {len(records)} record(s). Inserted {inserted} finding(s).")


if __name__ == "__main__":
    main()