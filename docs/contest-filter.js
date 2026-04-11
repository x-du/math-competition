/**
 * Two-level competition filter: groups (e.g. HMMT Feb) and leaf categories (individual + subject tests).
 * Exposes MathCompContestFilter.create(containerEl, options).
 */
(function (global) {
  "use strict";

  /** Old single-checkbox keys -> full set of leaf keys after split. */
  var LEGACY_EXPAND = {
    "hmmt-feb": [
      "hmmt-feb__individual",
      "hmmt-feb__algebra-number-theory",
      "hmmt-feb__combo",
      "hmmt-feb__geometry"
    ],
    "hmmt-nov": ["hmmt-nov__individual", "hmmt-nov__general", "hmmt-nov__theme"],
    "pumac-a": [
      "pumac-a__individual",
      "pumac-a__algebra",
      "pumac-a__combinator",
      "pumac-a__geometry",
      "pumac-a__number-theory"
    ],
    "pumac-b": [
      "pumac-b__individual",
      "pumac-b__algebra",
      "pumac-b__combinator",
      "pumac-b__geometry",
      "pumac-b__number-theory"
    ],
    cmimc: ["cmimc__individual", "cmimc__algebra", "cmimc__comb", "cmimc__geometry"],
    bmt: ["bmt__individual", "bmt__algebra", "bmt__calculus", "bmt__discrete", "bmt__geometry"]
  };

  function slugOf(record) {
    var slug = record && (record.contest_slug || record.contest);
    return slug ? String(slug).toLowerCase() : "";
  }

  function makeMatchers() {
    var m = {};

    function add(key, fn) {
      m[key] = fn;
    }

    add("usamo", function (s) { return s === "amo"; });
    add("usajmo", function (s) { return s === "jmo"; });
    add("imo", function (s) { return s.indexOf("imo") !== -1; });
    add("rmm", function (s) { return s.indexOf("rmm") !== -1; });
    add("egmo", function (s) { return s.indexOf("egmo") !== -1; });

    add("hmmt-feb__individual", function (s) { return s === "hmmt-feb"; });
    add("hmmt-feb__algebra-number-theory", function (s) { return s === "hmmt-feb-algebra-number-theory"; });
    add("hmmt-feb__combo", function (s) { return s === "hmmt-feb-combo"; });
    add("hmmt-feb__geometry", function (s) { return s === "hmmt-feb-geometry"; });

    add("hmmt-nov__individual", function (s) { return s === "hmmt-nov"; });
    add("hmmt-nov__general", function (s) { return s === "hmmt-nov-general"; });
    add("hmmt-nov__theme", function (s) { return s === "hmmt-nov-theme"; });

    add("pumac-a__individual", function (s) { return s === "pumac"; });
    add("pumac-a__algebra", function (s) { return s === "pumac-algebra"; });
    add("pumac-a__combinator", function (s) { return s === "pumac-combinator"; });
    add("pumac-a__geometry", function (s) { return s === "pumac-geometry"; });
    add("pumac-a__number-theory", function (s) { return s === "pumac-number-theory"; });

    add("pumac-b__individual", function (s) { return s === "pumac-b"; });
    add("pumac-b__algebra", function (s) { return s === "pumac-b-algebra"; });
    add("pumac-b__combinator", function (s) { return s === "pumac-b-combinator"; });
    add("pumac-b__geometry", function (s) { return s === "pumac-b-geometry"; });
    add("pumac-b__number-theory", function (s) { return s === "pumac-b-number-theory"; });

    add("mathcounts", function (s) { return s.indexOf("mathcounts") !== -1; });

    add("cmimc__individual", function (s) { return s === "cmimc"; });
    add("cmimc__algebra", function (s) { return s === "cmimc-algebra"; });
    add("cmimc__comb", function (s) { return s === "cmimc-comb"; });
    add("cmimc__geometry", function (s) { return s === "cmimc-geometry"; });

    add("arml", function (s) { return s.indexOf("arml") !== -1; });
    add("dmm", function (s) { return s.indexOf("dmm") !== -1; });
    add("cmm", function (s) { return s.indexOf("cmm") !== -1; });

    add("bmt__individual", function (s) { return s === "bmt"; });
    add("bmt__algebra", function (s) { return s === "bmt-algebra"; });
    add("bmt__calculus", function (s) { return s === "bmt-calculus"; });
    add("bmt__discrete", function (s) { return s === "bmt-discrete"; });
    add("bmt__geometry", function (s) { return s === "bmt-geometry"; });

    add("mmaths", function (s) { return s === "mmaths"; });
    add("mpfg", function (s) { return s === "mpfg"; });
    add("mpfg-olympiad", function (s) { return s.indexOf("mpfg-olympiad") !== -1; });
    add("bamo-8", function (s) { return s.indexOf("bamo-8") !== -1; });
    add("bamo-12", function (s) { return s.indexOf("bamo-12") !== -1; });
    add("brumo-a", function (s) { return s.indexOf("brumo-a") === 0; });

    return m;
  }

  var MATCHERS = makeMatchers();

  /** Fallback short names when `data.contests` has no row for the leaf slug. */
  var LABELS = {
    "hmmt-feb__individual": "HMMT Feb — Individual",
    "hmmt-feb__algebra-number-theory": "HMMT Feb — Algebra & Number Theory",
    "hmmt-feb__combo": "HMMT Feb — Combinatorics",
    "hmmt-feb__geometry": "HMMT Feb — Geometry",
    "hmmt-nov__individual": "HMMT Nov — Individual",
    "hmmt-nov__general": "HMMT Nov — General",
    "hmmt-nov__theme": "HMMT Nov — Theme",
    "pumac-a__individual": "PUMaC Div A — Individual",
    "pumac-a__algebra": "PUMaC Div A — Algebra",
    "pumac-a__combinator": "PUMaC Div A — Combinatorics",
    "pumac-a__geometry": "PUMaC Div A — Geometry",
    "pumac-a__number-theory": "PUMaC Div A — Number Theory",
    "pumac-b__individual": "PUMaC Div B — Individual",
    "pumac-b__algebra": "PUMaC Div B — Algebra",
    "pumac-b__combinator": "PUMaC Div B — Combinatorics",
    "pumac-b__geometry": "PUMaC Div B — Geometry",
    "pumac-b__number-theory": "PUMaC Div B — Number Theory",
    "cmimc__individual": "CMIMC — Individual",
    "cmimc__algebra": "CMIMC — Algebra & Number Theory",
    "cmimc__comb": "CMIMC — Combinatorics & CS",
    "cmimc__geometry": "CMIMC — Geometry",
    "bmt__individual": "BMT — Individual",
    "bmt__algebra": "BMT — Algebra",
    "bmt__calculus": "BMT — Calculus",
    "bmt__discrete": "BMT — Discrete",
    "bmt__geometry": "BMT — Geometry",
    usamo: "USAMO",
    usajmo: "USAJMO",
    imo: "IMO",
    rmm: "RMM",
    egmo: "EGMO",
    mathcounts: "Mathcounts",
    arml: "ARML",
    dmm: "DMM",
    cmm: "CMM",
    mmaths: "MMATHS",
    mpfg: "MPFG",
    "mpfg-olympiad": "MPFG Olympiad",
    "bamo-8": "BAMO-8",
    "bamo-12": "BAMO-12",
    "brumo-a": "BrUMO Div A"
  };

  /** Same broad order as the original flat checkbox list: olympiads, then HMMT / PUMaC, then the rest. */
  var GROUP_ORDER = [
    { multi: false, keys: ["usamo"] },
    { multi: false, keys: ["usajmo"] },
    { multi: false, keys: ["imo"] },
    { multi: false, keys: ["rmm"] },
    { multi: false, keys: ["egmo"] },
    { multi: true, title: "HMMT February", keys: LEGACY_EXPAND["hmmt-feb"] },
    { multi: true, title: "HMMT November", keys: LEGACY_EXPAND["hmmt-nov"] },
    { multi: true, title: "PUMaC Division A", keys: LEGACY_EXPAND["pumac-a"] },
    { multi: true, title: "PUMaC Division B", keys: LEGACY_EXPAND["pumac-b"] },
    { multi: false, keys: ["mathcounts"] },
    { multi: true, title: "CMIMC", keys: LEGACY_EXPAND.cmimc },
    { multi: false, keys: ["arml"] },
    { multi: false, keys: ["dmm"] },
    { multi: false, keys: ["cmm"] },
    { multi: false, keys: ["mmaths"] },
    { multi: false, keys: ["mpfg"] },
    { multi: false, keys: ["mpfg-olympiad"] },
    { multi: false, keys: ["bamo-8"] },
    { multi: false, keys: ["bamo-12"] },
    { multi: false, keys: ["brumo-a"] },
    { multi: true, title: "BMT", keys: LEGACY_EXPAND.bmt }
  ];

  function selectionMatchesGroupKeys(checkedArr, groupKeys) {
    if (!checkedArr || !groupKeys || checkedArr.length !== groupKeys.length) return false;
    var want = {};
    for (var i = 0; i < groupKeys.length; i++) want[groupKeys[i]] = true;
    for (var j = 0; j < checkedArr.length; j++) {
      if (!want[checkedArr[j]]) return false;
    }
    return true;
  }

  function allLeafKeysList() {
    var keys = [];
    for (var i = 0; i < GROUP_ORDER.length; i++) {
      var g = GROUP_ORDER[i];
      for (var j = 0; j < g.keys.length; j++) {
        keys.push(g.keys[j]);
      }
    }
    return keys;
  }

  var ALL_LEAF_KEYS = allLeafKeysList();

  /**
   * Map filter leaf key -> contests.csv folder_name (slug) for contest_name lookup.
   */
  var LEAF_KEY_TO_SLUG = {
    usamo: "amo",
    usajmo: "jmo",
    imo: "imo",
    rmm: "rmm",
    egmo: "egmo",
    "hmmt-feb__individual": "hmmt-feb",
    "hmmt-feb__algebra-number-theory": "hmmt-feb-algebra-number-theory",
    "hmmt-feb__combo": "hmmt-feb-combo",
    "hmmt-feb__geometry": "hmmt-feb-geometry",
    "hmmt-nov__individual": "hmmt-nov",
    "hmmt-nov__general": "hmmt-nov-general",
    "hmmt-nov__theme": "hmmt-nov-theme",
    "pumac-a__individual": "pumac",
    "pumac-a__algebra": "pumac-algebra",
    "pumac-a__combinator": "pumac-combinator",
    "pumac-a__geometry": "pumac-geometry",
    "pumac-a__number-theory": "pumac-number-theory",
    "pumac-b__individual": "pumac-b",
    "pumac-b__algebra": "pumac-b-algebra",
    "pumac-b__combinator": "pumac-b-combinator",
    "pumac-b__geometry": "pumac-b-geometry",
    "pumac-b__number-theory": "pumac-b-number-theory",
    mathcounts: "mathcounts-national-rank",
    "cmimc__individual": "cmimc",
    "cmimc__algebra": "cmimc-algebra",
    "cmimc__comb": "cmimc-comb",
    "cmimc__geometry": "cmimc-geometry",
    arml: "arml",
    dmm: "dmm",
    cmm: "cmm",
    mmaths: "mmaths",
    mpfg: "mpfg",
    "mpfg-olympiad": "mpfg-olympiad",
    "bamo-8": "bamo-8",
    "bamo-12": "bamo-12",
    "brumo-a": "brumo-a",
    "bmt__individual": "bmt",
    "bmt__algebra": "bmt-algebra",
    "bmt__calculus": "bmt-calculus",
    "bmt__discrete": "bmt-discrete",
    "bmt__geometry": "bmt-geometry"
  };

  /** Multi-group card title -> primary slug for contest_name (contests.csv). */
  var MULTI_GROUP_TITLE_TO_SLUG = {
    "HMMT February": "hmmt-feb",
    "HMMT November": "hmmt-nov",
    "PUMaC Division A": "pumac",
    "PUMaC Division B": "pumac-b",
    CMIMC: "cmimc",
    BMT: "bmt"
  };

  function migrateSavedArray(saved) {
    if (!saved || !saved.length) return { mode: "all" };
    if (saved.indexOf("all") >= 0 && saved.length === 1) return { mode: "all" };
    var out = [];
    var seen = {};
    for (var i = 0; i < saved.length; i++) {
      var v = saved[i];
      if (v === "all") continue;
      if (LEGACY_EXPAND[v]) {
        var exp = LEGACY_EXPAND[v];
        for (var j = 0; j < exp.length; j++) {
          var k = exp[j];
          if (!seen[k]) {
            seen[k] = true;
            out.push(k);
          }
        }
      } else if (MATCHERS[v]) {
        if (!seen[v]) {
          seen[v] = true;
          out.push(v);
        }
      }
    }
    if (!out.length) return { mode: "all" };
    return { mode: "leaves", leaves: out };
  }

  function noopApi() {
    return {
      getActiveContestFilterValues: function () { return ["all"]; },
      getContestFilterSummaryText: function () { return "All competitions selected"; },
      updateSummary: function () {},
      isContestFilterActive: function () { return false; },
      recordMatchesContestFilter: function () { return true; },
      getSelectedContestLabels: function () { return []; },
      restoreFromSavedArray: function () {},
      setContests: function () {}
    };
  }

  function create(containerEl, options) {
    options = options || {};
    if (!containerEl) return noopApi();

    var summaryEl = options.summaryEl;
    var mcpTimelineSummaryEl = options.mcpTimelineSummaryEl;
    var getMcpTimelineApplyFiltersChecked = options.getMcpTimelineApplyFiltersChecked || function () { return true; };
    var onChange = options.onChange || function () {};

    var allLeafKeys = ALL_LEAF_KEYS.slice();
    var allBox = null;
    var leafInputs = {};
    /** One entry per multi group: { leafKeys, groupAllBox (optional) } */
    var multiGroupMetas = [];
    /** From data.json `contests` (contests.csv): folder_name -> { contest_name, contest_name_long, ... } */
    var contestsBySlug = options.contests || {};

    function metaForSlug(slug) {
      return slug && contestsBySlug[slug] ? contestsBySlug[slug] : null;
    }

    /** Long display title from contests.csv `contest_name_long` (built into data.json). */
    function longTitleFromMeta(m) {
      if (!m || !m.contest_name_long) return "";
      return String(m.contest_name_long).trim();
    }

    /** Bold short name only (for multi-group header row; long title is on the next row). */
    function appendGroupHeadingShortName(el, meta, fallbackShort) {
      var shortText = meta && meta.contest_name ? String(meta.contest_name).trim() : "";
      if (!shortText) shortText = fallbackShort || "";
      var s = document.createElement("span");
      s.className = "contest-filter-short-name";
      s.textContent = shortText;
      el.appendChild(s);
    }

    function appendFirstLevelLabelSpans(el, meta, fallbackShort) {
      var shortText = meta && meta.contest_name ? String(meta.contest_name).trim() : "";
      if (!shortText) shortText = fallbackShort || "";
      var longText = meta ? longTitleFromMeta(meta) : "";
      if (longText && shortText && longText.toLowerCase() === shortText.toLowerCase()) longText = "";
      var wrap = document.createElement("span");
      wrap.className = "contest-filter-first-level-label";
      var s = document.createElement("span");
      s.className = "contest-filter-short-name";
      s.textContent = shortText;
      wrap.appendChild(s);
      if (longText) {
        var lt = document.createElement("span");
        lt.className = "contest-filter-long-name";
        lt.textContent = " " + longText;
        wrap.appendChild(lt);
      }
      el.appendChild(wrap);
    }

    function contestNameForLeafKey(key) {
      var slug = LEAF_KEY_TO_SLUG[key];
      var m = metaForSlug(slug);
      if (m && m.contest_name) return m.contest_name;
      return LABELS[key] || key;
    }

    function nestedCheckboxLabelForLeafKey(key) {
      var full = contestNameForLeafKey(key);
      if (full.indexOf(" — ") !== -1) return full.split(" — ").pop().trim();
      return full;
    }

    function multiGroupPrimarySlug(title) {
      return MULTI_GROUP_TITLE_TO_SLUG[title] || null;
    }

    /** Short label for toolbar summary (contest_name only, not contest_name_long). */
    function summaryShortLabelForGroup(grp) {
      var slug = multiGroupPrimarySlug(grp.title);
      var m = metaForSlug(slug);
      if (m && m.contest_name) return String(m.contest_name).trim();
      return grp.title;
    }

    function buildDom() {
      containerEl.className = "contest-filter-options contest-filter-options--two-level";
      containerEl.innerHTML = "";
      multiGroupMetas = [];

      var allLabel = document.createElement("label");
      allLabel.className = "contest-filter-option contest-filter-option--all";
      allBox = document.createElement("input");
      allBox.type = "checkbox";
      allBox.value = "all";
      allBox.checked = true;
      allLabel.appendChild(allBox);
      allLabel.appendChild(document.createTextNode(" All"));
      containerEl.appendChild(allLabel);

      var singleBuffer = [];

      function flushSingles() {
        if (!singleBuffer.length) return;
        for (var si = 0; si < singleBuffer.length; si++) {
          var flat = singleBuffer[si];
          var block = document.createElement("div");
          block.className = "contest-filter-first-level contest-filter-first-level--single";
          block.appendChild(flat);
          containerEl.appendChild(block);
        }
        singleBuffer = [];
      }

      for (var gi = 0; gi < GROUP_ORDER.length; gi++) {
        var grp = GROUP_ORDER[gi];
        if (grp.multi) {
          flushSingles();
          var gid = multiGroupMetas.length;
          var panelId = "cf-group-panel-" + String(gid);
          var meta = { leafKeys: grp.keys.slice(), groupAllBox: null };

          var wrap = document.createElement("div");
          wrap.className = "contest-filter-group";

          var header = document.createElement("div");
          header.className = "contest-filter-group-header";

          var toggle = document.createElement("button");
          toggle.type = "button";
          toggle.className = "contest-filter-group-toggle";
          toggle.setAttribute("aria-expanded", "true");
          toggle.setAttribute("aria-controls", panelId);
          var chev = document.createElement("span");
          chev.className = "contest-filter-group-chevron";
          chev.setAttribute("aria-hidden", "true");
          chev.textContent = "▼";
          var titleSpan = document.createElement("span");
          titleSpan.className = "contest-filter-group-heading-text";
          var gSlug = multiGroupPrimarySlug(grp.title);
          var gMeta = metaForSlug(gSlug);
          appendGroupHeadingShortName(titleSpan, gMeta, grp.title);
          toggle.appendChild(chev);
          toggle.appendChild(titleSpan);
          header.appendChild(toggle);

          var showGroupAll = grp.keys.length > 1;
          if (showGroupAll) {
            var allLab = document.createElement("label");
            allLab.className = "contest-filter-group-all-label";
            var ga = document.createElement("input");
            ga.type = "checkbox";
            ga.setAttribute("data-role", "group-all");
            ga.setAttribute("data-group-id", String(gid));
            ga.checked = true;
            meta.groupAllBox = ga;
            allLab.appendChild(ga);
            allLab.appendChild(document.createTextNode(" All"));
            header.appendChild(allLab);
          }

          wrap.appendChild(header);

          var gShort = gMeta && gMeta.contest_name ? String(gMeta.contest_name).trim() : "";
          if (!gShort) gShort = grp.title;
          var gLong = gMeta ? longTitleFromMeta(gMeta) : "";
          if (gLong && gShort && gLong.toLowerCase() === gShort.toLowerCase()) gLong = "";
          if (gLong) {
            var longRow = document.createElement("div");
            longRow.className = "contest-filter-group-long";
            longRow.textContent = gLong;
            wrap.appendChild(longRow);
          }

          var leaves = document.createElement("div");
          leaves.id = panelId;
          leaves.className = "contest-filter-group-leaves";
          for (var li = 0; li < grp.keys.length; li++) {
            var key = grp.keys[li];
            var shortLabel = nestedCheckboxLabelForLeafKey(key);
            var lab = document.createElement("label");
            lab.className = "contest-filter-option contest-filter-option--nested";
            var inp = document.createElement("input");
            inp.type = "checkbox";
            inp.value = key;
            inp.checked = true;
            lab.appendChild(inp);
            lab.appendChild(document.createTextNode(" " + shortLabel));
            leaves.appendChild(lab);
            leafInputs[key] = inp;
          }
          wrap.appendChild(leaves);
          containerEl.appendChild(wrap);
          multiGroupMetas.push(meta);
        } else {
          var key0 = grp.keys[0];
          var flat = document.createElement("label");
          flat.className = "contest-filter-option contest-filter-option--single";
          var inp0 = document.createElement("input");
          inp0.type = "checkbox";
          inp0.value = key0;
          inp0.checked = true;
          flat.appendChild(inp0);
          flat.appendChild(document.createTextNode(" "));
          appendFirstLevelLabelSpans(flat, metaForSlug(LEAF_KEY_TO_SLUG[key0]), contestNameForLeafKey(key0));
          leafInputs[key0] = inp0;
          singleBuffer.push(flat);
        }
      }
      flushSingles();
    }

    function syncAllGroupAllBoxes() {
      for (var g = 0; g < multiGroupMetas.length; g++) {
        var meta = multiGroupMetas[g];
        if (!meta.groupAllBox) continue;
        var keys = meta.leafKeys;
        var allOn = true;
        for (var i = 0; i < keys.length; i++) {
          var inp = leafInputs[keys[i]];
          if (!inp || !inp.checked) {
            allOn = false;
            break;
          }
        }
        meta.groupAllBox.checked = allOn;
      }
    }

    function getCheckedLeafKeys() {
      var sel = [];
      for (var i = 0; i < allLeafKeys.length; i++) {
        var k = allLeafKeys[i];
        var inp = leafInputs[k];
        if (inp && inp.checked) sel.push(k);
      }
      return sel;
    }

    function syncAllBoxFromLeaves() {
      if (!allBox) return;
      var checked = getCheckedLeafKeys();
      allBox.checked = checked.length === allLeafKeys.length;
    }

    function getActiveContestFilterValues() {
      var checked = getCheckedLeafKeys();
      if (!checked.length || checked.length === allLeafKeys.length) return ["all"];
      return checked.slice();
    }

    function getContestFilterSummaryText() {
      var checked = getCheckedLeafKeys();
      if (!checked.length || checked.length === allLeafKeys.length) {
        return "All competitions selected";
      }
      for (var gi = 0; gi < GROUP_ORDER.length; gi++) {
        var grp = GROUP_ORDER[gi];
        if (!grp.multi || !grp.keys || !grp.title) continue;
        if (selectionMatchesGroupKeys(checked, grp.keys)) {
          return summaryShortLabelForGroup(grp) + " selected";
        }
      }
      if (checked.length === 1) {
        var one = checked[0];
        return contestNameForLeafKey(one) + " selected";
      }
      return String(checked.length) + " competitions selected";
    }

    function updateMcpTimelineLine() {
      if (!mcpTimelineSummaryEl) return;
      var base = getContestFilterSummaryText();
      if (!getMcpTimelineApplyFiltersChecked()) {
        mcpTimelineSummaryEl.textContent = base + " · not applied to chart";
      } else {
        mcpTimelineSummaryEl.textContent = base;
      }
    }

    function updateSummary(timelineOnly) {
      if (!timelineOnly && summaryEl) {
        summaryEl.textContent = getContestFilterSummaryText();
      }
      updateMcpTimelineLine();
    }

    function isContestFilterActive() {
      var v = getActiveContestFilterValues();
      return v.length > 0 && v.indexOf("all") === -1;
    }

    function recordMatchesContestFilter(record) {
      if (!record) return false;
      var slug = slugOf(record);
      if (!slug) return false;
      var selected = getActiveContestFilterValues();
      if (!selected.length || selected.indexOf("all") !== -1) return true;
      for (var i = 0; i < selected.length; i++) {
        var fn = MATCHERS[selected[i]];
        if (typeof fn === "function" && fn(slug)) return true;
      }
      return false;
    }

    function getSelectedContestLabels() {
      var vals = getActiveContestFilterValues();
      if (!vals.length || vals.indexOf("all") !== -1) return [];
      var labels = [];
      for (var i = 0; i < vals.length; i++) {
        var vk = vals[i];
        labels.push(contestNameForLeafKey(vk));
      }
      return labels;
    }

    function restoreFromSavedArray(arr) {
      var mig = migrateSavedArray(arr);
      if (mig.mode === "all") {
        if (allBox) allBox.checked = true;
        for (var i = 0; i < allLeafKeys.length; i++) {
          var k = allLeafKeys[i];
          if (leafInputs[k]) leafInputs[k].checked = true;
        }
        syncAllGroupAllBoxes();
        syncAllBoxFromLeaves();
        return;
      }
      var want = {};
      for (var j = 0; j < mig.leaves.length; j++) {
        want[mig.leaves[j]] = true;
      }
      if (allBox) allBox.checked = false;
      for (var x = 0; x < allLeafKeys.length; x++) {
        var key = allLeafKeys[x];
        if (leafInputs[key]) leafInputs[key].checked = !!want[key];
      }
      syncAllGroupAllBoxes();
      syncAllBoxFromLeaves();
    }

    function onCheckboxChange(event) {
      var target = event.target;
      if (!target || target.type !== "checkbox") return;

      if (target.getAttribute("data-role") === "group-all") {
        var rawGid = target.getAttribute("data-group-id");
        var gid = rawGid == null ? NaN : parseInt(rawGid, 10);
        if (!isNaN(gid) && multiGroupMetas[gid]) {
          var keys = multiGroupMetas[gid].leafKeys;
          for (var gi = 0; gi < keys.length; gi++) {
            var leafInp = leafInputs[keys[gi]];
            if (leafInp) leafInp.checked = target.checked;
          }
        }
        syncAllBoxFromLeaves();
      } else if (target.value === "all") {
        for (var i = 0; i < allLeafKeys.length; i++) {
          var k = allLeafKeys[i];
          if (leafInputs[k]) leafInputs[k].checked = target.checked;
        }
        syncAllGroupAllBoxes();
      } else {
        if (allBox && !target.checked) allBox.checked = false;
        else if (allBox) {
          var allOn = true;
          for (var j = 0; j < allLeafKeys.length; j++) {
            var kk = allLeafKeys[j];
            if (leafInputs[kk] && !leafInputs[kk].checked) {
              allOn = false;
              break;
            }
          }
          allBox.checked = allOn;
        }
        syncAllGroupAllBoxes();
      }

      updateSummary();
      onChange();
    }

    function onGroupToggleClick(event) {
      var btn = event.target && event.target.closest
        ? event.target.closest(".contest-filter-group-toggle")
        : null;
      if (!btn) return;
      event.preventDefault();
      var wrap = btn.closest(".contest-filter-group");
      if (!wrap) return;
      var collapsed = wrap.classList.toggle("contest-filter-group--collapsed");
      btn.setAttribute("aria-expanded", collapsed ? "false" : "true");
    }

    function setContests(contests) {
      contestsBySlug = contests || {};
      var prev = getCheckedLeafKeys();
      buildDom();
      if (prev.length === allLeafKeys.length) {
        restoreFromSavedArray(["all"]);
      } else {
        restoreFromSavedArray(prev);
      }
      updateSummary();
    }

    buildDom();
    containerEl.addEventListener("change", onCheckboxChange);
    containerEl.addEventListener("click", onGroupToggleClick);
    updateSummary();

    return {
      getActiveContestFilterValues: getActiveContestFilterValues,
      getContestFilterSummaryText: getContestFilterSummaryText,
      updateSummary: updateSummary,
      isContestFilterActive: isContestFilterActive,
      recordMatchesContestFilter: recordMatchesContestFilter,
      getSelectedContestLabels: getSelectedContestLabels,
      restoreFromSavedArray: restoreFromSavedArray,
      setContests: setContests
    };
  }

  global.MathCompContestFilter = { create: create };
})(typeof window !== "undefined" ? window : this);
