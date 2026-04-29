"""
GC: Documentation freshness check (Phase 6).
Compares docs/api/*.md mtime vs corresponding src/api/ code files.
Flags docs that are more than 1 day behind the code they describe.
Run weekly via cron or manually.
"""
import pathlib
import sys
from datetime import datetime

STALE_THRESHOLD_SECONDS = 86400  # 1 day


def check_doc_freshness() -> list[dict]:
    stale = []
    docs_api = pathlib.Path("docs/api")
    src_api = pathlib.Path("src/api")

    if not docs_api.exists():
        print("docs/api/ not found — skipping freshness check")
        return stale

    for doc in sorted(docs_api.glob("*.md")):
        # Try to find matching code file by stem keyword
        keyword = doc.stem.split("_")[-1].lower()
        code_files = list(src_api.rglob(f"*{keyword}*")) if src_api.exists() else []

        if not code_files:
            continue

        doc_mtime = doc.stat().st_mtime
        code_mtime = max(f.stat().st_mtime for f in code_files)

        if code_mtime > doc_mtime + STALE_THRESHOLD_SECONDS:
            days_behind = int((code_mtime - doc_mtime) / 86400)
            stale.append({
                "doc": str(doc),
                "code_files": [str(f) for f in code_files],
                "days_behind": days_behind,
                "doc_updated": datetime.fromtimestamp(doc_mtime).strftime("%Y-%m-%d"),
                "code_updated": datetime.fromtimestamp(code_mtime).strftime("%Y-%m-%d"),
            })

    return stale


if __name__ == "__main__":
    stale = check_doc_freshness()

    if stale:
        print(f"⚠️  Stale documentation detected ({len(stale)} files):\n")
        for s in stale:
            print(f"  📄 {s['doc']}")
            print(f"     Doc last updated:  {s['doc_updated']}")
            print(f"     Code last updated: {s['code_updated']} ({s['days_behind']} days behind)")
            print(f"     Matching code:     {', '.join(s['code_files'])}\n")
        print("Action: Update the stale docs or run the relevant Agent with a doc-sync task.")
        sys.exit(1)
    else:
        print("✅ All API docs are up to date")
