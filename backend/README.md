# Backend

FastAPI API and background worker for the LegalTech MVP.

- Contract uploads now reject unreadable PDFs with HTTP `422` and avoid partial persistence on failure.
