from __future__ import annotations

import argparse
import json
import os
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from dotenv import load_dotenv

from app.domain.contract_analysis import (
    calculate_final_risk_score,
    evaluate_rules,
    extract_contract_facts,
    merge_analysis_items,
)
from app.domain.playbook import PLAYBOOK_CLAUSES
from app.infrastructure.contract_chunker import chunk_contract
from app.infrastructure.openai_client import OpenAIAnalysisClient
from app.schemas.analysis import AnalysisItem


DEFAULT_POLICY_RULES = [
    {"code": "MIN_TERM_MONTHS", "value": 48, "description": "Prazo minimo de vigencia: 48 meses"},
    {"code": "MAX_TERM_MONTHS", "value": 60, "description": "Prazo maximo de vigencia: 60 meses"},
    {"code": "MAX_FINE_MONTHS", "value": 3, "description": "Multa maxima: 3 alugueis"},
    {"code": "MAX_VALUE", "value": 3000, "description": "Valor maximo do contrato: R$ 3.000"},
    {"code": "GRACE_PERIOD_DAYS", "value": [0, 30, 60, 90], "description": "Periodos de carencia permitidos (dias)"},
]

CANONICAL_IDENTIFIER_ALIASES: dict[str, tuple[str, ...]] = {
    "prazo": ("PRAZO", "RENOVACAO", "PRAZO DE VIGENCIA"),
    "valor": ("VALOR", "ALUGUEL"),
    "reajuste": ("REAJUSTE",),
    "exclusividade": ("EXCLUSIVIDADE",),
    "cessao": ("CESSAO", "SUBLOC"),
    "garantia": ("GARANTIA", "FIADOR"),
    "vistorias": ("VISTORIA",),
    "obras": ("OBRAS", "BENFEITOR"),
    "infraestrutura": ("INFRA",),
    "assinaturas": ("ASSINAT", "FORMALIZ"),
    "condominio": ("CONDOMIN"),
    "nao-fazer": ("NAO_FAZER", "NAO FAZER"),
    "carencia": ("CARENCIA",),
}


@dataclass(frozen=True)
class BenchmarkPricing:
    # Source: https://platform.openai.com/pricing on 2026-03-25.
    input_cost_per_1m: float = 0.25
    output_cost_per_1m: float = 2.0


@dataclass(frozen=True)
class BenchmarkVersionCase:
    label: str
    text: str
    must_include_identifiers: tuple[str, ...] = ()
    must_exclude_identifiers: tuple[str, ...] = ()
    min_expected_score: float | None = None
    max_expected_score: float | None = None


@dataclass(frozen=True)
class BenchmarkScenario:
    scenario_id: str
    title: str
    versions: tuple[BenchmarkVersionCase, ...]
    expected_diff_identifiers: tuple[str, ...] = ()
    min_changed_identifiers: int = 1
    min_score_drop: float = 0.0


@dataclass(frozen=True)
class BenchmarkVersionResult:
    label: str
    final_risk_score: float
    observed_identifiers: set[str]
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float


