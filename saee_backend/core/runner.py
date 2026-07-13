"""Public-shell runner for SAEE MVP API requests."""

from __future__ import annotations

from saee_backend.core.evaluator import (
    AgentEvaluation,
    build_failure_report,
    build_ranking_items,
    build_stability_report,
    build_survival_curve,
    evaluate_agent_runs,
    mean_score,
)
from saee_backend.core.simulator import simulate_competition_runs, stable_id
from saee_backend.models.request import ScenarioBatchRequest
from saee_backend.models.response import (
    AgentScore,
    ComparisonRanking,
    DecisionResult,
    EvaluationRunSummary,
    FailureModeReport,
    OverallStats,
)
from saee_backend.services.public_input_contract import validate_scenario_request
from saee_backend.storage.memory_db import (
    AgentMetricRecord,
    AgentRunRecord,
    ExperimentResult,
)
from saee_backend.storage.secret_boundary import validate_persistable_experiment_result


def _request_payload(req: ScenarioBatchRequest) -> dict:
    return req.model_dump(mode="json")


def _experiment_id(req: ScenarioBatchRequest) -> str:
    return req.experiment_id or stable_id("exp", _request_payload(req))


def _run_id(req: ScenarioBatchRequest, experiment_id: str) -> str:
    payload = _request_payload(req)
    payload["resolved_experiment_id"] = experiment_id
    return stable_id("run", payload)


def _run_records(evaluations: list[AgentEvaluation]) -> list[AgentRunRecord]:
    records: list[AgentRunRecord] = []
    for evaluation in evaluations:
        for trace in evaluation.traces:
            records.append(
                AgentRunRecord(
                    agent_id=trace.agent_id,
                    run_index=trace.run_index,
                    scores=trace.scores,
                    alive=trace.alive,
                    collapse_step=trace.collapse_step,
                )
            )
    return records


def _metric_records(evaluations: list[AgentEvaluation]) -> list[AgentMetricRecord]:
    return [
        AgentMetricRecord(
            agent_id=evaluation.agent_id,
            stability_score=evaluation.stability_score,
            survival_score=evaluation.survival_score,
            failure_rate=evaluation.failure_rate,
            collapse_events=evaluation.collapse_events,
            drift_index=evaluation.drift_index,
            risk_score=evaluation.risk_score,
            ranking_score=evaluation.ranking_score,
        )
        for evaluation in evaluations
    ]


def _failure_modes_summary(failure_reports: list[FailureModeReport]) -> dict[str, list[str]]:
    return {
        report.agent_id: [mode.type for mode in report.failure_modes]
        for report in failure_reports
    }


def _decision_result(
    experiment_id: str,
    ranking: ComparisonRanking,
    failure_reports: list[FailureModeReport],
) -> DecisionResult:
    recommended_agent = ranking.ranking[0].agent_id if ranking.ranking else None
    confidence_score = ranking.ranking[0].score if ranking.ranking else 0.0
    return DecisionResult(
        recommended_agent=recommended_agent,
        confidence_score=confidence_score,
        ranking=ranking.ranking,
        failure_modes_summary=_failure_modes_summary(failure_reports),
    )


def run_scenario_batch(req: ScenarioBatchRequest) -> ExperimentResult:
    validate_scenario_request(req)
    experiment_id = _experiment_id(req)
    run_id = _run_id(req, experiment_id)
    repeat_runs = req.evaluation_config.repeat_runs
    traces_by_agent = simulate_competition_runs(req.agents, req.environment, repeat_runs)
    evaluations = [
        evaluate_agent_runs(
            agent.agent_id,
            traces_by_agent.get(agent.agent_id, []),
        )
        for agent in req.agents
    ]
    stability_reports = [build_stability_report(evaluation) for evaluation in evaluations]
    failure_reports = [build_failure_report(evaluation) for evaluation in evaluations]
    survival_curves = [build_survival_curve(evaluation) for evaluation in evaluations]
    ranking_items = build_ranking_items(evaluations)
    ranking = ComparisonRanking(experiment_id=experiment_id, ranking=ranking_items)
    score_by_agent = {item.agent_id: item.score for item in ranking_items}
    agent_scores = [
        AgentScore(agent_id=agent.agent_id, final_score=score_by_agent.get(agent.agent_id, 0.0))
        for agent in req.agents
    ]
    mean_stability = mean_score([evaluation.stability_score for evaluation in evaluations])
    mean_survival = mean_score([evaluation.survival_score for evaluation in evaluations])
    decision = _decision_result(experiment_id, ranking, failure_reports)
    divergence = max([score.final_score for score in agent_scores], default=0.0) - min(
        [score.final_score for score in agent_scores], default=0.0
    )
    summary = EvaluationRunSummary(
        experiment_id=experiment_id,
        run_id=run_id,
        status="completed",
        agents=agent_scores,
        overall_stats=OverallStats(
            mean_stability=mean_stability,
            mean_survival=mean_survival,
            divergence_index=round(divergence, 6),
        ),
        decision_result=decision,
        recommended_agent=decision.recommended_agent,
        confidence_score=decision.confidence_score,
    )
    result = ExperimentResult(
        summary=summary,
        stability_reports=stability_reports,
        failure_reports=failure_reports,
        survival_curves=survival_curves,
        ranking=ranking,
        runs=_run_records(evaluations),
        metrics=_metric_records(evaluations),
        agent_outputs={
            evaluation.agent_id: {
                "aggregate_scores": evaluation.aggregate_scores,
                "aggregate_alive": evaluation.aggregate_alive,
                "risk_score": evaluation.risk_score,
                "drift_index": evaluation.drift_index,
            }
            for evaluation in evaluations
        },
    )
    validate_persistable_experiment_result(result)
    return result
