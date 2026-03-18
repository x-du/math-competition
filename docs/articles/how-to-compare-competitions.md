---
title: How to Compare Math Competitions
description: "A framework for comparing US math competitions: integrity and reputation, competition impact index (MCP-weighted overlap with elite performers), and geographic reach (local vs. national draw)."
---

# How to Compare Math Competitions

When evaluating math competitions—for coaching decisions, admissions context, or understanding the competitive landscape—it helps to have a structured framework. This article presents three lenses: **integrity and reputation**, **competition impact**, and **geographic reach**.

---

## 1. Integrity and Reputation

Not all competitions are equally trustworthy. Cheating—leaked exams, weak proctoring, long testing windows—has affected some contests more than others. A strong result at a low-integrity contest tells you less than the same result at a high-integrity one.

**[Integrity in US Math Competitions](IntegrityInMathContest.md)** rates major contests on a 1–10 scale (1 = rampant cheating, 10 = very clean), based on community discussions (AoPS, Reddit), documented incidents, and structural analysis. Key takeaways:

| Integrity Level | Examples |
|---|---|
| **9** | USAMO/USAJMO, IMO, HMMT, MathCounts National — proof-based or tightly proctored, nearly impossible to fake |
| **8** | PUMaC, ARML, CMIMC, BMT, BAMO, DMM, CMM — in-person at university venues, strong proctoring |
| **7** | MMATHS — multi-site adds some variance |
| **4** | AIME — repeated leaks, school-proctored |
| **3** | AMC 10/12 — massive documented leaks |

**When comparing competitions, start with integrity.** A contest with a low rating may have inflated or unreliable results. For high-stakes decisions, prioritize consistency across multiple high-integrity contests. See [Using data to identify integrity issues](using-data-to-identify-integrity-issues.md) for how to use this database to spot red flags.

---

## 2. Competition Impact Index

**Definition:** The **Competition Impact Index** is the percentage of a competition’s top 100 ranked students who are in the overall top 100. The metric is MCP-weighted: it measures the share of overall elite MCP captured (higher-ranked students contribute more). See [MCP](mcp.md).

$$\text{Impact Index} = \frac{\sum \text{MCP of contest's top 100 who are in overall top 100}}{\sum \text{MCP of overall top 100}} \times 100\%$$

### What it measures

- **High impact** : The competition's top 100 capture a large share of overall elite MCP. Strong performance here correlates strongly with overall elite standing.
- **Lower impact** : The contest's top 100 capture less of the elite MCP pool. The competition may be more regional, target a different age group, or have a different skill profile.

### Results from this database

The impact index is computed from the current database for all competitions. **See the [Competition Ranking](../crank.html) page for live impact index data.** The index is most meaningful for contests with 50+ ranked participants; smaller contests can show very high values because their entire field is elite.

### How to use it

- **Recruitment and selection:** Competitions with high impact indices are strong signals of elite ability.
- **Calibration:** A student who ranks top 10 at HMMT February (high impact) has demonstrated ability against a field that heavily overlaps with the national elite. A top 10 at a lower-impact contest may still be impressive but reflects a different competitive context.
- **Pipeline analysis:** MathCounts National’s 44% overlap shows that many top middle schoolers go on to rank in the overall top 100 in high school.

---

## 3. Geographic Reach: Local vs. National

Some competitions draw primarily from their host region; others attract students from across the country. This affects how “national” a result really is.

**Definition:** For each competition, we store the **count of participants by state** (from `students.csv` or contest-specific results). This lets you see where each contest's field comes from.

### Results from this database

The database tracks state counts per contest. **See the [Competition Ranking](../crank.html) page → Attraction tab** for live data: select a competition to view its student distribution by state (pie chart and US map). Compare contests to see which draw nationally vs. regionally—e.g., BAMO and BMT are heavily California; HMMT February and PUMaC Division A draw from across the country.

### What this tells you

- **National competitions** (HMMT February, PUMaC Division A, CMIMC, BrUMO): No single state dominates. A top result means the student beat a nationally diverse field.
- **Regional competitions** (BAMO, BMT, CMM): One state (often the host) accounts for most participants. Strong results are meaningful but reflect a more geographically concentrated pool. BAMO explicitly targets the Bay Area; BMT and CMM draw heavily from California and the West Coast.
- **Mixed** (PUMaC Division B, DMM): Some local advantage but meaningful national participation.

Community discussions on AoPS and Reddit often note that East Coast competitions (HMMT, PUMaC, ARML) and West Coast competitions (BMT, BAMO, CMM) each have strong local ecosystems. Students who excel at both coasts’ contests demonstrate broad, consistent ability.

---

## Summary: A Quick Comparison Checklist

When comparing two competitions, consider:

1. **Integrity** — Is the contest high-integrity (8–9)? See [Integrity in US Math Competitions](IntegrityInMathContest.md).
2. **Impact Index** — What share of its top performers are in the overall top 100? Higher = stronger signal of elite standing.
3. **Geographic reach** — Is it national or regional? National draws make top results more comparable across regions.

| Factor | Question to Ask |
|---|---|
| Integrity | Can I trust the results? |
| Impact | Does this contest identify the same elite students as the broader system? |
| Geography | Is the field local or national? |

---

## Data Sources and Limitations

- **Integrity ratings:** LLM-generated from community discussions (AoPS, Reddit) and documented incidents. See disclaimer in [Integrity in US Math Competitions](IntegrityInMathContest.md).
- **Impact index:** Computed from this database’s MCP rankings. Only includes students with official recognition; contests that publish fewer results may have noisier indices.
- **Geographic data:** State comes from `students.csv` or contest-specific results (e.g., AMO, JMO, MathCounts). Some students have missing or inferred state.
- **Excluded from impact rankings:** IMO, EGMO, and RMM are international olympiads and are excluded from the Competition Ranking impact index. The US sends only 4–6 students to each per year, so the field is tiny and the impact index would be misleading. This framework compares *US* contests: the impact index measures overlap with the US top 100 by MCP, and geographic reach is about US state distribution. International olympiads draw from many countries and don't fit the same comparison—their prestige is well understood without needing a US-centric index.

For methodology details on MCP and rankings, see [MCP — Math Competition Points](mcp.md).

**Live rankings:** See the [Competition Ranking](../crank.html) page for impact index and geographic data computed from the current database.

---

*For feedback or suggestions: [mathcontestintegrity@gmail.com](mailto:mathcontestintegrity@gmail.com).*
