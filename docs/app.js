(function () {
  "use strict";

  var data = { students: [], contests: {} };
  var searchEl = document.getElementById("search");
  var resultsEl = document.getElementById("results");
  var emptyEl = document.getElementById("empty");
  var loadingEl = document.getElementById("loading");
  var hintEl = document.getElementById("search-hint");
  var contestListEl = document.getElementById("contest-list");
  var awardsRankingListEl = document.getElementById("awards-ranking-list");
  var topStudentsSectionEl = document.getElementById("top-students-section");
  var searchClearEl = document.getElementById("search-clear");
  var girlsOnlyEl = document.getElementById("girls-only");
  var gradeFilterEl = document.getElementById("grade-filter");
  var gradeFilterWrapEl = document.getElementById("grade-filter-wrap");
  var stateFilterEl = document.getElementById("state-filter");
  var contestFilterWrapEl = document.getElementById("contest-filter-wrap");
  var contestFilterEl = document.getElementById("contest-filter");
  var contestFilterTriggerEl = document.getElementById("contest-filter-trigger");
  var contestFilterSummaryEl = document.getElementById("contest-filter-summary");
  var sortToggleEl = document.getElementById("sort-toggle");

  var sortMode = "mcp"; // "records" or "mcp"
  var gradeFilterInitialized = false;

  var amoAlertList = [];
  var stateDistPopoverOpen = false;
  var latestStateDist = { students: {}, records: {} };

  function isAmoAlertFeatureEnabled() {
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
    mpfg: function (slug) { return slug === "mpfg"; },
    "mpfg-olympiad": function (slug) { return slug.indexOf("mpfg-olympiad") !== -1; },
    "bamo-8": function (slug) { return slug.indexOf("bamo-8") !== -1; },
    "bamo-12": function (slug) { return slug.indexOf("bamo-12") !== -1; },
    bmt: function (slug) { return slug.indexOf("bmt") === 0; }
  };

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

  function updateContestFilterSummary() {
    if (!contestFilterEl || !contestFilterSummaryEl) return;
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

    var text = "";
    if (allBox && allBox.checked && selectedNonAll.length === totalOptions) {
      text = "All selected";
    } else if (selectedNonAll.length === 0) {
      text = "All selected";
    } else if (selectedNonAll.length === 1) {
      text = selectedNonAll[0] + " selected";
    } else {
      text = String(selectedNonAll.length) + " contests selected";
    }

    contestFilterSummaryEl.textContent = text;
  }

  function recordMatchesContestFilter(record) {
    if (!record) return false;
    if (!contestFilterEl || !contestFilterWrapEl || contestFilterWrapEl.hidden) return true;
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

  function applyDemographicFilters(students) {
    var out = students || [];
    if (girlsOnlyEl && girlsOnlyEl.checked) {
      out = out.filter(function (s) {
        return (s.gender || "").toLowerCase() === "female";
      });
    }
    if (gradeFilterEl && gradeFilterWrapEl && !gradeFilterWrapEl.hidden && gradeFilterEl.value && gradeFilterEl.value !== "") {
      var wantLabel = gradeFilterEl.value;
      out = out.filter(function (s) {
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
      out = out.filter(function (s) {
        var st = (s.state || "").trim();
        if (wantState === "__other__") return !st || !US_STATES_SET[st];
        return st === wantState;
      });
    }
    return out;
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

  /** Returns grade label string (e.g. "G10", "U1") or "" if no grade. */
  function getGradeLabel(gradeIn2026) {
    var currentGrade = getCurrentGrade(gradeIn2026);
    if (currentGrade == null) return "";
    return currentGrade <= 12 ? "G" + currentGrade : "U" + (currentGrade - 12);
  }

  /** Sort key for grade labels: G6..G12 then U1, U2, ... */
  function gradeLabelSortKey(label) {
    if (!label || label === "") return -1;
    if (label.charAt(0) === "G") return parseInt(label.slice(1), 10);
    if (label.charAt(0) === "U") return 12 + parseInt(label.slice(1), 10);
    return -1;
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
    var cells = [
      "<td class=\"num\" data-col=\"year\">", escapeHtml(record.year || ""), "</td>"
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

  function renderStudent(student, contestsMap) {
    var records = (student.records || []).slice();
    records = records.filter(recordMatchesContestFilter);
    var grouped = groupRecordsByContest(records);
    var bySlug = grouped.bySlug;
    var slugs = grouped.slugs;
    var state = student.state || "";

    var sections = [];
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
    var mcpTotal = student.mcp != null ? Number(student.mcp) : 0;
    var statsHtml = "<span class=\"student-stats\">" +
      "<span class=\"student-stat\">" + totalRecords + (totalRecords === 1 ? " record" : " records") + "</span>" +
      (mcpTotal > 0 ? "<span class=\"student-stat\">" + mcpTotal + " MCP</span>" : "") +
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
              "<h3 class=\"mcp-breakdown-title\">" + escapeHtml(student.name || "Student") + " — MCP Breakdown — " + escapeHtml(String(mcpTotal)) + " pts</h3>" +
              "<canvas class=\"mcp-breakdown-canvas\" width=\"260\" height=\"260\"></canvas>" +
              "<div class=\"mcp-breakdown-legend\"></div>" +
              "<button type=\"button\" class=\"mcp-breakdown-close\" aria-label=\"Close\">×</button>" +
            "</div>" +
            "<div class=\"mcp-breakdown-backdrop\" aria-hidden=\"true\"></div>" +
          "</div>" +
          "<script type=\"application/json\" class=\"mcp-breakdown-data\">" + JSON.stringify(contribByContest) + "</script>" +
        "</span>";
    }

    return (
      "<article class=\"student-card\" data-student-id=\"" + escapeHtml(String(student.id)) + "\">" +
        "<div class=\"student-header\">" +
          "<h2 class=\"student-name\" data-student-name=\"" + escapeHtml(String(student.name || "")) + "\">" + escapeHtml(student.name) + (stateHtml ? " " + stateHtml : "") + gradeHtml + "</h2>" +
          statsHtml +
          aliasesHtml +
          mcpBtnHtml +
          "<button type=\"button\" class=\"export-pdf-student-btn\" aria-label=\"Export this student to PDF\">Export to PDF</button>" +
        "</div>" +
        "<div class=\"student-contests\">" + sections.join("") + "</div>" +
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
    for (var k in contests) if (Object.prototype.hasOwnProperty.call(contests, k)) slugs.push(k);
    slugs.sort(compareContestSlugs);
    var parts = [];
    var githubBase = "https://github.com/x-du/math-competition/blob/main/database/contests/";
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
          var yearHref = githubBase + slug + "/year%3D" + yr + "/" + encodeURIComponent(filename);
          var label = filenames.length > 1 ? yr + " (" + filename.replace(/^results_?/, "").replace(/\.csv$/i, "") + ")" : yr;
          yearLinks.push("<a href=\"" + yearHref + "\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"contest-list-year-link\">" + escapeHtml(label) + "</a>");
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
    gradeLabels.sort(function (a, b) {
      return gradeLabelSortKey(a) - gradeLabelSortKey(b);
    });

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
      var valToRestore = currentValue || "";
      var optExists = gradeFilterEl.querySelector("option[value=\"" + valToRestore + "\"]");
      if (!gradeFilterInitialized) {
        gradeFilterEl.value = "__hs__";
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
        if (wantState === "__other__") {
          return !st || !US_STATES_SET[st];
        }
        return st === wantState;
      });
    }

    var isGirlsOnly = girlsOnlyEl && girlsOnlyEl.checked;
    var counts = [];
    if (students && students.length) {
      for (var i = 0; i < students.length; i++) {
        var student = students[i];
        var records = (student.records || []).filter(recordMatchesContestFilter);
        var count = records.length;
        if (count > 0) {
          var mcpTotal;
          if (isGirlsOnly && student.mcp_w != null) {
            mcpTotal = Number(student.mcp_w);
          } else {
            mcpTotal = student.mcp != null ? Number(student.mcp) : 0;
          }
          counts.push({ student: student, recordsCount: count, mcpTotal: mcpTotal });
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
    var mcpLabel = (isGirlsOnly && sortMode === "mcp") ? "MCP-W" : "MCP";
    if (rankingTitleTextEl) {
      rankingTitleTextEl.textContent = sortMode === "mcp"
        ? "Top students by " + mcpLabel + " points"
        : "Top students by # of records";
    }
    if (subtitleEl) {
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
      var emptyMsg = (girlsOnlyEl && girlsOnlyEl.checked)
        ? "No female students with records in this view."
        : "No record data available yet.";
      awardsRankingListEl.innerHTML = "<li class=\"awards-ranking-empty\">" + escapeHtml(emptyMsg) + "</li>";
      return;
    }

    var isMcp = sortMode === "mcp";
    if (isMcp) {
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
      if (isMcp) {
        valueText = String(entry.mcpTotal) + " " + mcpLabel;
      } else {
        var label = entry.recordsCount === 1 ? "record" : "records";
        valueText = String(entry.recordsCount) + " " + label;
      }
      items.push(
        "<li class=\"awards-ranking-item\">" +
          "<span class=\"awards-ranking-position\">#" + (i + 1) + "</span>" +
          "<span class=\"awards-ranking-name\" data-student-name=\"" + escapeHtml(String(s.name || "")) + "\">" + escapeHtml(displayName) + gradeHtml + "</span>" +
          "<span class=\"awards-ranking-count\" data-student-name=\"" + escapeHtml(String(s.name || "")) + "\">" + escapeHtml(valueText) + "</span>" +
        "</li>"
      );
    }

    awardsRankingListEl.innerHTML = items.join("");
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
      if (popover.hidden) open(); else close();
    });
    if (closeBtn) closeBtn.addEventListener("click", close);
    if (backdrop) backdrop.addEventListener("click", close);
  }

  function clearAllFilters() {
    if (girlsOnlyEl) girlsOnlyEl.checked = false;
    if (gradeFilterEl) gradeFilterEl.value = "__hs__";
    if (stateFilterEl) stateFilterEl.value = "";
    sortMode = "mcp";
    if (sortToggleEl) {
      var opts = sortToggleEl.querySelectorAll(".sort-toggle-option");
      for (var i = 0; i < opts.length; i++) {
        if (opts[i].getAttribute("data-mode") === "mcp") {
          opts[i].classList.add("sort-toggle-option--active");
        } else {
          opts[i].classList.remove("sort-toggle-option--active");
        }
      }
    }
    if (contestFilterEl) {
      var allBox = contestFilterEl.querySelector("input[type='checkbox'][value='all']");
      var boxes = contestFilterEl.querySelectorAll("input[type='checkbox']");
      if (allBox) allBox.checked = true;
      for (var i = 0; i < boxes.length; i++) {
        if (boxes[i] !== allBox) boxes[i].checked = true;
      }
      updateContestFilterSummary();
    }
    renderTopStudentsByRecords();
  }

  function bindAmoAlertPopover() {
    var trigger = document.getElementById("amo-alert-trigger");
    var popover = document.getElementById("amo-alert-popover");
    var summaryEl = document.getElementById("amo-alert-summary");
    var listEl = document.getElementById("amo-alert-list");
    var closeBtn = popover && popover.querySelector(".amo-alert-popover-close");
    var backdrop = popover && popover.querySelector(".amo-alert-popover-backdrop");
    if (!trigger || !popover || !listEl) return;

    function closePopover() {
      popover.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
    }

    function openPopover() {
      var n = amoAlertList.length;
      if (summaryEl) {
        summaryEl.textContent = n === 1
          ? "1 student with AMO 2025 Gold, Silver, Bronze, or Honorable Mention has no prior track in JMO, AMO (prior years), HMMT Feb, HMMT Nov, CMIMC, BAMO-12, PUMaC Div A, ARML, or BMT. Tap a name to search."
          : n + " students with AMO 2025 Gold, Silver, Bronze, or Honorable Mention have no prior track in JMO, AMO (prior years), HMMT Feb, HMMT Nov, CMIMC, BAMO-12, PUMaC Div A, ARML, or BMT. Tap a name to search.";
      }
      var items = [];
      for (var i = 0; i < amoAlertList.length; i++) {
        var s = amoAlertList[i];
        var label = escapeHtml(s.name || "");
        if (s.state) label += " <span class=\"amo-alert-state\">(" + escapeHtml(s.state) + ")</span>";
        if (s.award) label += " <span class=\"amo-alert-award\">(" + escapeHtml(s.award) + ")</span>";
        items.push("<li class=\"amo-alert-list-item\"><button type=\"button\" class=\"amo-alert-student\" data-student-name=\"" + escapeHtml(String(s.name || "")) + "\">" + label + "</button></li>");
      }
      listEl.innerHTML = items.join("");
      popover.hidden = false;
      trigger.setAttribute("aria-expanded", "true");
    }

    trigger.addEventListener("click", function () {
      if (popover.hidden) openPopover(); else closePopover();
    });
    if (closeBtn) closeBtn.addEventListener("click", closePopover);
    if (backdrop) backdrop.addEventListener("click", closePopover);

    listEl.addEventListener("click", function (ev) {
      var btn = ev.target && ev.target.closest && ev.target.closest(".amo-alert-student");
      if (!btn) return;
      var name = (btn.getAttribute("data-student-name") || "").trim();
      if (!name || !searchEl) return;
      closePopover();
      clearAllFilters();
      searchEl.value = name;
      runSearch();
      searchEl.focus();
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

  function runSearch() {
    var query = (searchEl && searchEl.value) ? searchEl.value.trim() : "";
    emptyEl.hidden = true;
    resultsEl.innerHTML = "";

    if (searchClearEl) {
      searchClearEl.hidden = !query;
    }

    if (!query) {
      hintEl.textContent = "Enter at least one character to search.";
      if (topStudentsSectionEl) topStudentsSectionEl.hidden = false;
      return;
    }

    var matched = data.students.filter(function (s) { return matchStudent(s, query); });
    // Search results are not filtered by grade, state, or girls - show all matches

    var filteredByContest = matched.map(function (s) {
      var copy = {};
      for (var k in s) {
        if (Object.prototype.hasOwnProperty.call(s, k) && k !== "records") {
          copy[k] = s[k];
        }
      }
      var recs = s.records || [];
      copy.records = recs.filter(recordMatchesContestFilter);
      return copy;
    }).filter(function (s) {
      return (s.records || []).length > 0;
    });

    hintEl.textContent = filteredByContest.length === 0
      ? "No students found."
      : filteredByContest.length === 1
        ? "1 student found."
        : filteredByContest.length + " students found.";

    if (filteredByContest.length === 0) {
      emptyEl.hidden = false;
      if (topStudentsSectionEl) topStudentsSectionEl.hidden = false;
      return;
    }

    if (topStudentsSectionEl) topStudentsSectionEl.hidden = true;

    resultsEl.innerHTML = filteredByContest.map(function (s) { return renderStudent(s, data.contests || {}); }).join("");
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
    var JsPDFConstructor = (typeof jspdf !== "undefined" && jspdf.jsPDF) ? jspdf.jsPDF : (typeof jsPDF !== "undefined" ? jsPDF : null);
    if (!JsPDFConstructor) {
      alert("PDF export is not available. Please refresh the page and try again.");
      return;
    }
    var btn = cardEl.querySelector(".export-pdf-student-btn");
    if (btn) btn.disabled = true;
    var studentName = (student.name || "").trim();
    var state = (student.state || "").trim();
    var filename = "math-competition-" + (studentName ? studentName.replace(/\W+/g, "-") : "student") + ".pdf";

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
    for (var i = 0; i < counts.length; i++) {
      var state = (counts[i].student.state || "").trim() || "Unknown";
      studentsByState[state] = (studentsByState[state] || 0) + 1;
      recordsByState[state] = (recordsByState[state] || 0) + counts[i].recordsCount;
    }
    latestStateDist.students = studentsByState;
    latestStateDist.records = recordsByState;
  }

  function drawPieChartOnElements(canvas, legendEl, distMap) {
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
        ctx.font = "bold 11px 'DM Sans', sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(Math.round((slice.value / total) * 100) + "%", lx, ly);
      }
      startAngle += sliceAngle;
    }

    var legendHtml = [];
    for (var i = 0; i < main.length; i++) {
      var pct = ((main[i].value / total) * 100).toFixed(1);
      legendHtml.push(
        "<div class=\"state-dist-legend-item\">" +
          "<span class=\"state-dist-legend-swatch\" style=\"background:" + PIE_COLORS[i % PIE_COLORS.length] + "\"></span>" +
          "<span class=\"state-dist-legend-label\">" + escapeHtml(main[i].label) + "</span>" +
          "<span class=\"state-dist-legend-value\">" + main[i].value + " (" + pct + "%)</span>" +
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
    setLoading(true);
    var base = document.querySelector("script[src$='app.js']").src.replace(/\/[^/]*$/, "");
    fetch(base + "/data.json")
      .then(function (res) {
        if (!res.ok) throw new Error("Failed to load data: " + res.status);
        return res.json();
      })
      .then(function (json) {
        var si = json.slug_index || [];
        var km = json.key_map || {};
        var students = json.students || [];
        for (var s = 0; s < students.length; s++) {
          var recs = students[s].records || [];
          for (var r = 0; r < recs.length; r++) {
            var rec = recs[r];
            if (si.length && rec.c != null) { rec.contest_slug = si[rec.c]; delete rec.c; }
            for (var sk in km) {
              if (Object.prototype.hasOwnProperty.call(rec, sk)) {
                rec[km[sk]] = rec[sk]; delete rec[sk];
              }
            }
          }
        }
        data = json;
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
        if (typeof window.AmoAlertCheck !== "undefined" && window.AmoAlertCheck.getAmo2025GoldSilverNoTrack) {
          amoAlertList = window.AmoAlertCheck.getAmo2025GoldSilverNoTrack(data.students || []);
        }
        var amoTrigger = document.getElementById("amo-alert-trigger");
        if (amoTrigger) amoTrigger.hidden = !(isAmoAlertFeatureEnabled() && amoAlertList.length > 0);
        var reportBtn = document.getElementById("report-link-btn");
        if (reportBtn) reportBtn.hidden = !isAmoAlertFeatureEnabled();
        requestAnimationFrame(function () {
          renderContestList();
          updateContestFilterSummary();
          renderTopStudentsByRecords();
          bindContestListPopover();
          bindAmoAlertPopover();
          bindStateDistPopover();
          runSearch();
        });
      })
      .catch(function (err) {
        setLoading(false);
        resultsEl.innerHTML = "<p class=\"empty-state\">Could not load data. " + escapeHtml(String(err.message)) + "</p>";
      });
  }

  if (searchEl) {
    var debouncedSearch = debounce(runSearch, 120);
    searchEl.addEventListener("input", debouncedSearch);
    searchEl.addEventListener("search", runSearch);
  }

  if (searchClearEl) {
    searchClearEl.addEventListener("click", function () {
      if (!searchEl) return;
      searchEl.value = "";
      runSearch();
      searchEl.focus();
    });
  }

  if (girlsOnlyEl) {
    girlsOnlyEl.addEventListener("change", function () {
      renderTopStudentsByRecords();
      runSearch();
    });
  }

  if (gradeFilterEl) {
    gradeFilterEl.addEventListener("change", function () {
      renderTopStudentsByRecords();
      runSearch();
    });
  }

  if (stateFilterEl) {
    stateFilterEl.addEventListener("change", function () {
      renderTopStudentsByRecords();
      runSearch();
    });
  }

  if (sortToggleEl) {
    sortToggleEl.addEventListener("click", function () {
      sortMode = sortMode === "records" ? "mcp" : "records";
      var opts = sortToggleEl.querySelectorAll(".sort-toggle-option");
      for (var i = 0; i < opts.length; i++) {
        if (opts[i].getAttribute("data-mode") === sortMode) {
          opts[i].classList.add("sort-toggle-option--active");
        } else {
          opts[i].classList.remove("sort-toggle-option--active");
        }
      }
      renderTopStudentsByRecords();
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
        renderTopStudentsByRecords();
        runSearch();
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
      renderTopStudentsByRecords();
      runSearch();
    });
  }

  if (resultsEl) {
    resultsEl.addEventListener("click", function (event) {
      var target = event.target;
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
      if (!target || !target.classList || !target.classList.contains("student-name")) return;
      var nameAttr = target.getAttribute("data-student-name");
      var name = (nameAttr || target.textContent || "").trim();
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
    });
  }

  if (awardsRankingListEl) {
    awardsRankingListEl.addEventListener("click", function (event) {
      var target = event.target;
      while (target && target !== awardsRankingListEl && !target.getAttribute("data-student-name")) {
        target = target.parentNode;
      }
      if (!target || target === awardsRankingListEl) return;
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
