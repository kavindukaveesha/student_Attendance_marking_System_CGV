"""Server-rendered attendance charts (matplotlib Agg backend).

Course link: L8.3 (data visualization).
"""
import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


STATUS_COLOURS = {"present": "#16a34a", "absent": "#dc2626", "flagged": "#f59e0b"}
STATUS_VALUE = {"present": 1.0, "flagged": 0.5, "absent": 0.0}


def attendance_bar_png(records: list[dict], student_label: str = "") -> io.BytesIO:
    if not records:
        return _empty_chart(f"No records for {student_label}")

    dates = [r.get("date") or f"#{i+1}" for i, r in enumerate(records)]
    values = [STATUS_VALUE.get(r["status"], 0.0) for r in records]
    colours = [STATUS_COLOURS.get(r["status"], "#9ca3af") for r in records]

    fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
    ax.bar(dates, values, color=colours, edgecolor="#0f172a")
    ax.set_ylim(0, 1.1)
    ax.set_yticks([0, 0.5, 1.0])
    ax.set_yticklabels(["Absent", "Flagged", "Present"])
    ax.set_title(f"Attendance timeline — {student_label}")
    ax.set_xlabel("Session date")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf


def attendance_pie_png(records: list[dict], student_label: str = "") -> io.BytesIO:
    if not records:
        return _empty_chart(f"No records for {student_label}")

    counts: dict[str, int] = {"present": 0, "absent": 0, "flagged": 0}
    for r in records:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    labels = [k for k, v in counts.items() if v > 0]
    sizes = [counts[k] for k in labels]
    colours = [STATUS_COLOURS[k] for k in labels]

    fig, ax = plt.subplots(figsize=(5, 5), dpi=100)
    ax.pie(sizes, labels=labels, colors=colours, autopct="%1.0f%%", startangle=90)
    ax.set_title(f"Attendance summary — {student_label}")

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf


def _empty_chart(message: str) -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=12, color="#475569")
    ax.axis("off")
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf
