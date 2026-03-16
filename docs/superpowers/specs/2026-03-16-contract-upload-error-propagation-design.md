# Contract Upload Error Propagation Design

## Objective

Make the contracts frontend consume the backend `422` from `/api/uploads/contracts` and present a Portuguese, operator-friendly error instead of a generic failure.

## Scope

- frontend-only follow-up for `F1-A`
- preserve the existing happy path for successful uploads
- surface the unreadable-PDF case clearly in the contracts screen
- validate the behavior with unit coverage and an end-to-end upload using a file from disk

## Architecture

Keep the mapping at the transport boundary in `web/src/lib/api/contracts.ts`. The screen in `web/src/features/contracts/screens/contracts-screen.tsx` should continue to render `Error.message`, but the client should translate known backend `detail` values into UI copy before throwing.

This keeps HTTP-shape knowledge out of the screen and avoids creating a new cross-cutting error abstraction for a single known backend contract.

## Error Handling

- If the backend returns `422` with `detail = "Uploaded file is not a readable PDF"`, the client should throw `Error("O arquivo enviado nao e um PDF legivel.")`.
- If the backend returns another JSON error with a string `detail`, the client should throw that `detail`.
- If the backend response cannot be parsed or does not include a usable string, keep the fallback `Nao foi possivel enviar o contrato.`

## Testing

- add unit coverage in the API client for known-detail translation and generic fallback
- add screen coverage to prove the alert renders the propagated message
- add an E2E invalid-upload test that submits a `.pdf` file from disk with unreadable content and expects the operator-facing Portuguese error

## Out of Scope

- redesign of the contracts page
- typed frontend error hierarchy
- broad retry or telemetry work
