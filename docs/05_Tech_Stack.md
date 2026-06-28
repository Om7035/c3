# 05 Tech Stack

## Language and API

- Python 3.12
- FastAPI

## Modeling and Graphs

- Pydantic for contracts and validation
- NetworkX for graph representation and topological execution support

## LLM Abstraction

- LiteLLM for provider portability

## Runtime

- asyncio
- FastAPI background tasks where useful for non-blocking work

## Data and Infrastructure

- PostgreSQL for relational persistence
- Redis for short-lived execution state and caching
- optional future additions: Neo4j, DuckDB, object storage

## Search and Retrieval

- OpenSearch or Qdrant

## Execution Isolation

- Docker-based sandbox first
- E2B or Modal as alternatives if required by research velocity

## Frontend

- Next.js
- React
- Tailwind CSS

## Developer Tooling

- uv
- Ruff
- Black
- MyPy
- pytest
- Hypothesis
- coverage
- Docker
- GitHub Actions
