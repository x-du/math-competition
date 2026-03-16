import csv
import dataclasses
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
STUDENTS_CSV = ROOT / "database" / "students" / "students.csv"
JMO_ROOT = ROOT / "database" / "contests" / "jmo"

# Absolute paths to the awardee PDFs provided by the user
PDF_2022 = Path(
    "/Users/xiaochendu/Dropbox/Xdu/Patrick/AMO/20222023usajmoawardeesattached/2022 USAJMO Awardees.pdf"
)
PDF_2023 = Path(
    "/Users/xiaochendu/Dropbox/Xdu/Patrick/AMO/20222023usajmoawardeesattached/2023 USAJMO Awardees.pdf"
)


@dataclass
class Awardee:
    year: int
    full_name: str
    state_hint: str
    award_raw: str

    def normalized_award(self) -> str:
        """Map raw PDF award strings to the canonical contest award labels."""
        text = self.award_raw.strip().lower()
        if not text:
            raise ValueError(f"Empty award for {self.full_name!r} ({self.year})")

        if "top winner" in text:
            return "Top Honors"
        if text.startswith("winner"):
            # 2022 uses just "Winner"; 2023 non-top "Winner"
            return "Honors"
        if "honorable" in text:
            return "Honorable Mention"

        raise ValueError(
            f"Unrecognized award value {self.award_raw!r} "
            f"for {self.full_name!r} ({self.year})"
        )


def _normalize_name(first: str, last: str) -> str:
    """Return 'First Last' with basic title-casing and trimmed whitespace."""
    first = first.strip()
    last = last.strip()
    full = f"{first} {last}".strip()
    # Keep internal capitalization for things like McDonald, de la Cruz, etc.
    return " ".join(part[:1].upper() + part[1:] for part in full.split())


def _parse_2022_awardees() -> List[Awardee]:
    awardees: List[Awardee] = []

    with pdfplumber.open(PDF_2022) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue

            # First row is header: ["Last Name", "First Name", "School Name", "Award"]
            for row in table[1:]:
                if not row or all(cell is None or str(cell).strip() == "" for cell in row):
                    continue
                if len(row) < 4:
                    # Very defensive; shouldn't happen for these PDFs
                    continue

                last, first, _school, award_raw = row
                if (last or "").strip().lower() == "last name":
                    continue

                if not first or not last:
                    continue

                full_name = _normalize_name(first, last)
                # 2022 PDF does not include state; we rely on students.csv
                awardees.append(Awardee(2022, full_name, state_hint="", award_raw=award_raw or ""))

    return awardees


def _split_2023_name(raw: str) -> Tuple[str, str]:
    # Format is generally "Last, First ..."
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("Empty name cell in 2023 USAJMO PDF")

    if "," not in raw:
        # Fallback: treat last token as last name
        parts = raw.split()
        if len(parts) == 1:
            return parts[0], ""
        return parts[-1], " ".join(parts[:-1])

    last, first = raw.split(",", 1)
    return last.strip(), first.strip()


def _parse_2023_awardees() -> List[Awardee]:
    """Parse 2023 awardees, handling rows that are split across multiple lines.

    The 2023 PDF uses a table where long names / schools / awards are broken
    into several rows. We stream through each table and accumulate contiguous
    chunks until we have enough information (name + award) to emit an Awardee.
    """

    awardees: List[Awardee] = []

    with pdfplumber.open(PDF_2023) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue

            current_name_parts: List[str] = []
            current_state: str = ""
            current_award_parts: List[str] = []

            for row in table:
                if not row or all(cell is None or str(cell).strip() == "" for cell in row):
                    continue

                if len(row) < 4:
                    continue

                name_cell, _school, state_country, award_raw = row
                name_text = (name_cell or "").strip()
                state_text = (state_country or "").strip()
                award_text = (award_raw or "").strip()

                # Skip header rows
                if name_text and name_text.lower() == "name":
                    continue

                if name_text:
                    current_name_parts.append(name_text)

                if state_text:
                    current_state = state_text

                if award_text:
                    current_award_parts.append(award_text)

                award_lower = " ".join(current_award_parts).lower()
                has_award = ("winner" in award_lower) or ("mention" in award_lower)

                has_full_name = bool(current_name_parts) and (
                    len(current_name_parts) > 1
                    or not current_name_parts[-1].strip().endswith(",")
                )

                if not (has_award and has_full_name):
                    continue

                full_name_raw = " ".join(current_name_parts)
                last, first = _split_2023_name(full_name_raw)
                full_name = _normalize_name(first, last)

                awardees.append(
                    Awardee(
                        2023,
                        full_name=full_name,
                        state_hint=current_state,
                        award_raw=" ".join(current_award_parts),
                    )
                )

                current_name_parts = []
                current_state = ""
                current_award_parts = []

    return awardees