DEFAULT_BENCHMARK_CASES = [
    BenchmarkScenario(
        scenario_id="lease-redraft",
        title="Draft with missing safeguards versus corrected version",
        versions=(
            BenchmarkVersionCase(
                label="v1",
                text=(
                    "CONTRATO DE LOCACAO COMERCIAL\n"
                    "CLAUSULA 1 - PRAZO. O prazo de vigencia e de 24 meses.\n"
                    "CLAUSULA 2 - ALUGUEL. O aluguel mensal sera de R$ 8500,00, com carencia de 45 dias.\n"
                    "CLAUSULA 3 - CESSAO. O LOCATARIO podera ceder ou sublocar livremente o imovel.\n"
                    "CLAUSULA 4 - OBRAS. Reformas estruturais dependem de alinhamento futuro entre as partes.\n"
                ),
                must_include_identifiers=("PRAZO", "EXCLUSIVIDADE", "valor"),
                must_exclude_identifiers=(),
                min_expected_score=45,
            ),
            BenchmarkVersionCase(
                label="v2",
                text=(
                    "CONTRATO DE LOCACAO COMERCIAL\n"
                    "CLAUSULA 1 - PRAZO E RENOVACAO. O prazo de vigencia e de 60 meses. Nao havendo comunicacao em contrario, por qualquer das partes, com no minimo 90 dias antes do encerramento, este contrato sera renovado automaticamente por igual periodo.\n"
                    "CLAUSULA 2 - ALUGUEL E REAJUSTE. O aluguel mensal sera de R$ 2900,00, com carencia de 30 dias. O reajuste observara o indice IPCA, com periodicidade anual e data-base no aniversario do contrato, vedado aumento arbitrario sem criterio objetivo.\n"
                    "CLAUSULA 3 - EXCLUSIVIDADE E OBRIGACAO DE NAO FAZER. O LOCADOR nao locara, sublocara ou explorara ponto ou espaco comercial, dentro do mesmo imovel, para atividades de lavanderia ou afins. Caso se opere o distrato ou nao se efetive a renovacao por decisao unilateral do LOCADOR, este fica impedido de locar o ponto para lavanderias ou afins pelo prazo de 24 meses.\n"
                    "CLAUSULA 4 - CESSAO, SUBLOCACAO E DESTINACAO. E expressamente proibido ao LOCATARIO sublocar, ceder ou emprestar o imovel, no todo ou em parte, ou transferir o presente contrato. De forma excepcional, sera autorizada a exploracao do ponto exclusivamente por franqueados e parceiros comerciais da rede, sem qualquer cobranca adicional. Sob nenhuma hipotese podera ser alterada a destinacao do ponto comercial.\n"
                    "CLAUSULA 5 - GARANTIA LOCATICIA. A garantia da locacao fica expressamente definida na modalidade fiador, com responsabilidade solidaria clara e assinatura do fiador neste instrumento, em conformidade com a Lei 8.245/1991. Ocorrendo a necessidade de substituicao do fiador, a LOCATARIA apresentara novo fiador ou substituira a modalidade de garantia mediante aprovacao da administradora.\n"
                    "CLAUSULA 6 - VISTORIAS. Toda e qualquer vistoria sera realizada na presenca do LOCATARIO ou de pessoa por ele indicada, com laudos inicial e final anexados a este instrumento.\n"
                    "CLAUSULA 7 - OBRAS E BENFEITORIAS. O LOCATARIO nao podera realizar qualquer modificacao ou benfeitoria estrutural no imovel sem a previa e expressa autorizacao por escrito do LOCADOR. Ficam desde ja autorizadas adaptacao da rede eletrica trifasica, adequacoes de agua e esgoto, instalacao de equipamentos, divisorias internas, comunicacao visual, ACM, luminoso, exaustao, piso e relogios medidores necessarios a operacao.\n"
                    "CLAUSULA 8 - INFRAESTRUTURA, CONDOMINIO E RESCISAO. O LOCADOR manifesta sua ciencia quanto a necessidade de infraestrutura e licencas minimas necessarias para viabilizar a operacao da lavanderia, incluindo rede de agua, esgoto, energia trifasica e licencas publicas. O LOCADOR declara que inexiste estatuto ou convencao condominial que vede a presente atividade. Caso a infraestrutura ou as licencas inviabilizem tecnicamente ou legalmente a implantacao da loja, a presente avenca sera rescindida de pleno direito, sem penalidade para as partes, garantido ao LOCADOR o recebimento dos alugueis ate a data de entrega do ponto.\n"
                    "CLAUSULA 9 - ASSINATURAS E FORMALIZACAO. O instrumento sera assinado digitalmente por LOCADOR, LOCATARIA, fiador e duas testemunhas, com qualificacao minima suficiente para validade e execucao do contrato.\n"
                ),
                must_include_identifiers=(),
                must_exclude_identifiers=(),
                max_expected_score=45,
            ),
        ),
        expected_diff_identifiers=(),
        min_changed_identifiers=3,
        min_score_drop=40.0,
    )
]


