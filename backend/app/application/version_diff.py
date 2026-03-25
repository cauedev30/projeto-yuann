from __future__ import annotations

from difflib import ndiff

from app.db.models.analysis import ContractAnalysis, ContractAnalysisFinding
from app.db.models.contract import Contract, ContractVersion
from app.schemas.contract import (
    ContractFindingDiffItem,
    ContractFindingsDiff,
    ContractVersionComparisonResponse,
    ContractVersionSummary,
    ContractVersionTextDiff,
    ContractVersionTextDiffLine,
)


def _version_sort_key(version: ContractVersion) -> tuple[int, object, str]:
    return (version.version_number, version.created_at, version.id)


def latest_version_analysis(version: ContractVersion | None) -> ContractAnalysis | None:
    if version is None or not version.analyses:
        return None
    return max(version.analyses, key=lambda analysis: (analysis.created_at, analysis.id))


def _serialize_version(version: ContractVersion) -> ContractVersionSummary:
    metadata = version.extraction_metadata or {}
    return ContractVersionSummary(
        contract_version_id=version.id,
        version_number=version.version_number,
        created_at=version.created_at,
        source=version.source.value,
        original_filename=version.original_filename,
        used_ocr=bool(metadata.get("ocr_attempted")),
        text=version.text_content,
    )


def _build_text_diff(
    baseline_version: ContractVersion | None,
    selected_version: ContractVersion,
) -> ContractVersionTextDiff:
    if baseline_version is None:
        return ContractVersionTextDiff(has_changes=False, lines=[])

    baseline_lines = (baseline_version.text_content or "").splitlines()
    selected_lines = (selected_version.text_content or "").splitlines()
    lines: list[ContractVersionTextDiffLine] = []
    has_changes = False

    for line in ndiff(baseline_lines, selected_lines):
        if line.startswith("? "):
            continue

        kind = "unchanged"
        value = line[2:]
        if line.startswith("- "):
            kind = "removed"
            has_changes = True
        elif line.startswith("+ "):
            kind = "added"
            has_changes = True

        lines.append(ContractVersionTextDiffLine(kind=kind, value=value))

    return ContractVersionTextDiff(has_changes=has_changes, lines=lines)


def _finding_key(finding: ContractAnalysisFinding) -> str:
    return finding.clause_name.strip().casefold()


def _finding_change_type(
    previous_finding: ContractAnalysisFinding | None,
    current_finding: ContractAnalysisFinding | None,
) -> str | None:
    if previous_finding is None and current_finding is not None:
        return "added"
    if previous_finding is not None and current_finding is None:
        return "removed"
    if previous_finding is None or current_finding is None:
        return None

    if (
        previous_finding.status != current_finding.status
        or previous_finding.current_summary != current_finding.current_summary
        or previous_finding.risk_explanation != current_finding.risk_explanation
        or previous_finding.suggested_adjustment_direction
        != current_finding.suggested_adjustment_direction
    ):
        return "changed"

    return None


def _build_findings_diff(
    baseline_analysis: ContractAnalysis | None,
    selected_analysis: ContractAnalysis | None,
) -> ContractFindingsDiff:
    baseline_items = {
        _finding_key(finding): finding for finding in (baseline_analysis.findings if baseline_analysis else [])
    }
    selected_items = {
        _finding_key(finding): finding for finding in (selected_analysis.findings if selected_analysis else [])
    }

    items: list[ContractFindingDiffItem] = []
    for clause_key in sorted(set(baseline_items) | set(selected_items)):
        previous_finding = baseline_items.get(clause_key)
        current_finding = selected_items.get(clause_key)
        change_type = _finding_change_type(previous_finding, current_finding)
        if change_type is None:
            continue

        reference_finding = current_finding or previous_finding
        items.append(
            ContractFindingDiffItem(
                clause_name=reference_finding.clause_name if reference_finding else clause_key,
                change_type=change_type,
                previous_status=previous_finding.status if previous_finding is not None else None,
                current_status=current_finding.status if current_finding is not None else None,
                previous_summary=previous_finding.current_summary if previous_finding is not None else None,
                current_summary=current_finding.current_summary if current_finding is not None else None,
            )
        )

    return ContractFindingsDiff(items=items)


def _build_summary(
    *,
    selected_version: ContractVersion,
    baseline_version: ContractVersion | None,
    text_diff: ContractVersionTextDiff,
    findings_diff: ContractFindingsDiff,
) -> str:
    if baseline_version is None:
        return (
            f"Versao {selected_version.version_number} sem baseline disponivel para comparacao."
        )

    added_lines = sum(1 for line in text_diff.lines if line.kind == "added")
    removed_lines = sum(1 for line in text_diff.lines if line.kind == "removed")
    changed_findings = len(findings_diff.items)
    return (
        f"Comparacao da versao {selected_version.version_number} com a versao "
        f"{baseline_version.version_number}: {added_lines} trechos adicionados, "
        f"{removed_lines} removidos e {changed_findings} mudancas de achados."
    )


def resolve_baseline_version(
    contract: Contract,
    *,
    selected_version: ContractVersion,
    baseline_version_id: str | None = None,
) -> ContractVersion | None:
    if baseline_version_id is not None:
        for version in contract.versions:
            if version.id == baseline_version_id:
                return version
        return None

    ordered_versions = sorted(contract.versions, key=_version_sort_key, reverse=True)
    selected_index = next(
        (index for index, version in enumerate(ordered_versions) if version.id == selected_version.id),
        None,
    )
    if selected_index is None:
        return None
    if selected_index + 1 < len(ordered_versions):
        return ordered_versions[selected_index + 1]
    if selected_index > 0:
        return ordered_versions[selected_index - 1]
    return None


def build_contract_version_comparison(
    contract: Contract,
    *,
    selected_version: ContractVersion,
    baseline_version: ContractVersion | None,
) -> ContractVersionComparisonResponse:
    baseline_analysis = latest_version_analysis(baseline_version)
    selected_analysis = latest_version_analysis(selected_version)
    text_diff = _build_text_diff(baseline_version, selected_version)
    findings_diff = _build_findings_diff(baseline_analysis, selected_analysis)

    return ContractVersionComparisonResponse(
        selected_version=_serialize_version(selected_version),
        baseline_version=_serialize_version(baseline_version) if baseline_version is not None else None,
        summary=_build_summary(
            selected_version=selected_version,
            baseline_version=baseline_version,
            text_diff=text_diff,
            findings_diff=findings_diff,
        ),
        text_diff=text_diff,
        findings_diff=findings_diff,
    )
