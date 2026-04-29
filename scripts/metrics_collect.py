"""
DORA metrics collector (Phase 7).
Call record_deployment() after each deployment from your CI pipeline.
Data is stored as JSONL in metrics/deployments.jsonl for weekly_retrospective.py.

Usage in CI (after deployment step):
  python scripts/metrics_collect.py --success true --lead-time 12.5
"""
import argparse
import datetime
import json
import pathlib
import sys


METRICS_FILE = pathlib.Path("metrics/deployments.jsonl")


def record_deployment(success: bool, lead_time_minutes: float):
    METRICS_FILE.parent.mkdir(exist_ok=True)
    now = datetime.datetime.utcnow()
    record = {
        "timestamp": now.isoformat(),
        "success": success,
        "lead_time_minutes": round(lead_time_minutes, 1),
        "week": now.isocalendar()[1],
        "year": now.year,
    }
    with open(METRICS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    status = "✅ success" if success else "❌ failure"
    print(f"Recorded deployment: {status}, lead time: {lead_time_minutes:.1f} min")


def compute_weekly_summary() -> dict:
    if not METRICS_FILE.exists():
        return {}
    records = [json.loads(line) for line in METRICS_FILE.read_text().splitlines() if line]
    now = datetime.datetime.utcnow()
    this_week = now.isocalendar()[1]
    this_year = now.year
    week_records = [r for r in records if r.get("week") == this_week and r.get("year") == this_year]
    if not week_records:
        return {}
    failures = [r for r in week_records if not r["success"]]
    lead_times = [r["lead_time_minutes"] for r in week_records]
    return {
        "week": this_week,
        "deployments": len(week_records),
        "failures": len(failures),
        "change_failure_rate": round(len(failures) / len(week_records), 2),
        "avg_lead_time_minutes": round(sum(lead_times) / len(lead_times), 1),
    }


def main():
    parser = argparse.ArgumentParser(description="Record a deployment metric")
    parser.add_argument("--success", required=True, choices=["true", "false"])
    parser.add_argument("--lead-time", type=float, required=True,
                        help="Lead time in minutes (PR creation to deployment)")
    parser.add_argument("--summary", action="store_true",
                        help="Print this week's DORA summary instead of recording")
    args = parser.parse_args()

    if args.summary:
        summary = compute_weekly_summary()
        if summary:
            print(json.dumps(summary, indent=2))
        else:
            print("No deployment data for this week yet.")
        return

    record_deployment(
        success=(args.success == "true"),
        lead_time_minutes=args.lead_time,
    )


if __name__ == "__main__":
    main()
