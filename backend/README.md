# Backend

FastAPI API and background worker for the LegalTech MVP.

- Contract uploads now reject unreadable PDFs with HTTP `422` and avoid partial persistence on failure.
- Signed contract uploads now persist a structured extraction snapshot on `contract_versions.extraction_metadata` and rebuild the contract's canonical event schedule from the latest signed version.
