(function () {
  "use strict";

  var data = { students: [], contests: {} };
  /** USPS code -> full name; from data.json. Student `state` and record `state` store short codes for US. */
  var usStateLookup = {};
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
  var searchApplyLeaderboardFiltersEl = document.getElementById("search-apply-leaderboard-filters");
  var searchApplyFiltersWrapEl = document.getElementById("search-apply-filters-wrap");
  var contestFilterTriggerEl = document.getElementById("contest-filter-trigger");
  var contestFilterPopoverEl = document.getElementById("contest-filter-popover");
  var competitionYearFilterEl = document.getElementById("competition-year-filter");
  var sortToggleEl = document.getElementById("sort-toggle");
  var mcpPctSortRowEl = document.getElementById("mcp-pct-sort-row");
  var mcpPctSortBtnEl = document.getElementById("mcp-pct-sort-btn");

  var sortMode = "mcp"; // "records", "mcp", or "mcp_pct"
  var gradeFilterInitialized = false;
  var ratioSortAsc = false; // For MCP %: true = ascending (lowest first), false = descending (default)

  var stateDistPopoverOpen = false;
  var genderDistPopoverOpen = false;
  var gradeDistPopoverOpen = false;
  var latestStateDist = { students: {}, records: {}, mcp: {}, studentNamesByState: {} };
  var latestGenderDist = { students: {}, records: {}, mcp: {}, studentNamesByGender: {} };
  var latestGradeDist = { students: {}, records: {}, mcp: {}, studentNamesByGrade: {} };
  var mcpPctStatsCache = { key: null, html: "" };
  var mcpTimelinePopoverOpen = false;
  var mcpTimelineChartInstance = null;
  var mcpTimelineSelectedIds = [];
  var MCP_TIMELINE_MAX_STUDENTS = 20;
  var SEARCH_RESULTS_DISPLAY_LIMIT = 10;
  var openMcpTimelinePopover = null;
  var mcpTimelineApplyFiltersEl = document.getElementById("mcp-timeline-apply-filters");
  var savedFilters = {};
  var searchValueBeforeStudentCard = null;
  var contestFilter = MathCompContestFilter.create(null);
  var contestFilterPopoverOpen = false;
  var contestFilterHasPendingApply = false;

  var FILTERS_KEY = "mathcomp_filters";
  /** Replace with your deployed Google Apps Script URL for student-record error reports. */
  var STUDENT_RECORD_REPORT_APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzzI2_Wxp5S4iF87bzWfX-vw-ClBKva_M33GG-JV7PGKxE287tPnfBK41M5_0WI9nlLeQ/exec";
  var STUDENT_RECORD_REPORT_TYPES = {
    account_merge: "Account Merge",
    state_label: "Update State",
    grade_label: "Update Grade"
  };
  var studentReportMenuOpenEl = null;
  var studentReportMenuOpenCardEl = null;
  var studentReportIpPromise = null;
  var studentReportModalContext = null;
  var studentReportToastTimer = null;

  /** Download icon; SVG uses pointer-events:none via CSS so delegated clicks hit the button. */
  var CHART_DOWNLOAD_ICON_HTML =
    "<svg class=\"chart-png-download__svg\" width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><path d=\"M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4\"/><polyline points=\"7 10 12 15 17 10\"/><line x1=\"12\" y1=\"15\" x2=\"12\" y2=\"3\"/></svg>";

  /** Appended to the bottom of every exported chart PNG. */
  var PNG_EXPORT_FOOTER_TEXT = "mathintegrity.org";

  /** Loaded from docs/promotions.json */
  var featurePromotions = [];
  var activePromotionIndex = 0;
  var promotionPopoverOpen = false;
  var promotionOutsidePointerHandler = null;

  function parseDateAtStartOfDay(dateStr) {
    if (!dateStr) return null;
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(dateStr).trim());
    if (!m) return null;
    var y = parseInt(m[1], 10);
    var mo = parseInt(m[2], 10) - 1;
    var d = parseInt(m[3], 10);
    var dt = new Date(y, mo, d, 0, 0, 0, 0);
    if (isNaN(dt.getTime())) return null;
    return dt;
  }

  function getClientIpForStudentReport() {
    if (studentReportIpPromise) return studentReportIpPromise;
    studentReportIpPromise = fetch("https://api.ipify.org?format=json")
      .then(function (resp) { return resp.json(); })
      .then(function (json) { return (json && json.ip) ? String(json.ip) : "unknown"; })
      .catch(function () { return "unknown"; });
    return studentReportIpPromise;
  }

  function closeStudentReportMenu() {
    if (!studentReportMenuOpenEl) return;
    studentReportMenuOpenEl.hidden = true;
    if (studentReportMenuOpenCardEl && studentReportMenuOpenCardEl.classList) {
      studentReportMenuOpenCardEl.classList.remove("student-card--report-menu-open");
    }
    studentReportMenuOpenCardEl = null;
    studentReportMenuOpenEl = null;
  }

  function openStudentReportMenuForButton(triggerBtn) {
    if (!triggerBtn || !triggerBtn.closest) return;
    var wrap = triggerBtn.closest(".student-record-report-wrap");
    if (!wrap) return;
    var menu = wrap.querySelector(".student-record-report-menu");
    if (!menu) return;
    var willOpen = !!menu.hidden;
    closeStudentReportMenu();
    menu.hidden = !willOpen;
    if (willOpen) {
      var cardEl = triggerBtn.closest(".student-card");
      if (cardEl && cardEl.classList) {
        cardEl.classList.add("student-card--report-menu-open");
        studentReportMenuOpenCardEl = cardEl;
      }
    }
    studentReportMenuOpenEl = willOpen ? menu : null;
  }

  function getStudentReportCardPayload(cardEl) {
    if (!cardEl || !cardEl.getAttribute) return null;
    return {
      student_id: String(cardEl.getAttribute("data-student-id") || "").trim(),
      student_name: String(cardEl.getAttribute("data-student-name") || "").trim(),
      student_state: String(cardEl.getAttribute("data-student-state") || "").trim(),
      student_grade: String(cardEl.getAttribute("data-student-grade") || "").trim()
    };
  }

  function submitStudentRecordReport(payload) {
    if (!STUDENT_RECORD_REPORT_APPS_SCRIPT_URL) {
      return Promise.reject(new Error("Report endpoint is not configured. Set STUDENT_RECORD_REPORT_APPS_SCRIPT_URL in docs/app.js."));
    }
    var formBody = new URLSearchParams();
    for (var key in payload) {
      if (!Object.prototype.hasOwnProperty.call(payload, key)) continue;
      formBody.append(key, payload[key] == null ? "" : String(payload[key]));
    }
    // Google Apps Script web apps commonly do not return CORS headers for browser fetch reads.
    // Use no-cors fire-and-forget submission so reports can still be delivered from the browser.
    return fetch(STUDENT_RECORD_REPORT_APPS_SCRIPT_URL, {
      method: "POST",
      mode: "no-cors",
      headers: { "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8" },
      body: formBody.toString()
    });
  }

  function parseDateAtEndOfDay(dateStr) {
    if (!dateStr) return null;
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(dateStr).trim());
    if (!m) return null;
    var y = parseInt(m[1], 10);
    var mo = parseInt(m[2], 10) - 1;
    var d = parseInt(m[3], 10);
    var dt = new Date(y, mo, d, 23, 59, 59, 999);
    if (isNaN(dt.getTime())) return null;
    return dt;
  }

  function isPromotionInActiveWindow(promotion, now) {
    var nowDate = now || new Date();
    var start = parseDateAtStartOfDay(promotion && promotion.startDate);
    var end = parseDateAtEndOfDay(promotion && promotion.endDate);
    if (start && nowDate < start) return false;
    if (end && nowDate > end) return false;
    return true;
  }

  function isLocalhostHost() {
    if (typeof window === "undefined" || !window.location) return false;
    var host = String(window.location.hostname || "").toLowerCase();
    return host === "localhost" || host === "127.0.0.1" || host === "::1";
  }

  function getActivePromotions() {
    var out = [];
    var now = new Date();
    var localPreview = isLocalhostHost();
    for (var i = 0; i < featurePromotions.length; i++) {
      var p = featurePromotions[i];
      if (!p || !p.enabled) continue;
      var inWindow = isPromotionInActiveWindow(p, now);
      if (!inWindow) continue;
      if (localPreview && p.showOnLocalhost) {
        out.push(p);
        continue;
      }
      out.push(p);
    }
    return out;
  }

  function normalizePromotionIndex(count) {
    if (count <= 0) return 0;
    if (activePromotionIndex < 0) activePromotionIndex = count - 1;
    if (activePromotionIndex >= count) activePromotionIndex = 0;
    return activePromotionIndex;
  }

  function renderPromotionBanner() {
    var bannerEl = document.getElementById("promotion-banner");
    if (!bannerEl) return;
    if (promotionOutsidePointerHandler) {
      document.removeEventListener("pointerdown", promotionOutsidePointerHandler, true);
      promotionOutsidePointerHandler = null;
    }
    var activePromotions = getActivePromotions();
    if (!activePromotions.length) {
      bannerEl.hidden = true;
      bannerEl.innerHTML = "";
      promotionPopoverOpen = false;
      return;
    }
    var idx = normalizePromotionIndex(activePromotions.length);
    var promotion = activePromotions[idx];

    bannerEl.innerHTML = "";
    var popoverId = "promotion-banner-popover";

    var toggleEl = document.createElement("button");
    toggleEl.type = "button";
    toggleEl.className = "promotion-banner__toggle";
    toggleEl.setAttribute("aria-expanded", promotionPopoverOpen ? "true" : "false");
    toggleEl.setAttribute("aria-controls", popoverId);
    toggleEl.textContent = "📣 " + (promotion.label || "Featured competition");
    bannerEl.appendChild(toggleEl);

    var popoverEl = document.createElement("section");
    popoverEl.id = popoverId;
    popoverEl.className = "promotion-banner__popover";
    popoverEl.hidden = !promotionPopoverOpen;
    bannerEl.appendChild(popoverEl);

    function closePromotionPopover() {
      popoverEl.hidden = true;
      promotionPopoverOpen = false;
      toggleEl.setAttribute("aria-expanded", "false");
    }

    var dismissEl = document.createElement("button");
    dismissEl.type = "button";
    dismissEl.className = "promotion-banner__close promotion-banner__close--dismiss";
    dismissEl.setAttribute("aria-label", "Close promotion popover");
    dismissEl.textContent = "\u00d7";
    dismissEl.addEventListener("click", closePromotionPopover);
    popoverEl.appendChild(dismissEl);

    toggleEl.addEventListener("click", function () {
      var isOpening = !!popoverEl.hidden;
      popoverEl.hidden = !isOpening;
      promotionPopoverOpen = isOpening;
      toggleEl.setAttribute("aria-expanded", isOpening ? "true" : "false");
    });

    promotionOutsidePointerHandler = function (ev) {
      if (popoverEl.hidden) return;
      var target = ev && ev.target;
      if (!target) return;
      if (popoverEl.contains(target) || toggleEl.contains(target)) return;
      closePromotionPopover();
    };
    document.addEventListener("pointerdown", promotionOutsidePointerHandler, true);

    var contentEl = document.createElement("div");
    contentEl.className = "promotion-banner__content";
    popoverEl.appendChild(contentEl);

    if (promotion.label) {
      var labelEl = document.createElement("p");
      labelEl.className = "promotion-banner__label";
      labelEl.textContent = promotion.label;
      contentEl.appendChild(labelEl);
    }

    var titleEl = document.createElement("h2");
    titleEl.className = "promotion-banner__title";
    titleEl.textContent = promotion.title || "";
    contentEl.appendChild(titleEl);

    if (promotion.description) {
      var descEl = document.createElement("p");
      descEl.className = "promotion-banner__description";
      descEl.textContent = promotion.description;
      contentEl.appendChild(descEl);
    }

    var metaParts = [];
    if (promotion.dateText) metaParts.push("Date: " + promotion.dateText);
    if (promotion.locationText) metaParts.push("Location: " + promotion.locationText);
    if (promotion.audienceText) metaParts.push("Audience: " + promotion.audienceText);
    if (metaParts.length) {
      var metaEl = document.createElement("p");
      metaEl.className = "promotion-banner__meta";
      metaEl.textContent = metaParts.join(" \u00b7 ");
      contentEl.appendChild(metaEl);
    }

    if (promotion.href && promotion.ctaText) {
      var actionsEl = document.createElement("p");
      actionsEl.className = "promotion-banner__actions";
      var ctaEl = document.createElement("a");
      ctaEl.className = "promotion-banner__cta";
      ctaEl.href = promotion.href;
      ctaEl.target = "_blank";
      ctaEl.rel = "noopener noreferrer";
      ctaEl.textContent = promotion.ctaText;
      actionsEl.appendChild(ctaEl);
      contentEl.appendChild(actionsEl);
    }

    if (activePromotions.length > 1) {
      var pagerEl = document.createElement("div");
      pagerEl.className = "promotion-banner__pager";

      var prevEl = document.createElement("button");
      prevEl.type = "button";
      prevEl.className = "promotion-banner__pager-btn";
      prevEl.textContent = "\u2039 Prev";
      prevEl.setAttribute("aria-label", "Show previous promotion");
      prevEl.addEventListener("click", function () {
        activePromotionIndex = idx - 1;
        promotionPopoverOpen = true;
        renderPromotionBanner();
      });
      pagerEl.appendChild(prevEl);

      var statusEl = document.createElement("span");
      statusEl.className = "promotion-banner__pager-status";
      statusEl.textContent = String(idx + 1) + " / " + String(activePromotions.length);
      pagerEl.appendChild(statusEl);

      var nextEl = document.createElement("button");
      nextEl.type = "button";
      nextEl.className = "promotion-banner__pager-btn";
      nextEl.textContent = "Next \u203a";
      nextEl.setAttribute("aria-label", "Show next promotion");
      nextEl.addEventListener("click", function () {
        activePromotionIndex = idx + 1;
        promotionPopoverOpen = true;
        renderPromotionBanner();
      });
      pagerEl.appendChild(nextEl);

      contentEl.appendChild(pagerEl);
    }

    bannerEl.hidden = false;
  }

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
        contest: contestFilter.getActiveContestFilterValues(),
        searchApplyLeaderboardFilters: searchApplyLeaderboardFiltersEl ? searchApplyLeaderboardFiltersEl.checked : true,
        mcpTimelineApplyFilters: mcpTimelineApplyFiltersEl ? mcpTimelineApplyFiltersEl.checked : true,
        competitionYear: competitionYearFilterEl ? competitionYearFilterEl.value : ""
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
      if (f.contest && Array.isArray(f.contest)) {
        contestFilter.restoreFromSavedArray(f.contest);
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
    /* Show only when the user is searching — not on single-student card (?student_id=). */
    searchApplyFiltersWrapEl.hidden = !(q.length > 0) || sid != null;
  }

  function applyContestFilterChangesNow() {
    mcpPctStatsCache.key = null;
    populateCompetitionYearFilterOptions();
    saveFilters();
    renderTopStudentsByRecords();
    runSearch();
    refreshMcpTimelineIfOpen();
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

  /**
   * Competition (slug) + optional season year — leaderboard, search, MCP % stats.
   * Performance-by-year chart uses contest filter only (see filterRecordsForMcpTimeline), not year.
   */
  function recordMatchesCompetitionFilters(record) {
    if (!record || !contestFilter.recordMatchesContestFilter(record)) return false;
    if (!competitionYearFilterEl || !competitionYearFilterEl.value) return true;
    var want = String(competitionYearFilterEl.value).trim();
    var y = record.year != null ? String(record.year).trim() : "";
    return y === want;
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
      var recs = (s.records || []).filter(function (r) {
        return recordMatchesCompetitionFilters(r);
      });
      if (recs.length === 0) continue;
      out.push(copyStudentShallow(s, recs));
    }
    return out;
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

  /** Full state name → US FIPS (2-digit string) for choropleth map. */
  var STATE_TO_FIPS = {
    Alabama: "01", Alaska: "02", Arizona: "04", Arkansas: "05", California: "06",
    Colorado: "08", Connecticut: "09", Delaware: "10", "District of Columbia": "11",
    Florida: "12", Georgia: "13", Hawaii: "15", Idaho: "16", Illinois: "17",
    Indiana: "18", Iowa: "19", Kansas: "20", Kentucky: "21", Louisiana: "22",
    Maine: "23", Maryland: "24", Massachusetts: "25", Michigan: "26", Minnesota: "27",
    Mississippi: "28", Missouri: "29", Montana: "30", Nebraska: "31", Nevada: "32",
    "New Hampshire": "33", "New Jersey": "34", "New Mexico": "35", "New York": "36",
    "North Carolina": "37", "North Dakota": "38", Ohio: "39", Oklahoma: "40", Oregon: "41",
    Pennsylvania: "42", "Rhode Island": "44", "South Carolina": "45", "South Dakota": "46",
    Tennessee: "47", Texas: "48", Utah: "49", Vermont: "50", Virginia: "51",
    Washington: "53", "West Virginia": "54", Wisconsin: "55", Wyoming: "56"
  };
  var FIPS_TO_STATE = {};
  for (var sn in STATE_TO_FIPS) {
    if (Object.prototype.hasOwnProperty.call(STATE_TO_FIPS, sn)) {
      FIPS_TO_STATE[STATE_TO_FIPS[sn]] = sn;
    }
  }

  var MAP_GRADIENT_LOW = "#1e3a5f";
  var MAP_GRADIENT_HIGH = "#60a5fa";

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

  /** Sum mcp_contrib by contest name for pie chart; include MPFG/EGMO only when includeMcpWSlugs is true. */
  function buildContribByContestMap(records, contestsMap, includeMcpWSlugs) {
    var contribByContest = {};
    contestsMap = contestsMap || {};
    for (var ci = 0; ci < records.length; ci++) {
      var rec = records[ci];
      var contrib = rec.mcp_contrib;
      if (!contrib || contrib <= 0) continue;
      var cSlug = rec.contest_slug || rec.contest || "other";
      if (!includeMcpWSlugs && isMcpWOnlySlug(cSlug)) continue;
      var cInfo = contestsMap[cSlug];
      var cName = (cInfo && cInfo.contest_name) ? cInfo.contest_name : cSlug;
      contribByContest[cName] = (contribByContest[cName] || 0) + contrib;
    }
    for (var ck in contribByContest) {
      if (Object.prototype.hasOwnProperty.call(contribByContest, ck)) {
        contribByContest[ck] = Math.round(contribByContest[ck] * 100) / 100;
      }
    }
    return contribByContest;
  }

  function isFemaleStudent(student) {
    return (student && (student.gender || "").toLowerCase()) === "female";
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

  /** Show MCP-by-year PNG only when the line chart area is visible and a chart instance exists. */
  function syncMcpTimelineDownloadPngButtonVisibility() {
    var btn = document.getElementById("mcp-timeline-download-png");
    var toolbar = btn && btn.closest(".mcp-timeline-chart-toolbar");
    var wrap = document.getElementById("mcp-timeline-chart-wrap");
    var show = !!(mcpTimelineChartInstance && wrap && !wrap.hidden);
    if (btn) btn.hidden = !show;
    if (toolbar) toolbar.hidden = !show;
  }

  function renderMcpTimelineChart() {
    try {
      var canvas = document.getElementById("mcp-timeline-canvas");
      var emptyEl = document.getElementById("mcp-timeline-empty");
      var wrap = document.getElementById("mcp-timeline-chart-wrap");
      if (!canvas) return;
      if (typeof Chart === "undefined") {
        if (mcpTimelineChartInstance) {
          mcpTimelineChartInstance.destroy();
          mcpTimelineChartInstance = null;
        }
        if (wrap) wrap.hidden = true;
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
        if (wrap) wrap.hidden = true;
        if (emptyEl) {
          emptyEl.hidden = false;
          emptyEl.textContent = "Add one or more students above to plot MCP by year.";
        }
        return;
      }
      var years = timelineAnchorYearsFromStudents(selected, false);
      if (!years.length) {
        if (wrap) wrap.hidden = true;
        if (emptyEl) {
          emptyEl.hidden = false;
          emptyEl.textContent = "No MCP timeline data for the selected students.";
        }
        return;
      }
      if (wrap) wrap.hidden = false;
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
          animation: false,
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
            surfaceBackground: {
              beforeDraw: function (ch) {
                var c = ch.ctx;
                var t = getExportThemeColors();
                c.save();
                c.fillStyle = t.surface;
                c.fillRect(0, 0, ch.width, ch.height);
                c.restore();
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
      var timelineChartRef = mcpTimelineChartInstance;
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          if (mcpTimelineChartInstance !== timelineChartRef || !timelineChartRef) return;
          var tlCanvas = chartJsExportCanvas(timelineChartRef);
          if (tlCanvas && typeof timelineChartRef.resize === "function") {
            chartJsEnsureSize(timelineChartRef, tlCanvas);
            if (typeof timelineChartRef.update === "function") timelineChartRef.update("none");
          }
        });
      });
    } finally {
      syncMcpTimelineDownloadPngButtonVisibility();
    }
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
      contestFilter.updateSummary();
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

    var timelinePngBtn = document.getElementById("mcp-timeline-download-png");
    if (timelinePngBtn) {
      timelinePngBtn.addEventListener("click", function () {
        if (!mcpTimelineChartInstance) {
          alert("Add at least one student with MCP data to export the chart.");
          return;
        }
        if (!downloadChartJsInstanceAsPng(mcpTimelineChartInstance, "mcp-by-year.png")) {
          alert("Could not export the chart. Try again after the chart has finished drawing.");
        }
      });
    }

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
        contestFilter.updateSummary(true);
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

    var scheduleMcpTimelineChartResize = debounce(function () {
      if (!mcpTimelinePopoverOpen || !mcpTimelineChartInstance) return;
      var chart = mcpTimelineChartInstance;
      if (typeof chart.resize !== "function") return;
      chart.resize();
      if (typeof chart.update === "function") chart.update("none");
    }, 120);
    window.addEventListener("resize", scheduleMcpTimelineChartResize);
    window.addEventListener("orientationchange", function () {
      setTimeout(scheduleMcpTimelineChartResize, 160);
    });
  }

  /**
   * Records for Performance-by-year chart and timeline search.
   * When “Apply competition filters” is on: same contest selection as the main page, but not season year
   * (the chart is MCP over calendar years; filtering by one season would break the line).
   */
  function filterRecordsForMcpTimeline(records) {
    var recs = records || [];
    if (!mcpTimelineChartUsesLeaderboardFilters()) return recs;
    return recs.filter(function (r) {
      return contestFilter.recordMatchesContestFilter(r);
    });
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
      var st = expandUsStateAbbrev((s.state || "").trim());
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

  function getStudentReportModalStateSelectOptionsHtml() {
    var parts = ["<option value=\"\">Select a state</option>"];
    for (var i = 0; i < US_STATES.length; i++) {
      var nm = US_STATES[i];
      parts.push(
        "<option value=\"" + escapeHtml(nm) + "\">" + escapeHtml(nm) + "</option>"
      );
    }
    parts.push("<option value=\"__other__\">Other</option>");
    return parts.join("");
  }

  function buildStudentReportModalBodyHtml(issueType) {
    if (issueType === "account_merge") {
      return (
        "<div class=\"student-report-modal-field\">" +
          "<label for=\"sr-merge-input\">Other student (ID or name)</label>" +
          "<input type=\"text\" id=\"sr-merge-input\" class=\"student-report-modal-input\" autocomplete=\"off\" />" +
        "</div>"
      );
    }
    if (issueType === "state_label") {
      return (
        "<div class=\"student-report-modal-field\">" +
          "<label for=\"sr-select-state\">State</label>" +
          "<select id=\"sr-select-state\" class=\"student-report-modal-select\">" +
            getStudentReportModalStateSelectOptionsHtml() +
          "</select>" +
        "</div>" +
        "<div id=\"sr-state-other-wrap\" class=\"student-report-modal-field\" hidden>" +
          "<label for=\"sr-input-state-other\">Other (specify)</label>" +
          "<input type=\"text\" id=\"sr-input-state-other\" class=\"student-report-modal-input\" autocomplete=\"off\" />" +
        "</div>"
      );
    }
    if (issueType === "grade_label") {
      return (
        "<div class=\"student-report-modal-field\">" +
          "<label for=\"sr-grade-current\">Current grade</label>" +
          "<input type=\"text\" id=\"sr-grade-current\" class=\"student-report-modal-input\" autocomplete=\"off\" inputmode=\"numeric\" placeholder=\"e.g. 9, 10, 11\" />" +
        "</div>" +
        "<p class=\"student-report-modal-hint\">Enter school grade as a number (for example, 10 or 11).</p>"
      );
    }
    return "<p>Unknown report type.</p>";
  }

  function setStudentReportModalError(msg) {
    var err = document.getElementById("student-report-modal-error");
    if (!err) return;
    if (msg) {
      err.textContent = msg;
      err.hidden = false;
    } else {
      err.textContent = "";
      err.hidden = true;
    }
  }

  function wireStudentReportModalFields(issueType) {
    if (issueType === "state_label") {
      var sel = document.getElementById("sr-select-state");
      var owrap = document.getElementById("sr-state-other-wrap");
      var oin = document.getElementById("sr-input-state-other");
      if (sel && owrap) {
        function sync() {
          owrap.hidden = sel.value !== "__other__";
          if (oin && !owrap.hidden) {
            setTimeout(function () {
              oin.focus();
            }, 0);
          }
        }
        sel.addEventListener("change", sync);
        sync();
      }
    } else if (issueType === "account_merge") {
      var minp = document.getElementById("sr-merge-input");
      if (minp) {
        setTimeout(function () {
          minp.focus();
        }, 0);
      }
    } else if (issueType === "grade_label") {
      var gcur = document.getElementById("sr-grade-current");
      if (gcur) {
        setTimeout(function () {
          gcur.focus();
        }, 0);
      }
    }
  }

  function closeStudentReportModal() {
    var modal = document.getElementById("student-report-modal");
    if (modal) modal.hidden = true;
    document.body.classList.remove("student-report-modal-open");
    if (studentReportModalContext && studentReportModalContext.optionBtn) {
      studentReportModalContext.optionBtn.disabled = false;
    }
    studentReportModalContext = null;
  }

  function hideStudentReportToast() {
    if (studentReportToastTimer) {
      clearTimeout(studentReportToastTimer);
      studentReportToastTimer = null;
    }
    var el = document.getElementById("student-report-toast");
    if (el) {
      el.hidden = true;
      el.className = "student-report-toast";
    }
    var t = document.getElementById("student-report-toast-text");
    if (t) t.textContent = "";
  }

  /** kind: "success" | "error" */
  function showStudentReportToast(message, kind) {
    var el = document.getElementById("student-report-toast");
    var t = document.getElementById("student-report-toast-text");
    if (!el || !t) return;
    hideStudentReportToast();
    t.textContent = message;
    el.className = "student-report-toast" + (kind === "error" ? " student-report-toast--error" : " student-report-toast--success");
    el.setAttribute("role", kind === "error" ? "alert" : "status");
    el.setAttribute("aria-live", kind === "error" ? "assertive" : "polite");
    el.hidden = false;
    studentReportToastTimer = setTimeout(function () {
      hideStudentReportToast();
    }, 6000);
  }

  function readStudentReportModalAdditional(issueType, studentIdStr) {
    var issueLabel = STUDENT_RECORD_REPORT_TYPES[issueType] || issueType;
    if (issueType === "account_merge") {
      var minp = document.getElementById("sr-merge-input");
      var v = minp ? String(minp.value).trim() : "";
      if (!v) {
        setStudentReportModalError("Enter the other student\u2019s ID or name.");
        return null;
      }
      if (/^\d+$/.test(v) && String(v) === String(studentIdStr)) {
        setStudentReportModalError("Choose a different ID than this profile.");
        return null;
      }
      return { issue_type: issueType, issue_label: issueLabel, user_value: v };
    }
    if (issueType === "state_label") {
      var sel = document.getElementById("sr-select-state");
      var oin = document.getElementById("sr-input-state-other");
      if (!sel) return null;
      var st = "";
      if (sel.value === "__other__") {
        st = oin ? String(oin.value).trim() : "";
        if (!st) {
          setStudentReportModalError("Please specify a state or territory.");
          return null;
        }
      } else {
        st = String(sel.value).trim();
        if (!st) {
          setStudentReportModalError("Select a state.");
          return null;
        }
      }
      return { issue_type: issueType, issue_label: issueLabel, user_value: st };
    }
    if (issueType === "grade_label") {
      var gcurIn = document.getElementById("sr-grade-current");
      var v = gcurIn ? String(gcurIn.value).trim() : "";
      if (!v) {
        setStudentReportModalError("Enter the current grade (e.g. 9, 10, 11).");
        return null;
      }
      if (!/^\d+$/.test(v)) {
        setStudentReportModalError("Use a whole number for grade (e.g. 10 or 11).");
        return null;
      }
      return { issue_type: issueType, issue_label: issueLabel, user_value: v };
    }
    return null;
  }

  function submitStudentReportWithPayloadFromModal() {
    if (!studentReportModalContext) return;
    var cardEl = studentReportModalContext.cardEl;
    var additional = readStudentReportModalAdditional(
      studentReportModalContext.issueType,
      getStudentReportCardPayload(cardEl).student_id
    );
    if (!additional) return;
    setStudentReportModalError("");
    var studentPayload = getStudentReportCardPayload(cardEl);
    // Close first so the UI is not blocked by ipify + report POST (no-cors still waits on the network).
    closeStudentReportModal();
    getClientIpForStudentReport()
      .then(function (ip) {
        var payload = {
          issue_type: additional.issue_type,
          issue_label: additional.issue_label,
          student_id: studentPayload.student_id,
          student_name: studentPayload.student_name,
          student_state: studentPayload.student_state,
          student_grade: studentPayload.student_grade,
          user_value: additional.user_value != null ? additional.user_value : "",
          related_student: additional.user_value != null ? additional.user_value : "",
          related_student_id: additional.user_value != null ? additional.user_value : "",
          other_student: additional.user_value != null ? additional.user_value : "",
          page_url: (window && window.location && window.location.href) ? String(window.location.href) : "",
          user_agent: (navigator && navigator.userAgent) ? String(navigator.userAgent) : "",
          ip: ip || "unknown",
          submitted_at: new Date().toISOString()
        };
        return submitStudentRecordReport(payload);
      })
      .then(function () {
        showStudentReportToast("Report sent. Thank you.", "success");
      })
      .catch(function (err) {
        var msg = (err && err.message) ? err.message : "Couldn\u2019t send the report. Check your connection and try again.";
        showStudentReportToast(msg, "error");
      });
  }

  function openStudentReportModal(issueType, cardEl, optionBtn) {
    var modal = document.getElementById("student-report-modal");
    var body = document.getElementById("student-report-modal-body");
    var title = document.getElementById("student-report-modal-title");
    var sp = getStudentReportCardPayload(cardEl);
    if (!modal || !body || !title) return;
    if (!sp || !sp.student_id) {
      studentReportModalContext = { cardEl: cardEl, issueType: issueType, optionBtn: optionBtn };
      body.innerHTML = "<p>Could not identify the student record.</p>";
      title.textContent = "Error";
      setStudentReportModalError("");
      var sub0 = document.getElementById("student-report-modal-submit");
      if (sub0) sub0.hidden = true;
      modal.hidden = false;
      return;
    }
    studentReportModalContext = { cardEl: cardEl, issueType: issueType, optionBtn: optionBtn };
    title.textContent = STUDENT_RECORD_REPORT_TYPES[issueType] || "Report";
    body.innerHTML = buildStudentReportModalBodyHtml(issueType);
    setStudentReportModalError("");
    var sub1 = document.getElementById("student-report-modal-submit");
    if (sub1) sub1.hidden = false;
    if (issueType === "grade_label") {
      var gPref = document.getElementById("sr-grade-current");
      if (gPref) gPref.value = "";
    }
    wireStudentReportModalFields(issueType);
    modal.hidden = false;
    document.body.classList.add("student-report-modal-open");
  }

  function bindStudentReportModal() {
    var modal = document.getElementById("student-report-modal");
    if (!modal) return;
    var toastClose = document.getElementById("student-report-toast-close");
    if (toastClose) {
      toastClose.addEventListener("click", function () {
        hideStudentReportToast();
      });
    }
    var closeBtn = document.getElementById("student-report-modal-close");
    var cancelBtn = document.getElementById("student-report-modal-cancel");
    var subBtn = document.getElementById("student-report-modal-submit");
    var back = modal.querySelector(".student-report-modal-backdrop");
    function onClose() {
      closeStudentReportModal();
    }
    if (closeBtn) closeBtn.addEventListener("click", onClose);
    if (cancelBtn) cancelBtn.addEventListener("click", onClose);
    if (back) back.addEventListener("click", onClose);
    if (subBtn) {
      subBtn.addEventListener("click", function () {
        submitStudentReportWithPayloadFromModal();
      });
    }
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && modal && !modal.hidden) {
        onClose();
      }
    });
  }

  function sanitizeDownloadFilename(s, fallback) {
    var base = String(s || fallback || "chart").replace(/[^a-zA-Z0-9._-]+/g, "-").replace(/^-+|-+$/g, "");
    return base || fallback || "chart";
  }

  function downloadPngDataUrl(dataUrl, filename) {
    if (!dataUrl || !/^data:image\/png/i.test(String(dataUrl))) return false;
    var stem = String(filename || "chart").replace(/\.png$/i, "");
    var name = sanitizeDownloadFilename(stem, "chart") + ".png";
    var ua = typeof navigator !== "undefined" ? navigator.userAgent || "" : "";
    var isIOS =
      /iPhone|iPad|iPod/i.test(ua) ||
      (typeof navigator !== "undefined" &&
        navigator.platform === "MacIntel" &&
        navigator.maxTouchPoints > 1);
    var isFileProtocol = typeof location !== "undefined" && location.protocol === "file:";

    function triggerPngUrlDownload(url) {
      if (isIOS) {
        try {
          window.open(url, "_blank", "noopener,noreferrer");
        } catch (e) { /* ignore */ }
      }
      var a = document.createElement("a");
      a.href = url;
      a.download = name;
      a.rel = "noopener";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      if (isFileProtocol && !isIOS) {
        try {
          window.open(url, "_blank", "noopener,noreferrer");
        } catch (e2) { /* ignore */ }
      }
    }

    try {
      var comma = String(dataUrl).indexOf(",");
      if (comma < 0) return false;
      var b64 = String(dataUrl)
        .slice(comma + 1)
        .replace(/\s/g, "");
      var bin = atob(b64);
      var len = bin.length;
      var arr = new Uint8Array(len);
      for (var i = 0; i < len; i++) arr[i] = bin.charCodeAt(i);
      var blob = new Blob([arr], { type: "image/png" });
      var objUrl = URL.createObjectURL(blob);
      triggerPngUrlDownload(objUrl);
      setTimeout(function () {
        try { URL.revokeObjectURL(objUrl); } catch (eRev) { /* ignore */ }
      }, 60000);
      return true;
    } catch (e1) {
      try {
        triggerPngUrlDownload(dataUrl);
        return true;
      } catch (e2) {
        return false;
      }
    }
  }

  /** Resolved CSS theme tokens for canvas export (matches active light/dark). */
  function getExportThemeColors() {
    var root = typeof getComputedStyle !== "undefined" ? getComputedStyle(document.documentElement) : null;
    return {
      bg: (root && root.getPropertyValue("--bg").trim()) || "#0f0f12",
      surface: (root && root.getPropertyValue("--surface").trim()) || "#18181c",
      border: (root && root.getPropertyValue("--border").trim()) || "#2a2a30",
      text: (root && root.getPropertyValue("--text").trim()) || "#e4e4e7",
      textMuted: (root && root.getPropertyValue("--text-muted").trim()) || "#a1a1aa"
    };
  }

  function truncateExportLegendText(ctx, str, maxW) {
    if (!str || ctx.measureText(str).width <= maxW) return str;
    var ell = "…";
    var s = str;
    while (s.length > 1 && ctx.measureText(s + ell).width > maxW) s = s.slice(0, -1);
    return s + ell;
  }

  function measureDomLegendHeight(legendEl, width) {
    if (!legendEl || legendEl.querySelector(".state-dist-empty")) return 0;
    var items = legendEl.querySelectorAll(".state-dist-legend-item");
    if (!items.length) return 0;
    var rowFontPx = Math.max(11, Math.min(14, Math.round(width / 42)));
    var rowH = rowFontPx + 6;
    return 10 + items.length * rowH + 10;
  }

  function drawDomLegendOntoCanvas(ctx, width, startY, legendEl, xOff) {
    xOff = xOff || 0;
    if (!legendEl || legendEl.querySelector(".state-dist-empty")) return 0;
    var items = legendEl.querySelectorAll(".state-dist-legend-item");
    if (!items.length) return 0;
    var theme = getExportThemeColors();
    var labelCol = theme.text;
    var valueCol = theme.textMuted;
    var rowFontPx = Math.max(11, Math.min(14, Math.round(width / 42)));
    var rowH = rowFontPx + 6;
    var padX = 12;
    var padTop = 10;
    var swatchW = 10;
    var swatchH = 10;
    var gap = 8;
    var y = startY + padTop + rowH / 2;
    ctx.textBaseline = "middle";
    for (var i = 0; i < items.length; i++) {
      var item = items[i];
      var swEl = item.querySelector(".state-dist-legend-swatch");
      var lblEl = item.querySelector(".state-dist-legend-label");
      var valEl = item.querySelector(".state-dist-legend-value");
      var col = "#60a5fa";
      if (swEl) {
        var st = swEl.getAttribute("style") || "";
        var m = st.match(/background:\s*([^;]+)/i);
        if (m) col = m[1].trim();
        else col = getComputedStyle(swEl).backgroundColor || col;
      }
      var label = lblEl ? lblEl.textContent.trim() : "";
      var val = valEl ? valEl.textContent.trim() : "";
      ctx.fillStyle = col;
      ctx.fillRect(padX + xOff, y - swatchH / 2, swatchW, swatchH);
      var textX = padX + swatchW + gap + xOff;
      var maxW = width - textX + xOff - padX;
      ctx.font = rowFontPx + "px system-ui, -apple-system, \"Segoe UI\", sans-serif";
      ctx.textAlign = "left";
      ctx.fillStyle = labelCol;
      var valPart = val ? "  " + val : "";
      var valDraw = valPart ? truncateExportLegendText(ctx, valPart, maxW * 0.52) : "";
      var labelBudget = maxW - (valDraw ? ctx.measureText(valDraw).width : 0);
      var labelDraw = truncateExportLegendText(ctx, label, Math.max(8, labelBudget));
      ctx.fillText(labelDraw, textX, y);
      if (valDraw) {
        ctx.fillStyle = valueCol;
        ctx.fillText(valDraw, textX + ctx.measureText(labelDraw).width, y);
      }
      y += rowH;
    }
    return padTop + items.length * rowH + 10;
  }

  function legendColorFromDataset(ds) {
    var c = ds.borderColor || ds.backgroundColor;
    if (Array.isArray(c)) c = c[0];
    return c || "#888";
  }

  /**
   * Read legend label typography from chart.options (same object Chart.js uses on screen).
   * Falls back to the same defaults as renderMcpTimelineChart (size 11, system-ui sans).
   */
  function resolveChartJsLegendLabelStyle(chart) {
    var fontPx = 11;
    var fontFamily = "system-ui, sans-serif";
    var fontWeight = "";
    var boxW = 14;
    var boxH = 14;
    var itemPad = 12;
    try {
      var L =
        chart &&
        chart.options &&
        chart.options.plugins &&
        chart.options.plugins.legend &&
        chart.options.plugins.legend.labels;
      if (L && typeof L === "object") {
        var f = L.font;
        if (typeof f === "object" && f !== null && typeof f !== "function") {
          if (f.size != null) {
            var sz = typeof f.size === "number" ? f.size : parseFloat(f.size);
            if (!isNaN(sz) && sz > 0) fontPx = sz;
          }
          if (typeof f.family === "string" && f.family) fontFamily = f.family;
          if (f.weight != null && f.weight !== "") fontWeight = String(f.weight);
        }
        if (typeof L.boxWidth === "number") boxW = L.boxWidth;
        if (typeof L.boxHeight === "number") boxH = L.boxHeight;
        if (typeof L.padding === "number") itemPad = L.padding;
      }
    } catch (e) {
      /* keep defaults */
    }
    return {
      fontPx: fontPx,
      fontFamily: fontFamily,
      fontWeight: fontWeight,
      boxW: boxW,
      boxH: boxH,
      itemPad: itemPad
    };
  }

  /**
   * Layout matching MCP-by-year Chart.js legend: position bottom, usePointStyle + rect;
   * width = chart canvas width (bitmap px).
   */
  function buildChartJsBottomLegendLayout(chart, width) {
    if (!chart || !chart.data || !chart.data.datasets || !chart.data.datasets.length) {
      return null;
    }
    var st = resolveChartJsLegendLabelStyle(chart);
    var dss = chart.data.datasets;
    var padLR = 12;
    var padTop = 10;
    var padBot = 10;
    var boxW = st.boxW;
    var boxH = st.boxH;
    var itemPad = st.itemPad;
    var fontPx = st.fontPx;
    var swatchTextGap = Math.max(4, Math.round(fontPx * 0.45));
    var rowGap = 8;
    var wPart = st.fontWeight ? st.fontWeight + " " : "";
    var fontCanvasString = wPart + fontPx + "px " + st.fontFamily;
    var maxInnerW = Math.max(0, width - padLR * 2);
    var tmp = document.createElement("canvas");
    var tctx = tmp.getContext("2d");
    if (!tctx) return null;
    tctx.font = fontCanvasString;
    var items = [];
    for (var i = 0; i < dss.length; i++) {
      var ds = dss[i];
      var lab0 = ds.label != null ? String(ds.label) : "Series " + (i + 1);
      var tw0 = tctx.measureText(lab0).width;
      items.push({
        labelFull: lab0,
        color: legendColorFromDataset(ds),
        itemW: boxW + swatchTextGap + tw0
      });
    }
    var rows = [];
    var line = [];
    var lineUsed = 0;
    for (var j = 0; j < items.length; j++) {
      var raw = items[j];
      var prefix = line.length ? itemPad : 0;
      var lab = raw.labelFull;
      var tw = tctx.measureText(lab).width;
      var itemW = boxW + swatchTextGap + tw;
      var avail = maxInnerW - lineUsed - prefix;
      if (itemW > avail) {
        lab = truncateExportLegendText(tctx, raw.labelFull, Math.max(8, avail - boxW - swatchTextGap));
        tw = tctx.measureText(lab).width;
        itemW = boxW + swatchTextGap + tw;
      }
      if (line.length && lineUsed + prefix + itemW > maxInnerW) {
        rows.push(line);
        line = [];
        lineUsed = 0;
        prefix = 0;
        lab = raw.labelFull;
        tw = tctx.measureText(lab).width;
        itemW = boxW + swatchTextGap + tw;
        avail = maxInnerW;
        if (itemW > avail) {
          lab = truncateExportLegendText(tctx, raw.labelFull, Math.max(8, avail - boxW - swatchTextGap));
          tw = tctx.measureText(lab).width;
          itemW = boxW + swatchTextGap + tw;
        }
      }
      line.push({ label: lab, color: raw.color, itemW: itemW });
      lineUsed += prefix + itemW;
    }
    if (line.length) rows.push(line);
    var lineH = Math.max(boxH, Math.ceil(fontPx * 1.2));
    var totalH =
      padTop + rows.length * lineH + Math.max(0, rows.length - 1) * rowGap + padBot;
    return {
      totalH: totalH,
      rows: rows,
      padLR: padLR,
      padTop: padTop,
      padBot: padBot,
      boxW: boxW,
      boxH: boxH,
      swatchTextGap: swatchTextGap,
      itemPad: itemPad,
      fontPx: fontPx,
      fontCanvasString: fontCanvasString,
      lineH: lineH,
      rowGap: rowGap,
      maxInnerW: maxInnerW
    };
  }

  function drawChartJsBottomLegendOntoCanvas(ctx, startY, layout) {
    if (!layout || !layout.rows || !layout.rows.length) return 0;
    var theme = getExportThemeColors();
    var y = startY + layout.padTop;
    ctx.textBaseline = "middle";
    for (var ri = 0; ri < layout.rows.length; ri++) {
      var row = layout.rows[ri];
      var rowW = 0;
      for (var ci = 0; ci < row.length; ci++) {
        if (ci) rowW += layout.itemPad;
        rowW += row[ci].itemW;
      }
      var x = layout.padLR + Math.max(0, (layout.maxInnerW - rowW) / 2);
      var lineY = y + layout.lineH / 2;
      for (var cj = 0; cj < row.length; cj++) {
        var it = row[cj];
        if (cj > 0) x += layout.itemPad;
        var boxTop = lineY - layout.boxH / 2;
        ctx.fillStyle = it.color;
        ctx.fillRect(x, boxTop, layout.boxW, layout.boxH);
        ctx.font = layout.fontCanvasString || layout.fontPx + "px system-ui, sans-serif";
        ctx.textAlign = "left";
        ctx.fillStyle = theme.text;
        ctx.fillText(it.label, x + layout.boxW + layout.swatchTextGap, lineY);
        x += it.itemW;
      }
      y += layout.lineH;
      if (ri < layout.rows.length - 1) y += layout.rowGap;
    }
    return layout.totalH;
  }

  /**
   * [chart canvas][optional DOM or Chart.js dataset legend][footer with site label].
   * opts: { legendEl?: Element, chartJs?: Chart } — use chartJs for line charts (dataset rows).
   */
  function composeChartPngExport(sourceCanvas, opts) {
    opts = opts || {};
    var legendEl = opts.legendEl || null;
    var chartJs = opts.chartJs || null;
    if (!sourceCanvas || !sourceCanvas.getContext) return null;
    var sw = sourceCanvas.width;
    var sh = sourceCanvas.height;
    if (!sw || !sh) return null;
    var legH = 0;
    var chartLegendLayout = null;
    if (legendEl) legH = measureDomLegendHeight(legendEl, sw);
    if (!legH && chartJs) {
      chartLegendLayout = buildChartJsBottomLegendLayout(chartJs, sw);
      legH = chartLegendLayout && chartLegendLayout.totalH ? chartLegendLayout.totalH : 0;
    }
    var footerH = Math.max(26, Math.round(0.055 * sw));
    var out = document.createElement("canvas");
    out.width = sw;
    out.height = sh + legH + footerH;
    var ctx = out.getContext("2d");
    if (!ctx) return null;
    var theme = getExportThemeColors();
    ctx.fillStyle = theme.surface;
    ctx.fillRect(0, 0, sw, sh + legH + footerH);
    try {
      ctx.drawImage(sourceCanvas, 0, 0);
    } catch (e) {
      return null;
    }
    if (legendEl && legH > 0) {
      ctx.fillStyle = theme.surface;
      ctx.fillRect(0, sh, sw, legH);
      ctx.strokeStyle = theme.border;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, sh + 0.5);
      ctx.lineTo(sw, sh + 0.5);
      ctx.stroke();
      drawDomLegendOntoCanvas(ctx, sw, sh, legendEl);
    } else if (chartLegendLayout && legH > 0) {
      ctx.fillStyle = theme.surface;
      ctx.fillRect(0, sh, sw, legH);
      ctx.strokeStyle = theme.border;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, sh + 0.5);
      ctx.lineTo(sw, sh + 0.5);
      ctx.stroke();
      drawChartJsBottomLegendOntoCanvas(ctx, sh, chartLegendLayout);
    }
    var footTop = sh + legH;
    ctx.fillStyle = theme.surface;
    ctx.fillRect(0, footTop, sw, footerH);
    ctx.strokeStyle = theme.border;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, footTop + 0.5);
    ctx.lineTo(sw, footTop + 0.5);
    ctx.stroke();
    var fontPx = Math.max(12, Math.min(18, Math.round(sw / 36)));
    ctx.font = "600 " + fontPx + "px system-ui, -apple-system, \"Segoe UI\", sans-serif";
    ctx.fillStyle = theme.textMuted;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(PNG_EXPORT_FOOTER_TEXT, sw / 2, footTop + footerH / 2);
    return out;
  }

  /**
   * One PNG: three state-distribution pies (same layout as the popover), column titles, legends, optional footer.
   * opts.includeFooter — default true; set false when a US map block + single footer will be appended by export.
   */
  function composeStateDistributionTriplePng(canvases /* [3] */, legendEls /* [3] */, titles, opts) {
    opts = opts || {};
    var includeFooter = opts.includeFooter !== false;
    if (!canvases || canvases.length !== 3 || !legendEls || legendEls.length !== 3) return null;
    var c0 = canvases[0];
    var c1 = canvases[1];
    var c2 = canvases[2];
    if (!c0 || !c1 || !c2 || !c0.width || !c1.width || !c2.width || !c0.height || !c1.height || !c2.height) return null;
    var cwDev = Math.max(c0.width, c1.width, c2.width);
    var chDev = Math.max(c0.height, c1.height, c2.height);
    var cwCss = Math.max(c0.clientWidth || 0, c1.clientWidth || 0, c2.clientWidth || 0);
    var chCss = Math.max(c0.clientHeight || 0, c1.clientHeight || 0, c2.clientHeight || 0);
    var dpr =
      typeof window !== "undefined" && window.devicePixelRatio
        ? window.devicePixelRatio
        : 1;
    if (!cwCss) cwCss = Math.max(1, Math.round(cwDev / dpr));
    if (!chCss) chCss = Math.max(1, Math.round(chDev / dpr));
    var cw = cwCss;
    var ch = chCss;
    var theme = getExportThemeColors();
    var titleFontPx = Math.max(13, Math.min(17, Math.round(cw / 17)));
    var titleH = titleFontPx + 14;
    var gap = Math.max(16, Math.round(cw * 0.08));
    var outerPad = Math.max(14, Math.round(cw * 0.05));
    var legHs = [
      measureDomLegendHeight(legendEls[0], cw),
      measureDomLegendHeight(legendEls[1], cw),
      measureDomLegendHeight(legendEls[2], cw)
    ];
    var mainH = titleH + ch + Math.max(legHs[0], legHs[1], legHs[2]);
    var totalW = outerPad * 2 + 3 * cw + 2 * gap;
    var footerH = includeFooter ? Math.max(26, Math.round(0.045 * totalW)) : 0;
    var totalH = outerPad + mainH + footerH;
    var out = document.createElement("canvas");
    out.width = totalW;
    out.height = totalH;
    var ctx = out.getContext("2d");
    if (!ctx) return null;
    ctx.fillStyle = theme.surface;
    ctx.fillRect(0, 0, totalW, totalH);
    var titlesArr = titles || ["Students by State", "Records by State", "MCP by State"];
    ctx.textBaseline = "middle";
    for (var col = 0; col < 3; col++) {
      var x0 = outerPad + col * (cw + gap);
      var y0 = outerPad;
      var cvs = canvases[col];
      ctx.fillStyle = theme.text;
      ctx.font = "600 " + titleFontPx + "px system-ui, -apple-system, \"Segoe UI\", sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(titlesArr[col], x0 + cw / 2, y0 + titleH / 2);
      try {
        ctx.drawImage(cvs, 0, 0, cvs.width, cvs.height, x0, y0 + titleH, cw, ch);
      } catch (e) {
        return null;
      }
      var legY = y0 + titleH + ch;
      if (legHs[col] > 0) {
        ctx.strokeStyle = theme.border;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(x0 + 0.5, legY + 0.5);
        ctx.lineTo(x0 + cw - 0.5, legY + 0.5);
        ctx.stroke();
        drawDomLegendOntoCanvas(ctx, cw, legY, legendEls[col], x0);
      }
    }
    if (includeFooter) {
      var footTop = outerPad + mainH;
      ctx.fillStyle = theme.surface;
      ctx.fillRect(0, footTop, totalW, footerH);
      ctx.strokeStyle = theme.border;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, footTop + 0.5);
      ctx.lineTo(totalW, footTop + 0.5);
      ctx.stroke();
      var footFontPx = Math.max(12, Math.min(18, Math.round(totalW / 50)));
      ctx.font = "600 " + footFontPx + "px system-ui, -apple-system, \"Segoe UI\", sans-serif";
      ctx.fillStyle = theme.textMuted;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(PNG_EXPORT_FOOTER_TEXT, totalW / 2, footTop + footerH / 2);
    }
    return out;
  }

  function getMaxStateDistStudentCount() {
    var o = latestStateDist && latestStateDist.students ? latestStateDist.students : {};
    var m = 0;
    for (var k in o) {
      if (!Object.prototype.hasOwnProperty.call(o, k)) continue;
      var n = Number(o[k]);
      if (!isNaN(n) && n > 0 && n > m) m = n;
    }
    return m > 0 ? m : 1;
  }

  function waitForStateDistMapSvg(callback) {
    var container = document.getElementById("state-dist-us-map-container");
    if (!container) {
      callback(null);
      return;
    }
    var svg = container.querySelector("svg");
    if (svg) {
      callback(svg);
      return;
    }
    ensureStateDistUsMap();
    var start = Date.now();
    var tid = setInterval(function () {
      svg = container.querySelector("svg");
      var empty = container.querySelector(".state-dist-empty");
      var failed =
        empty &&
        (empty.textContent.indexOf("could not") !== -1 || empty.textContent.indexOf("Map could") !== -1);
      if (svg || failed || Date.now() - start > 15000) {
        clearInterval(tid);
        callback(svg || null);
      }
    }, 45);
  }

  function rasterizeSvgToCanvas(svgEl, outCssW, outCssH, callback) {
    if (!svgEl || typeof svgEl.cloneNode !== "function") {
      callback(null);
      return;
    }
    var clone = svgEl.cloneNode(true);
    clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    var vb = svgEl.viewBox && svgEl.viewBox.baseVal;
    var vw = vb && vb.width ? vb.width : parseFloat(svgEl.getAttribute("width")) || 500;
    var vh = vb && vb.height ? vb.height : parseFloat(svgEl.getAttribute("height")) || 320;
    clone.setAttribute("width", String(vw));
    clone.setAttribute("height", String(vh));
    var svgStr = new XMLSerializer().serializeToString(clone);
    var blob = new Blob([svgStr], { type: "image/svg+xml;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var img = new Image();
    img.onload = function () {
      var canvas = document.createElement("canvas");
      var dpr = Math.min(
        2,
        typeof window !== "undefined" && window.devicePixelRatio ? window.devicePixelRatio : 2
      );
      var ow = Math.max(1, Math.round(outCssW));
      var oh = Math.max(1, Math.round(outCssH));
      canvas.width = ow * dpr;
      canvas.height = oh * dpr;
      var ctx = canvas.getContext("2d");
      if (!ctx) {
        URL.revokeObjectURL(url);
        callback(null);
        return;
      }
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);
      var theme = getExportThemeColors();
      ctx.fillStyle = theme.surface;
      ctx.fillRect(0, 0, ow, oh);
      try {
        ctx.drawImage(img, 0, 0, ow, oh);
      } catch (e) {
        URL.revokeObjectURL(url);
        callback(null);
        return;
      }
      URL.revokeObjectURL(url);
      callback(canvas);
    };
    img.onerror = function () {
      URL.revokeObjectURL(url);
      callback(null);
    };
    img.src = url;
  }

  function drawStateDistExportFooter(ctx, totalW, footTop, footerH) {
    var theme = getExportThemeColors();
    ctx.fillStyle = theme.surface;
    ctx.fillRect(0, footTop, totalW, footerH);
    ctx.strokeStyle = theme.border;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, footTop + 0.5);
    ctx.lineTo(totalW, footTop + 0.5);
    ctx.stroke();
    var footFontPx = Math.max(12, Math.min(18, Math.round(totalW / 50)));
    ctx.font = "600 " + footFontPx + "px system-ui, -apple-system, \"Segoe UI\", sans-serif";
    ctx.fillStyle = theme.textMuted;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(PNG_EXPORT_FOOTER_TEXT, totalW / 2, footTop + footerH / 2);
  }

  /**
   * Append optional US map (rasterized SVG) and a single site footer below the triple-chart canvas.
   */
  function finalizeStateDistributionPngWithOptionalMap(tripleCanvas, done) {
    var theme = getExportThemeColors();
    var totalW = tripleCanvas.width;
    var outerPad = Math.max(14, Math.round(totalW * 0.05));
    var contentW = totalW - 2 * outerPad;
    var footerH = Math.max(26, Math.round(0.045 * totalW));

    waitForStateDistMapSvg(function (svg) {
      function onlyTriplePlusFooter() {
        var out = document.createElement("canvas");
        out.width = totalW;
        out.height = tripleCanvas.height + footerH;
        var ctx = out.getContext("2d");
        if (!ctx) {
          done(null);
          return;
        }
        ctx.fillStyle = theme.surface;
        ctx.fillRect(0, 0, totalW, out.height);
        ctx.drawImage(tripleCanvas, 0, 0);
        drawStateDistExportFooter(ctx, totalW, tripleCanvas.height, footerH);
        done(out);
      }

      if (!svg) {
        onlyTriplePlusFooter();
        return;
      }

      var vb = svg.viewBox && svg.viewBox.baseVal;
      var vw = vb && vb.width ? vb.width : 500;
      var vh = vb && vb.height ? vb.height : 320;
      var maxMapW = contentW;
      var maxMapH = 340;
      var scale = Math.min(maxMapW / vw, maxMapH / vh);
      var mapDrawW = Math.round(vw * scale);
      var mapDrawH = Math.round(vh * scale);

      rasterizeSvgToCanvas(svg, mapDrawW, mapDrawH, function (mapCanvas) {
        if (!mapCanvas) {
          onlyTriplePlusFooter();
          return;
        }

        var maxStudents = getMaxStateDistStudentCount();
        var sectionGap = 20;
        var mapTitleFont = Math.max(13, Math.min(17, Math.round(totalW / 17)));
        var mapTitleH = mapTitleFont + 16;
        var noteFont = Math.max(10, Math.min(13, Math.round(totalW / 55)));
        var noteH = noteFont + 12;
        var gradBarH = 20;
        var gradLabelH = Math.max(14, noteFont + 4);
        var gradBlockH = gradBarH + gradLabelH + 4;
        var mapBlockH = mapTitleH + noteH + mapCanvas.height + 12 + gradBlockH;
        var newH = tripleCanvas.height + sectionGap + mapBlockH + footerH;

        var out = document.createElement("canvas");
        out.width = totalW;
        out.height = newH;
        var ctx = out.getContext("2d");
        if (!ctx) {
          done(null);
          return;
        }
        ctx.fillStyle = theme.surface;
        ctx.fillRect(0, 0, totalW, newH);
        ctx.drawImage(tripleCanvas, 0, 0);

        ctx.strokeStyle = theme.border;
        ctx.lineWidth = 1;
        var splitY = tripleCanvas.height + sectionGap / 2;
        ctx.beginPath();
        ctx.moveTo(outerPad, splitY);
        ctx.lineTo(totalW - outerPad, splitY);
        ctx.stroke();

        var y = tripleCanvas.height + sectionGap;
        ctx.fillStyle = theme.text;
        ctx.font = "600 " + mapTitleFont + "px system-ui, -apple-system, \"Segoe UI\", sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("US map — students per state", totalW / 2, y + mapTitleH / 2);
        y += mapTitleH;
        ctx.font = noteFont + "px system-ui, -apple-system, \"Segoe UI\", sans-serif";
        ctx.fillStyle = theme.textMuted;
        ctx.fillText("Lighter blue = more students in this database.", totalW / 2, y + noteH / 2);
        y += noteH;
        var mapX = outerPad + (contentW - mapCanvas.width) / 2;
        ctx.drawImage(mapCanvas, mapX, y);
        y += mapCanvas.height + 12;

        var gradW = Math.min(200, contentW);
        var gx = outerPad + (contentW - gradW) / 2;
        var ggrad = ctx.createLinearGradient(gx, 0, gx + gradW, 0);
        ggrad.addColorStop(0, MAP_GRADIENT_LOW);
        ggrad.addColorStop(1, MAP_GRADIENT_HIGH);
        ctx.fillStyle = ggrad;
        ctx.fillRect(gx, y, gradW, gradBarH);
        ctx.strokeStyle = theme.border;
        ctx.lineWidth = 1;
        ctx.strokeRect(gx, y, gradW, gradBarH);
        y += gradBarH + 4;
        ctx.font = noteFont + "px system-ui, -apple-system, \"Segoe UI\", sans-serif";
        ctx.fillStyle = theme.textMuted;
        ctx.textAlign = "left";
        ctx.textBaseline = "top";
        ctx.fillText("0", gx, y);
        ctx.textAlign = "right";
        ctx.fillText(maxStudents + " students", gx + gradW, y);

        drawStateDistExportFooter(ctx, totalW, tripleCanvas.height + sectionGap + mapBlockH, footerH);
        done(out);
      });
    });
  }

  function downloadStateDistributionCombinedPng() {
    var cvs = [
      document.getElementById("state-dist-students-canvas"),
      document.getElementById("state-dist-records-canvas"),
      document.getElementById("state-dist-mcp-canvas")
    ];
    var legs = [
      document.getElementById("state-dist-students-legend"),
      document.getElementById("state-dist-records-legend"),
      document.getElementById("state-dist-mcp-legend")
    ];
    for (var i = 0; i < 3; i++) {
      if (!cvs[i] || !cvs[i].width || !cvs[i].height) {
        alert("Charts are not ready to export yet.");
        return false;
      }
    }
    var composed = composeStateDistributionTriplePng(cvs, legs, null, { includeFooter: false });
    if (!composed) {
      alert("Could not build the combined image.");
      return false;
    }
    finalizeStateDistributionPngWithOptionalMap(composed, function (finalCanvas) {
      if (!finalCanvas) {
        alert("Could not build the combined image.");
        return;
      }
      if (!downloadPngDataUrl(finalCanvas.toDataURL("image/png"), "state-distribution-by-state.png")) {
        alert("Could not start download.");
      }
    });
    return true;
  }

  function downloadGenderDistributionCombinedPng() {
    var cvs = [
      document.getElementById("gender-dist-students-canvas"),
      document.getElementById("gender-dist-records-canvas"),
      document.getElementById("gender-dist-mcp-canvas")
    ];
    var legs = [
      document.getElementById("gender-dist-students-legend"),
      document.getElementById("gender-dist-records-legend"),
      document.getElementById("gender-dist-mcp-legend")
    ];
    for (var i = 0; i < 3; i++) {
      if (!cvs[i] || !cvs[i].width || !cvs[i].height) {
        alert("Charts are not ready to export yet.");
        return false;
      }
    }
    var composed = composeStateDistributionTriplePng(
      cvs,
      legs,
      ["Students by Gender", "Records by Gender", "MCP by Gender"],
      { includeFooter: true }
    );
    if (!composed) {
      alert("Could not build the combined image.");
      return false;
    }
    if (!downloadPngDataUrl(composed.toDataURL("image/png"), "distribution-by-gender.png")) {
      alert("Could not start download.");
    }
    return true;
  }

  function downloadGradeDistributionCombinedPng() {
    var cvs = [
      document.getElementById("grade-dist-students-canvas"),
      document.getElementById("grade-dist-records-canvas"),
      document.getElementById("grade-dist-mcp-canvas")
    ];
    var legs = [
      document.getElementById("grade-dist-students-legend"),
      document.getElementById("grade-dist-records-legend"),
      document.getElementById("grade-dist-mcp-legend")
    ];
    for (var i = 0; i < 3; i++) {
      if (!cvs[i] || !cvs[i].width || !cvs[i].height) {
        alert("Charts are not ready to export yet.");
        return false;
      }
    }
    var composed = composeStateDistributionTriplePng(
      cvs,
      legs,
      ["Students by Grade", "Records by Grade", "MCP by Grade"],
      { includeFooter: true }
    );
    if (!composed) {
      alert("Could not build the combined image.");
      return false;
    }
    if (!downloadPngDataUrl(composed.toDataURL("image/png"), "distribution-by-grade.png")) {
      alert("Could not start download.");
    }
    return true;
  }

  function downloadCanvasAsPng(canvas, filename, legendEl) {
    if (!canvas || !canvas.getContext) return false;
    try {
      if (!canvas.width || !canvas.height) return false;
      var composed = composeChartPngExport(canvas, { legendEl: legendEl || null, chartJs: null });
      if (!composed) return false;
      return downloadPngDataUrl(composed.toDataURL("image/png"), filename);
    } catch (e) {
      return false;
    }
  }

  function chartJsExportCanvas(chart) {
    if (!chart) return null;
    return chart.canvas || (chart.ctx && chart.ctx.canvas) || null;
  }

  function chartJsEnsureSize(chart, canvas) {
    if (!chart || !canvas || typeof chart.resize !== "function") return;
    try {
      var w = canvas.width;
      var h = canvas.height;
      if (w > 0 && h > 0) return;
      var wrap =
        canvas.closest(".mcp-timeline-chart-wrap") ||
        canvas.closest(".attraction-chart-wrap") ||
        canvas.parentElement;
      if (wrap && wrap.getBoundingClientRect) {
        var r = wrap.getBoundingClientRect();
        var rw = Math.max(1, Math.floor(r.width));
        var rh = Math.max(1, Math.floor(r.height));
        try {
          chart.resize(rw, rh);
        } catch (resizeEx) {
          chart.resize();
        }
      } else {
        chart.resize();
      }
    } catch (e) { /* ignore */ }
  }

  function downloadChartJsInstanceAsPng(chart, filename) {
    var canvas = chartJsExportCanvas(chart);
    if (!chart || !canvas) return false;
    var plugins = chart.options.plugins || (chart.options.plugins = {});
    var legendOpts = plugins.legend || (plugins.legend = {});
    var hadDisplayKey = Object.prototype.hasOwnProperty.call(legendOpts, "display");
    var prevLegendDisplay = legendOpts.display;
    legendOpts.display = false;
    try {
      chartJsEnsureSize(chart, canvas);
      if (typeof chart.update === "function") chart.update("none");
      if ((!canvas.width || !canvas.height) && typeof chart.resize === "function") {
        chart.resize();
        if (typeof chart.update === "function") chart.update("none");
      }
      if (!canvas.width || !canvas.height) return false;
      var composed = composeChartPngExport(canvas, { legendEl: null, chartJs: chart });
      if (!composed) return false;
      return downloadPngDataUrl(composed.toDataURL("image/png"), filename);
    } catch (e) {
      return false;
    } finally {
      if (hadDisplayKey) legendOpts.display = prevLegendDisplay;
      else delete legendOpts.display;
      if (typeof chart.update === "function") chart.update("none");
    }
  }

  /** USPS code -> full name for display (student or contest row); non-US strings unchanged. */
  function expandUsStateAbbrev(val) {
    if (val == null || val === "") return "";
    var s = String(val).trim();
    if (usStateLookup && Object.prototype.hasOwnProperty.call(usStateLookup, s)) return usStateLookup[s];
    return s;
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
      if (key === "state") val = expandUsStateAbbrev(val);
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
    var female = isFemaleStudent(student);
    var grouped = groupRecordsByContest(records);
    var bySlug = grouped.bySlug;
    var slugs = grouped.slugs;
    var state = expandUsStateAbbrev(student.state || "");

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
    var totalMcpOpen = student.mcp != null ? Number(student.mcp) : 0;
    var totalMcpW = female && student.mcp_w != null ? Number(student.mcp_w) : totalMcpOpen;
    var contestFilterActiveCard = contestFilter.isContestFilterActive() && !useCanonicalMcpStats;
    var mcpOpenShown;
    var mcpWShown;
    if (useCanonicalMcpStats) {
      mcpOpenShown = totalMcpOpen;
      mcpWShown = female && student.mcp_w != null ? Number(student.mcp_w) : totalMcpOpen;
    } else {
      mcpOpenShown = computeMcpFromRecords(records, false);
      mcpWShown = female ? computeMcpFromRecords(records, true) : mcpOpenShown;
    }

    function mcpPctSuffixFor(totalShown, totalDenom) {
      if (sortMode !== "mcp_pct" || !contestFilterActiveCard || totalShown <= 0 || totalDenom <= 0) return "";
      var ratio = totalShown / totalDenom;
      var pctValCard = formatMcpPct(ratio);
      var contestLabelsCard = contestFilter.getSelectedContestLabels();
      var contestsStrCard = contestLabelsCard.length ? contestLabelsCard.join(", ") : "selected competitions";
      return " (<button type=\"button\" class=\"mcp-pct-trigger\" data-pct=\"" + escapeHtml(pctValCard) + "\" data-contests=\"" + escapeHtml(contestsStrCard) + "\">" + pctValCard + "%</button>)";
    }

    var mcpDisplay = "";
    if (female) {
      var parts = [];
      parts.push("<span class=\"student-stat\">" + formatMcpValue(mcpOpenShown) + " MCP" + mcpPctSuffixFor(mcpOpenShown, totalMcpOpen) + "</span>");
      parts.push("<span class=\"student-stat\">" + formatMcpValue(mcpWShown) + " MCP-W" + mcpPctSuffixFor(mcpWShown, totalMcpW) + "</span>");
      mcpDisplay = parts.join("");
    } else if (mcpOpenShown > 0) {
      mcpDisplay = "<span class=\"student-stat\">" + formatMcpValue(mcpOpenShown) + " MCP" + mcpPctSuffixFor(mcpOpenShown, totalMcpOpen) + "</span>";
    }
    var statsHtml = "<span class=\"student-stats\">" +
      "<span class=\"student-stat\">" + totalRecords + (totalRecords === 1 ? " record" : " records") + "</span>" +
      mcpDisplay +
      "</span>";

    function mcpBreakdownBlock(label, totalPts, contribJson) {
      return (
        "<span class=\"mcp-breakdown-wrap\">" +
          "<button type=\"button\" class=\"mcp-breakdown-btn\" aria-label=\"" + escapeHtml(label) + " breakdown\">" + escapeHtml(label) + "</button>" +
          "<div class=\"mcp-breakdown-popover\" hidden>" +
            "<div class=\"mcp-breakdown-popover-inner\">" +
              "<h3 class=\"mcp-breakdown-title\">" + escapeHtml(student.name || "Student") + " — " + escapeHtml(label) + " Breakdown — " + escapeHtml(formatMcpValue(totalPts)) + " pts</h3>" +
              "<canvas class=\"mcp-breakdown-canvas\" width=\"260\" height=\"260\"></canvas>" +
              "<button type=\"button\" class=\"mcp-breakdown-download-png chart-png-download chart-png-download--icon\" aria-label=\"Download chart as PNG\">" + CHART_DOWNLOAD_ICON_HTML + "</button>" +
              "<div class=\"mcp-breakdown-legend\"></div>" +
              "<button type=\"button\" class=\"mcp-breakdown-close\" aria-label=\"Close\">×</button>" +
            "</div>" +
            "<div class=\"mcp-breakdown-backdrop\" aria-hidden=\"true\"></div>" +
          "</div>" +
          "<script type=\"application/json\" class=\"mcp-breakdown-data\">" + contribJson + "</script>" +
        "</span>"
      );
    }

    var mcpBtnHtml = "";
    if (female) {
      if (mcpWShown > 0) {
        var contribW = buildContribByContestMap(records, contestsMap, true);
        if (Object.keys(contribW).length > 0) {
          mcpBtnHtml = mcpBreakdownBlock("MCP", mcpWShown, JSON.stringify(contribW));
        }
      }
    } else if (mcpOpenShown > 0) {
      var contribMale = buildContribByContestMap(records, contestsMap, false);
      if (Object.keys(contribMale).length > 0) {
        mcpBtnHtml = mcpBreakdownBlock("MCP", mcpOpenShown, JSON.stringify(contribMale));
      }
    }

    var contestsHtml = headerOnly ? "" : "<div class=\"student-contests\">" + sections.join("") + "</div>";
    var studentReportMenuHtml =
      "<span class=\"student-record-report-wrap\">" +
        "<button type=\"button\" class=\"student-record-report-trigger\" aria-label=\"Report a student record error\" title=\"Report a student record error\">🛠️</button>" +
        "<div class=\"student-record-report-menu\" hidden>" +
          "<p class=\"student-record-report-title\">Report student record error</p>" +
          "<button type=\"button\" class=\"student-record-report-option\" data-issue-type=\"account_merge\">Account Merge</button>" +
          "<button type=\"button\" class=\"student-record-report-option\" data-issue-type=\"state_label\">Update State</button>" +
          "<button type=\"button\" class=\"student-record-report-option\" data-issue-type=\"grade_label\">Update Grade</button>" +
        "</div>" +
      "</span>";
    var headerActionsHtml =
      "<div class=\"student-header-actions\">" +
        mcpBtnHtml +
        "<button type=\"button\" class=\"student-card-performance-btn\" data-student-id=\"" +
        escapeHtml(String(student.id)) +
        "\" aria-label=\"Open performance by year chart for this student\">Performance</button>" +
        "<button type=\"button\" class=\"export-pdf-student-btn\" aria-label=\"Export this student to PDF\">PDF</button>" +
        studentReportMenuHtml +
      "</div>";
    var studentNameSafe = String(student.name || "").trim();
    var stateSafe = String(state || "").trim();
    var gradeSafe = String(gradeLabel || "").trim();
    return (
      "<article class=\"student-card\" data-student-id=\"" + escapeHtml(String(student.id)) + "\" data-student-name=\"" + escapeHtml(studentNameSafe) + "\" data-student-state=\"" + escapeHtml(stateSafe) + "\" data-student-grade=\"" + escapeHtml(gradeSafe) + "\">" +
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
      var filesByYearForSlug = contestYearFiles[slug] || {};
      var yearSet = {};
      for (var y1 in filesByYearForSlug) if (Object.prototype.hasOwnProperty.call(filesByYearForSlug, y1)) yearSet[y1] = true;
      var years = [];
      for (var yk in yearSet) if (Object.prototype.hasOwnProperty.call(yearSet, yk)) years.push(yk);
      years.sort(function (a, b) { return b.localeCompare(a, undefined, { numeric: true }); });
      var nameHtml = (c && c.website)
        ? "<a href=\"" + escapeHtml(c.website) + "\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"contest-list-link\">" + escapeHtml(name) + "</a>"
        : "<span class=\"contest-list-item\">" + escapeHtml(name) + "</span>";
      var yearLinks = [];
      var filesByYear = filesByYearForSlug;
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
        var st = expandUsStateAbbrev((s.state || "").trim());
        if (wantState === "__none__") return !st;
        if (wantState === "__other__") return st && !US_STATES_SET[st];
        if (wantState === "US") return st && US_STATES_SET[st];
        return st === wantState;
      });
    }

    var isGirlsOnly = girlsOnlyEl && girlsOnlyEl.checked;
    var contestFilterActive = contestFilter.isContestFilterActive();
    var isMcpPct = sortMode === "mcp_pct";

    if (mcpPctSortRowEl) mcpPctSortRowEl.hidden = !isMcpPct;
    var mcpPctSortTextEl = document.getElementById("mcp-pct-sort-text");
    if (mcpPctSortTextEl) mcpPctSortTextEl.textContent = ratioSortAsc ? "Sorted ascending (lowest contribution first)." : "Sorted descending (highest contribution first).";
    if (mcpPctSortBtnEl) mcpPctSortBtnEl.textContent = ratioSortAsc ? "Sort ascending ↑" : "Sort descending ↓";

    var counts = [];
    if (students && students.length) {
      for (var i = 0; i < students.length; i++) {
        var student = students[i];
        var records = (student.records || []).filter(function (r) {
          return recordMatchesCompetitionFilters(r);
        });
        var count = records.length;
        if (count > 0) {
          var mcpTotal = null;
          var mcpRatio = null;
          /* MCP from the same record set as counts (competition + season year filters). */
          var filteredMcp = computeMcpFromRecords(records, isGirlsOnly);
          var totalMcp = isGirlsOnly && student.mcp_w != null ? Number(student.mcp_w) : (student.mcp != null ? Number(student.mcp) : 0);
          if (sortMode === "mcp") {
            mcpTotal = filteredMcp;
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
            mcpTotal = filteredMcp;
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
    computeGenderDistributions(counts);
    computeGradeDistributions(counts);
    if (stateDistPopoverOpen) renderStateDistCharts();
    if (genderDistPopoverOpen) renderGenderDistCharts();
    if (gradeDistPopoverOpen) renderGradeDistCharts();

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
        var contestFilterKey = contestFilter.getActiveContestFilterValues().join(",");
        var yearPart = competitionYearFilterEl && competitionYearFilterEl.value ? "|y:" + competitionYearFilterEl.value : "";
        if (mcpPctStatsCache.key !== contestFilterKey + yearPart) {
          var allStudents = data.students || [];
          var allForStats = [];
          for (var ai = 0; ai < allStudents.length; ai++) {
            var st = allStudents[ai];
            var totalMcpSt = st.mcp != null ? Number(st.mcp) : 0;
            if (totalMcpSt <= 0) continue;
            var recsFiltered = (st.records || []).filter(function (r) {
              return recordMatchesCompetitionFilters(r);
            });
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
          mcpPctStatsCache.key = contestFilterKey + yearPart;
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
            var contestLabels = contestFilter.getSelectedContestLabels();
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
      var state = expandUsStateAbbrev(s.state || "");
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
          var contestLabels = contestFilter.getSelectedContestLabels();
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
          awardsRankingFiltersEl.hidden = true;
          awardsRankingFiltersEl.style.display = "none";
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
          hintEl.textContent = "1 student found. Full competition history below.";
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
      if (awardsRankingFiltersEl) {
        awardsRankingFiltersEl.hidden = false;
        awardsRankingFiltersEl.style.display = "";
      }
      if (searchInputWrapEl) searchInputWrapEl.hidden = false;
      if (hintEl) hintEl.hidden = false;
      if (studentCardBackEl) studentCardBackEl.hidden = true;
      syncSearchPerformanceButtonVisibility();
      syncSearchApplyFiltersToggleVisibility();
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
          ? "<p>No name matches with your current filters. Try turning off <strong>Apply filters to search</strong> or widening Girls / Grade / State / Competition / Year filters.</p>"
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
    var state = expandUsStateAbbrev((student.state || "").trim());
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
            var keyK = keys[k];
            var val = r[keyK];
            if (keyK === "state") val = expandUsStateAbbrev(val);
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
    var studentNamesByState = {};
    for (var i = 0; i < counts.length; i++) {
      var state = expandUsStateAbbrev((counts[i].student.state || "").trim()) || "Unknown";
      studentsByState[state] = (studentsByState[state] || 0) + 1;
      recordsByState[state] = (recordsByState[state] || 0) + counts[i].recordsCount;
      var mcp = counts[i].mcpTotal != null ? Number(counts[i].mcpTotal) : 0;
      mcpByState[state] = (mcpByState[state] || 0) + mcp;
      var nm = ((counts[i].student && counts[i].student.name) || "").trim() || "—";
      if (!studentNamesByState[state]) studentNamesByState[state] = [];
      studentNamesByState[state].push(nm);
    }
    for (var st in studentNamesByState) {
      if (Object.prototype.hasOwnProperty.call(studentNamesByState, st)) {
        studentNamesByState[st].sort(function (a, b) { return a.localeCompare(b, undefined, { sensitivity: "base" }); });
      }
    }
    latestStateDist.students = studentsByState;
    latestStateDist.records = recordsByState;
    latestStateDist.mcp = mcpByState;
    latestStateDist.studentNamesByState = studentNamesByState;
  }

  function genderLabelForStudent(student) {
    var g = ((student && student.gender) || "").trim().toLowerCase();
    if (g === "female") return "Female";
    if (g === "male") return "Male";
    return "Unknown";
  }

  function computeGenderDistributions(counts) {
    var studentsByGender = {};
    var recordsByGender = {};
    var mcpByGender = {};
    var studentNamesByGender = {};
    for (var i = 0; i < counts.length; i++) {
      var gender = genderLabelForStudent(counts[i].student);
      studentsByGender[gender] = (studentsByGender[gender] || 0) + 1;
      recordsByGender[gender] = (recordsByGender[gender] || 0) + counts[i].recordsCount;
      var mcp = counts[i].mcpTotal != null ? Number(counts[i].mcpTotal) : 0;
      mcpByGender[gender] = (mcpByGender[gender] || 0) + mcp;
      var nm = ((counts[i].student && counts[i].student.name) || "").trim() || "—";
      if (!studentNamesByGender[gender]) studentNamesByGender[gender] = [];
      studentNamesByGender[gender].push(nm);
    }
    for (var k in studentNamesByGender) {
      if (Object.prototype.hasOwnProperty.call(studentNamesByGender, k)) {
        studentNamesByGender[k].sort(function (a, b) { return a.localeCompare(b, undefined, { sensitivity: "base" }); });
      }
    }
    latestGenderDist.students = studentsByGender;
    latestGenderDist.records = recordsByGender;
    latestGenderDist.mcp = mcpByGender;
    latestGenderDist.studentNamesByGender = studentNamesByGender;
  }

  function computeGradeDistributions(counts) {
    var studentsByGrade = {};
    var recordsByGrade = {};
    var mcpByGrade = {};
    var studentNamesByGrade = {};
    for (var i = 0; i < counts.length; i++) {
      var lab = getGradeLabel(counts[i].student && counts[i].student.grade_in_2026);
      var gradeKey = lab || "No grade";
      studentsByGrade[gradeKey] = (studentsByGrade[gradeKey] || 0) + 1;
      recordsByGrade[gradeKey] = (recordsByGrade[gradeKey] || 0) + counts[i].recordsCount;
      var mcpG = counts[i].mcpTotal != null ? Number(counts[i].mcpTotal) : 0;
      mcpByGrade[gradeKey] = (mcpByGrade[gradeKey] || 0) + mcpG;
      var nmG = ((counts[i].student && counts[i].student.name) || "").trim() || "—";
      if (!studentNamesByGrade[gradeKey]) studentNamesByGrade[gradeKey] = [];
      studentNamesByGrade[gradeKey].push(nmG);
    }
    for (var kg in studentNamesByGrade) {
      if (Object.prototype.hasOwnProperty.call(studentNamesByGrade, kg)) {
        studentNamesByGrade[kg].sort(function (a, b) { return a.localeCompare(b, undefined, { sensitivity: "base" }); });
      }
    }
    latestGradeDist.students = studentsByGrade;
    latestGradeDist.records = recordsByGrade;
    latestGradeDist.mcp = mcpByGrade;
    latestGradeDist.studentNamesByGrade = studentNamesByGrade;
  }

  function drawPieChartOnElements(canvas, legendEl, distMap, valueFormatter, sliceNamesResolver) {
    if (!canvas || !legendEl) return;

    if (canvas._stateDistPieClickHandler) {
      canvas.removeEventListener("click", canvas._stateDistPieClickHandler);
      canvas._stateDistPieClickHandler = null;
    }
    canvas.style.cursor = "";

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
      var dpr0 = window.devicePixelRatio || 1;
      var z = 260;
      canvas.width = z * dpr0;
      canvas.height = z * dpr0;
      canvas.style.width = z + "px";
      canvas.style.height = z + "px";
      ctx0.setTransform(1, 0, 0, 1, 0, 0);
      ctx0.scale(dpr0, dpr0);
      ctx0.fillStyle = getExportThemeColors().surface;
      ctx0.fillRect(0, 0, z, z);
      legendEl.innerHTML = "<p class=\"state-dist-empty\">No data available.</p>";
      canvas._stateDistPieHit = null;
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
    var pieBg = getExportThemeColors().surface;
    ctx.fillStyle = pieBg;
    ctx.fillRect(0, 0, cssSize, cssSize);

    var cx = cssSize / 2;
    var cy = cssSize / 2;
    var radius = cssSize / 2 - 8;
    var startAngle = -Math.PI / 2;
    var segmentsMeta = [];

    for (var i = 0; i < main.length; i++) {
      var slice = main[i];
      var sliceAngle = (slice.value / total) * 2 * Math.PI;
      segmentsMeta.push({ label: slice.label, sliceAngle: sliceAngle });
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, radius, startAngle, startAngle + sliceAngle);
      ctx.closePath();
      ctx.fillStyle = PIE_COLORS[i % PIE_COLORS.length];
      ctx.fill();
      var pieTheme = getExportThemeColors();
      ctx.strokeStyle = pieTheme.border;
      ctx.lineWidth = 2;
      ctx.stroke();

      var share = slice.value / total;
      var midAngle = startAngle + sliceAngle / 2;
      var labelR = radius * 0.64;
      var lx = cx + Math.cos(midAngle) * labelR;
      var ly = cy + Math.sin(midAngle) * labelR;
      var pctStr = (share * 100).toFixed(1) + "%";
      var fontPx = share < 0.04 ? 9 : share < 0.1 ? 10 : 11;
      if (sliceAngle < 0.18) fontPx = Math.min(fontPx, 9);
      ctx.font = "bold " + fontPx + "px system-ui, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillStyle = "#ffffff";
      ctx.shadowColor = "rgba(0,0,0,0.5)";
      ctx.shadowBlur = 3;
      ctx.shadowOffsetX = 0;
      ctx.shadowOffsetY = 1;
      ctx.fillText(pctStr, lx, ly);
      ctx.shadowBlur = 0;
      ctx.shadowOffsetY = 0;
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

    if (typeof sliceNamesResolver === "function") {
      var otherBucketLabels = [];
      for (var oi = MAX_SLICES; oi < entries.length; oi++) {
        otherBucketLabels.push(entries[oi].label);
      }
      canvas._stateDistPieHit = {
        cssSize: cssSize,
        cx: cx,
        cy: cy,
        radius: radius,
        segments: segmentsMeta,
        otherStateLabels: otherBucketLabels
      };
      canvas.style.cursor = "pointer";
      canvas._stateDistPieClickHandler = function (ev) {
        ev.stopPropagation();
        var meta = canvas._stateDistPieHit;
        if (!meta || !meta.segments || !meta.segments.length) return;
        var rect = canvas.getBoundingClientRect();
        var px = ((ev.clientX - rect.left) / rect.width) * meta.cssSize;
        var py = ((ev.clientY - rect.top) / rect.height) * meta.cssSize;
        var dx = px - meta.cx;
        var dy = py - meta.cy;
        var dist = Math.sqrt(dx * dx + dy * dy);
        if (dist > meta.radius) return;
        var ang = Math.atan2(dy, dx);
        var fromTop = ang + Math.PI / 2;
        if (fromTop < 0) fromTop += 2 * Math.PI;
        if (fromTop >= 2 * Math.PI - 1e-10) fromTop -= 2 * Math.PI;
        var cum = 0;
        var idx = -1;
        for (var si = 0; si < meta.segments.length; si++) {
          var sa = meta.segments[si].sliceAngle;
          var nextCum = cum + sa;
          var last = si === meta.segments.length - 1;
          if (fromTop >= cum - 1e-9 && (last ? fromTop <= nextCum + 1e-7 : fromTop < nextCum - 1e-9)) {
            idx = si;
            break;
          }
          cum = nextCum;
        }
        if (idx < 0) return;
        var sliceLabel = meta.segments[idx].label;
        var got = sliceNamesResolver(sliceLabel, meta.otherStateLabels);
        showStateDistStudentNamesTooltip(ev.clientX, ev.clientY, got.title, got.names);
      };
      canvas.addEventListener("click", canvas._stateDistPieClickHandler);
    } else {
      canvas._stateDistPieHit = null;
    }
  }

  function interpolateUsMapColor(t) {
    function parseHex(hex) {
      return [
        parseInt(hex.slice(1, 3), 16),
        parseInt(hex.slice(3, 5), 16),
        parseInt(hex.slice(5, 7), 16)
      ];
    }
    var a = parseHex(MAP_GRADIENT_LOW);
    var b = parseHex(MAP_GRADIENT_HIGH);
    var r = Math.round(a[0] + (b[0] - a[0]) * t);
    var g = Math.round(a[1] + (b[1] - a[1]) * t);
    var bl = Math.round(a[2] + (b[2] - a[2]) * t);
    return "#" + [r, g, bl].map(function (x) { return x.toString(16).padStart(2, "0"); }).join("");
  }

  function syncStateDistUsMapColors() {
    var container = document.getElementById("state-dist-us-map-container");
    if (!container || !container.querySelector("svg")) return;
    updateStateDistUsMapColors(latestStateDist.students || {});
  }

  /**
   * Mirror .state-dist-us-map-state-label in style.css via inline styles so SVG→PNG export
   * (XMLSerializer) picks up the same typography and stroke halo as the live page.
   */
  function applyStateDistUsMapLabelStyles(container) {
    if (typeof d3 === "undefined") return;
    var theme = getExportThemeColors();
    var labels = d3.select(container).selectAll(".state-dist-us-map-state-label");
    if (labels.empty()) return;
    labels
      .style("font-size", "9px")
      .style("font-weight", "600")
      .style("font-family", 'system-ui, -apple-system, "Segoe UI", sans-serif')
      .style("fill", theme.text)
      .style("stroke", theme.bg)
      .style("stroke-width", "2px")
      .style("paint-order", "stroke fill")
      .style("pointer-events", "none")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central");
  }

  function updateStateDistUsMapColors(distMap) {
    if (typeof d3 === "undefined") return;
    var container = document.getElementById("state-dist-us-map-container");
    if (!container) return;
    var states = d3.select(container).selectAll(".state-dist-us-map-state");
    if (states.empty()) return;
    var merged = distMap || {};
    var fipsToCount = {};
    var vals = [];
    for (var stateName in merged) {
      if (!Object.prototype.hasOwnProperty.call(merged, stateName)) continue;
      var fips = STATE_TO_FIPS[stateName];
      if (fips) {
        var n = Number(merged[stateName]);
        if (!isNaN(n) && n > 0) {
          fipsToCount[fips] = n;
          vals.push(n);
        }
      }
    }
    var maxCount = vals.length ? Math.max.apply(null, vals) : 1;
    function colorScale(count) {
      if (count <= 0) return "#2a2a30";
      return interpolateUsMapColor(Math.min(1, count / maxCount));
    }
    states.each(function () {
      var fips = this.getAttribute("data-fips");
      var fid = String(fips || "").padStart(2, "0");
      var count = fipsToCount[fid] || 0;
      var color = colorScale(count);
      this.style.setProperty("fill", color);
      this.setAttribute("fill", color);
    });
    var labels = d3.select(container).selectAll(".state-dist-us-map-state-label");
    if (!labels.empty()) {
      labels.text(function () {
        var fips = this.getAttribute("data-fips");
        var fid = String(fips).padStart(2, "0");
        var count = fipsToCount[fid] || 0;
        return count > 0 ? String(count) : "";
      });
      applyStateDistUsMapLabelStyles(container);
    }
    var legendEl = document.getElementById("state-dist-us-map-gradient-legend");
    if (legendEl && maxCount > 0 && vals.length > 0) {
      var gradientId = "state-dist-map-gradient-fill";
      legendEl.innerHTML =
        "<div class=\"map-gradient-bar-wrap\">" +
        "<svg width=\"200\" height=\"20\" class=\"map-gradient-bar\">" +
        "<defs><linearGradient id=\"" + gradientId + "\" x1=\"0\" x2=\"1\" y1=\"0\" y2=\"0\">" +
        "<stop offset=\"0\" stop-color=\"" + MAP_GRADIENT_LOW + "\"/>" +
        "<stop offset=\"1\" stop-color=\"" + MAP_GRADIENT_HIGH + "\"/>" +
        "</linearGradient></defs>" +
        "<rect width=\"200\" height=\"20\" fill=\"url(#" + gradientId + ")\"/>" +
        "</svg></div>" +
        "<div class=\"map-gradient-labels\"><span>0</span><span>" + maxCount + " students</span></div>";
      legendEl.hidden = false;
      legendEl.style.display = "block";
    } else if (legendEl) {
      legendEl.innerHTML = "";
      legendEl.hidden = true;
    }
  }

  var stateDistMapOutsideClickBound = false;
  var stateDistMapTooltipClickStopBound = false;
  var stateDistNamesEscapeBound = false;

  function clearStateDistMapStudentNameTooltip() {
    var tip = document.getElementById("state-dist-us-map-tooltip");
    if (tip) {
      tip.classList.remove("state-dist-us-map-tooltip--names");
      tip.textContent = "";
      tip.innerHTML = "";
      tip.style.display = "none";
      tip.style.pointerEvents = "";
      tip.setAttribute("aria-hidden", "true");
    }
  }

  function bindStateDistMapOutsideDismiss() {
    if (stateDistMapOutsideClickBound) return;
    stateDistMapOutsideClickBound = true;
    /* Capture phase: runs before canvas/map stopPropagation so outside clicks always dismiss the name list. */
    document.addEventListener(
      "click",
      function (ev) {
        if (!stateDistPopoverOpen && !genderDistPopoverOpen && !gradeDistPopoverOpen) return;
        var tip = document.getElementById("state-dist-us-map-tooltip");
        if (!tip || !tip.classList.contains("state-dist-us-map-tooltip--names")) return;
        var el = ev.target;
        if (!el || !el.closest) return;
        if (el.closest("#state-dist-us-map-tooltip")) return;
        if (el.closest(".state-dist-us-map-wrap")) return;
        clearStateDistMapStudentNameTooltip();
      },
      true
    );
  }

  function bindStateDistNamesEscapeDismiss() {
    if (stateDistNamesEscapeBound) return;
    stateDistNamesEscapeBound = true;
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      var tip = document.getElementById("state-dist-us-map-tooltip");
      if (!tip || !tip.classList.contains("state-dist-us-map-tooltip--names")) return;
      if (!stateDistPopoverOpen && !genderDistPopoverOpen && !gradeDistPopoverOpen) return;
      e.preventDefault();
      clearStateDistMapStudentNameTooltip();
    });
  }

  /** Student list for a pie slice; "Other" merges names from states rolled past MAX_SLICES. */
  function getStudentNamesForStateDistSlice(sliceLabel, otherStateLabels) {
    if (sliceLabel === "Other" && otherStateLabels && otherStateLabels.length) {
      var seen = {};
      var all = [];
      for (var i = 0; i < otherStateLabels.length; i++) {
        var st = otherStateLabels[i];
        var arr =
          latestStateDist.studentNamesByState && latestStateDist.studentNamesByState[st]
            ? latestStateDist.studentNamesByState[st]
            : [];
        for (var j = 0; j < arr.length; j++) {
          var nm = arr[j];
          if (!seen[nm]) {
            seen[nm] = true;
            all.push(nm);
          }
        }
      }
      all.sort(function (a, b) {
        return a.localeCompare(b, undefined, { sensitivity: "base" });
      });
      return {
        title: "Other (" + otherStateLabels.length + " states)",
        names: all
      };
    }
    var names =
      latestStateDist.studentNamesByState && latestStateDist.studentNamesByState[sliceLabel]
        ? latestStateDist.studentNamesByState[sliceLabel].slice()
        : [];
    return { title: sliceLabel, names: names };
  }

  function getStudentNamesForGenderDistSlice(sliceLabel, otherGenderLabels) {
    if (sliceLabel === "Other" && otherGenderLabels && otherGenderLabels.length) {
      var seenG = {};
      var allG = [];
      for (var gi = 0; gi < otherGenderLabels.length; gi++) {
        var gk = otherGenderLabels[gi];
        var arrG =
          latestGenderDist.studentNamesByGender && latestGenderDist.studentNamesByGender[gk]
            ? latestGenderDist.studentNamesByGender[gk]
            : [];
        for (var gj = 0; gj < arrG.length; gj++) {
          var nmg = arrG[gj];
          if (!seenG[nmg]) {
            seenG[nmg] = true;
            allG.push(nmg);
          }
        }
      }
      allG.sort(function (a, b) {
        return a.localeCompare(b, undefined, { sensitivity: "base" });
      });
      return {
        title: "Other (" + otherGenderLabels.length + " categories)",
        names: allG
      };
    }
    var namesG =
      latestGenderDist.studentNamesByGender && latestGenderDist.studentNamesByGender[sliceLabel]
        ? latestGenderDist.studentNamesByGender[sliceLabel].slice()
        : [];
    return { title: sliceLabel, names: namesG };
  }

  function getStudentNamesForGradeDistSlice(sliceLabel, otherGradeLabels) {
    if (sliceLabel === "Other" && otherGradeLabels && otherGradeLabels.length) {
      var seenGr = {};
      var allGr = [];
      for (var ri = 0; ri < otherGradeLabels.length; ri++) {
        var rk = otherGradeLabels[ri];
        var arrR =
          latestGradeDist.studentNamesByGrade && latestGradeDist.studentNamesByGrade[rk]
            ? latestGradeDist.studentNamesByGrade[rk]
            : [];
        for (var rj = 0; rj < arrR.length; rj++) {
          var nmr = arrR[rj];
          if (!seenGr[nmr]) {
            seenGr[nmr] = true;
            allGr.push(nmr);
          }
        }
      }
      allGr.sort(function (a, b) {
        return a.localeCompare(b, undefined, { sensitivity: "base" });
      });
      return {
        title: "Other (" + otherGradeLabels.length + " grades)",
        names: allGr
      };
    }
    var namesR =
      latestGradeDist.studentNamesByGrade && latestGradeDist.studentNamesByGrade[sliceLabel]
        ? latestGradeDist.studentNamesByGrade[sliceLabel].slice()
        : [];
    return { title: sliceLabel, names: namesR };
  }

  function showStateDistStudentNamesTooltip(clientX, clientY, title, names) {
    bindStateDistMapOutsideDismiss();
    bindStateDistNamesEscapeDismiss();
    var tooltip = document.getElementById("state-dist-us-map-tooltip");
    if (!tooltip) return;
    if (!stateDistMapTooltipClickStopBound) {
      stateDistMapTooltipClickStopBound = true;
      tooltip.addEventListener("click", function (e) {
        if (e.target && e.target.closest && e.target.closest(".state-dist-us-map-tooltip-close")) return;
        e.stopPropagation();
      });
    }
    tooltip.classList.add("state-dist-us-map-tooltip--names");
    var closeBtnHtml =
      "<button type=\"button\" class=\"state-dist-us-map-tooltip-close\" aria-label=\"Close name list\">×</button>";
    if (!names || !names.length) {
      tooltip.innerHTML =
        "<div class=\"state-dist-us-map-tooltip-head-row\">" +
        "<p class=\"state-dist-us-map-tooltip-empty\">" +
        escapeHtml(title) +
        ": no students in this leaderboard view.</p>" +
        closeBtnHtml +
        "</div>";
    } else {
      var listHtml = names
        .map(function (n) {
          return "<li>" + escapeHtml(n) + "</li>";
        })
        .join("");
      tooltip.innerHTML =
        "<div class=\"state-dist-us-map-tooltip-head-row\">" +
        "<div class=\"state-dist-us-map-tooltip-head\">" +
        "<strong>" +
        escapeHtml(title) +
        "</strong> " +
        "<span class=\"state-dist-us-map-names-count\">(" +
        names.length +
        ")</span></div>" +
        closeBtnHtml +
        "</div>" +
        "<ul class=\"state-dist-us-map-tooltip-namelist\">" +
        listHtml +
        "</ul>";
    }
    var closeBtn = tooltip.querySelector(".state-dist-us-map-tooltip-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        clearStateDistMapStudentNameTooltip();
      });
    }
    tooltip.style.display = "block";
    tooltip.style.position = "fixed";
    tooltip.style.pointerEvents = "auto";
    var approxW = 340;
    var approxH = 280;
    tooltip.style.left =
      Math.max(8, Math.min(clientX + 12, window.innerWidth - approxW - 8)) + "px";
    tooltip.style.top =
      Math.max(8, Math.min(clientY + 12, window.innerHeight - approxH - 8)) + "px";
    tooltip.setAttribute("aria-hidden", "false");
  }

  function ensureStateDistUsMap() {
    if (typeof d3 === "undefined" || typeof topojson === "undefined" || !topojson.feature) return;
    var container = document.getElementById("state-dist-us-map-container");
    if (!container) return;
    if (container.querySelector("svg")) {
      syncStateDistUsMapColors();
      return;
    }
    if (container.getAttribute("data-map-loading") === "1") return;
    container.setAttribute("data-map-loading", "1");
    container.innerHTML = "<p class=\"state-dist-empty\">Loading map…</p>";
    var tooltip = document.getElementById("state-dist-us-map-tooltip");
    bindStateDistMapOutsideDismiss();
    fetch("https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json")
      .then(function (r) {
        if (!r.ok) throw new Error(String(r.status));
        return r.json();
      })
      .then(function (us) {
        container.removeAttribute("data-map-loading");
        var states = topojson.feature(us, us.objects.states);
        var rawW = container.offsetWidth || (container.parentElement && container.parentElement.offsetWidth) || 500;
        var width = Math.max(200, Math.min(520, rawW));
        var height = 320;
        var projection = d3.geoAlbersUsa().fitSize([width, height], states);
        var path = d3.geoPath().projection(projection);
        container.innerHTML = "";
        var svg = d3.select(container).append("svg")
          .attr("viewBox", "0 0 " + width + " " + height)
          .attr("preserveAspectRatio", "xMidYMid meet");
        var g = svg.append("g");
        g.selectAll("path")
          .data(states.features)
          .join("path")
          .attr("class", "state-dist-us-map-state")
          .attr("data-fips", function (d) { return d.id; })
          .attr("d", path)
          .on("mouseover", function (ev, d) {
            if (!tooltip) return;
            if (tooltip.classList.contains("state-dist-us-map-tooltip--names")) return;
            var fips = String(d.id).padStart(2, "0");
            var stateName = FIPS_TO_STATE[fips] || ("State " + fips);
            var count = 0;
            if (latestStateDist && latestStateDist.students) {
              count = latestStateDist.students[stateName] || 0;
            }
            tooltip.textContent = stateName + ": " + count + " students";
            tooltip.style.display = "block";
            tooltip.style.position = "fixed";
            tooltip.style.left = ev.pageX + 12 + "px";
            tooltip.style.top = ev.pageY + 12 + "px";
            tooltip.setAttribute("aria-hidden", "false");
          })
          .on("mouseout", function () {
            if (!tooltip) return;
            if (tooltip.classList.contains("state-dist-us-map-tooltip--names")) return;
            tooltip.style.display = "none";
            tooltip.setAttribute("aria-hidden", "true");
          })
          .on("mousemove", function (ev) {
            if (!tooltip) return;
            if (tooltip.classList.contains("state-dist-us-map-tooltip--names")) return;
            tooltip.style.left = ev.pageX + 12 + "px";
            tooltip.style.top = ev.pageY + 12 + "px";
          })
          .on("click", function (ev, d) {
            ev.stopPropagation();
            var fipsClick = String(d.id).padStart(2, "0");
            var stateNameClick = FIPS_TO_STATE[fipsClick] || ("State " + fipsClick);
            var names =
              latestStateDist.studentNamesByState && latestStateDist.studentNamesByState[stateNameClick]
                ? latestStateDist.studentNamesByState[stateNameClick].slice()
                : [];
            showStateDistStudentNamesTooltip(ev.clientX, ev.clientY, stateNameClick, names);
          });
        var labelsG = g.append("g").attr("class", "state-dist-us-map-labels");
        labelsG.selectAll("text")
          .data(states.features)
          .join("text")
          .attr("class", "state-dist-us-map-state-label")
          .attr("data-fips", function (d) { return d.id; })
          .each(function (d) {
            var c = path.centroid(d);
            var ok = Number.isFinite(c[0]) && Number.isFinite(c[1]);
            d3.select(this)
              .attr("x", ok ? c[0] : 0)
              .attr("y", ok ? c[1] : 0)
              .attr("opacity", ok ? 1 : 0)
              .text("");
          });
        syncStateDistUsMapColors();
        requestAnimationFrame(function () {
          syncStateDistUsMapColors();
        });
      })
      .catch(function () {
        container.removeAttribute("data-map-loading");
        container.innerHTML = "<p class=\"state-dist-empty\">Map could not be loaded.</p>";
      });
  }

  function renderStateDistCharts() {
    drawPieChartOnElements(
      document.getElementById("state-dist-students-canvas"),
      document.getElementById("state-dist-students-legend"),
      latestStateDist.students,
      undefined,
      getStudentNamesForStateDistSlice
    );
    drawPieChartOnElements(
      document.getElementById("state-dist-records-canvas"),
      document.getElementById("state-dist-records-legend"),
      latestStateDist.records,
      undefined,
      getStudentNamesForStateDistSlice
    );
    drawPieChartOnElements(
      document.getElementById("state-dist-mcp-canvas"),
      document.getElementById("state-dist-mcp-legend"),
      latestStateDist.mcp,
      function (v) { return Math.round(v).toLocaleString() + " MCP"; },
      getStudentNamesForStateDistSlice
    );
    syncStateDistUsMapColors();
  }

  function renderGenderDistCharts() {
    drawPieChartOnElements(
      document.getElementById("gender-dist-students-canvas"),
      document.getElementById("gender-dist-students-legend"),
      latestGenderDist.students,
      undefined,
      getStudentNamesForGenderDistSlice
    );
    drawPieChartOnElements(
      document.getElementById("gender-dist-records-canvas"),
      document.getElementById("gender-dist-records-legend"),
      latestGenderDist.records,
      undefined,
      getStudentNamesForGenderDistSlice
    );
    drawPieChartOnElements(
      document.getElementById("gender-dist-mcp-canvas"),
      document.getElementById("gender-dist-mcp-legend"),
      latestGenderDist.mcp,
      function (v) { return Math.round(v).toLocaleString() + " MCP"; },
      getStudentNamesForGenderDistSlice
    );
  }

  function renderGradeDistCharts() {
    drawPieChartOnElements(
      document.getElementById("grade-dist-students-canvas"),
      document.getElementById("grade-dist-students-legend"),
      latestGradeDist.students,
      undefined,
      getStudentNamesForGradeDistSlice
    );
    drawPieChartOnElements(
      document.getElementById("grade-dist-records-canvas"),
      document.getElementById("grade-dist-records-legend"),
      latestGradeDist.records,
      undefined,
      getStudentNamesForGradeDistSlice
    );
    drawPieChartOnElements(
      document.getElementById("grade-dist-mcp-canvas"),
      document.getElementById("grade-dist-mcp-legend"),
      latestGradeDist.mcp,
      function (v) { return Math.round(v).toLocaleString() + " MCP"; },
      getStudentNamesForGradeDistSlice
    );
  }

  function closeGenderDistPopoverUi() {
    var pop = document.getElementById("gender-dist-popover");
    var tr = document.getElementById("gender-dist-trigger");
    if (pop) pop.hidden = true;
    if (tr) tr.setAttribute("aria-expanded", "false");
    genderDistPopoverOpen = false;
    clearStateDistMapStudentNameTooltip();
  }

  function closeGradeDistPopoverUi() {
    var pop = document.getElementById("grade-dist-popover");
    var tr = document.getElementById("grade-dist-trigger");
    if (pop) pop.hidden = true;
    if (tr) tr.setAttribute("aria-expanded", "false");
    gradeDistPopoverOpen = false;
    clearStateDistMapStudentNameTooltip();
  }

  function closeStateDistPopoverUi() {
    var pop = document.getElementById("state-dist-popover");
    var tr = document.getElementById("state-dist-trigger");
    if (pop) pop.hidden = true;
    if (tr) tr.setAttribute("aria-expanded", "false");
    stateDistPopoverOpen = false;
    clearStateDistMapStudentNameTooltip();
  }

  function bindStateDistPopover() {
    var trigger = document.getElementById("state-dist-trigger");
    var popover = document.getElementById("state-dist-popover");
    var closeBtn = popover && popover.querySelector(".state-dist-popover-close");
    var backdrop = popover && popover.querySelector(".state-dist-popover-backdrop");
    if (!trigger || !popover) return;

    function openPopover() {
      closeGenderDistPopoverUi();
      closeGradeDistPopoverUi();
      popover.hidden = false;
      trigger.setAttribute("aria-expanded", "true");
      stateDistPopoverOpen = true;
      renderStateDistCharts();
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          ensureStateDistUsMap();
        });
      });
    }

    function closePopover() {
      closeStateDistPopoverUi();
    }

    trigger.addEventListener("click", function () {
      if (popover.hidden) openPopover(); else closePopover();
    });
    if (closeBtn) closeBtn.addEventListener("click", closePopover);
    if (backdrop) backdrop.addEventListener("click", closePopover);

    var stateDistAllPngBtn = document.getElementById("state-dist-download-all-png");
    if (stateDistAllPngBtn) {
      stateDistAllPngBtn.addEventListener("click", function () {
        downloadStateDistributionCombinedPng();
      });
    }
  }

  function bindGenderDistPopover() {
    var trigger = document.getElementById("gender-dist-trigger");
    var popover = document.getElementById("gender-dist-popover");
    var closeBtn = popover && popover.querySelector(".state-dist-popover-close");
    var backdrop = popover && popover.querySelector(".state-dist-popover-backdrop");
    if (!trigger || !popover) return;

    function openPopover() {
      closeStateDistPopoverUi();
      closeGradeDistPopoverUi();
      popover.hidden = false;
      trigger.setAttribute("aria-expanded", "true");
      genderDistPopoverOpen = true;
      renderGenderDistCharts();
    }

    function closePopover() {
      closeGenderDistPopoverUi();
    }

    trigger.addEventListener("click", function () {
      if (popover.hidden) openPopover(); else closePopover();
    });
    if (closeBtn) closeBtn.addEventListener("click", closePopover);
    if (backdrop) backdrop.addEventListener("click", closePopover);

    var pngBtn = document.getElementById("gender-dist-download-all-png");
    if (pngBtn) {
      pngBtn.addEventListener("click", function () {
        downloadGenderDistributionCombinedPng();
      });
    }
  }

  function bindGradeDistPopover() {
    var trigger = document.getElementById("grade-dist-trigger");
    var popover = document.getElementById("grade-dist-popover");
    var closeBtn = popover && popover.querySelector(".state-dist-popover-close");
    var backdrop = popover && popover.querySelector(".state-dist-popover-backdrop");
    if (!trigger || !popover) return;

    function openPopover() {
      closeStateDistPopoverUi();
      closeGenderDistPopoverUi();
      popover.hidden = false;
      trigger.setAttribute("aria-expanded", "true");
      gradeDistPopoverOpen = true;
      renderGradeDistCharts();
    }

    function closePopover() {
      closeGradeDistPopoverUi();
    }

    trigger.addEventListener("click", function () {
      if (popover.hidden) openPopover(); else closePopover();
    });
    if (closeBtn) closeBtn.addEventListener("click", closePopover);
    if (backdrop) backdrop.addEventListener("click", closePopover);

    var pngBtn = document.getElementById("grade-dist-download-all-png");
    if (pngBtn) {
      pngBtn.addEventListener("click", function () {
        downloadGradeDistributionCombinedPng();
      });
    }
  }

  /**
   * Fill season-year dropdown with years that have at least one record matching the current
   * competition filter (ignores the year dropdown itself). Omits years with no matching competitions.
   */
  function populateCompetitionYearFilterOptions() {
    if (!competitionYearFilterEl || !data || !data.students) return;
    var seen = {};
    var years = [];
    var students = data.students;
    for (var i = 0; i < students.length; i++) {
      var recs = students[i].records || [];
      for (var j = 0; j < recs.length; j++) {
        var rec = recs[j];
        if (!contestFilter.recordMatchesContestFilter(rec)) continue;
        var y = rec.year;
        if (y == null || y === "") continue;
        var ys = String(y).trim();
        if (!ys) continue;
        if (!seen[ys]) {
          seen[ys] = true;
          years.push(ys);
        }
      }
    }
    years.sort(function (a, b) {
      var na = parseInt(a, 10);
      var nb = parseInt(b, 10);
      if (!isNaN(na) && !isNaN(nb) && na !== nb) return nb - na;
      return String(b).localeCompare(String(a), undefined, { numeric: true });
    });
    var want =
      savedFilters && savedFilters.competitionYear != null && savedFilters.competitionYear !== ""
        ? String(savedFilters.competitionYear)
        : competitionYearFilterEl.value || "";
    while (competitionYearFilterEl.options.length > 1) {
      competitionYearFilterEl.remove(1);
    }
    for (var k = 0; k < years.length; k++) {
      var opt = document.createElement("option");
      opt.value = years[k];
      opt.textContent = years[k];
      competitionYearFilterEl.appendChild(opt);
    }
    if (want && seen[want]) {
      competitionYearFilterEl.value = want;
    } else {
      competitionYearFilterEl.value = "";
    }
  }

  function init() {
    bindThemeToggle();
    bindSiteNavDrawer();
    contestFilter = MathCompContestFilter.create(document.getElementById("contest-filter"), {
      summaryEl: document.getElementById("contest-filter-summary"),
      mcpTimelineSummaryEl: document.getElementById("mcp-timeline-contest-summary"),
      getMcpTimelineApplyFiltersChecked: function () {
        return !!(mcpTimelineApplyFiltersEl && mcpTimelineApplyFiltersEl.checked);
      },
      onChange: function () {
        if (contestFilterPopoverOpen) {
          contestFilterHasPendingApply = true;
          return;
        }
        applyContestFilterChangesNow();
      }
    });
    if (competitionYearFilterEl) {
      competitionYearFilterEl.addEventListener("change", function () {
        mcpPctStatsCache.key = null;
        saveFilters();
        renderTopStudentsByRecords();
        runSearch();
        refreshMcpTimelineIfOpen();
        contestFilter.updateSummary(true);
      });
    }
    restoreFilters();
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
      }).catch(function () { return {}; }),
      fetch(base + "/promotions.json").then(function (res) {
        if (!res.ok) return [];
        return res.json();
      }).catch(function () { return []; })
    ]).then(function (arr) {
      var json = arr[0];
      var branchCfg = arr[1];
      var promotionsCfg = arr[2];
      if (Array.isArray(promotionsCfg)) featurePromotions = promotionsCfg;
      else if (promotionsCfg && Array.isArray(promotionsCfg.promotions)) featurePromotions = promotionsCfg.promotions;
      else featurePromotions = [];
      activePromotionIndex = 0;
      renderPromotionBanner();
      usStateLookup = json.us_state_lookup || {};
      if (typeof window !== "undefined") window.usStateLookup = usStateLookup;
      var si = json.slug_index || [];
      var km = json.key_map || {};
      var students = json.students || [];
      for (var s = 0; s < students.length; s++) {
        var stu = students[s];
        var stuKeys = Object.keys(stu);
        for (var sji = 0; sji < stuKeys.length; sji++) {
          var sjk = stuKeys[sji];
          var stuLong = km[sjk];
          if (stuLong) {
            stu[stuLong] = stu[sjk];
            delete stu[sjk];
          }
        }
        var recs = stu.records || [];
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
      if (typeof contestFilter.setContests === "function") {
        contestFilter.setContests(data.contests || {});
      }
      populateCompetitionYearFilterOptions();
      setLoading(false);
      requestAnimationFrame(function () {
        renderContestList();
        contestFilter.updateSummary();
        renderTopStudentsByRecords();
        bindContestListPopover();
        bindStateDistPopover();
        bindGenderDistPopover();
        bindGradeDistPopover();
        bindMcpTimelinePopover();
        bindMcpPctPopover();
        bindCsvPopover();
        bindStudentReportModal();
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
      if (contestFilterPopoverEl && contestFilterPopoverEl.hidden) contestFilterTriggerEl.click();
    });
  }

  if (contestFilterTriggerEl && contestFilterWrapEl) {
    (function () {
      var popover = contestFilterPopoverEl;
      if (!popover) return;
      var closeBtn = popover.querySelector(".contest-filter-popover-close");
      var backdrop = popover.querySelector(".contest-filter-popover-backdrop");
      var inner = popover.querySelector(".contest-filter-popover-inner");
      var bodyLocked = false;
      var lockedScrollY = 0;

      function lockBodyScroll() {
        if (bodyLocked) return;
        lockedScrollY = window.pageYOffset || document.documentElement.scrollTop || 0;
        document.body.classList.add("contest-filter-popover-open");
        document.body.style.top = "-" + String(lockedScrollY) + "px";
        bodyLocked = true;
      }

      function unlockBodyScroll() {
        if (!bodyLocked) return;
        document.body.classList.remove("contest-filter-popover-open");
        document.body.style.top = "";
        window.scrollTo(0, lockedScrollY);
        bodyLocked = false;
      }

      function openPopover() {
        popover.hidden = false;
        contestFilterTriggerEl.setAttribute("aria-expanded", "true");
        contestFilterPopoverOpen = true;
        contestFilterHasPendingApply = false;
        lockBodyScroll();
      }

      function closePopover() {
        var shouldApply = contestFilterHasPendingApply;
        popover.hidden = true;
        contestFilterTriggerEl.setAttribute("aria-expanded", "false");
        contestFilterPopoverOpen = false;
        contestFilterHasPendingApply = false;
        unlockBodyScroll();
        if (shouldApply) {
          applyContestFilterChangesNow();
        }
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
      if (inner) {
        inner.addEventListener("click", function (e) {
          e.stopPropagation();
        });
      }

      // Make taps on rows feel instant on touch devices by toggling the checkbox on touchend,
      // and firing a normal change event. This avoids waiting for delayed click synthesis.
      popover.addEventListener(
        "touchend",
        function (e) {
          var label =
            e.target &&
            e.target.closest &&
            e.target.closest(".contest-filter-option, .contest-filter-group-all-label");
          if (!label) return;
          var checkbox = label.querySelector('input[type="checkbox"]');
          if (!checkbox) return;
          e.preventDefault();
          e.stopPropagation();
          checkbox.checked = !checkbox.checked;
          var changeEvent = new Event("change", { bubbles: true });
          checkbox.dispatchEvent(changeEvent);
        },
        { passive: false }
      );
    })();
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
    var reportTriggerBtn = target && target.closest ? target.closest(".student-record-report-trigger") : null;
    if (reportTriggerBtn) {
      event.preventDefault();
      event.stopPropagation();
      openStudentReportMenuForButton(reportTriggerBtn);
      return;
    }
    var reportOptionBtn = target && target.closest ? target.closest(".student-record-report-option") : null;
    if (reportOptionBtn) {
      event.preventDefault();
      event.stopPropagation();
      var issueType = String(reportOptionBtn.getAttribute("data-issue-type") || "");
      var cardForReport = reportOptionBtn.closest(".student-card");
      closeStudentReportMenu();
      if (!issueType || !cardForReport) return;
      openStudentReportModal(issueType, cardForReport, reportOptionBtn);
      return;
    }
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
    var breakdownOpenBtn = target && target.closest ? target.closest(".mcp-breakdown-btn") : null;
    if (breakdownOpenBtn) {
      var wrap = breakdownOpenBtn.closest(".mcp-breakdown-wrap");
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
    var breakdownPngBtn = target && target.closest ? target.closest(".mcp-breakdown-download-png") : null;
    if (breakdownPngBtn) {
      var popInner = breakdownPngBtn.closest(".mcp-breakdown-popover-inner");
      var bdCanvas = popInner && popInner.querySelector(".mcp-breakdown-canvas");
      var titleEl = popInner && popInner.querySelector(".mcp-breakdown-title");
      var titleText = titleEl ? titleEl.textContent.trim() : "mcp-breakdown";
      var fname = sanitizeDownloadFilename(titleText.split(/\s[—-]\s/)[0] || titleText, "mcp-breakdown") + "-breakdown";
      var bdLeg = popInner && popInner.querySelector(".mcp-breakdown-legend");
      if (!downloadCanvasAsPng(bdCanvas, fname + ".png", bdLeg)) {
        alert("Could not export chart.");
      }
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
  document.addEventListener("click", function (event) {
    if (!studentReportMenuOpenEl) return;
    var target = event.target;
    if (target && target.closest && target.closest(".student-record-report-wrap")) return;
    closeStudentReportMenu();
  }, true);

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
