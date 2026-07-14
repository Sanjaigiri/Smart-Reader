"""Renders an executive-ready PDF sprint report using reportlab:
an executive summary with a progress bar and RAG health indicator, a status
pie chart, a summary table, a Backlog Items table with live status
attribution, a Team Performance table (who completed how much, how fast),
a Task Timing table (who took each task and when, who finished it and
when, how long it took), a full Movement Log, assignee/label breakdowns, a
blocked-items list, and page-numbered footers.

Attribution: every "Changed By" value - current status and full history -
comes straight from GitHub's own timeline (see
github_client.fetch_status_history / ProjectV2ItemStatusChangedEvent). This
is retroactively accurate and does not depend on any background process
having been running.
"""
import os
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether, PageBreak
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend

from sprint_report import build_scope, compute_timing, build_team_performance, format_duration, last_touched_by

# Sibling of Smart-Reader itself, not nested inside the tool's own code
# folder - Smart-Reader/tools/sprint_reporting_agent/../../.. == SMART_READER/
REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "sprint_reports"))

STATUS_COLORS = {
    "Done": colors.HexColor("#1a7f37"),
    "Testing": colors.HexColor("#9a6700"),
    "In Progress": colors.HexColor("#0969da"),
    "Todo": colors.HexColor("#57606a"),
}
RAG_GREEN = colors.HexColor("#1a7f37")
RAG_AMBER = colors.HexColor("#9a6700")
RAG_RED = colors.HexColor("#cf222e")

CELL_STYLE = ParagraphStyle("cell", fontName="Helvetica", fontSize=9, leading=11)
HEADER_STYLE = ParagraphStyle("header", fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=colors.white)


def _status_style(status):
    color = STATUS_COLORS.get(status, colors.black)
    return ParagraphStyle(f"status-{status}", fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=color)


