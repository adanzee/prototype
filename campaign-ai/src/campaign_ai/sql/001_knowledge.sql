BEGIN;

CREATE SCHEMA IF NOT EXISTS knowledge;

CREATE TABLE IF NOT EXISTS knowledge.sources (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    url text NOT NULL UNIQUE,
    title text NOT NULL,
    kind text NOT NULL CHECK (
        kind IN ('study', 'market_report', 'campaign', 'guidance')
    ),
    collected_on date NOT NULL,
    published_on date,
    doi text
);

CREATE TABLE IF NOT EXISTS knowledge.evidence (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id bigint NOT NULL REFERENCES knowledge.sources(id),
    finding text NOT NULL,
    locator text NOT NULL,
    limitation text NOT NULL,
    markets text[] NOT NULL DEFAULT '{}',
    audience text NOT NULL DEFAULT '',
    category text NOT NULL DEFAULT '',
    channel text NOT NULL DEFAULT '',
    topics text[] NOT NULL DEFAULT '{}',
    status text NOT NULL DEFAULT 'pending' CHECK (
        status IN ('pending', 'approved', 'rejected')
    ),
    created_at timestamptz NOT NULL DEFAULT now()
);

COMMIT;