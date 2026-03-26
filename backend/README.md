# Backend

FastAPI API and background worker for the LegalTech MVP.

- Contract uploads now reject unreadable PDFs with HTTP `422` and avoid partial persistence on failure.
- Signed contract uploads now persist a structured extraction snapshot on `contract_versions.extraction_metadata` and rebuild the contract's canonical event schedule from the latest signed version.
- The runtime now uses OpenAI as the only LLM integration, defaulting to `gpt-5-mini` when `OPENAI_MODEL` is not set.
- Benchmark the F6-E analysis stack with `py -3.13 -m tests.support.openai_benchmark --runs 3 --output ../docs/squad/artifacts/2026-03-25-f6-e-openai-benchmark.json` after setting `OPENAI_API_KEY`.