def _escape(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _cell(text):
    return Paragraph(_escape(text), CELL_STYLE)


def _header_cell(text):
    return Paragraph(str(text), HEADER_STYLE)


def _status_cell(status):
    return Paragraph(str(status), _status_style(status))


def _default_out_path():
    # Always the same filename so there's exactly one obvious file to open -
    # no pile of timestamped PDFs to get confused between. Pass an explicit
    # path to --pdf if you want to keep a dated snapshot instead.
    return os.path.join(REPORTS_DIR, "latest_report.pdf")


def _rag_color(done_pct, blocked_count):
    if blocked_count:
        return RAG_RED
    if done_pct >= 70:
        return RAG_GREEN
    if done_pct >= 40:
        return RAG_AMBER
    return RAG_RED


def _progress_bar(pct, width, height=0.8 * cm):
    d = Drawing(width, height)
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#d0d7de"), strokeColor=None))
    fill_width = width * max(0.0, min(pct, 100.0)) / 100.0
    color = RAG_GREEN if pct >= 70 else RAG_AMBER if pct >= 40 else RAG_RED
    if fill_width > 0:
        d.add(Rect(0, 0, fill_width, height, fillColor=color, strokeColor=None))
    d.add(String(width / 2, height / 2 - 3.5, f"{pct:.0f}% complete",
                  fontSize=9, fontName="Helvetica-Bold",
                  fillColor=colors.white if pct >= 35 else colors.black, textAnchor="middle"))
    return d


def _status_pie(by_status, size=4 * cm):
    """Pie chart with a proper side legend instead of labels stuck onto the
    slices - inline slice labels can overflow the drawing's bounding box and
    collide with whatever is above/below it in the page flow; a legend never
    does."""
    statuses = sorted(by_status.items(), key=lambda kv: -len(kv[1]))
    if not statuses:
        return None
    width, height = 12 * cm, size + 1 * cm
    d = Drawing(width, height)
    pie = Pie()
    pie.x = 0.8 * cm
    pie.y = 0.5 * cm
    pie.width = size
    pie.height = size
    pie.data = [len(v) for _, v in statuses]
    pie.labels = None
    pie.slices.strokeWidth = 0.75
    pie.slices.strokeColor = colors.white
    for i, (status, _) in enumerate(statuses):
        pie.slices[i].fillColor = STATUS_COLORS.get(status, colors.grey)
    d.add(pie)

    legend = Legend()
    legend.x = size + 1.8 * cm
    legend.y = height - 0.3 * cm
    legend.dx = 8
    legend.dy = 8
    legend.dxTextSpace = 6
    legend.deltay = 14
    legend.fontName = "Helvetica"
    legend.fontSize = 9
    legend.alignment = "left"
    # Default columnMaximum is 3, which wraps a 4th+ entry into a second
    # column instead of stacking it below - force everything into one column.
    legend.columnMaximum = max(len(statuses), 1)
    legend.colorNamePairs = [
        (STATUS_COLORS.get(status, colors.grey), f"{status} ({len(v)})") for status, v in statuses
    ]
    d.add(legend)
    return d


def _footer(canvas, doc, project_title):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#57606a"))
    canvas.drawString(1.5 * cm, 1 * cm, f"Sprint Reporting Agent - {project_title}")
    canvas.drawRightString(A4[0] - 1.5 * cm, 1 * cm, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf(items, transitions, project_title, start, end, out_path=None):
    if not out_path:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        out_path = _default_out_path()
    else:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)

    scope = build_scope(items, transitions, start, end)
    scoped = scope["scoped"]
    by_status = scope["by_status"]
    by_assignee = scope["by_assignee"]
    by_label = scope["by_label"]
    blocked_items = scope["blocked_items"]

    total = sum(len(v) for v in by_status.values())
    done = len(by_status.get("Done", []))
    done_pct = (done / total * 100.0) if total else 0.0
    rag_color = _rag_color(done_pct, len(blocked_items))
    rag_label = "AT RISK" if rag_color == RAG_RED else ("NEEDS ATTENTION" if rag_color == RAG_AMBER else "ON TRACK")

    days_left = None
    if end:
        try:
            end_date = datetime.strptime(end, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            days_left = (end_date - datetime.now(timezone.utc)).days
        except ValueError:
            days_left = None

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(out_path, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.8 * cm,
                             leftMargin=1.5 * cm, rightMargin=1.5 * cm)
    story = []

    story.append(Paragraph(f"Sprint Report - {project_title}", styles["Title"]))
    if start or end:
        story.append(Paragraph(f"Sprint window: {start or 'open'} to {end or 'open'}"
                                + (f" ({days_left} day(s) remaining)" if days_left is not None else ""),
                                styles["Normal"]))
        if scope["excluded_count"]:
            story.append(Paragraph(
                f"({scope['excluded_count']} item(s) excluded - no activity in this window)",
                styles["Normal"]))
    story.append(Paragraph(
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    # --- Backlog items table (up top - the primary content) ---
    item_rows = [[_header_cell(h) for h in
                  ("ID", "Title", "Status", "Assignee(s)", "Changed By", "Created", "Closed")]]
    for item_id, (item, moves) in sorted(scoped.items(), key=lambda kv: kv[1][0]["number"] or 0):
        last_by, _ = last_touched_by(item, moves)
        item_rows.append([
            _cell(f"#{item['number']}"),
            _cell(item["title"]),
            _status_cell(item["status"]),
            _cell(", ".join(item["assignees"]) or "Unassigned"),
            _cell(last_by or "unknown"),
            _cell((item["created_at"] or "")[:16].replace("T", " ")),
            _cell((item["closed_at"] or "-")[:16].replace("T", " ")),
        ])
    # NOT wrapped in KeepTogether - this table grows with the backlog size,
    # so it should split naturally across pages (it repeats its header row)
    # rather than getting shoved onto a fresh page and leaving a blank gap.
    story.append(Paragraph("Backlog Items", styles["Heading2"]))
    story.append(_styled_table(
        item_rows, col_widths=[1.2 * cm, 4.4 * cm, 2.1 * cm, 2.3 * cm, 2.4 * cm, 2.8 * cm, 2.8 * cm]))
    story.append(Spacer(1, 0.6 * cm))

    # --- Executive summary: RAG status, progress bar, pie chart ---
    exec_block = [Paragraph("Executive Summary", styles["Heading2"])]
    rag_style = ParagraphStyle("rag", fontName="Helvetica-Bold", fontSize=13, textColor=rag_color)
    exec_block.append(Paragraph(f"{rag_label}  -  {done} of {total} items done", rag_style))
    exec_block.append(Spacer(1, 0.2 * cm))
    exec_block.append(_progress_bar(done_pct, width=15 * cm))
    exec_block.append(Spacer(1, 0.3 * cm))
    if blocked_items:
        exec_block.append(Paragraph(
            f"{len(blocked_items)} item(s) currently blocked - see Blocked Items below.", styles["Normal"]))
    pie = _status_pie(by_status)
    if pie:
        exec_block.append(Spacer(1, 0.2 * cm))
        exec_block.append(pie)
    story.append(KeepTogether(exec_block))
    story.append(Spacer(1, 0.5 * cm))

    # --- Summary table ---
    summary_rows = [[_header_cell("Status"), _header_cell("Count")]]
    for status, v in sorted(by_status.items()):
        summary_rows.append([_status_cell(status), _cell(len(v))])
    story.append(KeepTogether([
        Paragraph("Summary", styles["Heading2"]),
        _styled_table(summary_rows, col_widths=[8 * cm, 3 * cm]),
    ]))
    story.append(Spacer(1, 0.4 * cm))

    if by_assignee:
        rows = [[_header_cell("Assignee"), _header_cell("Breakdown")]]
        for assignee, counts in sorted(by_assignee.items()):
            rows.append([_cell(assignee), _cell(", ".join(f"{n} {s}" for s, n in sorted(counts.items())))])
        story.append(KeepTogether([
            Paragraph("By assignee", styles["Heading3"]),
            _styled_table(rows, col_widths=[5 * cm, 10 * cm]),
        ]))
        story.append(Spacer(1, 0.4 * cm))

    if by_label:
        rows = [[_header_cell("Label"), _header_cell("Breakdown")]]
        for label, counts in sorted(by_label.items()):
            rows.append([_cell(label), _cell(", ".join(f"{n} {s}" for s, n in sorted(counts.items())))])
        story.append(KeepTogether([
            Paragraph("By label", styles["Heading3"]),
            _styled_table(rows, col_widths=[5 * cm, 10 * cm]),
        ]))
        story.append(Spacer(1, 0.4 * cm))

    if blocked_items:
        rows = [[_header_cell("ID"), _header_cell("Title")]]
        rows += [[_cell(f"#{i['number']}"), _cell(i["title"])] for i in blocked_items]
        story.append(KeepTogether([
            Paragraph("Blocked items", styles["Heading3"]),
            _styled_table(rows, col_widths=[2 * cm, 13 * cm]),
        ]))
        story.append(Spacer(1, 0.6 * cm))

    # --- Team performance: who's completing work, how fast, who's active ---
    # Each major section from here on starts on its own fresh page - avoids
    # both a heading getting orphaned alone at the bottom of a page AND a
    # section awkwardly starting mid-page with little room left.
    story.append(PageBreak())
    team_stats = build_team_performance(scoped)
    team_block = [Paragraph("Team Performance", styles["Heading2"])]
    if team_stats:
        rows = [[_header_cell(h) for h in ("Person", "Completed", "Currently Active", "Avg Time Taken")]]
        for person, stats in sorted(team_stats.items(), key=lambda kv: -kv[1]["completed"]):
            avg = (sum(stats["durations"]) / len(stats["durations"])) if stats["durations"] else None
            rows.append([_cell(person), _cell(stats["completed"]), _cell(stats["active"]),
                         _cell(format_duration(avg))])
        team_block.append(_styled_table(rows, col_widths=[5 * cm, 3 * cm, 4 * cm, 4 * cm]))
    else:
        team_block.append(Paragraph("No attributed activity yet.", styles["Normal"]))
    story.append(KeepTogether(team_block))
    story.append(Spacer(1, 0.6 * cm))

    # --- Task timing: who took each task, who finished it, how long it took ---
    # "-" means that step hasn't happened yet; "unknown" means it happened but
    # was logged before per-transition attribution existed.
    timing_rows = [[_header_cell(h) for h in
                    ("ID", "Title", "Taken By", "Started", "Completed By", "Finished", "Duration")]]
    any_timing = False
    for item_id, (item, moves) in sorted(scoped.items(), key=lambda kv: kv[1][0]["number"] or 0):
        timing = compute_timing(item, moves)
        if not (timing["taken_at"] or timing["completed_at"]):
            continue
        any_timing = True
        who_taken = timing["taken_by"] or ("unknown" if timing["taken_at"] else "-")
        who_done = timing["completed_by"] or ("unknown" if timing["completed_at"] else "-")
        timing_rows.append([
            _cell(f"#{item['number']}"),
            _cell(item["title"]),
            _cell(who_taken),
            _cell((timing["taken_at"] or "")[:16].replace("T", " ") if timing["taken_at"] else "-"),
            _cell(who_done),
            _cell((timing["completed_at"] or "")[:16].replace("T", " ") if timing["completed_at"] else "-"),
            _cell(format_duration(timing["duration_seconds"])),
        ])
    # NOT KeepTogether - grows with the backlog size, should split naturally.
    story.append(PageBreak())
    story.append(Paragraph("Task Timing", styles["Heading2"]))
    if any_timing:
        story.append(_styled_table(
            timing_rows, col_widths=[1.1 * cm, 3.6 * cm, 2.3 * cm, 2.8 * cm, 2.3 * cm, 2.8 * cm, 2.1 * cm]))
    else:
        story.append(Paragraph(
            "No task has been both picked up and completed yet.",
            styles["Normal"]))
    story.append(Spacer(1, 0.6 * cm))

    # --- Movement log: ID, from -> to, who, when ---
    move_rows = [[_header_cell(h) for h in ("ID", "Title", "From", "To", "Changed By", "Detected At (UTC)")]]
    any_moves = False
    for item_id, (item, moves) in sorted(scoped.items(), key=lambda kv: kv[1][0]["number"] or 0):
        for t in moves:
            any_moves = True
            move_rows.append([
                _cell(f"#{item['number']}"),
                _cell(item["title"]),
                _cell(t["from_status"]),
                _cell(t["to_status"]),
                _cell(t.get("changed_by") or "unknown"),
                _cell(t["detected_at"][:19].replace("T", " ")),
            ])
    # NOT KeepTogether - grows with move count, should split naturally.
    story.append(PageBreak())
    story.append(Paragraph("Movement Log (full history, from GitHub)", styles["Heading2"]))
    if any_moves:
        story.append(_styled_table(
            move_rows, col_widths=[1.2 * cm, 4.0 * cm, 2.1 * cm, 2.1 * cm, 2.6 * cm, 4.0 * cm]))
    else:
        story.append(Paragraph(
            "No column moves recorded for any item yet.",
            styles["Normal"]))

    def _on_page(canvas, doc_):
        _footer(canvas, doc_, project_title)

    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    return out_path


def _styled_table(rows, col_widths):
    table = Table(rows, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24292f")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d7de")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8fa")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    table.setStyle(TableStyle(style))
    return table
