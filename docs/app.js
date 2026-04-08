(function () {
  "use strict";

  var data = { students: [], contests: {} };
  /** Latest competition season year per contest_slug (global), for MCP decay — see build_search_data.get_time_weight. */
  var maxMcpYearBySlugGlobal = {};
  var searchEl = document.getElementById("search");
  var searchInputWrapEl = document.getElementById("search-input-wrap");
  var studentCardBackEl = document.getElementById("student-card-back");
  var resultsEl = document.getElementById("results");
  var emptyEl = document.getElementById("empty");
  var loadingEl = document.getElementById("loading");
  var hintEl = document.getElementById("search-hint");
  var contestListEl = document.getElementById("contest-list");
  var awardsRankingListEl = document.getElementById("awards-ranking-list");
  var topStudentsSectionEl = document.getElementById("top-students-section");
  var awardsRankingFiltersEl = document.getElementById("awards-ranking-filters");
  var searchClearEl = document.getElementById("search-clear");
  var girlsOnlyEl = document.getElementById("girls-only");
  var gradeFilterEl = document.getElementById("grade-filter");
  var gradeFilterWrapEl = document.getElementById("grade-filter-wrap");
  var stateFilterEl = document.getElementById("state-filter");
  var contestFilterWrapEl = document.getElementById("contest-filter-wrap");
  var contestFilterEl = document.getElementById("contest-filter");
  var searchApplyLeaderboardFiltersEl = document.getElementById("search-apply-leaderboard-filters");
  var searchApplyFiltersWrapEl = document.getElementById("search-apply-filters-wrap");
  var contestFilterTriggerEl = document.getElementById("contest-filter-trigger");
  var contestFilterSummaryEl = document.getElementById("contest-filter-summary");
  var sortToggleEl = document.getElementById("sort-toggle");
  var mcpPctSortRowEl = document.getElementById("mcp-pct-sort-row");
  var mcpPctSortBtnEl = document.getElementById("mcp-pct-sort-btn");

  var sortMode = "mcp"; // "records", "mcp", or "mcp_pct"
  var gradeFilterInitialized = false;
  var ratioSortAsc = false; // For MCP %: true = ascending (lowest first), false = descending (default)

  var stateDistPopoverOpen = false;
  var latestStateDist = { students: {}, records: {}, mcp: {} };
  var mcpPctStatsCache = { key: null, html: "" };
  var mcpTimelinePopoverOpen = false;
  var mcpTimelineChartInstance = null;
  var mcpTimelineSelectedIds = [];
  var MCP_TIMELINE_MAX_STUDENTS = 20;
  var SEARCH_RESULTS_DISPLAY_LIMIT = 20;
  var openMcpTimelinePopover = null;
  var mcpTimelineApplyFiltersEl = document.getElementById("mcp-timeline-apply-filters");
  var savedFilters = {};
  var searchValueBeforeStudentCard = null;

  var FILTERS_KEY = "mathcomp_filters";

  function getStudentIdFromUrl() {
    try {
      var params = new URLSearchParams(window.location.search);
      var id = params.get("student_id");
      if (id == null || id === "") return null;
      var n = parseInt(id, 10);
      return isNaN(n) ? null : n;
    } catch (e) { return null; }
  }

  function navigateToStudentCard(studentId) {
    try {
      var url = new URL(window.location.href);
      url.searchParams.set("student_id", String(studentId));
      window.history.replaceState({}, "", url.toString());
    } catch (e) { /* ignore */ }
  }

  function clearStudentIdFromUrl() {
    try {
      var url = new URL(window.location.href);
      url.searchParams.delete("student_id");
      window.history.replaceState({}, "", url.toString());
    } catch (e) { /* ignore */ }
  }

  /** Same as Back to search: leave single-student URL view and show the search results list. */
  function exitStudentCardViewToSearchResults() {
    if (getStudentIdFromUrl() == null) return;
    if (searchEl) searchEl.blur();
    if (searchEl) searchEl.value = (searchValueBeforeStudentCard != null ? searchValueBeforeStudentCard : "");
    searchValueBeforeStudentCard = null;
    clearStudentIdFromUrl();
    if (searchInputWrapEl) searchInputWrapEl.hidden = false;
    if (studentCardBackEl) studentCardBackEl.hidden = true;
    runSearch();
  }

  function navigateToStudentAndScroll(studentId) {
    navigateToStudentCard(studentId);
    runSearch();
    if (searchEl) searchEl.blur();
    var firstCard = resultsEl && resultsEl.querySelector(".student-card");
    if (firstCard && typeof firstCard.scrollIntoView === "function") {
      firstCard.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function saveFilters() {
    try {
      var f = {
        girls: girlsOnlyEl ? girlsOnlyEl.checked : false,
        grade: gradeFilterEl ? gradeFilterEl.value : "",
        state: stateFilterEl ? stateFilterEl.value : "",
        sortMode: sortMode,
        ratioSortAsc: ratioSortAsc,
        search: searchEl ? searchEl.value : "",
        contest: getActiveContestFilterValues(),
        searchApplyLeaderboardFilters: searchApplyLeaderboardFiltersEl ? searchApplyLeaderboardFiltersEl.checked : true,
        mcpTimelineApplyFilters: mcpTimelineApplyFiltersEl ? mcpTimelineApplyFiltersEl.checked : true
      };
      savedFilters = f;
      localStorage.setItem(FILTERS_KEY, JSON.stringify(f));
    } catch (e) { /* ignore */ }
  }

  function restoreFilters() {
    try {
      var s = localStorage.getItem(FILTERS_KEY);
      if (!s) return;
      var f = JSON.parse(s);
      savedFilters = f;
      if (girlsOnlyEl && f.girls != null) girlsOnlyEl.checked = !!f.girls;
      if (stateFilterEl && f.state != null) stateFilterEl.value = f.state;
      if (searchEl && f.search != null) searchEl.value = f.search;
      if (f.sortMode) sortMode = f.sortMode;
      if (f.ratioSortAsc != null) ratioSortAsc = f.ratioSortAsc;
      if (sortToggleEl) {
        var opts = sortToggleEl.querySelectorAll(".sort-toggle-option");
        for (var oi = 0; oi < opts.length; oi++) {
          opts[oi].classList.toggle("sort-toggle-option--active", opts[oi].getAttribute("data-mode") === sortMode);
        }
      }
      if (contestFilterEl && f.contest && Array.isArray(f.contest)) {
        var allBox = contestFilterEl.querySelector("input[type='checkbox'][value='all']");
        var boxes = contestFilterEl.querySelectorAll("input[type='checkbox']");
        var isAll = f.contest.length === 0 || f.contest.indexOf("all") >= 0;
        for (var i = 0; i < boxes.length; i++) {
          var val = boxes[i].value;
          boxes[i].checked = val === "all" ? isAll : (f.contest.indexOf(val) >= 0);
        }
      }
      if (searchApplyLeaderboardFiltersEl && f.searchApplyLeaderboardFilters != null) {
        searchApplyLeaderboardFiltersEl.checked = !!f.searchApplyLeaderboardFilters;
      }
      if (mcpTimelineApplyFiltersEl) {
        if (f.mcpTimelineApplyFilters != null) {
          mcpTimelineApplyFiltersEl.checked = !!f.mcpTimelineApplyFilters;
        } else if (f.mcpTimelineApplyContestFilter != null) {
          mcpTimelineApplyFiltersEl.checked = !!f.mcpTimelineApplyContestFilter;
        }
      }
    } catch (e) { /* ignore */ }
  }

  function shouldApplySearchLeaderboardFilters() {
    return !!(searchApplyLeaderboardFiltersEl && searchApplyLeaderboardFiltersEl.checked);
  }

  function syncSearchApplyFiltersToggleVisibility() {
    if (!searchApplyFiltersWrapEl) return;
    var q = (searchEl && searchEl.value) ? searchEl.value.trim() : "";
    var sid = getStudentIdFromUrl();
    searchApplyFiltersWrapEl.hidden = !(q.length > 0 || sid != null);
  }

  function syncSearchPerformanceButtonVisibility() {
    var wrap = document.getElementById("search-performance-trigger-wrap");
    if (!wrap) return;
    /* Hide only on single-student record view (?student_id=); keep visible for search results */
    wrap.hidden = getStudentIdFromUrl() != null;
  }

  function copyStudentShallow(student, records) {
    var copy = {};
    for (var k in student) {
      if (Object.prototype.hasOwnProperty.call(student, k) && k !== "records") {
        copy[k] = student[k];
      }
    }
    copy.records = records || [];
    return copy;
  }

  function buildSearchResultStudents(nameMatched) {
    if (!shouldApplySearchLeaderboardFilters()) {
      return nameMatched.map(function (s) {
        return copyStudentShallow(s, s.records || []);
      }).filter(function (s) {
        return (s.records || []).length > 0;
      });
    }
    var afterDemo = applyDemographicFilters(nameMatched);
    var out = [];
    for (var i = 0; i < afterDemo.length; i++) {
      var s = afterDemo[i];
      var recs = (s.records || []).filter(recordMatchesContestFilter);
      if (recs.length === 0) continue;
      out.push(copyStudentShallow(s, recs));
    }
    return out;
  }

  // TEMP: set to true to show hidden feature without ?a=1; set to false to require URL param again
  var FORCE_HIDDEN_FEATURE = true;
  function showHiddenFeature() {
    if (FORCE_HIDDEN_FEATURE) return true;
    try {
      var params = new URLSearchParams(window.location.search);
      return params.get("a") === "1";
    } catch (e) {
      return false;
    }
  }

  var US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming"
  ];
  var US_STATES_SET = {};
  for (var i = 0; i < US_STATES.length; i++) US_STATES_SET[US_STATES[i]] = true;

  function debounce(fn, ms) {
    var timeout;
    return function () {
      var args = arguments;
      clearTimeout(timeout);
      timeout = setTimeout(function () { fn.apply(null, args); }, ms);
    };
  }

  function formatMcpPct(ratio) {
    var pctVal = Math.round(Math.min(ratio, 1) * 10000) / 100;
    return parseFloat(pctVal.toFixed(2)).toString();
  }

  function formatMcpValue(n) {
    if (n == null || isNaN(n)) return "—";
    return parseFloat(Number(n).toFixed(2)).toString();
  }

  var CONTEST_FILTER_CONFIG = {
    all: function () { return true; },
    usamo: function (slug) { return slug === "amo"; },
    usajmo: function (slug) { return slug === "jmo"; },
    imo: function (slug) { return slug.indexOf("imo") !== -1; },
    rmm: function (slug) { return slug.indexOf("rmm") !== -1; },
    egmo: function (slug) { return slug.indexOf("egmo") !== -1; },
    "hmmt-feb": function (slug) { return slug.indexOf("hmmt-feb") === 0; },
    "hmmt-nov": function (slug) { return slug.indexOf("hmmt-nov") === 0; },
    "pumac-a": function (slug) {
      if (slug.indexOf("pumac-b") === 0) return false;
      return slug.indexOf("pumac") === 0;
    },
    "pumac-b": function (slug) { return slug.indexOf("pumac-b") === 0; },
    mathcounts: function (slug) { return slug.indexOf("mathcounts") !== -1; },
    cmimc: function (slug) { return slug.indexOf("cmimc") !== -1; },
    arml: function (slug) { return slug.indexOf("arml") !== -1; },
    dmm: function (slug) { return slug.indexOf("dmm") !== -1; },
    cmm: function (slug) { return slug.indexOf("cmm") !== -1; },
    mmaths: function (slug) { return slug === "mmaths"; },
    mpfg: function (slug) { return slug === "mpfg"; },
    "mpfg-olympiad": function (slug) { return slug.indexOf("mpfg-olympiad") !== -1; },
    "bamo-8": function (slug) { return slug.indexOf("bamo-8") !== -1; },
    "bamo-12": function (slug) { return slug.indexOf("bamo-12") !== -1; },
    "brumo-a": function (slug) { return slug.indexOf("brumo-a") === 0; },
    bmt: function (slug) { return slug.indexOf("bmt") === 0; }
  };

  var CONTEST_FILTER_LABELS = {
    usamo: "USAMO", usajmo: "USAJMO", imo: "IMO", rmm: "RMM", egmo: "EGMO",
    "hmmt-feb": "HMMT Feb", "hmmt-nov": "HMMT Nov", "pumac-a": "PUMaC Div A", "pumac-b": "PUMaC Div B",
    mathcounts: "Mathcounts", cmimc: "CMIMC", arml: "ARML", dmm: "DMM", cmm: "CMM",
    mmaths: "MMATHS", mpfg: "MPFG", "mpfg-olympiad": "MPFG Olympiad", "bamo-8": "BAMO-8", "bamo-12": "BAMO-12", "brumo-a": "BrUMO Div A", bmt: "BMT"
  };

  function getSelectedContestLabels() {
    var vals = getActiveContestFilterValues();
    if (!vals.length || vals.indexOf("all") !== -1) return [];
    var labels = [];
    for (var i = 0; i < vals.length; i++) {
      var lbl = CONTEST_FILTER_LABELS[vals[i]];
      if (lbl) labels.push(lbl);
    }
    return labels;
  }

  function getActiveContestFilterValues() {
    if (!contestFilterEl) return [];
    var inputs = contestFilterEl.querySelectorAll("input[type='checkbox']");
    var selected = [];
    for (var i = 0; i < inputs.length; i++) {
      if (inputs[i].checked) selected.push(inputs[i].value);
    }
    if (!selected.length || selected.indexOf("all") !== -1) {
      return ["all"];
    }
    return selected;
  }

  function getContestFilterSummaryText() {
    if (!contestFilterEl) return "All selected";
    var boxes = contestFilterEl.querySelectorAll("input[type='checkbox']");
    var allBox = contestFilterEl.querySelector("input[type='checkbox'][value='all']");
    var totalOptions = boxes.length - (allBox ? 1 : 0);
    var selectedNonAll = [];

    for (var i = 0; i < boxes.length; i++) {
      var box = boxes[i];
      if (box.value === "all") continue;
      if (box.checked) {
        var label = box.parentNode && box.parentNode.textContent
          ? box.parentNode.textContent.trim()
          : box.value;
        selectedNonAll.push(label);
      }
    }

    if (allBox && allBox.checked && selectedNonAll.length === totalOptions) {
      return "All selected";
    }
    if (selectedNonAll.length === 0) {
      return "All selected";
    }
    if (selectedNonAll.length === 1) {
      return selectedNonAll[0] + " selected";
    }
    return String(selectedNonAll.length) + " competitions selected";
  }

  function updateMcpTimelineContestSummary() {
    var el = document.getElementById("mcp-timeline-contest-summary");
    if (!el) return;
    var base = getContestFilterSummaryText();
    if (mcpTimelineApplyFiltersEl && !mcpTimelineApplyFiltersEl.checked) {
      el.textContent = base + " · not applied to chart";
    } else {
      el.textContent = base;
    }
  }

  function updateContestFilterSummary() {
    var text = getContestFilterSummaryText();
    if (contestFilterSummaryEl) contestFilterSummaryEl.textContent = text;
    updateMcpTimelineContestSummary();
  }

  function isContestFilterActive() {
    if (!contestFilterEl) return false;
    var selected = getActiveContestFilterValues();
    return selected.length > 0 && selected.indexOf("all") === -1;
  }

  function isMcpWOnlySlug(slug) {
    if (!slug) return false;
    var s = String(slug).toLowerCase();
    return s === "mpfg" || s.indexOf("mpfg-olympiad") !== -1 || s === "egmo";
  }

  var MATHCOUNTS_MCP_SLUG = "mathcounts-national-rank";

  /** Mirrors scripts/build_search_data.py get_time_weight(contestYear, slug, referenceYear). */
  function timeDecayWeightForPublishedMcp(contestYear, slug, referenceYear) {
    if (contestYear == null || isNaN(contestYear) || referenceYear == null || isNaN(referenceYear)) return 0;
    var s = String(slug || "").toLowerCase();
    if (s === MATHCOUNTS_MCP_SLUG) return 1;
    var yearsAgo = referenceYear - contestYear;
    if (yearsAgo < 0 || yearsAgo > 3) return 0;
    return Math.pow(0.5, yearsAgo);
  }

  /**
   * Sum mcp_points × time decay as of calendar year anchorYear. Per contest, decay uses
   * reference year min(anchorYear, latest season for that slug in the DB), matching published MCP
   * at the last chart year. Skips results with season year > anchorYear.
   */
  function computeMcpFromRecordsAsOf(records, anchorYear, useMcpWCounting) {
    var total = 0;
    for (var i = 0; i < records.length; i++) {
      var r = records[i];
      var slug = r.contest_slug || r.contest || "";
      if (!useMcpWCounting && isMcpWOnlySlug(slug)) continue;
      var pts = r.mcp_points;
      if (pts == null || Number(pts) <= 0) continue;
      var cy = parseInt(String(r.year || ""), 10);
      if (isNaN(cy) || cy > anchorYear) continue;
      var contestMax = maxMcpYearBySlugGlobal[slug];
      if (contestMax == null || isNaN(contestMax)) contestMax = anchorYear;
      var refY = Math.min(anchorYear, contestMax);
      var w = timeDecayWeightForPublishedMcp(cy, slug, refY);
      if (w <= 0) continue;
      total += Number(pts) * w;
    }
    return Math.round(total * 100) / 100;
  }

  function getMcpAtTimelineYear(student, anchorYear, useMcpWCounting) {
    var recs = filterRecordsForMcpTimeline(student.records || []);
    return computeMcpFromRecordsAsOf(recs, anchorYear, useMcpWCounting);
  }

  function computeMcpFromRecords(records, isGirlsOnly) {
    var total = 0;
    for (var i = 0; i < records.length; i++) {
      var contrib = records[i].mcp_contrib;
      if (contrib != null && contrib > 0) {
        if (isGirlsOnly) {
          total += Number(contrib);
        } else {
          var slug = records[i].contest_slug || records[i].contest || "";
          if (!isMcpWOnlySlug(slug)) total += Number(contrib);
        }
      }
    }
    return total;
  }

  function mcpTimelineChartUsesLeaderboardFilters() {
    return !mcpTimelineApplyFiltersEl || mcpTimelineApplyFiltersEl.checked;
  }

  function timelineUseMcpWCounting() {
    var tg = document.getElementById("mcp-timeline-girls-only");
    return !!(tg && tg.checked);
  }

  /** X-axis: min..max competition season among records used for the chart (see filter checkbox). */
  function timelineAnchorYearsFromStudents(students, useMcpWCounting) {
    var minY = Infinity;
    var maxY = -Infinity;
    for (var s = 0; s < students.length; s++) {
      var recs = filterRecordsForMcpTimeline(students[s].records || []);
      for (var i = 0; i < recs.length; i++) {
        var r = recs[i];
        var slug = r.contest_slug || r.contest || "";
        if (!useMcpWCounting && isMcpWOnlySlug(slug)) continue;
        var pts = r.mcp_points;
        if (pts == null || Number(pts) <= 0) continue;
        var y = parseInt(String(r.year || ""), 10);
        if (isNaN(y)) continue;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
    if (minY === Infinity || maxY === -Infinity) return [];
    var arr = [];
    for (var ay = minY; ay <= maxY; ay++) arr.push(ay);
    return arr;
  }

  /** Latest competition season year in the DB used for MCP-by-year ranking (same record rules as the chart axis). */
  function getTimelineGlobalMaxSeasonYear(useMcpWCounting) {
    var maxY = -Infinity;
    var students = data.students || [];
    for (var s = 0; s < students.length; s++) {
      var recs = filterRecordsForMcpTimeline(students[s].records || []);
      for (var i = 0; i < recs.length; i++) {
        var r = recs[i];
        var slug = r.contest_slug || r.contest || "";
        if (!useMcpWCounting && isMcpWOnlySlug(slug)) continue;
        var pts = r.mcp_points;
        if (pts == null || Number(pts) <= 0) continue;
        var y = parseInt(String(r.year || ""), 10);
        if (!isNaN(y) && y > maxY) maxY = y;
      }
    }
    if (maxY === -Infinity) {
      try {
        return new Date().getFullYear();
      } catch (e) {
        return 2026;
      }
    }
    return maxY;
  }

  var MCP_TIMELINE_TOP_PRESET_COUNT = 10;

  /** Replace chart selection with top students by MCP as of the latest season year (honors Apply competition filters + MCP-W per chart rules). */
  function setMcpTimelineSelectionToTopByLatestYear() {
    var useW = timelineUseMcpWCounting();
    var anchorY = getTimelineGlobalMaxSeasonYear(useW);
    var scored = [];
    var students = data.students || [];
    for (var si = 0; si < students.length; si++) {
      var st = students[si];
      if (!studentMatchesMcpTimelineDemographics(st)) continue;
      var mcpY = getMcpAtTimelineYear(st, anchorY, useW);
      if (mcpY <= 0) continue;
      scored.push({ id: st.id, mcp: mcpY });
    }
    scored.sort(function (a, b) {
      if (b.mcp !== a.mcp) return b.mcp - a.mcp;
      return String(a.id).localeCompare(String(b.id));
    });
    var n = MCP_TIMELINE_TOP_PRESET_COUNT;
    var next = [];
    for (var k = 0; k < scored.length && next.length < n; k++) {
      next.push(String(scored[k].id));
    }
    mcpTimelineSelectedIds = next;
  }

  function findStudentById(sid) {
    var students = data.students || [];
    var want = String(sid);
    for (var i = 0; i < students.length; i++) {
      if (String(students[i].id) === want) return students[i];
    }
    return null;
  }

  function getTimelineChartColorVars() {
    var styles = getComputedStyle(document.documentElement);
    return {
      text: styles.getPropertyValue("--text").trim() || "#e4e4e7",
      muted: styles.getPropertyValue("--text-muted").trim() || "#a1a1aa",
      border: styles.getPropertyValue("--border").trim() || "#2a2a30",
      accent: styles.getPropertyValue("--accent").trim() || "#7c9ce0"
    };
  }

  function renderMcpTimelineChips() {
    var el = document.getElementById("mcp-timeline-chips");
    if (!el) return;
    var parts = [];
    for (var i = 0; i < mcpTimelineSelectedIds.length; i++) {
      var st = findStudentById(mcpTimelineSelectedIds[i]);
      if (!st) continue;
      var nm = st.name || "Student";
      parts.push(
        "<span class=\"mcp-timeline-chip\">" +
          escapeHtml(nm) +
          "<button type=\"button\" class=\"mcp-timeline-chip-remove\" data-student-id=\"" +
          escapeHtml(String(st.id)) +
          "\" aria-label=\"Remove " +
          escapeHtml(nm) +
          "\">×</button></span>"
      );
    }
    el.innerHTML = parts.join("");
    var clearAllEl = document.getElementById("mcp-timeline-clear-all");
    if (clearAllEl) clearAllEl.disabled = mcpTimelineSelectedIds.length === 0;
  }

  function renderMcpTimelineChart() {
    var canvas = document.getElementById("mcp-timeline-canvas");
    var emptyEl = document.getElementById("mcp-timeline-empty");
    if (!canvas) return;
    if (typeof Chart === "undefined") {
      if (emptyEl) {
        emptyEl.hidden = false;
        emptyEl.textContent = "Chart library failed to load.";
      }
      return;
    }
    var selected = [];
    for (var si = 0; si < mcpTimelineSelectedIds.length; si++) {
      var fs = findStudentById(mcpTimelineSelectedIds[si]);
      if (fs) selected.push(fs);
    }
    if (mcpTimelineChartInstance) {
      mcpTimelineChartInstance.destroy();
      mcpTimelineChartInstance = null;
    }
    if (!selected.length) {
      if (emptyEl) {
        emptyEl.hidden = false;
        emptyEl.textContent = "Add one or more students above to plot MCP by year.";
      }
      return;
    }
    var years = timelineAnchorYearsFromStudents(selected, false);
    if (!years.length) {
      if (emptyEl) {
        emptyEl.hidden = false;
        emptyEl.textContent = "No MCP timeline data for the selected students.";
      }
      return;
    }
    if (emptyEl) emptyEl.hidden = true;
    var colors = getTimelineChartColorVars();
    var labels = years.map(String);
    var datasets = [];
    for (var di = 0; di < selected.length; di++) {
      var stud = selected[di];
      var series = years.map(function (y) { return getMcpAtTimelineYear(stud, y, false); });
      var col = PIE_COLORS[di % PIE_COLORS.length];
      datasets.push({
        label: stud.name || "Student",
        data: series,
        borderColor: col,
        backgroundColor: col,
        borderWidth: 2,
        pointRadius: 2,
        tension: 0.15,
        fill: false
      });
    }
    var ctx = canvas.getContext("2d");
    mcpTimelineChartInstance = new Chart(ctx, {
      type: "line",
      data: { labels: labels, datasets: datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              color: colors.text,
              usePointStyle: true,
              pointStyle: "rect",
              boxWidth: 14,
              boxHeight: 14,
              padding: 12,
              font: { family: "system-ui, sans-serif", size: 11 }
            }
          },
          tooltip: {
            itemSort: function (a, b) {
              var ya = a.parsed.y != null ? Number(a.parsed.y) : 0;
              var yb = b.parsed.y != null ? Number(b.parsed.y) : 0;
              return yb - ya;
            },
            callbacks: {
              label: function (c) {
                var v = c.parsed.y;
                return (c.dataset.label || "") + ": " + formatMcpValue(v);
              }
            }
          }
        },
        scales: {
          x: {
            ticks: { color: colors.muted, maxRotation: 45, font: { size: 10 } },
            grid: { color: colors.border }
          },
          y: {
            beginAtZero: true,
            ticks: {
              color: colors.muted,
              callback: function (v) { return formatMcpValue(v); }
            },
            grid: { color: colors.border }
          }
        }
      }
    });
  }

  function refreshMcpTimelineIfOpen() {
    if (!mcpTimelinePopoverOpen) return;
    renderMcpTimelineChips();
    renderMcpTimelineChart();
  }

  function bindMcpTimelinePopover() {
    var trigger = document.getElementById("mcp-timeline-trigger");
    var popover = document.getElementById("mcp-timeline-popover");
    var closeBtn = popover && popover.querySelector(".mcp-timeline-popover-close");
    var backdrop = popover && popover.querySelector(".mcp-timeline-popover-backdrop");
    var searchInput = document.getElementById("mcp-timeline-student-search");
    var searchResults = document.getElementById("mcp-timeline-search-results");
    var chipsEl = document.getElementById("mcp-timeline-chips");
    var clearAllBtn = document.getElementById("mcp-timeline-clear-all");
    var top10Btn = document.getElementById("mcp-timeline-top-10");
    if (!trigger || !popover) return;

    function clearMcpTimelineStudentSearchUi() {
      if (searchInput) searchInput.value = "";
      if (searchResults) {
        searchResults.hidden = true;
        searchResults.innerHTML = "";
      }
    }

    function addTimelineStudentIfRoom(sid) {
      if (sid == null || sid === "") return false;
      for (var i = 0; i < mcpTimelineSelectedIds.length; i++) {
        if (String(mcpTimelineSelectedIds[i]) === String(sid)) return false;
      }
      if (mcpTimelineSelectedIds.length >= MCP_TIMELINE_MAX_STUDENTS) return false;
      mcpTimelineSelectedIds.push(String(sid));
      return true;
    }

    function openPopover(opts) {
      opts = opts || {};
      var resetMainSearch = opts.resetMainSearch !== false;
      if (resetMainSearch) {
        if (searchEl) searchEl.value = "";
        searchValueBeforeStudentCard = null;
        clearStudentIdFromUrl();
        runSearch();
      }
      updateContestFilterSummary();
      if (opts.ensureStudentId != null && opts.ensureStudentId !== "") {
        addTimelineStudentIfRoom(opts.ensureStudentId);
      }
      popover.hidden = false;
      trigger.setAttribute("aria-expanded", "true");
      mcpTimelinePopoverOpen = true;
      renderMcpTimelineChips();
      renderMcpTimelineChart();
      if (searchInput) {
        setTimeout(function () { searchInput.focus(); }, 0);
      }
    }

    openMcpTimelinePopover = openPopover;

    function closePopover() {
      popover.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
      mcpTimelinePopoverOpen = false;
      if (searchResults) {
        searchResults.hidden = true;
        searchResults.innerHTML = "";
      }
      if (searchInput) searchInput.value = "";
    }

    function runTimelineSearch() {
      if (!searchInput || !searchResults) return;
      var q = (searchInput.value || "").trim();
      if (!q) {
        searchResults.hidden = true;
        searchResults.innerHTML = "";
        return;
      }
      var useW = timelineUseMcpWCounting();
      var all = data.students || [];
      var matches = [];
      for (var i = 0; i < all.length; i++) {
        var st = all[i];
        if (computeMcpFromRecords(filterRecordsForMcpTimeline(st.records || []), useW) <= 0) continue;
        if (!matchStudent(st, q)) continue;
        matches.push(st);
        if (matches.length >= 30) break;
      }
      if (!matches.length) {
        searchResults.innerHTML = "<li class=\"mcp-timeline-search-empty\"><span>No matches</span></li>";
        searchResults.hidden = false;
        return;
      }
      var li = [];
      for (var j = 0; j < matches.length; j++) {
        var m = matches[j];
        li.push(
          "<li role=\"presentation\"><button type=\"button\" role=\"option\" class=\"mcp-timeline-pick-student\" data-student-id=\"" +
            escapeHtml(String(m.id)) +
            "\">" +
            escapeHtml(m.name || "Student") +
            "</button></li>"
        );
      }
      searchResults.innerHTML = li.join("");
      searchResults.hidden = false;
    }

    var debouncedTimelineSearch = debounce(runTimelineSearch, 120);

    trigger.addEventListener("click", function () {
      if (popover.hidden) openPopover({ resetMainSearch: true }); else closePopover();
    });
    if (closeBtn) closeBtn.addEventListener("click", closePopover);
    if (backdrop) backdrop.addEventListener("click", closePopover);

    if (top10Btn) {
      top10Btn.addEventListener("click", function () {
        setMcpTimelineSelectionToTopByLatestYear();
        clearMcpTimelineStudentSearchUi();
        renderMcpTimelineChips();
        renderMcpTimelineChart();
        if (searchInput) searchInput.focus();
      });
    }

    if (clearAllBtn) {
      clearAllBtn.addEventListener("click", function () {
        mcpTimelineSelectedIds = [];
        clearMcpTimelineStudentSearchUi();
        renderMcpTimelineChips();
        renderMcpTimelineChart();
        if (searchInput) searchInput.focus();
      });
    }

    if (searchInput) {
      searchInput.addEventListener("input", debouncedTimelineSearch);
      searchInput.addEventListener("focus", function () {
        if ((searchInput.value || "").trim()) runTimelineSearch();
      });
    }

    if (searchResults) {
      searchResults.addEventListener("click", function (e) {
        var btn = e.target && e.target.closest && e.target.closest(".mcp-timeline-pick-student");
        if (!btn) return;
        var sid = btn.getAttribute("data-student-id");
        if (!sid) return;
        if (!addTimelineStudentIfRoom(sid)) return;
        clearMcpTimelineStudentSearchUi();
        renderMcpTimelineChips();
        renderMcpTimelineChart();
      });
    }

    if (chipsEl) {
      chipsEl.addEventListener("click", function (e) {
        var rm = e.target && e.target.closest && e.target.closest(".mcp-timeline-chip-remove");
        if (!rm) return;
        var sid = rm.getAttribute("data-student-id");
        if (!sid) return;
        var next = [];
        for (var i = 0; i < mcpTimelineSelectedIds.length; i++) {
          if (String(mcpTimelineSelectedIds[i]) !== String(sid)) next.push(mcpTimelineSelectedIds[i]);
        }
        mcpTimelineSelectedIds = next;
        renderMcpTimelineChips();
        renderMcpTimelineChart();
      });
    }

    if (mcpTimelineApplyFiltersEl) {
      mcpTimelineApplyFiltersEl.addEventListener("change", function () {
        saveFilters();
        updateMcpTimelineContestSummary();
        renderMcpTimelineChart();
        if (searchInput && (searchInput.value || "").trim()) runTimelineSearch();
      });
    }

    function onMcpTimelineDemographicChange() {
      renderMcpTimelineChart();
      if (searchInput && (searchInput.value || "").trim()) runTimelineSearch();
    }

    var mcpTgirls = document.getElementById("mcp-timeline-girls-only");
    var mcpTgrade = document.getElementById("mcp-timeline-grade-filter");
    var mcpTstate = document.getElementById("mcp-timeline-state-filter");
    if (mcpTgirls) mcpTgirls.addEventListener("change", onMcpTimelineDemographicChange);
    if (mcpTgrade) mcpTgrade.addEventListener("change", onMcpTimelineDemographicChange);
    if (mcpTstate) mcpTstate.addEventListener("change", onMcpTimelineDemographicChange);

    document.addEventListener("click", function (e) {
      if (!mcpTimelinePopoverOpen || !searchResults || searchResults.hidden) return;
      if (!popover.contains(e.target)) return;
      if (searchInput && (e.target === searchInput || searchInput.contains(e.target))) return;
      if (searchResults.contains(e.target)) return;
      searchResults.hidden = true;
    });

    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape" || !mcpTimelinePopoverOpen) return;
      closePopover();
    });
  }

  /** Records for Performance-by-year chart and search; respects contest filter only when timeline “Apply filters” is on. */
  function filterRecordsForMcpTimeline(records) {
    var recs = records || [];
    if (!mcpTimelineChartUsesLeaderboardFilters()) return recs;
    return recs.filter(recordMatchesContestFilter);
  }

  function recordMatchesContestFilter(record) {
    if (!record) return false;
    if (!contestFilterEl) return true;
    var slug = record.contest_slug || record.contest || "";
    if (!slug) return false;
    slug = String(slug).toLowerCase();
    var selected = getActiveContestFilterValues();
    if (!selected.length || selected.indexOf("all") !== -1) return true;
    for (var i = 0; i < selected.length; i++) {
      var key = selected[i];
      var fn = CONTEST_FILTER_CONFIG[key];
      if (typeof fn === "function" && fn(slug)) return true;
    }
    return false;
  }

  function setLoading(busy) {
    loadingEl.setAttribute("aria-busy", busy ? "true" : "false");
    loadingEl.hidden = !busy;
  }

  function normalize(s) {
    return (s || "").toLowerCase().trim();
  }

  function matchStudent(student, query) {
    if (!query) return false;
    var q = normalize(query);
    if (normalize(student.name).indexOf(q) !== -1) return true;
    for (var i = 0; i < (student.aliases || []).length; i++) {
      if (normalize(student.aliases[i]).indexOf(q) !== -1) return true;
    }
    return false;
  }

  function studentMatchesDemographicsWithControls(s, girlsEl, gradeEl, gradeWrap, stateEl) {
    if (!s) return false;
    if (girlsEl && girlsEl.checked && (s.gender || "").toLowerCase() !== "female") return false;
    if (gradeEl && gradeWrap && !gradeWrap.hidden && gradeEl.value && gradeEl.value !== "") {
      var wantLabel = gradeEl.value;
      var lab = getGradeLabel(s.grade_in_2026);
      var key = gradeLabelSortKey(lab);
      if (wantLabel === "__none__") {
        if (lab !== "") return false;
      } else if (wantLabel === "__hs__") {
        if (!((key >= 9 && key <= 12) || lab === "")) return false;
      } else if (wantLabel === "__prehs__") {
        if (!(key > 0 && key < 9)) return false;
      } else if (wantLabel === "__hof__") {
        if (!(key > 12)) return false;
      } else if (lab !== wantLabel) {
        return false;
      }
    }
    if (stateEl && stateEl.value && stateEl.value !== "") {
      var wantState = stateEl.value;
      var st = (s.state || "").trim();
      if (wantState === "__none__") {
        if (st) return false;
      } else if (wantState === "__other__") {
        if (!st || US_STATES_SET[st]) return false;
      } else if (wantState === "US") {
        if (!st || !US_STATES_SET[st]) return false;
      } else if (st !== wantState) {
        return false;
      }
    }
    return true;
  }

  function applyDemographicFilters(students) {
    return (students || []).filter(function (s) {
      return studentMatchesDemographicsWithControls(s, girlsOnlyEl, gradeFilterEl, gradeFilterWrapEl, stateFilterEl);
    });
  }

  function studentMatchesMcpTimelineDemographics(s) {
    return studentMatchesDemographicsWithControls(
      s,
      document.getElementById("mcp-timeline-girls-only"),
      document.getElementById("mcp-timeline-grade-filter"),
      document.getElementById("mcp-timeline-grade-filter-wrap"),
      document.getElementById("mcp-timeline-state-filter")
    );
  }

  function syncMcpTimelineSelectFromMain(timelineSel, mainSel) {
    if (!timelineSel || !mainSel) return;
    var prev = timelineSel.value;
    timelineSel.innerHTML = mainSel.innerHTML;
    var keep = false;
    for (var i = 0; i < timelineSel.options.length; i++) {
      if (timelineSel.options[i].value === prev) {
        keep = true;
        break;
      }
    }
    timelineSel.value = keep ? prev : "";
  }

  function syncMcpTimelineSelectOptionsAfterLeaderboardRefresh() {
    syncMcpTimelineSelectFromMain(document.getElementById("mcp-timeline-grade-filter"), gradeFilterEl);
    syncMcpTimelineSelectFromMain(document.getElementById("mcp-timeline-state-filter"), stateFilterEl);
  }

  function escapeHtml(s) {
    var div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
  }

  /**
   * Current grade based on grade_in_2026 (grade at Jan 1, 2026).
   * New school year starts Sept 1 each year.
   * Returns null if gradeIn2026 is missing or invalid.
   */
  function getCurrentGrade(gradeIn2026) {
    if (gradeIn2026 == null || gradeIn2026 === "") return null;
    var g = parseInt(String(gradeIn2026).trim(), 10);
    if (isNaN(g)) return null;
    var d = new Date();
    var y = d.getFullYear();
    var m = d.getMonth() + 1;
    var day = d.getDate();
    if (y < 2026) return g;
    var bumps = (m > 9 || (m === 9 && day >= 1)) ? (y - 2026 + 1) : (y - 2026);
    return g + bumps;
  }

  /**
   * Returns grade label string.
   * - current grade <= 8: M + year, e.g. M2026 (M(2026 + 8 - grade_in_2026))
   * - current grade <= 12: H + year, e.g. H2027 (H(2026 + 12 - grade_in_2026))
   * - current grade > 12: U + year, e.g. U2029 (U(2026 + 16 - grade_in_2026))
   */
  function getGradeLabel(gradeIn2026) {
    var currentGrade = getCurrentGrade(gradeIn2026);
    if (currentGrade == null) return "";
    var g = parseInt(String(gradeIn2026).trim(), 10);
    if (isNaN(g)) return "";
    if (currentGrade <= 8) return "M" + (2026 + 8 - g);
    if (currentGrade <= 12) return "H" + (2026 + 12 - g);
    return "U" + (2026 + 16 - g);
  }

  /** Sort key for grade labels: M2026..M2033 (1-8), H2026..H2029 (9-12), U2026.. (13+). */
  function gradeLabelSortKey(label) {
    if (!label || label === "") return -1;
    var prefix = label.charAt(0);
    var rest = label.slice(1);
    var year = parseInt(rest, 10);
    if (isNaN(year)) return -1;
    if (prefix === "M") return 2034 - year;  // M2026 -> 8, M2033 -> 1
    if (prefix === "H") return 2038 - year;  // H2026 -> 12, H2029 -> 9
    if (prefix === "U") return 2042 - year;  // U2029 -> 13, U2028 -> 14
    return -1;
  }

  /** Display order for grade selector: H2026..H2029 first, then M2026.., then U.. */
  function gradeLabelDisplayOrder(a, b) {
    var prefixOrder = { H: 0, M: 1, U: 2 };
    var pa = a.charAt(0);
    var pb = b.charAt(0);
    var ya = parseInt(a.slice(1), 10) || 0;
    var yb = parseInt(b.slice(1), 10) || 0;
    var oa = prefixOrder[pa];
    var ob = prefixOrder[pb];
    if (oa != null && ob != null && oa !== ob) return oa - ob;
    return ya - yb;
  }

  function recordToDisplayKeys(record) {
    var skip = { contest: true, year: true, contest_slug: true };
    var keys = [];
    for (var k in record) {
      if (!skip[k] && Object.prototype.hasOwnProperty.call(record, k)) {
        keys.push(k);
      }
    }
    return keys.sort();
  }

  var MCP_COLUMNS = { mcp_points: true, mcp_rank: true, mcp_contrib: true };
  var COLUMN_TOOLTIPS = {
    mcp_contrib: "Time-weighted MCP points this result contributes to the student\u2019s total MCP score. Recent results count more; older results decay by 50% per year."
  };

  function allRecordHeaders(records) {
    var set = {};
    for (var r = 0; r < records.length; r++) {
      var keys = recordToDisplayKeys(records[r]);
      for (var i = 0; i < keys.length; i++) set[keys[i]] = true;
    }
    var arr = [];
    for (var k in set) if (Object.prototype.hasOwnProperty.call(set, k)) arr.push(k);
    arr.sort(function (a, b) {
      var aMcp = MCP_COLUMNS[a] ? 1 : 0;
      var bMcp = MCP_COLUMNS[b] ? 1 : 0;
      if (aMcp !== bMcp) return aMcp - bMcp;
      return a.localeCompare(b);
    });
    return arr;
  }

  function compareContestSlugs(a, b) {
    var orderMap = data && data.contest_order_map ? data.contest_order_map : null;
    if (orderMap) {
      var hasA = Object.prototype.hasOwnProperty.call(orderMap, a);
      var hasB = Object.prototype.hasOwnProperty.call(orderMap, b);
      if (hasA && hasB) return orderMap[a] - orderMap[b];
      if (hasA && !hasB) return -1;
      if (!hasA && hasB) return 1;
    }
    return a.localeCompare(b);
  }

  function renderRecordRow(record, allKeys) {
    var slug = record.contest_slug || record.contest || "";
    var yr = record.year || "";
    var yearContent = (slug && yr)
      ? "<a href=\"#\" class=\"csv-row-year-link\" data-contest=\"" + escapeHtml(slug) + "\" data-year=\"" + escapeHtml(yr) + "\">" + escapeHtml(yr) + "</a>"
      : escapeHtml(yr);
    var cells = [
      "<td class=\"num\" data-col=\"year\">", yearContent, "</td>"
    ];
    for (var i = 0; i < allKeys.length; i++) {
      var key = allKeys[i];
      var val = record[key] != null ? record[key] : "";
      var cellClass = key === "rank" ? "num rank-" + (val === "1" || val === 1 ? "1" : (val === "2" || val === 2 || val === "3" || val === 3 ? "2" : "")) : "num";
      cells.push("<td class=\"" + cellClass + "\" data-col=\"" + escapeHtml(key) + "\">", escapeHtml(String(val)), "</td>");
    }
    return "<tr>" + cells.join("") + "</tr>";
  }

  function renderContestInfo(slug, contestsMap) {
    var c = (contestsMap || {})[slug];
    if (!c) return "";
    var parts = ["<div class=\"contest-info\">"];
    parts.push("<h3 class=\"contest-info-title\">" + escapeHtml(c.contest_name || slug) + "</h3>");
    if (c.description) {
      parts.push("<p class=\"contest-info-description\">" + escapeHtml(c.description) + "</p>");
    }
    if (c.website) {
      parts.push("<a href=\"" + escapeHtml(c.website) + "\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"contest-info-website\">Visit website</a>");
    }
    parts.push("</div>");
    return parts.join("");
  }

  function groupRecordsByContest(records) {
    var bySlug = {};
    for (var i = 0; i < records.length; i++) {
      var r = records[i];
      var slug = r.contest_slug || r.contest || "other";
      if (!bySlug[slug]) bySlug[slug] = [];
      bySlug[slug].push(r);
    }
    var slugs = [];
    for (var s in bySlug) if (Object.prototype.hasOwnProperty.call(bySlug, s)) slugs.push(s);
    slugs.sort(compareContestSlugs);
    return { bySlug: bySlug, slugs: slugs };
  }

  function renderStudent(student, contestsMap, headerOnly, opts) {
    opts = opts || {};
    var useCanonicalMcpStats = !!opts.useCanonicalMcpStats;
    var records = (student.records || []).slice();
    var grouped = groupRecordsByContest(records);
    var bySlug = grouped.bySlug;
    var slugs = grouped.slugs;
    var state = student.state || "";

    var sections = [];
    if (!headerOnly) {
      for (var i = 0; i < slugs.length; i++) {
        var slug = slugs[i];
        var contestRecords = bySlug[slug];
        contestRecords.sort(function (a, b) {
          var yA = a.year || "";
          var yB = b.year || "";
          return yA > yB ? -1 : yA < yB ? 1 : 0;
        });
        var allKeys = allRecordHeaders(contestRecords);
        var headerCells = "<th data-col=\"year\">" + escapeHtml("Year") + "</th>" + allKeys.map(function (k) {
          var label = k.replace(/_/g, " ");
          var tip = COLUMN_TOOLTIPS[k];
          var tipAttr = tip ? " data-tooltip=\"" + escapeHtml(tip) + "\" class=\"has-tooltip\" tabindex=\"0\" role=\"button\"" : "";
          return "<th data-col=\"" + escapeHtml(k) + "\"" + tipAttr + ">" + escapeHtml(label) + "</th>";
        }).join("");
        var rows = contestRecords.map(function (r) { return renderRecordRow(r, allKeys); }).join("");

        sections.push(
          "<div class=\"contest-section\">" +
            renderContestInfo(slug, contestsMap) +
            "<div class=\"records-table-wrap\">" +
              "<table class=\"records-table\">" +
                "<thead><tr>" + headerCells + "</tr></thead>" +
                "<tbody>" + rows + "</tbody>" +
              "</table>" +
            "</div>" +
          "</div>"
        );
      }
    }

    var aliasesHtml = "";
    if (student.aliases && student.aliases.length) {
      aliasesHtml = "<span class=\"student-aliases\">Also known as: " +
        student.aliases.map(function (a) { return escapeHtml(a); }).join(", ") +
        "</span>";
    }

    var stateHtml = "";
    if (state) {
      stateHtml = "<span class=\"student-state\">(" + escapeHtml(String(state)) + ")</span>";
    }

    var gradeHtml = "";
    var gradeLabel = getGradeLabel(student.grade_in_2026);
    if (gradeLabel) {
      gradeHtml = " <span class=\"awards-ranking-grade\" title=\"Current grade (school year starts Sept 1)\">" + escapeHtml(gradeLabel) + "</span>";
    }

    var totalRecords = records.length;
    var mcpTotal;
    var isGirlsOnlyCard = (document.getElementById("girls-only") || {}).checked;
    var totalMcp = isGirlsOnlyCard && student.mcp_w != null ? Number(student.mcp_w) : (student.mcp != null ? Number(student.mcp) : 0);
    var contestFilterActiveCard = isContestFilterActive() && !useCanonicalMcpStats;
    if (contestFilterActiveCard) {
      mcpTotal = computeMcpFromRecords(records, isGirlsOnlyCard);
    } else {
      mcpTotal = totalMcp;
    }
    var mcpPctSuffix = "";
    if (sortMode === "mcp_pct" && contestFilterActiveCard && mcpTotal > 0 && totalMcp > 0) {
      var ratio = mcpTotal / totalMcp;
      var pctValCard = formatMcpPct(ratio);
      var contestLabelsCard = getSelectedContestLabels();
      var contestsStrCard = contestLabelsCard.length ? contestLabelsCard.join(", ") : "selected competitions";
      mcpPctSuffix = " (<button type=\"button\" class=\"mcp-pct-trigger\" data-pct=\"" + escapeHtml(pctValCard) + "\" data-contests=\"" + escapeHtml(contestsStrCard) + "\">" + pctValCard + "%</button>)";
    }
    var mcpDisplay = mcpTotal > 0 ? "<span class=\"student-stat\">" + formatMcpValue(mcpTotal) + " MCP" + mcpPctSuffix + "</span>" : "";
    var statsHtml = "<span class=\"student-stats\">" +
      "<span class=\"student-stat\">" + totalRecords + (totalRecords === 1 ? " record" : " records") + "</span>" +
      mcpDisplay +
      "</span>";

    var mcpBtnHtml = "";
    if (mcpTotal > 0) {
      var contribByContest = {};
      for (var ci = 0; ci < records.length; ci++) {
        var rec = records[ci];
        var contrib = rec.mcp_contrib;
        if (!contrib || contrib <= 0) continue;
        var cSlug = rec.contest_slug || rec.contest || "other";
        var cInfo = (contestsMap || {})[cSlug];
        var cName = (cInfo && cInfo.contest_name) ? cInfo.contest_name : cSlug;
        contribByContest[cName] = (contribByContest[cName] || 0) + contrib;
      }
      for (var ck in contribByContest) {
        if (Object.prototype.hasOwnProperty.call(contribByContest, ck)) {
          contribByContest[ck] = Math.round(contribByContest[ck] * 100) / 100;
        }
      }
      mcpBtnHtml =
        "<span class=\"mcp-breakdown-wrap\">" +
          "<button type=\"button\" class=\"mcp-breakdown-btn\" aria-label=\"MCP breakdown\">MCP</button>" +
          "<div class=\"mcp-breakdown-popover\" hidden>" +
            "<div class=\"mcp-breakdown-popover-inner\">" +
              "<h3 class=\"mcp-breakdown-title\">" + escapeHtml(student.name || "Student") + " — MCP Breakdown — " + escapeHtml(formatMcpValue(mcpTotal)) + " pts</h3>" +
              "<canvas class=\"mcp-breakdown-canvas\" width=\"260\" height=\"260\"></canvas>" +
              "<div class=\"mcp-breakdown-legend\"></div>" +
              "<button type=\"button\" class=\"mcp-breakdown-close\" aria-label=\"Close\">×</button>" +
            "</div>" +
            "<div class=\"mcp-breakdown-backdrop\" aria-hidden=\"true\"></div>" +
          "</div>" +
          "<script type=\"application/json\" class=\"mcp-breakdown-data\">" + JSON.stringify(contribByContest) + "</script>" +
        "</span>";
    }

    var contestsHtml = headerOnly ? "" : "<div class=\"student-contests\">" + sections.join("") + "</div>";
    var headerActionsHtml =
      "<div class=\"student-header-actions\">" +
        mcpBtnHtml +
        "<button type=\"button\" class=\"student-card-performance-btn\" data-student-id=\"" +
        escapeHtml(String(student.id)) +
        "\" aria-label=\"Open performance by year chart for this student\">Performance</button>" +
        "<button type=\"button\" class=\"export-pdf-student-btn\" aria-label=\"Export this student to PDF\">PDF</button>" +
      "</div>";
    return (
      "<article class=\"student-card\" data-student-id=\"" + escapeHtml(String(student.id)) + "\">" +
        "<div class=\"student-header\">" +
          "<h2 class=\"student-name\" data-student-name=\"" + escapeHtml(String(student.name || "")) + "\">" + escapeHtml(student.name) + (stateHtml ? " " + stateHtml : "") + gradeHtml + "</h2>" +
          statsHtml +
          aliasesHtml +
          headerActionsHtml +
        "</div>" +
        contestsHtml +
      "</article>"
    );
  }

  function renderContestList() {
    if (!contestListEl) return;
    var contests = data.contests || {};
    var contestYearFiles = data.contest_year_files || {};
    var yearsBySlug = {};
    var students = data.students || [];
    for (var s = 0; s < students.length; s++) {
      var recs = students[s].records || [];
      for (var r = 0; r < recs.length; r++) {
        var slug = recs[r].contest_slug;
        if (!slug) continue;
        if (!yearsBySlug[slug]) yearsBySlug[slug] = {};
        yearsBySlug[slug][recs[r].year] = true;
      }
    }
    var slugs = [];
    for (var k in contests) if (Object.prototype.hasOwnProperty.call(contests, k)) {
      if (k.indexOf("mk-national") === 0) continue;  // Record only; not shown on website
      slugs.push(k);
    }
    slugs.sort(compareContestSlugs);
    var parts = [];
    var csvViewerBase = "csv-viewer.html";
    for (var i = 0; i < slugs.length; i++) {
      var slug = slugs[i];
      var c = contests[slug];
      var name = (c && c.contest_name) ? c.contest_name : slug;
      var years = [];
      if (yearsBySlug[slug]) {
        for (var y in yearsBySlug[slug]) if (Object.prototype.hasOwnProperty.call(yearsBySlug[slug], y)) years.push(y);
        years.sort(function (a, b) { return b.localeCompare(a, undefined, { numeric: true }); });
      }
      var nameHtml = (c && c.website)
        ? "<a href=\"" + escapeHtml(c.website) + "\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"contest-list-link\">" + escapeHtml(name) + "</a>"
        : "<span class=\"contest-list-item\">" + escapeHtml(name) + "</span>";
      var yearLinks = [];
      var filesByYear = contestYearFiles[slug] || {};
      for (var j = 0; j < years.length; j++) {
        var yr = years[j];
        var fileEntry = filesByYear[yr] || "results.csv";
        var filenames = Array.isArray(fileEntry) ? fileEntry : [fileEntry];
        for (var f = 0; f < filenames.length; f++) {
          var filename = filenames[f] || "results.csv";
          var branch = (data.branch && data.branch !== "main") ? data.branch : "";
          var yearHref = csvViewerBase + "?contest=" + encodeURIComponent(slug) + "&year=" + encodeURIComponent(yr) + "&file=" + encodeURIComponent(filename) + "&name=" + encodeURIComponent(name) + (branch ? "&branch=" + encodeURIComponent(branch) : "");
          var label = filenames.length > 1 ? yr + " (" + filename.replace(/^results_?/, "").replace(/\.csv$/i, "") + ")" : yr;
          yearLinks.push("<a href=\"" + yearHref + "\" class=\"contest-list-year-link\">" + escapeHtml(label) + "</a>");
        }
      }
      var yearLine = yearLinks.length ? "<span class=\"contest-list-years\">" + yearLinks.join(", ") + "</span>" : "";
      parts.push("<div class=\"contest-list-block\">" + nameHtml + (yearLine ? "<br>" + yearLine : "") + "</div>");
    }
    contestListEl.innerHTML = parts.length ? parts.join("") : "";
  }

  function renderTopStudentsByRecords() {
    if (!awardsRankingListEl) return;
    var students = data.students || [];
    var withRecords = (students || []).filter(function (s) {
      var recs = s.records || [];
      return recs.length > 0;
    });

    var gradeLabelSet = {};
    var hasNoGrade = false;
    for (var i = 0; i < withRecords.length; i++) {
      var lab = getGradeLabel(withRecords[i].grade_in_2026);
      if (lab === "") hasNoGrade = true;
      else gradeLabelSet[lab] = true;
    }
    var gradeLabels = [];
    for (var k in gradeLabelSet) {
      if (Object.prototype.hasOwnProperty.call(gradeLabelSet, k) && gradeLabelSortKey(k) <= 12) {
        gradeLabels.push(k);
      }
    }
    gradeLabels.sort(gradeLabelDisplayOrder);

    if (gradeFilterEl) {
      var currentValue = gradeFilterEl.value;
      gradeFilterEl.innerHTML = "<option value=\"\">All grades</option>";

      var hsOpt = document.createElement("option");
      hsOpt.value = "__hs__";
      hsOpt.textContent = "High School";
      gradeFilterEl.appendChild(hsOpt);

      var preHsOpt = document.createElement("option");
      preHsOpt.value = "__prehs__";
      preHsOpt.textContent = "Pre High School";
      gradeFilterEl.appendChild(preHsOpt);

      var hofOpt = document.createElement("option");
      hofOpt.value = "__hof__";
      hofOpt.textContent = "Hall of Fame";
      gradeFilterEl.appendChild(hofOpt);

      for (var j = 0; j < gradeLabels.length; j++) {
        var opt = document.createElement("option");
        opt.value = gradeLabels[j];
        opt.textContent = gradeLabels[j];
        gradeFilterEl.appendChild(opt);
      }
      if (hasNoGrade) {
        var noneOpt = document.createElement("option");
        noneOpt.value = "__none__";
        noneOpt.textContent = "No grade";
        gradeFilterEl.appendChild(noneOpt);
      }
      var valToRestore = currentValue !== undefined && currentValue !== null ? currentValue : (savedFilters && "grade" in savedFilters ? savedFilters.grade : "__hs__");
      var optExists = false;
      for (var oi = 0; oi < gradeFilterEl.options.length; oi++) {
        if (gradeFilterEl.options[oi].value === valToRestore) {
          optExists = true;
          break;
        }
      }
      if (!gradeFilterInitialized) {
        var toUse = (savedFilters && "grade" in savedFilters) ? savedFilters.grade : "__hs__";
        var toUseExists = false;
        for (var oj = 0; oj < gradeFilterEl.options.length; oj++) {
          if (gradeFilterEl.options[oj].value === toUse) {
            toUseExists = true;
            break;
          }
        }
        gradeFilterEl.value = toUseExists ? toUse : "__hs__";
        gradeFilterInitialized = true;
      } else if (optExists) {
        gradeFilterEl.value = valToRestore;
      } else {
        gradeFilterEl.value = "__hs__";
      }
    }

    if (girlsOnlyEl && girlsOnlyEl.checked) {
      students = students.filter(function (s) {
        return (s.gender || "").toLowerCase() === "female";
      });
    }
    if (gradeFilterEl && gradeFilterWrapEl && !gradeFilterWrapEl.hidden && gradeFilterEl.value && gradeFilterEl.value !== "") {
      var wantLabel = gradeFilterEl.value;
      students = students.filter(function (s) {
        var lab = getGradeLabel(s.grade_in_2026);
        var key = gradeLabelSortKey(lab);
        if (wantLabel === "__none__") return lab === "";
        if (wantLabel === "__hs__") return (key >= 9 && key <= 12) || lab === "";
        if (wantLabel === "__prehs__") return key > 0 && key < 9;
        if (wantLabel === "__hof__") return key > 12;
        return lab === wantLabel;
      });
    }
    if (stateFilterEl && stateFilterEl.value && stateFilterEl.value !== "") {
      var wantState = stateFilterEl.value;
      students = students.filter(function (s) {
        var st = (s.state || "").trim();
        if (wantState === "__none__") return !st;
        if (wantState === "__other__") return st && !US_STATES_SET[st];
        if (wantState === "US") return st && US_STATES_SET[st];
        return st === wantState;
      });
    }

    var isGirlsOnly = girlsOnlyEl && girlsOnlyEl.checked;
    var contestFilterActive = isContestFilterActive();
    var isMcpPct = sortMode === "mcp_pct";

    if (mcpPctSortRowEl) mcpPctSortRowEl.hidden = !isMcpPct;
    var mcpPctSortTextEl = document.getElementById("mcp-pct-sort-text");
    if (mcpPctSortTextEl) mcpPctSortTextEl.textContent = ratioSortAsc ? "Sorted ascending (lowest contribution first)." : "Sorted descending (highest contribution first).";
    if (mcpPctSortBtnEl) mcpPctSortBtnEl.textContent = ratioSortAsc ? "Sort ascending ↑" : "Sort descending ↓";

    var counts = [];
    if (students && students.length) {
      for (var i = 0; i < students.length; i++) {
        var student = students[i];
        var records = (student.records || []).filter(recordMatchesContestFilter);
        var count = records.length;
        if (count > 0) {
          var mcpTotal = null;
          var mcpRatio = null;
          var filteredMcp = contestFilterActive ? computeMcpFromRecords(records, isGirlsOnly) : null;
          var totalMcp = isGirlsOnly && student.mcp_w != null ? Number(student.mcp_w) : (student.mcp != null ? Number(student.mcp) : 0);
          if (sortMode === "mcp") {
            mcpTotal = contestFilterActive ? filteredMcp : totalMcp;
            if (contestFilterActive && totalMcp > 0) {
              mcpRatio = filteredMcp / totalMcp;
            }
          } else if (sortMode === "mcp_pct") {
            if (contestFilterActive && totalMcp > 0) {
              mcpRatio = filteredMcp / totalMcp;
            }
            mcpTotal = totalMcp;
          } else {
            /* For records sort: still populate mcpTotal for state distribution chart */
            mcpTotal = contestFilterActive ? filteredMcp : totalMcp;
          }
          counts.push({ student: student, recordsCount: count, mcpTotal: mcpTotal, mcpRatio: mcpRatio });
        }
      }
    }

    var totalCountEl = document.getElementById("total-student-count");
    if (totalCountEl) totalCountEl.textContent = String(counts.length);
    var totalRecords = 0;
    for (var j = 0; j < counts.length; j++) totalRecords += counts[j].recordsCount;
    var totalRecordEl = document.getElementById("total-record-count");
    if (totalRecordEl) totalRecordEl.textContent = String(totalRecords);

    var rankingTitleTextEl = document.getElementById("ranking-title-text");
    var subtitleEl = topStudentsSectionEl && topStudentsSectionEl.querySelector(".awards-ranking-subtitle");
    var mcpLabel = (isGirlsOnly && (sortMode === "mcp" || sortMode === "mcp_pct")) ? "MCP-W" : "MCP";
    if (rankingTitleTextEl) {
      if (isMcpPct) {
        rankingTitleTextEl.textContent = "Students by " + mcpLabel + " contribution %";
      } else {
        rankingTitleTextEl.textContent = sortMode === "mcp"
          ? "Top students by " + mcpLabel + " points"
          : "Top students by # of records";
      }
    }
    if (subtitleEl && !isMcpPct) {
      if (sortMode === "mcp") {
        subtitleEl.innerHTML = "Sorted by total " + mcpLabel + " (Math Competition Points" + (isGirlsOnly ? " — Women" : "") + "). Points are awarded by competition tier and placement, with recent results weighted more. " +
          "<a href=\"articles/mcp.html\" target=\"_blank\" rel=\"noopener\">Learn more</a>. " +
          "Under community review. Send feedback to: <a href=\"mailto:mathcontestintegrity@gmail.com\">mathcontestintegrity@gmail.com</a>.";
      } else {
        subtitleEl.textContent = "Sorted by number of competition records in this database. Not a ranking of ability or talent.";
      }
    }

    computeStateDistributions(counts);
    if (stateDistPopoverOpen) renderStateDistCharts();

    if (!counts.length) {
      if (subtitleEl && isMcpPct) {
        subtitleEl.innerHTML = "Select a few competitions, e.g. AMO, to see the contribution of that competition to the total MCP. Shows how much of each student's total MCP comes from the selected competitions. See <a href=\"articles/mcp.html#11-mcp-\" target=\"_blank\" rel=\"noopener\">MCP %</a> section for details. " +
          "<a href=\"#\" class=\"mcp-pct-filter-link\">Open competition filter</a>";
      }
      var emptyMsg = (girlsOnlyEl && girlsOnlyEl.checked)
        ? "No female students with records in this view."
        : "No record data available yet.";
      awardsRankingListEl.innerHTML = "<li class=\"awards-ranking-empty\">" + escapeHtml(emptyMsg) + "</li>";
      awardsRankingListEl.setAttribute("aria-busy", "false");
      syncMcpTimelineSelectOptionsAfterLeaderboardRefresh();
      refreshMcpTimelineIfOpen();
      return;
    }

    if (isMcpPct && !contestFilterActive) {
      if (subtitleEl) {
        subtitleEl.innerHTML = "Select a few competitions to see MCP contribution %. See <a href=\"articles/mcp.html#11-mcp-\" target=\"_blank\" rel=\"noopener\">MCP %</a> section for details. " +
          "<a href=\"#\" class=\"mcp-pct-filter-link\">Open competition filter</a>";
      }
      awardsRankingListEl.innerHTML = "";
      awardsRankingListEl.setAttribute("aria-busy", "false");
      syncMcpTimelineSelectOptionsAfterLeaderboardRefresh();
      refreshMcpTimelineIfOpen();
      return;
    }

    var isMcp = sortMode === "mcp";
    var isMcpPctSort = sortMode === "mcp_pct";
    if (isMcpPctSort) {
      var RATIO_EPS = 1e-10; // Treat ratios within epsilon as equal (avoids fp noise for 100%, etc.)
      counts.sort(function (a, b) {
        var ra = Math.min(a.mcpRatio != null ? a.mcpRatio : -1, 1);
        var rb = Math.min(b.mcpRatio != null ? b.mcpRatio : -1, 1);
        var cmp = ratioSortAsc ? ra - rb : rb - ra;
        if (Math.abs(cmp) >= RATIO_EPS) return cmp;
        // Tie on ratio: break by MCP value (higher MCP first when descending, lower first when ascending)
        var ma = a.mcpTotal != null ? a.mcpTotal : 0;
        var mb = b.mcpTotal != null ? b.mcpTotal : 0;
        var mcpCmp = ratioSortAsc ? ma - mb : mb - ma;
        if (mcpCmp !== 0) return mcpCmp;
        var nameA = (a.student && a.student.name) || "";
        var nameB = (b.student && b.student.name) || "";
        return nameA.localeCompare(nameB);
      });
    } else if (isMcp) {
      counts.sort(function (a, b) {
        if (b.mcpTotal !== a.mcpTotal) return b.mcpTotal - a.mcpTotal;
        var nameA = (a.student && a.student.name) || "";
        var nameB = (b.student && b.student.name) || "";
        return nameA.localeCompare(nameB);
      });
    } else {
      counts.sort(function (a, b) {
        if (b.recordsCount !== a.recordsCount) return b.recordsCount - a.recordsCount;
        var nameA = (a.student && a.student.name) || "";
        var nameB = (b.student && b.student.name) || "";
        return nameA.localeCompare(nameB);
      });
    }

    var top = counts.slice(0, 100);

    if (subtitleEl && isMcpPct) {
      var statsHtml = "";
      if (contestFilterActive) {
        var contestFilterKey = getActiveContestFilterValues().join(",");
        if (mcpPctStatsCache.key !== contestFilterKey) {
          var allStudents = data.students || [];
          var allForStats = [];
          for (var ai = 0; ai < allStudents.length; ai++) {
            var st = allStudents[ai];
            var totalMcpSt = st.mcp != null ? Number(st.mcp) : 0;
            if (totalMcpSt <= 0) continue;
            var recsFiltered = (st.records || []).filter(recordMatchesContestFilter);
            var filteredMcpSt = computeMcpFromRecords(recsFiltered, false);
            var ratioSt = filteredMcpSt / totalMcpSt;
            allForStats.push({ totalMcp: totalMcpSt, mcpRatio: ratioSt });
          }
          allForStats.sort(function (a, b) { return b.totalMcp - a.totalMcp; });
          var top100ByMcp = allForStats.slice(0, 100);
          var ratios = [];
          for (var k = 0; k < top100ByMcp.length; k++) {
            var r = top100ByMcp[k].mcpRatio;
            if (r != null && !isNaN(r)) ratios.push(r);
          }
          mcpPctStatsCache.key = contestFilterKey;
          if (ratios.length > 0) {
            var sum = 0;
            var minR = ratios[0];
            var maxR = ratios[0];
            for (var kk = 0; kk < ratios.length; kk++) {
              sum += ratios[kk];
              if (ratios[kk] < minR) minR = ratios[kk];
              if (ratios[kk] > maxR) maxR = ratios[kk];
            }
            var avg = sum / ratios.length;
            var sortedRatios = ratios.slice().sort(function (a, b) { return a - b; });
            var median = sortedRatios.length % 2 === 1
              ? sortedRatios[Math.floor(sortedRatios.length / 2)]
              : (sortedRatios[sortedRatios.length / 2 - 1] + sortedRatios[sortedRatios.length / 2]) / 2;
            var fmt = function (x) { return formatMcpPct(x) + "%"; };
            var contestLabels = getSelectedContestLabels();
            var contestPhrase = contestLabels.length > 0 ? contestLabels.join(", ") : "selected competitions";
            mcpPctStatsCache.html = " Among the top 100 students by total MCP, contribution from " + contestPhrase + ": avg " + fmt(avg) + ", min " + fmt(minR) + ", max " + fmt(maxR) + ", median " + fmt(median) + ". Due to limited data, do not make judgments without careful review.";
          } else {
            mcpPctStatsCache.html = "";
          }
        }
        statsHtml = mcpPctStatsCache.html;
      }
      subtitleEl.innerHTML = "Select a few competitions, e.g. AMO, to see the contribution of that competition to the total MCP. Shows how much of each student's total MCP comes from the selected competitions. See <a href=\"articles/mcp.html#11-mcp-\" target=\"_blank\" rel=\"noopener\">MCP %</a> section for details." +
        statsHtml + " <a href=\"#\" class=\"mcp-pct-filter-link\">Open competition filter</a>";
    }

    var items = [];
    for (var i = 0; i < top.length; i++) {
      var entry = top[i];
      var s = entry.student || {};
      var state = s.state || "";
      var displayName = String(s.name || "");
      if (state) {
        displayName += " (" + state + ")";
      }
      var gradeHtml = "";
      var gradeLabel = getGradeLabel(s.grade_in_2026);
      if (gradeLabel) {
        gradeHtml = " <span class=\"awards-ranking-grade\" title=\"Current grade (school year starts Sept 1)\">" + gradeLabel + "</span>";
      }
      var valueText;
      if (isMcp || isMcpPctSort) {
        valueText = formatMcpValue(entry.mcpTotal) + " " + mcpLabel;
        if (isMcpPctSort && contestFilterActive && entry.mcpRatio != null) {
          var pctVal = formatMcpPct(entry.mcpRatio);
          var contestLabels = getSelectedContestLabels();
          var contestsStr = contestLabels.length ? contestLabels.join(", ") : "selected competitions";
          valueText += " (<button type=\"button\" class=\"mcp-pct-trigger\" data-pct=\"" + escapeHtml(pctVal) + "\" data-contests=\"" + escapeHtml(contestsStr) + "\">" + pctVal + "%</button>)";
        }
      } else {
        var label = entry.recordsCount === 1 ? "record" : "records";
        valueText = String(entry.recordsCount) + " " + label;
      }
      items.push(
        "<li class=\"awards-ranking-item\">" +
          "<span class=\"awards-ranking-position\">#" + (i + 1) + "</span>" +
          "<span class=\"awards-ranking-name\" data-student-id=\"" + escapeHtml(String(s.id || "")) + "\" data-student-name=\"" + escapeHtml(String(s.name || "")) + "\">" + escapeHtml(displayName) + gradeHtml + "</span>" +
          "<span class=\"awards-ranking-count\" data-student-id=\"" + escapeHtml(String(s.id || "")) + "\" data-student-name=\"" + escapeHtml(String(s.name || "")) + "\">" + valueText + "</span>" +
        "</li>"
      );
    }

    awardsRankingListEl.innerHTML = items.join("");
    awardsRankingListEl.setAttribute("aria-busy", "false");
    syncMcpTimelineSelectOptionsAfterLeaderboardRefresh();
    refreshMcpTimelineIfOpen();
  }

  var THEME_STORAGE_KEY = "theme";
  /* One SVG in the DOM at a time; swap markup on toggle (previous stroke icons). */
  var THEME_TOGGLE_SVG_SUN =
    '<svg class="theme-toggle-svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41m11.32-11.32l1.41-1.41"/></svg>';
  var THEME_TOGGLE_SVG_MOON =
    '<svg class="theme-toggle-svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';

  function getDocumentTheme() {
    return document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
  }

  function applyDocumentTheme(theme) {
    var root = document.documentElement;
    if (theme === "light") {
      root.setAttribute("data-theme", "light");
    } else {
      root.removeAttribute("data-theme");
    }
    try {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch (e) {}
    var btn = document.getElementById("theme-toggle");
    if (btn) {
      if (theme === "light") {
        btn.setAttribute("aria-label", "Switch to dark mode");
        btn.setAttribute("title", "Dark mode");
      } else {
        btn.setAttribute("aria-label", "Switch to light mode");
        btn.setAttribute("title", "Light mode");
      }
      var ic = btn.querySelector(".theme-toggle-icon");
      if (ic) {
        ic.innerHTML = theme === "light" ? THEME_TOGGLE_SVG_MOON : THEME_TOGGLE_SVG_SUN;
      }
    }
    refreshMcpTimelineIfOpen();
  }

  function bindThemeToggle() {
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;
    applyDocumentTheme(getDocumentTheme());
    btn.addEventListener("click", function () {
      applyDocumentTheme(getDocumentTheme() === "light" ? "dark" : "light");
    });
  }

  function closeSiteNavDrawer() {
    var drawer = document.getElementById("site-nav-drawer");
    var toggle = document.getElementById("site-nav-toggle");
    if (!drawer || drawer.hidden) return;
    drawer.hidden = true;
    if (toggle) {
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Open menu");
    }
    document.body.classList.remove("site-nav-open");
  }

  function bindSiteNavDrawer() {
    var toggle = document.getElementById("site-nav-toggle");
    var drawer = document.getElementById("site-nav-drawer");
    if (!toggle || !drawer) return;
    var backdrop = drawer.querySelector(".site-nav-drawer-backdrop");
    var closeBtn = drawer.querySelector(".site-nav-drawer-close");
    var panel = drawer.querySelector(".site-nav-drawer-panel");

    function openDrawer() {
      drawer.hidden = false;
      toggle.setAttribute("aria-expanded", "true");
      toggle.setAttribute("aria-label", "Close menu");
      document.body.classList.add("site-nav-open");
    }

    function isOpen() {
      return !drawer.hidden;
    }

    toggle.addEventListener("click", function () {
      if (isOpen()) closeSiteNavDrawer();
      else openDrawer();
    });
    if (backdrop) {
      backdrop.addEventListener("click", closeSiteNavDrawer);
    }
    if (closeBtn) {
      closeBtn.addEventListener("click", closeSiteNavDrawer);
    }
    if (panel) {
      panel.addEventListener("click", function (e) {
        var a = e.target && e.target.closest && e.target.closest("a.site-nav-item");
        if (a && a.getAttribute("href")) closeSiteNavDrawer();
      });
    }
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && isOpen()) closeSiteNavDrawer();
    });
  }

  function bindContestListPopover() {
    var trigger = document.getElementById("contest-list-trigger");
    var popover = document.getElementById("contest-list-popover");
    var closeBtn = popover && popover.querySelector(".contest-list-popover-close");
    var backdrop = popover && popover.querySelector(".contest-list-popover-backdrop");
    if (!trigger || !popover) return;

    function open() {
      popover.hidden = false;
      trigger.setAttribute("aria-expanded", "true");
    }
    function close() {
      popover.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
    }

    trigger.addEventListener("click", function () {
      if (popover.hidden) {
        closeSiteNavDrawer();
        open();
      } else {
        close();
      }
    });
    if (closeBtn) closeBtn.addEventListener("click", close);
    if (backdrop) backdrop.addEventListener("click", close);
  }

  var searchRafId = null;
  function runSearch() {
    saveFilters();
    var query = (searchEl && searchEl.value) ? searchEl.value.trim() : "";
    var urlStudentId = getStudentIdFromUrl();
    syncSearchPerformanceButtonVisibility();
    syncSearchApplyFiltersToggleVisibility();
    emptyEl.hidden = true;
    resultsEl.innerHTML = "";

    if (searchClearEl) {
      searchClearEl.hidden = !query && !urlStudentId;
    }
    var inStudentCardView = !!urlStudentId;
    if (searchInputWrapEl) searchInputWrapEl.hidden = inStudentCardView;
    if (hintEl) hintEl.hidden = inStudentCardView;
    if (studentCardBackEl) studentCardBackEl.hidden = !inStudentCardView;

    if (urlStudentId != null) {
      var student = null;
      for (var i = 0; i < data.students.length; i++) {
        if (data.students[i].id === urlStudentId) {
          student = data.students[i];
          break;
        }
      }
      if (student) {
        searchValueBeforeStudentCard = (searchEl && searchEl.value) ? searchEl.value.trim() : "";
        if (searchEl) searchEl.value = (student.name || "").trim();
        if (searchClearEl) searchClearEl.hidden = true;
        if (topStudentsSectionEl) topStudentsSectionEl.hidden = true;
        if (awardsRankingFiltersEl) {
          awardsRankingFiltersEl.hidden = false;
          awardsRankingFiltersEl.style.display = "";
        }
        if (shouldApplySearchLeaderboardFilters()) {
          var demo = applyDemographicFilters([student]);
          if (!demo.length) {
            hintEl.textContent = "Student excluded by your filters.";
            emptyEl.hidden = false;
            emptyEl.innerHTML = "<p>This student does not match your Girls / Grade / State filters. Use <strong>Back to search</strong>, then adjust filters or turn off <strong>Apply filters to search</strong>.</p>";
            syncSearchApplyFiltersToggleVisibility();
            return;
          }
        }
        var recs = (student.records || []).slice();
        var copy = copyStudentShallow(student, recs);
        if (recs.length > 0) {
          hintEl.textContent = "1 student found. Full history below; filters apply to search and the leaderboard.";
          resultsEl.innerHTML = renderStudent(copy, data.contests || {}, false, { useCanonicalMcpStats: true });
        } else {
          hintEl.textContent = "No records for this student.";
          emptyEl.hidden = false;
          emptyEl.innerHTML = "<p class=\"empty-state\">No records for this student.</p>";
        }
        syncSearchApplyFiltersToggleVisibility();
        return;
      }
      clearStudentIdFromUrl();
      if (searchInputWrapEl) searchInputWrapEl.hidden = false;
      if (hintEl) hintEl.hidden = false;
      if (studentCardBackEl) studentCardBackEl.hidden = true;
      syncSearchPerformanceButtonVisibility();
    }

    if (!query) {
      hintEl.textContent = "Enter at least one character to search.";
      if (topStudentsSectionEl) topStudentsSectionEl.hidden = false;
      if (awardsRankingFiltersEl) {
        awardsRankingFiltersEl.hidden = false;
        awardsRankingFiltersEl.style.display = "";
      }
      syncSearchApplyFiltersToggleVisibility();
      return;
    }

    if (awardsRankingFiltersEl) {
      awardsRankingFiltersEl.hidden = false;
      awardsRankingFiltersEl.style.display = "";
    }

    syncSearchApplyFiltersToggleVisibility();

    if (searchRafId) cancelAnimationFrame(searchRafId);
    searchRafId = requestAnimationFrame(function () {
      searchRafId = null;
      var q = (searchEl && searchEl.value) ? searchEl.value.trim() : "";
      if (q !== query) return;
      syncSearchApplyFiltersToggleVisibility();

      var matched = data.students.filter(function (s) { return matchStudent(s, query); });
      var searchResults = buildSearchResultStudents(matched);

      var total = searchResults.length;
      var lim = SEARCH_RESULTS_DISPLAY_LIMIT;
      var toRender = total > lim ? searchResults.slice(0, lim) : searchResults;
      var filterNote = shouldApplySearchLeaderboardFilters() ? " Filters above apply." : "";
      hintEl.textContent = total === 0
        ? "No students found." + filterNote
        : total === 1
          ? "1 student found." + filterNote
          : total > lim
            ? total + " students found. Showing first " + lim + "." + filterNote
            : total + " students found." + filterNote;

      if (total === 0) {
        emptyEl.hidden = false;
        emptyEl.innerHTML = shouldApplySearchLeaderboardFilters()
          ? "<p>No name matches with your current filters. Try turning off <strong>Apply filters to search</strong> or widening Girls / Grade / State / Competition filter.</p>"
          : "<p>No students match your search. Try a different name or partial name.</p>";
        if (topStudentsSectionEl) topStudentsSectionEl.hidden = false;
        return;
      }

      if (topStudentsSectionEl) topStudentsSectionEl.hidden = true;

      resultsEl.innerHTML = toRender.map(function (s) { return renderStudent(s, data.contests || {}, true); }).join("");
    });
  }

  function keysForPdfDisplay(records, slug) {
    var keys = allRecordHeaders(records);
    var omit = { p1: 1, p2: 1, p3: 1, p4: 1, p5: 1, p6: 1, p7: 1, p8: 1, p9: 1, p10: 1 };
    if (slug === "dmm") {
      omit.q1 = 1; omit.q2 = 1; omit.q3 = 1; omit.q4 = 1; omit.q5 = 1;
      omit.q6 = 1; omit.q7 = 1; omit.q8 = 1; omit.q9 = 1; omit.q10 = 1;
    }
    return keys.filter(function (k) { return !omit[k]; });
  }

  var jspdfLoadPromise = null;
  function loadJsPdf(cb) {
    var JsPDFConstructor = (typeof jspdf !== "undefined" && jspdf.jsPDF) ? jspdf.jsPDF : (typeof jsPDF !== "undefined" ? jsPDF : null);
    if (JsPDFConstructor) { cb(JsPDFConstructor); return; }
    if (jspdfLoadPromise) {
      jspdfLoadPromise.then(function () {
        var C = (typeof jspdf !== "undefined" && jspdf.jsPDF) ? jspdf.jsPDF : (typeof jsPDF !== "undefined" ? jsPDF : null);
        cb(C);
      });
      return;
    }
    jspdfLoadPromise = new Promise(function (resolve, reject) {
      var s1 = document.createElement("script");
      s1.src = "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js";
      s1.crossOrigin = "anonymous";
      s1.onload = function () {
        var s2 = document.createElement("script");
        s2.src = "https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.3/jspdf.plugin.autotable.min.js";
        s2.crossOrigin = "anonymous";
        s2.onload = function () { resolve(); };
        s2.onerror = reject;
        document.body.appendChild(s2);
      };
      s1.onerror = reject;
      document.body.appendChild(s1);
    });
    jspdfLoadPromise.then(function () {
      var C = (typeof jspdf !== "undefined" && jspdf.jsPDF) ? jspdf.jsPDF : (typeof jsPDF !== "undefined" ? jsPDF : null);
      cb(C);
    }).catch(function () { cb(null); });
  }

  function exportStudentToPdf(cardEl) {
    if (!cardEl) return;
    var studentId = cardEl.getAttribute("data-student-id");
    if (studentId == null || studentId === "") return;
    var id = parseInt(studentId, 10);
    if (isNaN(id)) return;
    var student = null;
    for (var i = 0; i < data.students.length; i++) {
      if (data.students[i].id === id) {
        student = data.students[i];
        break;
      }
    }
    if (!student) {
      alert("Student data not found.");
      return;
    }
    var btn = cardEl.querySelector(".export-pdf-student-btn");
    if (btn) btn.disabled = true;
    var studentName = (student.name || "").trim();
    var state = (student.state || "").trim();
    var filename = "math-competition-" + (studentName ? studentName.replace(/\W+/g, "-") : "student") + ".pdf";

    loadJsPdf(function (JsPDFConstructor) {
      if (!JsPDFConstructor) {
        alert("PDF export is not available. Please refresh the page and try again.");
        if (btn) btn.disabled = false;
        return;
      }
      try {
        var doc = new JsPDFConstructor({ orientation: "p", unit: "mm", format: "a4" });
      var margin = 10;
      var y = margin;

      doc.setFontSize(14);
      doc.text(studentName + (state ? " (" + state + ")" : ""), margin, y);
      y += 8;

      if (student.aliases && student.aliases.length) {
        doc.setFontSize(9);
        doc.setTextColor(100, 100, 100);
        doc.text("Also known as: " + student.aliases.join(", "), margin, y);
        doc.setTextColor(0, 0, 0);
        y += 6;
      }

      var records = student.records || [];
      var grouped = groupRecordsByContest(records);
      var slugs = grouped.slugs;
      var bySlug = grouped.bySlug;
      var contestsMap = data.contests || {};

      for (var s = 0; s < slugs.length; s++) {
        var slug = slugs[s];
        var contestRecords = bySlug[slug].slice();
        contestRecords.sort(function (a, b) {
          var yA = a.year || "";
          var yB = b.year || "";
          return yA > yB ? -1 : yA < yB ? 1 : 0;
        });
        var keys = keysForPdfDisplay(contestRecords, slug);
        var contestInfo = contestsMap[slug];
        var contestTitle = (contestInfo && contestInfo.contest_name) ? contestInfo.contest_name : slug.replace(/-/g, " ");

        if (y > 250) {
          doc.addPage();
          y = margin;
        }
        doc.setFontSize(11);
        doc.text(contestTitle, margin, y);
        y += 6;

        var contestDescription = (contestInfo && contestInfo.description) ? String(contestInfo.description) : "";
        if (contestDescription) {
          if (y > 260) {
            doc.addPage();
            y = margin;
          }
          doc.setFontSize(9);
          doc.setTextColor(80, 80, 80);
          var descLines = doc.splitTextToSize(contestDescription, 190 - margin * 2);
          doc.text(descLines, margin, y);
          doc.setTextColor(0, 0, 0);
          y += (descLines.length * 4.5);
        }

        var contestWebsite = (contestInfo && contestInfo.website) ? String(contestInfo.website) : "";
        if (contestWebsite) {
          if (y > 270) {
            doc.addPage();
            y = margin;
          }
          doc.setFontSize(8);
          doc.setTextColor(0, 0, 238);
          doc.text(contestWebsite, margin, y);
          doc.setTextColor(0, 0, 0);
          y += 5;
        }

        var headers = ["Year"].concat(keys.map(function (k) { return k.replace(/_/g, " "); }));
        var body = contestRecords.map(function (r) {
          var row = [r.year != null ? String(r.year) : ""];
          for (var k = 0; k < keys.length; k++) {
            var val = r[keys[k]];
            row.push(val != null ? String(val) : "");
          }
          return row;
        });
        doc.autoTable({
          head: [headers],
          body: body,
          startY: y,
          margin: { left: margin },
          theme: "grid",
          styles: { fontSize: 8 },
          headStyles: { fontSize: 8, fillColor: [96, 165, 250], textColor: [255, 255, 255] }
        });
        y = doc.lastAutoTable.finalY + 10;
      }

        doc.save(filename);
      } catch (err) {
        alert("Failed to generate PDF: " + (err && err.message ? err.message : "Unknown error"));
      }
      if (btn) btn.disabled = false;
    });
  }

  var PIE_COLORS = [
    "#60a5fa", "#f472b6", "#34d399", "#fbbf24", "#a78bfa",
    "#fb923c", "#22d3ee", "#f87171", "#4ade80", "#e879f9",
    "#38bdf8", "#facc15", "#2dd4bf", "#818cf8", "#fb7185",
    "#a3e635", "#c084fc", "#fca5a1", "#67e8f9", "#94a3b8"
  ];

  function computeStateDistributions(counts) {
    var studentsByState = {};
    var recordsByState = {};
    var mcpByState = {};
    for (var i = 0; i < counts.length; i++) {
      var state = (counts[i].student.state || "").trim() || "Unknown";
      studentsByState[state] = (studentsByState[state] || 0) + 1;
      recordsByState[state] = (recordsByState[state] || 0) + counts[i].recordsCount;
      var mcp = counts[i].mcpTotal != null ? Number(counts[i].mcpTotal) : 0;
      mcpByState[state] = (mcpByState[state] || 0) + mcp;
    }
    latestStateDist.students = studentsByState;
    latestStateDist.records = recordsByState;
    latestStateDist.mcp = mcpByState;
  }

  function drawPieChartOnElements(canvas, legendEl, distMap, valueFormatter) {
    if (!canvas || !legendEl) return;

    var entries = [];
    for (var k in distMap) {
      if (Object.prototype.hasOwnProperty.call(distMap, k)) {
        entries.push({ label: k, value: distMap[k] });
      }
    }
    entries.sort(function (a, b) { return b.value - a.value; });

    var total = 0;
    for (var i = 0; i < entries.length; i++) total += entries[i].value;

    if (total === 0) {
      var ctx0 = canvas.getContext("2d");
      ctx0.clearRect(0, 0, canvas.width, canvas.height);
      legendEl.innerHTML = "<p class=\"state-dist-empty\">No data available.</p>";
      return;
    }

    var MAX_SLICES = 15;
    var main = entries.slice(0, MAX_SLICES);
    var otherValue = 0;
    for (var i = MAX_SLICES; i < entries.length; i++) otherValue += entries[i].value;
    if (otherValue > 0) main.push({ label: "Other", value: otherValue });

    var dpr = window.devicePixelRatio || 1;
    var cssSize = 260;
    canvas.width = cssSize * dpr;
    canvas.height = cssSize * dpr;
    canvas.style.width = cssSize + "px";
    canvas.style.height = cssSize + "px";
    var ctx = canvas.getContext("2d");
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, cssSize, cssSize);

    var cx = cssSize / 2;
    var cy = cssSize / 2;
    var radius = cssSize / 2 - 8;
    var startAngle = -Math.PI / 2;

    for (var i = 0; i < main.length; i++) {
      var slice = main[i];
      var sliceAngle = (slice.value / total) * 2 * Math.PI;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, radius, startAngle, startAngle + sliceAngle);
      ctx.closePath();
      ctx.fillStyle = PIE_COLORS[i % PIE_COLORS.length];
      ctx.fill();
      ctx.strokeStyle = "#18181c";
      ctx.lineWidth = 2;
      ctx.stroke();

      if (slice.value / total > 0.05) {
        var midAngle = startAngle + sliceAngle / 2;
        var labelR = radius * 0.65;
        var lx = cx + Math.cos(midAngle) * labelR;
        var ly = cy + Math.sin(midAngle) * labelR;
        ctx.fillStyle = "#fff";
        ctx.font = "bold 11px system-ui, sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(Math.round((slice.value / total) * 100) + "%", lx, ly);
      }
      startAngle += sliceAngle;
    }

    var legendHtml = [];
    var fmt = typeof valueFormatter === "function" ? valueFormatter : function (v) { return v; };
    for (var i = 0; i < main.length; i++) {
      var pct = ((main[i].value / total) * 100).toFixed(1);
      legendHtml.push(
        "<div class=\"state-dist-legend-item\">" +
          "<span class=\"state-dist-legend-swatch\" style=\"background:" + PIE_COLORS[i % PIE_COLORS.length] + "\"></span>" +
          "<span class=\"state-dist-legend-label\">" + escapeHtml(main[i].label) + "</span>" +
          "<span class=\"state-dist-legend-value\">" + fmt(main[i].value) + " (" + pct + "%)</span>" +
        "</div>"
      );
    }
    legendEl.innerHTML = legendHtml.join("");
  }

  function renderStateDistCharts() {
    drawPieChartOnElements(
      document.getElementById("state-dist-students-canvas"),
      document.getElementById("state-dist-students-legend"),
      latestStateDist.students
    );
    drawPieChartOnElements(
      document.getElementById("state-dist-records-canvas"),
      document.getElementById("state-dist-records-legend"),
      latestStateDist.records
    );
    drawPieChartOnElements(
      document.getElementById("state-dist-mcp-canvas"),
      document.getElementById("state-dist-mcp-legend"),
      latestStateDist.mcp,
      function (v) { return Math.round(v).toLocaleString() + " MCP"; }
    );
  }

  function bindStateDistPopover() {
    var trigger = document.getElementById("state-dist-trigger");
    var popover = document.getElementById("state-dist-popover");
    var closeBtn = popover && popover.querySelector(".state-dist-popover-close");
    var backdrop = popover && popover.querySelector(".state-dist-popover-backdrop");
    if (!trigger || !popover) return;

    function openPopover() {
      popover.hidden = false;
      trigger.setAttribute("aria-expanded", "true");
      stateDistPopoverOpen = true;
      renderStateDistCharts();
    }

    function closePopover() {
      popover.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
      stateDistPopoverOpen = false;
    }

    trigger.addEventListener("click", function () {
      if (popover.hidden) openPopover(); else closePopover();
    });
    if (closeBtn) closeBtn.addEventListener("click", closePopover);
    if (backdrop) backdrop.addEventListener("click", closePopover);
  }

  function init() {
    bindThemeToggle();
    bindSiteNavDrawer();
    restoreFilters();
    if (!showHiddenFeature() && sortMode === "mcp_pct") {
      sortMode = "mcp";
      if (sortToggleEl) {
        var opts = sortToggleEl.querySelectorAll(".sort-toggle-option");
        for (var oi = 0; oi < opts.length; oi++) {
          opts[oi].classList.toggle("sort-toggle-option--active", opts[oi].getAttribute("data-mode") === "mcp");
        }
      }
      saveFilters();
    }
    document.querySelectorAll(".awards-ranking-controls").forEach(function (el) {
      el.style.visibility = "visible";
    });
    setLoading(true);
    var base = document.querySelector("script[src$='app.js']").src.replace(/\/[^/]*$/, "");
    Promise.all([
      fetch(base + "/data.json").then(function (res) {
        if (!res.ok) throw new Error("Failed to load data: " + res.status);
        return res.json();
      }),
      fetch(base + "/branch.json").then(function (res) {
        return res.ok ? res.json() : {};
      }).catch(function () { return {}; })
    ]).then(function (arr) {
      var json = arr[0];
      var branchCfg = arr[1];
      var si = json.slug_index || [];
      var km = json.key_map || {};
      var students = json.students || [];
      for (var s = 0; s < students.length; s++) {
        var recs = students[s].records || [];
        for (var r = 0; r < recs.length; r++) {
          var rec = recs[r];
          if (si.length && rec.c != null) {
            rec.contest_slug = si[rec.c];
            delete rec.c;
          }
          var keys = Object.keys(rec);
          for (var ki = 0; ki < keys.length; ki++) {
            var sk = keys[ki];
            var longKey = km[sk];
            if (longKey) {
              rec[longKey] = rec[sk];
              delete rec[sk];
            }
          }
        }
      }
      maxMcpYearBySlugGlobal = {};
      for (var sx = 0; sx < students.length; sx++) {
        var rs = students[sx].records || [];
        for (var rx = 0; rx < rs.length; rx++) {
          var rr = rs[rx];
          var sl = rr.contest_slug;
          if (!sl) continue;
          var mpp = rr.mcp_points;
          if (mpp == null || Number(mpp) <= 0) continue;
          var yy = parseInt(String(rr.year || ""), 10);
          if (isNaN(yy)) continue;
          if (maxMcpYearBySlugGlobal[sl] == null || yy > maxMcpYearBySlugGlobal[sl]) {
            maxMcpYearBySlugGlobal[sl] = yy;
          }
        }
      }
      data = json;
      data.branch = (branchCfg && branchCfg.branch) ? branchCfg.branch : "main";
      var order = json.contest_order || [];
      var orderMap = {};
      if (order && order.length) {
        for (var i = 0; i < order.length; i++) {
          var slug = order[i];
          if (slug != null && orderMap[slug] == null) {
            orderMap[slug] = i;
          }
        }
      }
      data.contest_order_map = orderMap;
      setLoading(false);
      var mcpPctOption = document.getElementById("mcp-pct-sort-option");
      if (mcpPctOption) mcpPctOption.hidden = !showHiddenFeature();
      requestAnimationFrame(function () {
        renderContestList();
        updateContestFilterSummary();
        renderTopStudentsByRecords();
        bindContestListPopover();
        bindStateDistPopover();
        bindMcpTimelinePopover();
        bindMcpPctPopover();
        bindCsvPopover();
        runSearch();
      });
    }).catch(function (err) {
      setLoading(false);
      resultsEl.innerHTML = "<p class=\"empty-state\">Could not load data. " + escapeHtml(String(err.message)) + "</p>";
    });
  }

  if (searchEl) {
    var debouncedSearch = debounce(runSearch, 80);
    searchEl.addEventListener("input", debouncedSearch);
    searchEl.addEventListener("search", runSearch);
  }

  if (searchClearEl) {
    searchClearEl.addEventListener("click", function () {
      if (!searchEl) return;
      searchEl.value = "";
      clearStudentIdFromUrl();
      runSearch();
      searchEl.focus();
    });
  }

  if (studentCardBackEl) {
    studentCardBackEl.addEventListener("click", function (e) {
      e.preventDefault();
      exitStudentCardViewToSearchResults();
    });
  }

  window.addEventListener("popstate", function () {
    runSearch();
  });

  if (girlsOnlyEl) {
    girlsOnlyEl.addEventListener("change", function () {
      saveFilters();
      renderTopStudentsByRecords();
      runSearch();
      refreshMcpTimelineIfOpen();
    });
  }

  if (gradeFilterEl) {
    gradeFilterEl.addEventListener("change", function () {
      saveFilters();
      renderTopStudentsByRecords();
      runSearch();
      refreshMcpTimelineIfOpen();
    });
  }

  if (stateFilterEl) {
    stateFilterEl.addEventListener("change", function () {
      saveFilters();
      renderTopStudentsByRecords();
      runSearch();
      refreshMcpTimelineIfOpen();
    });
  }

  if (searchApplyLeaderboardFiltersEl) {
    searchApplyLeaderboardFiltersEl.addEventListener("change", function () {
      saveFilters();
      runSearch();
    });
  }

  if (sortToggleEl) {
    sortToggleEl.addEventListener("click", function (e) {
      var opt = e.target && e.target.closest && e.target.closest(".sort-toggle-option");
      if (!opt) return;
      var mode = opt.getAttribute("data-mode");
      if (!mode || mode === sortMode) return;
      sortMode = mode;
      var opts = sortToggleEl.querySelectorAll(".sort-toggle-option");
      for (var i = 0; i < opts.length; i++) {
        opts[i].classList.toggle("sort-toggle-option--active", opts[i].getAttribute("data-mode") === sortMode);
      }
      saveFilters();
      renderTopStudentsByRecords();
      runSearch();
    });
  }

  if (mcpPctSortBtnEl) {
    mcpPctSortBtnEl.addEventListener("click", function () {
      ratioSortAsc = !ratioSortAsc;
      saveFilters();
      renderTopStudentsByRecords();
    });
  }

  if (topStudentsSectionEl && contestFilterTriggerEl) {
    topStudentsSectionEl.addEventListener("click", function (e) {
      var link = e.target && e.target.closest && e.target.closest(".mcp-pct-filter-link");
      if (!link) return;
      e.preventDefault();
      var popover = document.getElementById("contest-filter-popover");
      if (popover && popover.hidden) contestFilterTriggerEl.click();
    });
  }

  if (contestFilterTriggerEl && contestFilterWrapEl) {
    (function () {
      var popover = document.getElementById("contest-filter-popover");
      if (!popover) return;
      var closeBtn = popover.querySelector(".contest-filter-popover-close");
      var backdrop = popover.querySelector(".contest-filter-popover-backdrop");

      function openPopover() {
        popover.hidden = false;
        contestFilterTriggerEl.setAttribute("aria-expanded", "true");
      }

      function closePopover() {
        popover.hidden = true;
        contestFilterTriggerEl.setAttribute("aria-expanded", "false");
      }

      contestFilterTriggerEl.addEventListener("click", function () {
        if (popover.hidden) openPopover(); else closePopover();
      });
      if (closeBtn) {
        closeBtn.addEventListener("click", closePopover);
      }
      if (backdrop) {
        backdrop.addEventListener("click", closePopover);
      }
    })();
  }

  if (contestFilterEl) {
    contestFilterEl.addEventListener("change", function (event) {
      var target = event.target;
      if (!target || !target.type || target.type !== "checkbox") {
        updateContestFilterSummary();
        renderTopStudentsByRecords();
        runSearch();
        refreshMcpTimelineIfOpen();
        return;
      }
      var allBox = contestFilterEl.querySelector("input[type='checkbox'][value='all']");
      var boxes = contestFilterEl.querySelectorAll("input[type='checkbox']");
      if (target.value === "all") {
        for (var i = 0; i < boxes.length; i++) {
          if (boxes[i] !== allBox) {
            boxes[i].checked = target.checked;
          }
        }
      } else if (allBox) {
        if (!target.checked) {
          allBox.checked = false;
        } else {
          var allChecked = true;
          for (var j = 0; j < boxes.length; j++) {
            if (boxes[j] === allBox) continue;
            if (!boxes[j].checked) {
              allChecked = false;
              break;
            }
          }
          allBox.checked = allChecked;
        }
      }
      updateContestFilterSummary();
      saveFilters();
      renderTopStudentsByRecords();
      runSearch();
      refreshMcpTimelineIfOpen();
    });
  }

  var RAW_BASE = "https://raw.githubusercontent.com/x-du/math-competition/";
  var CSV_VIEWER_BASE = "csv-viewer.html";

  function showCsvPopover(contest, year) {
    var csvPopover = document.getElementById("csv-popover");
    var csvTitle = document.getElementById("csv-popover-title");
    var csvLoading = document.getElementById("csv-popover-loading");
    var csvError = document.getElementById("csv-popover-error");
    var csvTableWrap = document.getElementById("csv-popover-table-wrap");
    var csvTable = document.getElementById("csv-popover-table");
    var csvOpenTab = document.getElementById("csv-popover-open-tab");
    if (!csvPopover || !csvTitle) return;

    var contestYearFiles = data.contest_year_files || {};
    var filesByYear = contestYearFiles[contest] || {};
    var fileEntry = filesByYear[year] || "results.csv";
    var file = Array.isArray(fileEntry) ? (fileEntry[0] || "results.csv") : fileEntry;

    var contestInfo = (data.contests || {})[contest] || {};
    var contestName = contestInfo.contest_name || contest;
    var title = contestName + " " + year;
    csvTitle.textContent = title;
    csvLoading.hidden = false;
    csvError.hidden = true;
    csvTableWrap.hidden = true;
    csvOpenTab.hidden = true;
    csvPopover.hidden = false;

    var branch = (data.branch && data.branch !== "main") ? data.branch : "main";
    var rawUrl = RAW_BASE + encodeURIComponent(branch) + "/database/contests/" + encodeURIComponent(contest) + "/year%3D" + encodeURIComponent(year) + "/" + encodeURIComponent(file);
    var viewerUrl = CSV_VIEWER_BASE + "?contest=" + encodeURIComponent(contest) + "&year=" + encodeURIComponent(year) + "&file=" + encodeURIComponent(file) + "&name=" + encodeURIComponent(contestName);

    fetch(rawUrl)
      .then(function (res) {
        if (!res.ok) throw new Error("Failed to load: " + res.status);
        return res.text();
      })
      .then(function (text) {
        csvLoading.hidden = true;
        var result = (typeof Papa !== "undefined" && Papa.parse) ? Papa.parse(text, { header: true, skipEmptyLines: true }) : { data: [], meta: { fields: [] }, errors: [] };
        if (result.errors && result.errors.length) {
          csvError.textContent = "Parse error: " + (result.errors[0].message || "Unknown");
          csvError.hidden = false;
          csvOpenTab.href = viewerUrl;
          csvOpenTab.hidden = false;
          return;
        }
        var csvData = result.data || [];
        var fields = (result.meta.fields || []).filter(function (f) { return f !== "student_id"; });
        if (!fields.length && csvData.length) fields = Object.keys(csvData[0]).filter(function (f) { return f !== "student_id"; });
        if (!csvData.length && !fields.length) {
          csvError.textContent = "Empty or invalid CSV.";
          csvError.hidden = false;
          csvOpenTab.href = viewerUrl;
          csvOpenTab.hidden = false;
          return;
        }
        var colAlign = [];
        for (var i = 0; i < fields.length; i++) {
          var allNum = true;
          for (var r = 0; r < csvData.length; r++) {
            var v = csvData[r][fields[i]];
            if (v != null && String(v).trim() !== "" && !/^\d+(\.\d+)?$/.test(String(v).trim())) {
              allNum = false;
              break;
            }
          }
          colAlign[i] = allNum ? "num" : "";
        }
        var thead = "<thead><tr>";
        for (var i = 0; i < fields.length; i++) {
          thead += "<th scope=\"col\"" + (colAlign[i] ? " class=\"" + colAlign[i] + "\"" : "") + ">" + escapeHtml(fields[i]) + "</th>";
        }
        thead += "</tr></thead>";
        var tbody = "<tbody>";
        for (var r = 0; r < csvData.length; r++) {
          tbody += "<tr>";
          for (var i = 0; i < fields.length; i++) {
            var val = csvData[r][fields[i]] != null ? String(csvData[r][fields[i]]) : "";
            tbody += "<td" + (colAlign[i] ? " class=\"" + colAlign[i] + "\"" : "") + ">" + escapeHtml(val) + "</td>";
          }
          tbody += "</tr>";
        }
        tbody += "</tbody>";
        csvTable.innerHTML = thead + tbody;
        csvTableWrap.hidden = false;
        csvOpenTab.href = viewerUrl;
        csvOpenTab.hidden = false;
      })
      .catch(function (err) {
        csvLoading.hidden = true;
        csvError.textContent = "Could not load CSV: " + (err.message || err);
        csvError.hidden = false;
        csvOpenTab.href = viewerUrl;
        csvOpenTab.hidden = false;
      });
  }

  function handleResultsClick(event) {
    var target = event.target;
    var yearLink = target && target.closest ? target.closest(".csv-row-year-link") : null;
    if (yearLink) {
      event.preventDefault();
      var contest = yearLink.getAttribute("data-contest");
      var year = yearLink.getAttribute("data-year");
      if (contest && year) showCsvPopover(contest, year);
      return;
    }
    var perfYearBtn = target && target.closest && target.closest(".student-card-performance-btn");
    if (perfYearBtn) {
      event.preventDefault();
      event.stopPropagation();
      var sid = perfYearBtn.getAttribute("data-student-id");
      function openPerfPopover() {
        if (openMcpTimelinePopover && sid != null && sid !== "") {
          openMcpTimelinePopover({ resetMainSearch: false, ensureStudentId: sid });
        }
      }
      if (getStudentIdFromUrl() != null) {
        exitStudentCardViewToSearchResults();
        requestAnimationFrame(openPerfPopover);
      } else {
        openPerfPopover();
      }
      return;
    }
    if (target && target.classList && target.classList.contains("export-pdf-student-btn")) {
      var card = target.closest(".student-card");
      if (card) exportStudentToPdf(card);
      return;
    }
    if (target && target.classList && target.classList.contains("mcp-breakdown-btn")) {
      var wrap = target.closest(".mcp-breakdown-wrap");
      if (!wrap) return;
      var popover = wrap.querySelector(".mcp-breakdown-popover");
      var dataEl = wrap.querySelector(".mcp-breakdown-data");
      if (!popover || !dataEl) return;
      popover.hidden = false;
      var canvas = popover.querySelector(".mcp-breakdown-canvas");
      var legend = popover.querySelector(".mcp-breakdown-legend");
      try {
        var contribData = JSON.parse(dataEl.textContent);
        drawPieChartOnElements(canvas, legend, contribData);
      } catch (e) { /* ignore */ }
      return;
    }
    if (target && target.classList && (target.classList.contains("mcp-breakdown-close") || target.classList.contains("mcp-breakdown-backdrop"))) {
      var pop = target.closest(".mcp-breakdown-popover");
      if (pop) pop.hidden = true;
      return;
    }
    var nameEl = target && target.closest ? target.closest(".student-name") : null;
    if (!nameEl) return;
    var card = nameEl.closest ? nameEl.closest(".student-card") : null;
    var studentId = card ? card.getAttribute("data-student-id") : null;
    if (studentId != null && studentId !== "") {
      event.preventDefault();
      navigateToStudentAndScroll(studentId);
      return;
    }
    var nameAttr = nameEl.getAttribute("data-student-name");
    var name = (nameAttr || nameEl.textContent || "").trim();
    if (!name || !searchEl) return;
    searchEl.value = name;
    runSearch();
    searchEl.blur();
    if (typeof searchEl.setSelectionRange === "function") {
      var len = name.length;
      searchEl.setSelectionRange(len, len);
    }
    var firstCard = resultsEl.querySelector(".student-card");
    if (firstCard && typeof firstCard.scrollIntoView === "function") {
      firstCard.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  if (resultsEl) {
    resultsEl.addEventListener("click", handleResultsClick);
  }

  function openMcpPctPopover(triggerEl) {
    if (!triggerEl) return;
    var pct = triggerEl.getAttribute("data-pct");
    var contests = triggerEl.getAttribute("data-contests") || "selected contests";
    var bodyEl = document.getElementById("mcp-pct-popover-body");
    var popover = document.getElementById("mcp-pct-popover");
    if (!bodyEl || !popover) return;
    bodyEl.textContent = "MCP points achieved in " + contests + " is " + (pct != null ? pct : "—") + "% of the total MCP.";
    popover.hidden = false;
  }

  function handleMcpPctTrigger(event) {
    var target = event.target;
    var el = target && target.nodeType === 1 ? target : (target && (target.parentElement || target.parentNode));
    var mcpTrigger = el && el.closest ? el.closest(".mcp-pct-trigger") : null;
    if (mcpTrigger) {
      event.preventDefault();
      event.stopPropagation();
      openMcpPctPopover(mcpTrigger);
    }
  }

  document.addEventListener("click", handleMcpPctTrigger, true);
  document.addEventListener("touchend", handleMcpPctTrigger, true);

  function bindMcpPctPopover() {
    var popover = document.getElementById("mcp-pct-popover");
    var closeBtn = popover && popover.querySelector(".mcp-pct-popover-close");
    var backdrop = popover && popover.querySelector(".mcp-pct-popover-backdrop");
    if (!popover) return;
    function close() { popover.hidden = true; }
    if (closeBtn) closeBtn.addEventListener("click", close);
    if (backdrop) backdrop.addEventListener("click", close);
  }

  function bindCsvPopover() {
    var popover = document.getElementById("csv-popover");
    var closeBtn = popover && popover.querySelector(".csv-popover-close");
    var backdrop = popover && popover.querySelector(".csv-popover-backdrop");
    if (!popover) return;
    function close() { popover.hidden = true; }
    if (closeBtn) closeBtn.addEventListener("click", close);
    if (backdrop) backdrop.addEventListener("click", close);
  }

  if (awardsRankingListEl) {
    awardsRankingListEl.addEventListener("click", function (event) {
      var target = event.target;
      while (target && target !== awardsRankingListEl && !target.getAttribute("data-student-name")) {
        target = target.parentNode;
      }
      if (!target || target === awardsRankingListEl) return;
      var studentId = target.getAttribute("data-student-id");
      if (studentId != null && studentId !== "") {
        event.preventDefault();
        navigateToStudentAndScroll(studentId);
        return;
      }
      var name = (target.getAttribute("data-student-name") || target.textContent || "").trim();
      if (!name || !searchEl) return;
      searchEl.value = name;
      runSearch();
      searchEl.blur();
      if (typeof searchEl.setSelectionRange === "function") {
        var len = name.length;
        searchEl.setSelectionRange(len, len);
      }
      var firstCard = resultsEl && resultsEl.querySelector(".student-card");
      if (firstCard && typeof firstCard.scrollIntoView === "function") {
        firstCard.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  }

  // Tap-friendly tooltip for column headers
  (function () {
    var activeTooltip = null;
    function dismissTooltip() {
      if (activeTooltip && activeTooltip.parentNode) {
        activeTooltip.parentNode.removeChild(activeTooltip);
      }
      activeTooltip = null;
    }
    document.addEventListener("click", function (ev) {
      var th = ev.target && ev.target.closest ? ev.target.closest(".has-tooltip") : null;
      if (!th) { dismissTooltip(); return; }
      var text = th.getAttribute("data-tooltip");
      if (!text) return;
      ev.stopPropagation();
      dismissTooltip();
      var tip = document.createElement("div");
      tip.className = "col-tooltip";
      tip.textContent = text;
      th.style.position = "relative";
      th.appendChild(tip);
      activeTooltip = tip;
    }, true);
  })();

  // Dismiss keyboard on mobile when tapping outside the search box
  if (searchEl) {
    var searchWrap = document.querySelector(".search-wrap");
    function dismissKeyboardIfOutside(ev) {
      if (!searchEl) return;
      if (searchWrap && searchWrap.contains(ev.target)) return;
      searchEl.blur();
    }
    document.addEventListener("click", dismissKeyboardIfOutside, false);
    document.addEventListener("touchend", dismissKeyboardIfOutside, false);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
