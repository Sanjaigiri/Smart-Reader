"""Generates a Markdown sprint report: each backlog item's created date,
its FULL Status transition history with real GitHub-side timestamps and
actors (fetched live, no background poller required - see
github_client.fetch_status_history), current status, assignee, labels,
custom fields (Priority/Size/Estimate/etc.), and a blocked flag - grouped
by column, assignee, and label.

Usage: python sprint_report.py [--out report.md] [--sprint-start YYYY-MM-DD] [--sprint-end YYYY-MM-DD]

Sprint window can also be set via SPRINT_START / SPRINT_END in .env. Leave
both unset to report on all items regardless of date.
"""
import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime

if sys.stdout.encoding is None or sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from github_client import load_config, fetch_project_items, fetch_status_history


def fetch_transitions(token, items):
    """The real, complete transition history per item, straight from
    GitHub's timeline - accurate retroactively, no poller needed."""
    by_item = {}
    for item_id, item in items.items():
        owner, repo, number = item.get("repo_owner"), item.get("repo_name"), item.get("number")
        if not (owner and repo and number):
            by_item[item_id] = []
            continue
        history = fetch_status_history(token, owner, repo, number)
        by_item[item_id] = [
            {
                "from_status": h["from_status"],
                "to_status": h["to_status"],
                "changed_by": h["changed_by"],
                "detected_at": h["changed_at"],
            }
            for h in history
        ]
    return by_item


def _date_in_range(iso_ts, start, end):
    if not iso_ts:
        return False
    date_part = iso_ts[:10]
    if start and date_part < start:
        return False
    if end and date_part > end:
        return False
    return True


def is_in_sprint(item, moves, start, end):
    if not start and not end:
        return True
    if _date_in_range(item["created_at"], start, end):
        return True
    if _date_in_range(item["closed_at"], start, end):
        return True
    return any(_date_in_range(t["detected_at"], start, end) for t in moves)


def is_blocked(item):
    if any(label.strip().lower() == "blocked" for label in item["labels"]):
        return True
    val = item["fields"].get("Blocked")
    return bool(val) and str(val).strip().lower() in ("yes", "true", "blocked")


def _parse_iso(ts):
    if not ts:
        return None
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def format_duration(seconds):
    if seconds is None:
        return "-"
    seconds = int(seconds)
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def compute_timing(item, moves):
    """Who picked up an item and when, who finished it and when, and how
    long it took - built from the Movement Log (real GitHub actor +
    timestamp per move, see github_client.fetch_project_items). Answers
    "who took this task at what time, and who completed it at what time".
    """
    taken = next((t for t in moves if t["to_status"] == "In Progress"), None)
    done = next((t for t in moves if t["to_status"] == "Done"), None)
    taken_at = taken["detected_at"] if taken else None
    completed_at = done["detected_at"] if done else None
    duration_seconds = None
    t0, t1 = _parse_iso(taken_at), _parse_iso(completed_at)
    if t0 and t1:
        duration_seconds = (t1 - t0).total_seconds()
    return {
        "taken_at": taken_at,
        "taken_by": (taken or {}).get("changed_by"),
        "completed_at": completed_at,
        "completed_by": (done or {}).get("changed_by"),
        "duration_seconds": duration_seconds,
    }


def build_team_performance(scoped):
    """Per-person stats: how many tasks they completed and how long each
    took, plus how many they currently have active (In Progress/Testing,
    attributed to whoever most recently changed that item's status)."""
    stats = defaultdict(lambda: {"completed": 0, "active": 0, "durations": []})
    for item_id, (item, moves) in scoped.items():
        timing = compute_timing(item, moves)
        if timing["completed_by"]:
            stats[timing["completed_by"]]["completed"] += 1
            if timing["duration_seconds"] is not None:
                stats[timing["completed_by"]]["durations"].append(timing["duration_seconds"])
        if item["status"] in ("In Progress", "Testing") and item.get("status_changed_by"):
            stats[item["status_changed_by"]]["active"] += 1
    return stats


def build_scope(items, transitions, start, end):
    """Filters items to the sprint window and computes the breakdowns shared
    by both the Markdown and PDF renderers. Returns a dict with: scoped
    ({item_id: (item, moves)}), excluded_count, by_status, by_assignee,
    by_label, blocked_items.
    """
    all_count = len(items)
    scoped = {}
    for item_id, item in items.items():
        moves = [t for t in transitions.get(item_id, []) if t["from_status"] != "(new)"]
        if is_in_sprint(item, moves, start, end):
            scoped[item_id] = (item, moves)
    excluded_count = all_count - len(scoped)

    by_status = defaultdict(list)
    by_assignee = defaultdict(lambda: defaultdict(int))
    by_label = defaultdict(lambda: defaultdict(int))
    blocked_items = []

    for item_id, (item, moves) in scoped.items():
        by_status[item["status"]].append((item_id, item))
        assignees = item["assignees"] or ["Unassigned"]
        for a in assignees:
            by_assignee[a][item["status"]] += 1
        for label in item["labels"]:
            by_label[label][item["status"]] += 1
        if is_blocked(item):
            blocked_items.append(item)

    return {
        "scoped": scoped,
        "excluded_count": excluded_count,
        "by_status": by_status,
        "by_assignee": by_assignee,
        "by_label": by_label,
        "blocked_items": blocked_items,
    }


