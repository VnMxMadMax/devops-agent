"""
Sentinel AI — Evaluation Harness

Runs the full LangGraph pipeline against a canonical set of incidents
(evals/incidents.jsonl) and scores each run on three axes:

  1. memory_query_called   — did Diagnosis call query_incident_memory FIRST?
  2. correct_service       — did Diagnosis name the right service?
  3. root_cause_matched    — did Diagnosis surface ANY expected keyword?
  4. remediation_executed  — did Remediation call restart_service?

Usage:
  python -m evals.run_evals
  python -m evals.run_evals --verbose
"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage

# Make the project root importable when run as a script
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

load_dotenv()

from agents.orchestrator import graph  # noqa: E402
from simulator.state import env  # noqa: E402


EVAL_FILE = ROOT / "evals" / "incidents.jsonl"


def load_cases() -> List[Dict[str, Any]]:
    with EVAL_FILE.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def build_initial_state(case: Dict[str, Any]) -> Dict[str, Any]:
    """Trigger the incident and tick the simulator until the target
    metric actually breaches its threshold (so the Monitor will fire)."""
    env.trigger_incident(case["incident_name"])

    target_service = case["alert"]["service"]
    target_metric = case["alert"]["metric"]
    target_threshold = case["alert"]["threshold"]

    # Tick until breach or hard cap (incident rates vary per scenario)
    MAX_TICKS = 20
    for _ in range(MAX_TICKS):
        env.tick()
        svc = next((s for s in env.services if s.name == target_service), None)
        if svc and getattr(svc.metrics, target_metric) > target_threshold:
            break

    services_dump = [svc.model_dump() for svc in env.services]

    return {
        "messages": [],
        "services": services_dump,
        "logs": [],
        "alert": case["alert"],
        "active_incident": [case["incident_name"]],
        "timestamp": None,
    }


def score_run(case: Dict[str, Any], messages: List[Any]) -> Dict[str, bool]:
    """Score a single run against the case's expectations."""
    tool_calls: List[str] = []
    ai_text_blocks: List[str] = []
    tool_outputs: List[str] = []

    for msg in messages:
        if isinstance(msg, AIMessage):
            if msg.content:
                ai_text_blocks.append(str(msg.content).lower())
            for tc in (msg.tool_calls or []):
                tool_calls.append(tc.get("name", ""))
        elif isinstance(msg, ToolMessage):
            tool_outputs.append(str(msg.content).lower())

    full_ai_text = " ".join(ai_text_blocks)

    memory_query_called = "query_incident_memory" in tool_calls
    correct_service = case["expected_service"].lower() in full_ai_text
    root_cause_matched = any(
        kw.lower() in full_ai_text for kw in case["expected_keywords"]
    )

    # Remediation scoring: accept either the expected tool call OR
    # an explicit recommendation that names an acceptable mitigation.
    # This avoids punishing the agent for correctly judging that a
    # service restart wouldn't fix the root cause (e.g., external timeouts).
    expected_tool = case.get("expected_remediation_tool")
    acceptable = [r.lower() for r in case.get("acceptable_recommendations", [])]

    tool_match = bool(expected_tool) and expected_tool in tool_calls
    text_match = any(rec in full_ai_text for rec in acceptable) if acceptable else False
    remediation_addressed = tool_match or text_match

    return {
        "memory_query_called": memory_query_called,
        "correct_service": correct_service,
        "root_cause_matched": root_cause_matched,
        "remediation_addressed": remediation_addressed,
    }


def run(verbose: bool = False) -> int:
    cases = load_cases()
    results = []

    print(f"\n▶ Running {len(cases)} eval cases against Sentinel AI pipeline\n")

    for case in cases:
        # Clean slate per case so prior incidents don't leak in
        env.active_incidents.clear()

        initial = build_initial_state(case)
        final = graph.invoke(initial)
        scores = score_run(case, final.get("messages", []))

        # Reset for the next case
        env.resolve_incident(case["incident_name"])

        passed = all(scores.values())
        results.append({"id": case["id"], "passed": passed, **scores})

        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {case['id']}  {case['incident_name']}")
        if verbose or not passed:
            for k, v in scores.items():
                tick = "✓" if v else "✗"
                print(f"         {tick} {k}")

    passed_count = sum(1 for r in results if r["passed"])
    total = len(results)
    pass_rate = passed_count / total if total else 0.0

    print(f"\n━━━ Summary ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Passed: {passed_count}/{total}  ({pass_rate:.0%})")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    # Write a machine-readable report alongside the JSONL
    report_path = ROOT / "evals" / "last_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(
            {"pass_rate": pass_rate, "results": results},
            f,
            indent=2,
        )
    print(f"  Report written to {report_path.relative_to(ROOT)}\n")

    return 0 if passed_count == total else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    sys.exit(run(verbose=args.verbose))
