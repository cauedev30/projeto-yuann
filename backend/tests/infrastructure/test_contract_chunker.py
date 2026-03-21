"""Tests for contract text chunker with clause-aware splitting."""

import pytest

from app.infrastructure.contract_chunker import ContractChunk, chunk_contract


class TestContractChunk:
    """Tests for the ContractChunk dataclass."""

    def test_contract_chunk_fields(self):
        chunk = ContractChunk(header="CLÁUSULA PRIMEIRA", content="Texto da cláusula.", source_page=None)
        assert chunk.header == "CLÁUSULA PRIMEIRA"
        assert chunk.content == "Texto da cláusula."
        assert chunk.source_page is None

    def test_contract_chunk_with_page(self):
        chunk = ContractChunk(header="Art. 1", content="Conteúdo.", source_page=3)
        assert chunk.source_page == 3


class TestChunkContractByCláusula:
    """Tests for splitting by CLÁUSULA pattern."""

    def test_split_single_clausula(self):
        text = "CLÁUSULA PRIMEIRA\nConteúdo da primeira cláusula."
        chunks = chunk_contract(text)
        assert len(chunks) == 1
        assert chunks[0].header == "CLÁUSULA PRIMEIRA"
        assert "Conteúdo da primeira cláusula." in chunks[0].content

    def test_split_multiple_clausulas(self):
        text = (
            "CLÁUSULA PRIMEIRA\n"
            "Conteúdo da primeira cláusula.\n"
            "CLÁUSULA SEGUNDA\n"
            "Conteúdo da segunda cláusula.\n"
            "CLÁUSULA TERCEIRA\n"
            "Conteúdo da terceira cláusula."
        )
        chunks = chunk_contract(text)
        assert len(chunks) == 3
        assert chunks[0].header == "CLÁUSULA PRIMEIRA"
        assert chunks[1].header == "CLÁUSULA SEGUNDA"
        assert chunks[2].header == "CLÁUSULA TERCEIRA"

    def test_split_clausula_roman_numerals(self):
        text = (
            "CLÁUSULA I\n"
            "Primeiro conteúdo.\n"
            "CLÁUSULA II\n"
            "Segundo conteúdo."
        )
        chunks = chunk_contract(text)
        assert len(chunks) == 2
        assert chunks[0].header == "CLÁUSULA I"
        assert chunks[1].header == "CLÁUSULA II"

    def test_header_preserved_in_content(self):
        text = (
            "CLÁUSULA PRIMEIRA\n"
            "Conteúdo da primeira cláusula.\n"
            "CLÁUSULA SEGUNDA\n"
            "Conteúdo da segunda cláusula."
        )
        chunks = chunk_contract(text)
        assert chunks[0].content.startswith("CLÁUSULA PRIMEIRA")
        assert chunks[1].content.startswith("CLÁUSULA SEGUNDA")


class TestChunkContractByArtigo:
    """Tests for splitting by Art. pattern."""

    def test_split_by_artigo(self):
        text = (
            "Art. 1 Disposições gerais.\n"
            "Conteúdo do artigo 1.\n"
            "Art. 2 Obrigações.\n"
            "Conteúdo do artigo 2."
        )
        chunks = chunk_contract(text)
        assert len(chunks) == 2
        assert chunks[0].header == "Art. 1"
        assert chunks[1].header == "Art. 2"

    def test_split_by_artigo_multidigit(self):
        text = (
            "Art. 10 Primeiro.\n"
            "Conteúdo.\n"
            "Art. 25 Segundo.\n"
            "Outro conteúdo."
        )
        chunks = chunk_contract(text)
        assert len(chunks) == 2
        assert chunks[0].header == "Art. 10"
        assert chunks[1].header == "Art. 25"

    def test_artigo_no_space_after_dot(self):
        text = (
            "Art.1 Primeiro.\n"
            "Conteúdo.\n"
            "Art.2 Segundo.\n"
            "Outro conteúdo."
        )
        chunks = chunk_contract(text)
        assert len(chunks) == 2


class TestChunkContractFallback:
    """Tests for fallback chunking when no clause markers found."""

    def test_empty_text(self):
        chunks = chunk_contract("")
        assert chunks == []

    def test_short_text_no_markers(self):
        text = "Este é um texto curto sem marcadores de cláusula."
        chunks = chunk_contract(text)
        assert len(chunks) == 1
        assert chunks[0].header == ""
        assert chunks[0].content == text

    def test_fallback_long_text_creates_overlapping_chunks(self):
        # Create text longer than 2000 chars
        text = "A" * 5000
        chunks = chunk_contract(text)
        assert len(chunks) > 1
        # Verify overlap: end of one chunk overlaps with start of next
        for i in range(len(chunks) - 1):
            current_end = chunks[i].content[-200:]
            next_start = chunks[i + 1].content[:200]
            assert current_end == next_start

    def test_fallback_chunks_have_empty_header(self):
        text = "B" * 5000
        chunks = chunk_contract(text)
        for chunk in chunks:
            assert chunk.header == ""

    def test_source_page_is_none(self):
        text = "CLÁUSULA PRIMEIRA\nConteúdo."
        chunks = chunk_contract(text)
        for chunk in chunks:
            assert chunk.source_page is None


class TestChunkContractMixed:
    """Tests for text with preamble before first clause."""

    def test_preamble_before_clausulas(self):
        text = (
            "CONTRATO DE PRESTAÇÃO DE SERVIÇOS\n"
            "Partes envolvidas: Empresa X e Empresa Y.\n"
            "CLÁUSULA PRIMEIRA\n"
            "Conteúdo da primeira cláusula.\n"
            "CLÁUSULA SEGUNDA\n"
            "Conteúdo da segunda cláusula."
        )
        chunks = chunk_contract(text)
        # Preamble should be included as first chunk or merged
        assert len(chunks) >= 2
        # The clause chunks should have proper headers
        clause_chunks = [c for c in chunks if c.header.startswith("CLÁUSULA")]
        assert len(clause_chunks) == 2
