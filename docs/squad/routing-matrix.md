# Routing Matrix

Use this matrix after task classification. Mandatory routes cannot be skipped. Manual override may add rigor, but it cannot remove mandatory QA for touched implementation areas.

## Trigger Matrix

| Trigger | Mandatory Role |
| --- | --- |
| any relevant task | `implementation-manager` |
| architecture, API contract, persistence, integration, deploy behavior, or cross-cutting flow changes | `tech-lead` |
| changes under `backend/` or backend contracts | `backend-engineer` |
| changes under `web/` or operator UX flows | `frontend-engineer` |
| backend implementation ran | `qa-backend` |
| frontend implementation ran | `qa-frontend` |
| setup, behavior, API, UX flow, operating guidance, or memory changed | `documentation-engineer` |

## Minimum Paths By Task Class

### Low-Risk Single-Area
| Changed Area | Route |
| --- | --- |
| backend only | `implementation-manager` -> `backend-engineer` -> `qa-backend` |
| frontend only | `implementation-manager` -> `frontend-engineer` -> `qa-frontend` |
| docs or memory only | `implementation-manager` -> `documentation-engineer` |

### Medium-Risk Feature
| Changed Area | Route |
| --- | --- |
| backend with contract or boundary impact | `implementation-manager` -> `tech-lead` -> `backend-engineer` -> `qa-backend` -> `documentation-engineer` |
| frontend with UX flow impact | `implementation-manager` -> `frontend-engineer` -> `qa-frontend` -> `documentation-engineer` |
| frontend with API or workflow coupling | `implementation-manager` -> `tech-lead` -> `frontend-engineer` -> `qa-frontend` -> `documentation-engineer` |

### High-Risk Cross-Cutting
| Changed Area | Route |
| --- | --- |
| backend plus frontend | `implementation-manager` -> `tech-lead` -> `backend-engineer` and `frontend-engineer` -> `qa-backend` and `qa-frontend` -> `documentation-engineer` |
| deploy or infrastructure-sensitive refactor | `implementation-manager` -> `tech-lead` -> relevant engineer(s) -> relevant QA -> `documentation-engineer` |

## Manual Override
- `implementation-manager` may add extra roles for unusual risk.
- `tech-lead` may request another engineer review if the route underestimates architecture risk.
- QA may request `documentation-engineer` even when docs were initially omitted, if the implementation changed operator or setup behavior.

## Fallback Rule
If classification is ambiguous, route upward in rigor instead of skipping a specialist.
