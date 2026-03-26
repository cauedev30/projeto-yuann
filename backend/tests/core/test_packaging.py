from __future__ import annotations

from pathlib import Path
import tomllib


def test_backend_packaging_declares_pymupdf_dependency() -> None:
    backend_dir = Path(__file__).resolve().parents[2]

    pyproject = tomllib.loads((backend_dir / "pyproject.toml").read_text())
    requirements = (backend_dir / "requirements.txt").read_text().splitlines()

    pyproject_dependencies = pyproject["project"]["dependencies"]

    assert any(dependency.startswith("PyMuPDF") for dependency in pyproject_dependencies)
    assert any(requirement.startswith("PyMuPDF") for requirement in requirements)


def test_backend_packaging_does_not_declare_gemini_dependency() -> None:
    backend_dir = Path(__file__).resolve().parents[2]

    pyproject = tomllib.loads((backend_dir / "pyproject.toml").read_text())
    requirements = (backend_dir / "requirements.txt").read_text().splitlines()

    pyproject_dependencies = pyproject["project"]["dependencies"]

    assert all("google-genai" not in dependency for dependency in pyproject_dependencies)
    assert all("google-genai" not in requirement for requirement in requirements)
