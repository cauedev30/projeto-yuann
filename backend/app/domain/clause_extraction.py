from __future__ import annotations
import re
from dataclasses import dataclass

@dataclass
class ClauseItem:
    title: str
    content: str
    order_index: int

CLAUSE_PATTERNS = [
    re.compile(r"CLÁUSULA\s+(\d+)ª?\s*[-–—]\s*(.+)", re.IGNORECASE),
    re.compile(r"Art\.?\s*(\d+)º?\s*[-–—.]\s*(.+)", re.IGNORECASE),
    re.compile(r"^(\d+)\.\s+([A-Z][A-Z\s]+)$", re.MULTILINE),
    re.compile(r"^(CLÁUSULA|ARTIGO)\s+(.+)$", re.IGNORECASE | re.MULTILINE),
]

def extract_clauses(contract_text: str) -> list[ClauseItem]:
    text = contract_text.replace("\r\n", "\n").replace("\r", "\n")
    matches: list[tuple[int, str, int]] = []

    for pattern in CLAUSE_PATTERNS:
        for m in pattern.finditer(text):
            start = m.start()
            title = m.group(2).strip() if m.lastindex and m.lastindex >= 2 else m.group(1).strip()
            matches.append((start, title, start))

    if not matches:
        return []

    matches.sort(key=lambda x: x[0])
    # deduplicate by start position, keeping first (most specific) match
    seen: set[int] = set()
    deduped: list[tuple[int, str, int]] = []
    for start, title, _ in matches:
        if start not in seen:
            seen.add(start)
            deduped.append((start, title, start))
    matches = deduped
    clauses: list[ClauseItem] = []
    for i, (start, title, _) in enumerate(matches):
        end = matches[i + 1][0] if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        clauses.append(ClauseItem(title=title, content=content, order_index=i))

    return clauses
