"""Parse info.xml (subject + students in sheet row order)."""
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_info(xml_path: str | Path) -> tuple[dict, list[dict]]:
    tree = ET.parse(str(xml_path))
    root = tree.getroot()

    subject = {
        "code": root.findtext("subject/code") or "",
        "title": root.findtext("subject/title") or "",
        "lecturer": root.findtext("subject/lecturer") or "",
        "date": root.findtext("subject/date") or "",
        "hall": root.findtext("subject/hall") or "",
    }

    students: list[dict] = []
    for s in root.findall("students/student"):
        students.append(
            {
                "no": int(s.findtext("no") or 0),
                "index": s.findtext("index") or "",
                "title": s.findtext("title") or "",
                "name": s.findtext("name") or "",
            }
        )

    students.sort(key=lambda s: s["no"])
    return subject, students