def load_students() -> Tuple[List[Dict[str, str]], Dict[str, Dict[str, str]], int]:
    with STUDENTS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows: List[Dict[str, str]] = list(reader)

    by_name: Dict[str, Dict[str, str]] = {}
    max_id = 0
    for row in rows:
        name_key = row["student_name"].strip().lower()
        if name_key:
            # Prefer the first occurrence
            by_name.setdefault(name_key, row)

        try:
            sid = int(row["student_id"])
            if sid > max_id:
                max_id = sid
        except (ValueError, TypeError):
            continue

    return rows, by_name, max_id


def save_students(rows: List[Dict[str, str]]) -> None:
    fieldnames = ["student_id", "student_name", "state", "team_ids", "alias"]
    with STUDENTS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "student_id": row.get("student_id", ""),
                    "student_name": row.get("student_name", ""),
                    "state": row.get("state", ""),
                    "team_ids": row.get("team_ids", ""),
                    "alias": row.get("alias", ""),
                }
            )


def write_results(year: int, rows: List[Tuple[str, str, str, str]]) -> None:
    year_dir = JMO_ROOT / f"year={year}"
    year_dir.mkdir(parents=True, exist_ok=True)
    path = year_dir / "results.csv"

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "student_name", "state", "award"])
        for sid, name, state, award in rows:
            writer.writerow([sid, name, state, award])


def main() -> None:
    students_rows, students_by_name, max_id = load_students()
    next_id = max_id + 1

    new_students: List[Dict[str, str]] = []

    def find_or_add_student(name: str, state_hint: str) -> Tuple[str, str, str]:
        nonlocal next_id

        key = name.strip().lower()
        if not key:
            raise ValueError("Empty student name")

        if key in students_by_name:
            row = students_by_name[key]
            # If we have a better state from the PDF, fill in missing state
            if not row.get("state") and state_hint:
                row["state"] = state_hint
            return row["student_id"], row["student_name"], row.get("state", "") or state_hint or ""

        sid = str(next_id)
        next_id += 1
        row = {
            "student_id": sid,
            "student_name": name,
            "state": state_hint,
            "team_ids": "",
            "alias": "",
        }
        students_rows.append(row)
        students_by_name[key] = row
        new_students.append(row)
        return sid, name, state_hint

    awardees_2022 = _parse_2022_awardees()
    awardees_2023 = _parse_2023_awardees()

    results_2022: List[Tuple[str, str, str, str]] = []
    results_2023: List[Tuple[str, str, str, str]] = []

    for a in awardees_2022:
        award_norm = a.normalized_award()
        sid, canon_name, state = find_or_add_student(a.full_name, a.state_hint)
        results_2022.append((sid, canon_name, state, award_norm))

    for a in awardees_2023:
        award_norm = a.normalized_award()
        sid, canon_name, state = find_or_add_student(a.full_name, a.state_hint)
        results_2023.append((sid, canon_name, state, award_norm))

    # Persist updates
    save_students(students_rows)
    write_results(2022, results_2022)
    write_results(2023, results_2023)

    print(f"Parsed {len(awardees_2022)} awardees for 2022")
    print(f"Parsed {len(awardees_2023)} awardees for 2023")
    print(f"New students added: {len(new_students)}")
    if new_students:
        print("First few new students:")
        for row in new_students[:10]:
            print(row["student_id"], row["student_name"], row["state"])


if __name__ == "__main__":
    main()