def normalize_identifier(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    stripped = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    collapsed = " ".join(stripped.strip().split())
    if collapsed.isupper():
        return collapsed
    return collapsed.lower()


def canonicalize_identifier(value: str) -> str:
    normalized = normalize_identifier(value)
    normalized_upper = normalized.upper()

    for canonical, markers in CANONICAL_IDENTIFIER_ALIASES.items():
        if any(marker in normalized_upper for marker in markers):
            return canonical

    return normalized


def derive_item_identifier(item: AnalysisItem) -> str:
    clause_code = item.metadata.get("clause_code")
    if isinstance(clause_code, str) and clause_code.strip():
        return canonicalize_identifier(clause_code)
    return canonicalize_identifier(item.clause_name)


def estimate_analysis_cost_usd(
    *,
    prompt_tokens: int,
    completion_tokens: int,
    pricing: BenchmarkPricing,
) -> float:
    input_cost = (prompt_tokens / 1_000_000) * pricing.input_cost_per_1m
    output_cost = (completion_tokens / 1_000_000) * pricing.output_cost_per_1m
    return round(input_cost + output_cost, 6)


def evaluate_version_expectations(
    *,
    version_result: BenchmarkVersionResult,
    must_include_identifiers: tuple[str, ...],
    must_exclude_identifiers: tuple[str, ...],
    min_expected_score: float | None,
    max_expected_score: float | None,
) -> dict[str, Any]:
    normalized_required = {canonicalize_identifier(identifier) for identifier in must_include_identifiers}
    normalized_excluded = {canonicalize_identifier(identifier) for identifier in must_exclude_identifiers}

    missing_identifiers = sorted(normalized_required - version_result.observed_identifiers)
    unexpected_identifiers = sorted(version_result.observed_identifiers & normalized_excluded)

    score_within_expected_range = True
    if min_expected_score is not None and version_result.final_risk_score < min_expected_score:
        score_within_expected_range = False
    if max_expected_score is not None and version_result.final_risk_score > max_expected_score:
        score_within_expected_range = False

    return {
        "missing_identifiers": missing_identifiers,
        "unexpected_identifiers": unexpected_identifiers,
        "score_within_expected_range": score_within_expected_range,
        "quality_passed": not missing_identifiers and not unexpected_identifiers and score_within_expected_range,
    }


def compare_version_results(
    previous: BenchmarkVersionResult,
    current: BenchmarkVersionResult,
) -> dict[str, Any]:
    return {
        "from_label": previous.label,
        "to_label": current.label,
        "changed_identifiers": sorted(previous.observed_identifiers ^ current.observed_identifiers),
        "score_delta": round(current.final_risk_score - previous.final_risk_score, 2),
    }


def evaluate_diff_expectations(
    *,
    diff: dict[str, Any],
    expected_identifiers: tuple[str, ...],
    min_changed_identifiers: int,
    min_score_drop: float,
) -> dict[str, Any]:
    expected_diff = {canonicalize_identifier(identifier) for identifier in expected_identifiers}
    changed_identifiers = set(diff["changed_identifiers"])
    missing_expected_identifiers = sorted(expected_diff - changed_identifiers)
    changed_identifiers_count = len(changed_identifiers)
    score_drop_passed = float(diff["score_delta"]) <= (0 - float(min_score_drop))
    diff_passed = (
        not missing_expected_identifiers
        and changed_identifiers_count >= min_changed_identifiers
        and score_drop_passed
    )

    return {
        "missing_expected_identifiers": missing_expected_identifiers,
        "changed_identifiers_count": changed_identifiers_count,
        "score_drop_passed": score_drop_passed,
        "diff_passed": diff_passed,
    }


def load_benchmark_cases(path: Path | None = None) -> list[BenchmarkScenario]:
    if path is None:
        return list(DEFAULT_BENCHMARK_CASES)

    raw_cases = json.loads(path.read_text(encoding="utf-8"))
    cases: list[BenchmarkScenario] = []
    for case in raw_cases:
        versions = tuple(
            BenchmarkVersionCase(
                label=version["label"],
                text=version["text"],
                must_include_identifiers=tuple(version.get("must_include_identifiers", [])),
                must_exclude_identifiers=tuple(version.get("must_exclude_identifiers", [])),
                min_expected_score=version.get("min_expected_score"),
                max_expected_score=version.get("max_expected_score"),
            )
            for version in case["versions"]
        )
        cases.append(
            BenchmarkScenario(
                scenario_id=case["scenario_id"],
                title=case["title"],
                versions=versions,
                expected_diff_identifiers=tuple(case.get("expected_diff_identifiers", [])),
                min_changed_identifiers=int(case.get("min_changed_identifiers", 1)),
                min_score_drop=float(case.get("min_score_drop", 0.0)),
            )
        )
    return cases


def _llm_item_to_analysis_item(item: Any) -> AnalysisItem:
    clause_code = str(getattr(item, "clause_code", "")).strip().upper()
    return AnalysisItem(
        clause_name=str(getattr(item, "clause_title", "")).strip() or clause_code,
        status=str(getattr(item, "severity", "attention")),
        severity="high" if str(getattr(item, "severity", "attention")) == "critical" else "medium",
        current_summary=str(getattr(item, "explanation", "")).strip(),
        policy_rule=clause_code,
        risk_explanation=str(getattr(item, "explanation", "")).strip(),
        suggested_adjustment_direction=str(getattr(item, "suggested_correction", "")).strip(),
        metadata={
            "category": "essencial" if clause_code in {"EXCLUSIVIDADE", "PRAZO", "ASSINATURAS"} else "redacao",
            "essential_clause": clause_code in {"EXCLUSIVIDADE", "PRAZO", "ASSINATURAS"},
            "risk_score": getattr(item, "risk_score", 0),
            "clause_code": clause_code,
            "page_reference": getattr(item, "page_reference", None),
        },
    )


def run_version_case(
    *,
    client: OpenAIAnalysisClient,
    version: BenchmarkVersionCase,
    pricing: BenchmarkPricing,
) -> BenchmarkVersionResult:
    chunk_texts = [chunk.content for chunk in chunk_contract(version.text)]
    llm_result = client.analyze_contract(chunks=chunk_texts, playbook=list(PLAYBOOK_CLAUSES))
    llm_items = [_llm_item_to_analysis_item(item) for item in llm_result.items]
    deterministic_result = evaluate_rules(DEFAULT_POLICY_RULES, extract_contract_facts(version.text))
    merged_items = merge_analysis_items(llm_items, deterministic_result.items)
    filtered_items = [item for item in merged_items if item.status != "conforme"]
    final_risk_score = calculate_final_risk_score(
        llm_score=float(llm_result.contract_risk_score),
        llm_items=llm_items,
        deterministic_items=deterministic_result.items,
    )
    usage = client.last_analysis_usage
    prompt_tokens = usage.prompt_tokens if usage is not None else 0
    completion_tokens = usage.completion_tokens if usage is not None else 0
    total_tokens = usage.total_tokens if usage is not None else 0

    return BenchmarkVersionResult(
        label=version.label,
        final_risk_score=final_risk_score,
        observed_identifiers={derive_item_identifier(item) for item in filtered_items},
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        estimated_cost_usd=estimate_analysis_cost_usd(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            pricing=pricing,
        ),
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the F6-E OpenAI benchmark against local contract scenarios.")
    parser.add_argument("--cases", type=Path, default=None, help="Optional JSON file with benchmark scenarios.")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON output path.")
    parser.add_argument("--runs", type=int, default=2, help="Number of analysis runs per version.")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-5-mini"), help="OpenAI model override.")
    parser.add_argument("--max-score-spread", type=float, default=20.0, help="Maximum acceptable score spread for repeated runs.")
    parser.add_argument("--max-average-cost-usd", type=float, default=0.03, help="Maximum acceptable average cost per version run.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is required to run the benchmark.", file=sys.stderr)
        return 2

    client = OpenAIAnalysisClient(api_key=api_key, model=args.model)
    pricing = BenchmarkPricing()
    cases = load_benchmark_cases(args.cases)

    scenario_reports: list[dict[str, Any]] = []
    all_costs: list[float] = []
    all_spreads: list[float] = []
    overall_acceptance = True

    for case in cases:
        version_reports: list[dict[str, Any]] = []
        scenario_acceptance = True
        version_results_for_diff: list[BenchmarkVersionResult] = []

        for version in case.versions:
            runs = [
                run_version_case(client=client, version=version, pricing=pricing)
                for _ in range(max(args.runs, 1))
            ]
            version_results_for_diff.append(runs[-1])
            scores = [run.final_risk_score for run in runs]
            costs = [run.estimated_cost_usd for run in runs]
            score_spread = round(max(scores) - min(scores), 2)
            evaluation = evaluate_version_expectations(
                version_result=runs[-1],
                must_include_identifiers=version.must_include_identifiers,
                must_exclude_identifiers=version.must_exclude_identifiers,
                min_expected_score=version.min_expected_score,
                max_expected_score=version.max_expected_score,
            )
            evaluation["score_spread"] = score_spread
            evaluation["stability_passed"] = score_spread <= args.max_score_spread

            all_costs.extend(costs)
            all_spreads.append(score_spread)
            scenario_acceptance = scenario_acceptance and evaluation["quality_passed"] and evaluation["stability_passed"]

            version_reports.append(
                {
                    "label": version.label,
                    "runs": [
                        {
                            "final_risk_score": run.final_risk_score,
                            "observed_identifiers": sorted(run.observed_identifiers),
                            "prompt_tokens": run.prompt_tokens,
                            "completion_tokens": run.completion_tokens,
                            "total_tokens": run.total_tokens,
                            "estimated_cost_usd": run.estimated_cost_usd,
                        }
                        for run in runs
                    ],
                    "average_score": round(mean(scores), 2),
                    "average_cost_usd": round(mean(costs), 6),
                    "evaluation": evaluation,
                }
            )

        diff_reports: list[dict[str, Any]] = []
        for previous, current in zip(version_results_for_diff, version_results_for_diff[1:]):
            diff = compare_version_results(previous, current)
            diff.update(
                evaluate_diff_expectations(
                    diff=diff,
                    expected_identifiers=case.expected_diff_identifiers,
                    min_changed_identifiers=case.min_changed_identifiers,
                    min_score_drop=case.min_score_drop,
                )
            )
            scenario_acceptance = scenario_acceptance and diff["diff_passed"]
            diff_reports.append(diff)

        scenario_reports.append(
            {
                "scenario_id": case.scenario_id,
                "title": case.title,
                "versions": version_reports,
                "diffs": diff_reports,
                "scenario_passed": scenario_acceptance,
            }
        )
        overall_acceptance = overall_acceptance and scenario_acceptance

    average_cost = round(mean(all_costs), 6) if all_costs else 0.0
    max_score_spread = round(max(all_spreads), 2) if all_spreads else 0.0
    if average_cost > args.max_average_cost_usd:
        overall_acceptance = False

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": args.model,
        "pricing": {
            "input_cost_per_1m": pricing.input_cost_per_1m,
            "output_cost_per_1m": pricing.output_cost_per_1m,
        },
        "scenarios": scenario_reports,
        "overall": {
            "average_cost_usd": average_cost,
            "max_score_spread": max_score_spread,
            "max_average_cost_usd": args.max_average_cost_usd,
            "max_allowed_score_spread": args.max_score_spread,
            "acceptable": overall_acceptance,
        },
    }

    output = json.dumps(report, ensure_ascii=True, indent=2)
    print(output)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")

    return 0 if overall_acceptance else 1


if __name__ == "__main__":
    raise SystemExit(main())
