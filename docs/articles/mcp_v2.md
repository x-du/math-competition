---
title: MCP v2 — Math Competition Points (Version 2)
description: "MCP v2 upgrades the point distribution algorithm: min_pts is now calculated dynamically based on competition size and number of awardees, rather than fixed at 50% of max_pts. All other MCP rules remain unchanged."
---

# MCP v2 — Point Distribution Upgrade

This document describes the **MCP v2** upgrade. It amends the point distribution algorithm in Section 3 of [MCP v1](mcp.md). All other rules — competition tiers, subject tests, time decay, special rules, aggregation, etc. — remain as defined in the original MCP specification.

---

## Why v2?

v2 addresses limitations of v1 that arise from how competitions publish results:

1. **Reflects true competition size.** v1 used the number of awardees as N, so a student who placed 50th among 2,000 was scored as if they were 50th among 50. v2 uses the actual competition size, so points better match performance in the full field.

2. **Fair across different publication practices.** HMMT publishes top 50; BMT publishes top 50%; USAMO publishes only awards. v1 gave the last person in our data 50% of max_pts in every case. v2 adjusts for each competition’s structure.

3. **Accounts for selection.** Selective competitions (USAMO, HMMT, MPFG) have pre-qualified fields. v2 uses a higher floor for these so that even the last qualifier gets points that reflect an elite field.

4. **Future-proof.** If full results become available later, the same formula applies without change. No recalibration is needed.

5. **Simpler floor rule.** v2 uses a clear rule: min_pts = 10 for open competitions, higher for selective ones — instead of a fixed 50% of max_pts for all.

---

## What Changes in v2

**Only the point distribution formula changes** for competitions that use the power-law curve. Specifically:

- **Grand Slam (IMO, EGMO, RMM):** Point distribution is **unchanged from v1** — medal-based (Gold/Silver/Bronze), not the power-law formula.
- **N in the formula:** In v1, N is the **total number of awardees** (students we have ranks for). In v2, N is the **size of the competition** (total participants).
- **MCP v1:** `min_pts` is fixed at 50% of `max_pts` for all competitions.
- **MCP v2:** `min_pts` is decided by whether the competition has a selection process. If **no** selection process (open competition), use **10**. If there **is** a selection process (selective competition), assign a **higher value**.
- **Points assignment:** Since we only know the awardees, we only calculate and assign points for the awardees.

---

## New Point Distribution Algorithm (v2)

### Formula (unchanged structure)

The power-law curve remains:

$$\text{mcp}\_\text{points}(r) = \text{min}\_\text{pts} + (\text{max}\_\text{pts} - \text{min}\_\text{pts}) \times \left(\frac{N - r}{N - 1}\right)^k$$

| Variable | Description |
|---|---|
| `r` | The current rank being calculated |
| `max_pts` | The maximum points awarded (at Rank 1) = Tier × weight |
| `min_pts` | **Calculated** (see below) — the floor at Rank N |
| `N` | The **total size of the competition** (all participants). *In v1, N was the number of awardees; in v2, N is the competition size.* |
| `k` | The steepness coefficient (3) |

### Dynamic `min_pts` Calculation

In v2, `min_pts` is decided by whether the competition has a selection process:

- **No selection process** (open competition): `min_pts` = **10**. Examples: ARML, BAMO, DMM, CMIMC, MMATHS, CMM, BMT, BrUMO.
- **Selection process** (selective competition): `min_pts` = **higher value**. Examples: USAMO, USAJMO, HMMT February, HMMT November, MPFG, MathCounts National. The exact higher value can be defined in the implementation (e.g., based on tier or competition size).

*Note: IMO, EGMO, and RMM use medal-based points (Gold/Silver/Bronze) as in v1; the power-law formula and min_pts do not apply to them.*

### Awardees Only Receive Points

**Since we only know the awardees, we only calculate and assign points for the awardees.** Students whose ranks are unknown (e.g., ranks 51–2000 when only top 50 are recognized) receive **0 points**.

### Full Competition Records

