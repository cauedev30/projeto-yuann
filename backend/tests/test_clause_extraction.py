from app.domain.clause_extraction import extract_clauses, ClauseItem

def test_extract_clauses_basic():
    text = """
CLÁUSULA 1 - OBJETO
O objeto do presente contrato é a locação do imóvel.
CLÁUSULA 2 - PRAZO
O prazo de vigência é de 60 meses.
"""
    clauses = extract_clauses(text)
    assert len(clauses) == 2
    assert clauses[0].title == "OBJETO"
    assert "locação" in clauses[0].content
    assert clauses[1].title == "PRAZO"
    assert "60 meses" in clauses[1].content

def test_extract_clauses_artigo():
    text = "Art. 1º - Do Objeto\nLocação do imóvel.\nArt. 2º - Do Prazo\n60 meses."
    clauses = extract_clauses(text)
    assert len(clauses) == 2
    assert "Objeto" in clauses[0].title
