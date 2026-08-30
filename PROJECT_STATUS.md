# JobSearch — Project Status

## Features we have

- MongoDB datastore (Docker: mongo + mongo-express UI)
- Schema-flexible listings storage, one collection for all sources
- Dedup via unique index on (source, source_id)
- Python ingestion framework (connector interface + upsert pipeline)
- Arbeitnow connector — free, no API key — ~2,190 listings ingested
- RapidAPI "Jobs API" (Indeed) connector — 1,000 listings ingested
- Git repo with working history, pushed to GitHub

## What we still need

- Normalize fields across sources (title, company, location, etc.)
- A search/query interface to actually search stored listings
- Scheduled re-ingestion to keep listings fresh
- Staleness handling (mark old listings as expired)
- A plan for RapidAPI quota (current key is exhausted)
- More connectors, if desired (Bing, LinkedIn, Xing via same RapidAPI key)

## What hasn't been discussed yet

- The AI / text-to-speech customer-facing app
- The point-and-click UI customer-facing app
- Hosting / deployment plan
- User accounts / authentication
- Budget for paid API tiers
- Data retention and privacy policy for stored listings

## Timeline — what's next

1. Normalize listing fields across sources
2. Build a basic search/query CLI
3. Add scheduled re-ingestion
4. Resolve RapidAPI quota (upgrade plan or add free sources)
5. Start on the AI/TTS app or the point-and-click UI app