**The same algorithm applies when full competition records become available.** Whether we have partial data (top 50 of 2000) or complete data (all 2000 ranks), the formula, `min_pts` calculation, and point distribution remain identical. No migration or recalibration is needed — we simply assign points to more students as their ranks become known.

---

## Worked Example

| Parameter | Value |
|---|---|
| Competition size (N) | 2000 |
| Number of awardees (A) | 50 (top 50 only) |
| Tier | 1000 |
| `max_pts` | 1000 |
| `min_pts` | 10 |

**Anchor points:**
- **Rank 1:** 1000 points
- **Rank 2000:** 10 points (theoretical floor; we have no data for this rank)

**Rank 50** (last awarded rank) is calculated via the formula with r = 50, N = 2000, max_pts = 1000, min_pts = 10:

$$\text{mcp}\_\text{points}(50) = 10 + (1000 - 10) \times \left(\frac{2000 - 50}{2000 - 1}\right)^3 \approx 10 + 990 \times 0.928 \approx 929$$

**Ranks 51–2000:** No official recognition → **0 points**.

---

## Estimated Competition Sizes

The v2 algorithm requires the **total competition size (N)** for each event. Below are estimated sizes from official websites, [AoPS](https://artofproblemsolving.com/), and recent results. Numbers may vary by year.

| Competition | Tier | Est. Size (N) | Awardees | Selection | min_pts |
|---|---|---|---|---|---|
| **HMMT February** | 1000 | ~800 | ~50 | Selective (invitation/registration) | 100 |
| **HMMT November** | 500 | ~720 | ~50 | Open | 10 |
| **PUMaC Division A** | 1000 | ~180 | ~40–45 | Open | 10 |
| **PUMaC Division B** | 500 | ~180 | ~32–48 | Open | 10 |
| **BMT Individual** | 1000 | ~630 | ~135–315 | Open | 10 |
| **ARML Individual** | 1000 | ~1,600 | ~45–65 | Open | 10 |
| **USAMO** | 1000 | ~280 | ~135–155 | Selective (AMC/AIME qualifiers) | 200 |
| **USAJMO** | 500 | ~220 | ~143–166 | Selective (AMC/AIME qualifiers) | 200 |
| **CMIMC** | 500 | ~200 | ~10 | Open | 10 |
| **BAMO-12** | 500 | ~240 | ~25–36 | Open | 10 |
| **BAMO-8** | 250 | ~420 | ~30–35 | Open | 10 |
| **MathCounts National** | 500 | 224 | 56 | Selective (state qualifiers) | 100 |
| **MPFG** | 500 | ~275 | ~60–75 | Selective (AMC qualifiers) | 100 |
| **MPFG-Olympiad** | 500 | ~75 | ~20–32 | Selective (MPFG invitees) | 100 |
| **MMATHS** | 250 | ~750 | ~99–105 | Open | 10 |
| **DMM** | 250 | ~270 | ~51 | Open | 10 |
| **CMM** | 250 | ~60 | ~10 | Open | 10 |
| **BrUMO Division A** | 250 | ~300 | ~22–24 | Open | 10 |

*Note: Numbers from official websites, AoPS, and recent results. May vary by year. Awardees = students we have ranks for per year (those who receive MCP points). Open = min_pts 10; Selective = min_pts higher (implementation-defined).*

---

## What Stays the Same

All other MCP rules from [mcp.md](mcp.md) apply unchanged:

- **Grand Slam (IMO, EGMO, RMM):** Medal-based points (Gold/Silver/Bronze) — same as v1
- Competition tiers (2000, 1000, 500, 250)
- `mcp_rank` normalization (average-rank-for-ties, award blocks)
- Subject tests at 50% weight
- 4-year rolling window and geometric time decay
- MathCounts special rules (no decay, no window)
- MCP-W (MPFG, MPFG-Olympiad, EGMO)
- MCP % and aggregation

---

## Disclaimer

**MCP v2 is in beta and under community review.** The dynamic `min_pts` calculation may be refined as we gather feedback. For suggestions: [mathcontestintegrity@gmail.com](mailto:mathcontestintegrity@gmail.com).