def render_report(items, transitions, project_title, start, end):
    scope = build_scope(items, transitions, start, end)
    scoped = scope["scoped"]
    excluded_count = scope["excluded_count"]
    by_status = scope["by_status"]
    by_assignee = scope["by_assignee"]
    by_label = scope["by_label"]
    blocked_items = scope["blocked_items"]

    lines = [f"# Sprint Report: {project_title}", ""]
    if start or end:
        lines.append(f"**Sprint window:** {start or '(open start)'} to {end or '(open end)'}")
        if excluded_count:
            lines.append(f"*(excluded {excluded_count} item(s) with no activity in this window)*")
        lines.append("")

    lines.append("## Summary")
    for status, entries in sorted(by_status.items()):
        lines.append(f"- **{status}**: {len(entries)}")
    lines.append("")

    lines.append("### By assignee")
    if by_assignee:
        for assignee, counts in sorted(by_assignee.items()):
            parts = ", ".join(f"{n} {status}" for status, n in sorted(counts.items()))
            lines.append(f"- **{assignee}**: {parts}")
    else:
        lines.append("- (no items in scope)")
    lines.append("")

    lines.append("### By label")
    if by_label:
        for label, counts in sorted(by_label.items()):
            parts = ", ".join(f"{n} {status}" for status, n in sorted(counts.items()))
            lines.append(f"- **{label}**: {parts}")
    else:
        lines.append("- (no labels found on any item)")
    lines.append("")

    lines.append("### Blocked")
    if blocked_items:
        for item in blocked_items:
            lines.append(f"- #{item['number']} — {item['title']}")
    else:
        lines.append("- None flagged")
    lines.append("")

    team_stats = build_team_performance(scoped)
    lines.append("## Team Performance")
    if team_stats:
        for person, stats in sorted(team_stats.items()):
            avg = (sum(stats["durations"]) / len(stats["durations"])) if stats["durations"] else None
            lines.append(f"- **{person}**: {stats['completed']} completed "
                          f"(avg {format_duration(avg)}), {stats['active']} currently active")
    else:
        lines.append("- No attributed activity yet")
    lines.append("")

    lines.append("## Items")
    for item_id, (item, moves) in sorted(scoped.items(), key=lambda kv: kv[1][0]["number"] or 0):
        lines.append(f"### #{item['number']} — {item['title']}")
        lines.append(f"- Current status: **{item['status']}**")
        if item.get("status_changed_by"):
            lines.append(f"- Last changed by: {item['status_changed_by']} at {item.get('status_updated_at')}")
        if is_blocked(item):
            lines.append("- ⚠ Blocked")
        lines.append(f"- Assignee(s): {', '.join(item['assignees']) or 'Unassigned'}")
        lines.append(f"- Labels: {', '.join(item['labels']) or '(none)'}")
        for field_name, value in item["fields"].items():
            lines.append(f"- {field_name}: {value}")
        lines.append(f"- Created: {item['created_at']}")
        if item["closed_at"]:
            lines.append(f"- Closed: {item['closed_at']}")
        timing = compute_timing(item, moves)
        if timing["taken_by"] or timing["completed_by"]:
            if timing["taken_by"]:
                lines.append(f"- Taken by {timing['taken_by']} at {timing['taken_at']}")
            if timing["completed_by"]:
                lines.append(f"- Completed by {timing['completed_by']} at {timing['completed_at']}")
            lines.append(f"- Time taken: {format_duration(timing['duration_seconds'])}")
        if moves:
            lines.append("- Status history (full, from GitHub):")
            for t in moves:
                who = t.get("changed_by") or "unknown"
                lines.append(f"  - {t['detected_at']}: {t['from_status']} → {t['to_status']} (by {who})")
        else:
            lines.append("- Status history: none (item has never changed status)")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=None, help="Write report to this file instead of stdout")
    parser.add_argument("--sprint-start", default=None, help="YYYY-MM-DD, overrides SPRINT_START in .env")
    parser.add_argument("--sprint-end", default=None, help="YYYY-MM-DD, overrides SPRINT_END in .env")
    parser.add_argument("--pdf", nargs="?", const="", default=None,
                         help="Write a PDF report instead of Markdown. Optionally pass a path; "
                              "defaults to reports/sprint_report_<timestamp>.pdf")
    args = parser.parse_args()

    token, owner, number = load_config()
    start = args.sprint_start or os.environ.get("SPRINT_START") or None
    end = args.sprint_end or os.environ.get("SPRINT_END") or None
    project_title = f"{owner}'s project #{number}"

    items = fetch_project_items(token, owner, number)
    transitions = fetch_transitions(token, items)

    if args.pdf is not None:
        from pdf_report import build_pdf
        out_path = args.pdf or None
        out_path = build_pdf(items, transitions, project_title, start, end, out_path)
        print(f"PDF report written to {out_path}")
        return

    report = render_report(items, transitions, project_title, start, end)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report written to {args.out}")
    else:
        print(report)


if __name__ == "__main__":
    main()
