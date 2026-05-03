"""Deduplicate BMT contest rows: official PDFs repeat names across tier sections."""

from __future__ import annotations

import csv
import io
import sys
from pathlib import Path
from typing import Any

BMT_AWARD_ORDER: dict[str, int] = {
    "Top Scores": 0,
    "Distinguished HM (Top 20%)": 1,
    "Honorable Mention (Top 50%)": 2,
}

TOP_SCORES = "Top Scores"
DISTINGUISHED_HM = "Distinguished HM (Top 20%)"
HONORABLE_MENTION = "Honorable Mention (Top 50%)"


def _fmt_mcp_rank(v: float) -> str:
    n = int(round(v))
    if abs(v - n) < 1e-9:
        return str(n)
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def assign_bmt_mcp_ranks(rows: list[dict[str, Any]]) -> None:
    """
    Set mcp_rank per docs/articles/mcp.md (bmt mode): Top Scores use average-rank-for-ties
    on published rank; DHM and HM each use the midpoint of their contiguous position block
    among listed awardees (positions follow Top, then DHM, then HM).
    Mutates rows in place; preserves list order.
    """
    top = [r for r in rows if (r.get("award") or "").strip() == TOP_SCORES]
    dhm = [r for r in rows if (r.get("award") or "").strip() == DISTINGUISHED_HM]
    hm = [r for r in rows if (r.get("award") or "").strip() == HONORABLE_MENTION]

    n_top = len(top)
    n_dhm = len(dhm)
    n_hm = len(hm)

    def _rank_sort_key(r: dict[str, Any]) -> float:
        s = (r.get("rank") or "").strip()
        try:
            return float(s)
        except ValueError:
            return 1e30

    top_sorted = sorted(top, key=_rank_sort_key)
    pos = 1
    i = 0
    mcp_by_id: dict[int, str] = {}

    while i < len(top_sorted):
        rk = _rank_sort_key(top_sorted[i])
        j = i
        while j < len(top_sorted) and _rank_sort_key(top_sorted[j]) == rk:
            j += 1
        k = j - i
        avg_pos = (pos + pos + k - 1) / 2.0
        mr = _fmt_mcp_rank(avg_pos)
        for r in top_sorted[i:j]:
            mcp_by_id[id(r)] = mr
        pos += k
        i = j

    dhm_mr = ""
    if n_dhm:
        lo = n_top + 1
        hi = n_top + n_dhm
        dhm_mr = _fmt_mcp_rank((lo + hi) / 2.0)

    hm_mr = ""
    if n_hm:
        lo = n_top + n_dhm + 1
        hi = n_top + n_dhm + n_hm
        hm_mr = _fmt_mcp_rank((lo + hi) / 2.0)

    for r in rows:
        a = (r.get("award") or "").strip()
        if a == TOP_SCORES:
            r["mcp_rank"] = mcp_by_id.get(id(r), "")
        elif a == DISTINGUISHED_HM:
            r["mcp_rank"] = dhm_mr
        elif a == HONORABLE_MENTION:
            r["mcp_rank"] = hm_mr


def award_rank(award: str) -> int:
    a = (award or "").strip()
    if a not in BMT_AWARD_ORDER:
        raise ValueError(f"Unknown BMT award: {award!r}")
    return BMT_AWARD_ORDER[a]


def _int_or_big(s: str) -> int:
    s = (s or "").strip()
    if not s:
        return 10**9
    try:
        return int(float(s))
    except ValueError:
        return 10**9


def dedupe_bmt_dict_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Keep one row per student_id — the best award tier (Top Scores > DHM > HM).

    Tie-break within tier: lower mcp_rank, then earlier input order among candidates.

    Output row order matches the original CSV: first occurrence of each kept row
    (same subsequence order as the source file).
    """
    by_id: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    for i, r in enumerate(rows):
        sid = str(r.get("student_id") or "").strip()
        if not sid:
            continue
        by_id.setdefault(sid, []).append((i, r))

    winner: dict[str, dict[str, Any]] = {}
    for sid in sorted(by_id.keys(), key=lambda x: int(x) if x.isdigit() else x):
        candidates = by_id[sid]
        best = min(award_rank(r["award"]) for _, r in candidates)
        tier_best = [(i, r) for i, r in candidates if award_rank(r["award"]) == best]
        tier_best.sort(key=lambda ir: (_int_or_big(str(ir[1].get("mcp_rank", ""))), ir[0]))
        winner[sid] = tier_best[0][1]

    out: list[dict[str, Any]] = []
    seen_sid: set[str] = set()
    for r in rows:
        sid = str(r.get("student_id") or "").strip()
        if not sid:
            continue
        if sid in seen_sid:
            continue
        if r is winner[sid]:
            out.append(r)
            seen_sid.add(sid)

    return out


def _csv_text(fieldnames: list[str], rows: list[dict[str, Any]]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def normalize_bmt_results_csv(path: Path) -> tuple[bool, int]:
    """
    Dedupe by student_id (best tier), recalculate mcp_rank for every row, write if changed.

    Returns (wrote_file, duplicate_rows_removed).
    """
    raw = path.read_text(encoding="utf-8")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames or "student_id" not in fieldnames:
            return False, 0
        rows = list(reader)

    before_n = len(rows)
    out = dedupe_bmt_dict_rows(rows)
    assign_bmt_mcp_ranks(out)

    removed = before_n - len(out)
    new_csv = _csv_text(list(fieldnames), out)
    if new_csv == raw:
        return False, removed

    path.write_text(new_csv, encoding="utf-8")
    return True, removed


def dedupe_bmt_results_csv(path: Path) -> tuple[bool, int]:
    """Backward-compatible alias for normalize_bmt_results_csv."""
    return normalize_bmt_results_csv(path)


def main() -> int:
    """Rewrite all BMT results.csv under database/contests when needed."""
    repo = Path(__file__).resolve().parents[1]
    contests = repo / "database" / "contests"
    changed = 0
    removed = 0
    for folder in ("bmt", "bmt-algebra", "bmt-calculus", "bmt-discrete", "bmt-geometry"):
        for year in (2023, 2024, 2025):
            p = contests / folder / f"year={year}" / "results.csv"
            if not p.is_file():
                continue
            ok, n = normalize_bmt_results_csv(p)
            if ok:
                changed += 1
                removed += n
                extra = f", removed {n} duplicate row(s)" if n else ", recalculated mcp_rank"
                print(f"{p.relative_to(repo)}{extra}")
    print(f"Done. Files updated: {changed}, duplicate rows removed (total): {removed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
