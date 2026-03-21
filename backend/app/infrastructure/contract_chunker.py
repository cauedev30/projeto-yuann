"""Contract text chunker with clause-aware splitting.

Splits contract text into meaningful chunks based on clause markers
(CLÁUSULA, Art.) or falls back to character-based chunking with overlap.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ContractChunk:
    """A chunk of contract text."""

    header: str
    content: str
    source_page: int | None


# Primary: CLÁUSULA followed by word chars (e.g. CLÁUSULA PRIMEIRA, CLÁUSULA I)
_CLAUSULA_RE = re.compile(r"^(CLÁUSULA\s+\w+)", re.MULTILINE)

# Secondary: Art. followed by optional space and digits
_ARTIGO_RE = re.compile(r"^(Art\.\s*\d+)", re.MULTILINE)

_FALLBACK_CHUNK_SIZE = 2000
_FALLBACK_OVERLAP = 200


def chunk_contract(text: str) -> list[ContractChunk]:
    """Split contract text into chunks based on clause/article markers.

    Strategy:
    1. Try splitting by CLÁUSULA pattern
    2. Try splitting by Art. pattern
    3. Fallback to ~2000 char chunks with 200 char overlap
    """
    if not text or not text.strip():
        return []

    # Try CLÁUSULA first
    chunks = _split_by_pattern(text, _CLAUSULA_RE)
    if chunks is not None:
        return chunks

    # Try Art.
    chunks = _split_by_pattern(text, _ARTIGO_RE)
    if chunks is not None:
        return chunks

    # Fallback
    return _fallback_chunks(text)


def _split_by_pattern(text: str, pattern: re.Pattern) -> list[ContractChunk] | None:
    """Split text by a regex pattern. Returns None if pattern not found."""
    matches = list(pattern.finditer(text))
    if not matches:
        return None

    chunks: list[ContractChunk] = []

    # Handle preamble (text before first match)
    preamble = text[: matches[0].start()].strip()
    if preamble:
        chunks.append(ContractChunk(header="", content=preamble, source_page=None))

    for i, match in enumerate(matches):
        header = match.group(1)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        chunks.append(ContractChunk(header=header, content=content, source_page=None))

    return chunks


def _fallback_chunks(text: str) -> list[ContractChunk]:
    """Split text into fixed-size chunks with overlap."""
    chunks: list[ContractChunk] = []
    step = _FALLBACK_CHUNK_SIZE - _FALLBACK_OVERLAP
    pos = 0

    while pos < len(text):
        end = pos + _FALLBACK_CHUNK_SIZE
        chunk_text = text[pos:end]
        chunks.append(ContractChunk(header="", content=chunk_text, source_page=None))
        pos += step

    return chunks
