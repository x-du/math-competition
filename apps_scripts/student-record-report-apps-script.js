/**
 * Google Apps Script for student-record error reports.
 *
 * Setup (same style as old script):
 * 1) Open your target Google Sheet.
 * 2) Open Extensions -> Apps Script from that Sheet (bound script).
 * 3) Deploy as Web App:
 *    - Execute as: Me
 *    - Who has access: Anyone
 * 4) Copy the Web App URL and paste it into:
 *    docs/app.js -> STUDENT_RECORD_REPORT_APPS_SCRIPT_URL
 */

const SHEET_NAME = "StudentRecordReports";

function doGet() {
  return json_({
    ok: true,
    service: "student-record-report",
    sheet_name: SHEET_NAME
  });
}

const MAX_SUBMISSIONS_PER_IP_PER_DAY = 20;

function doPost(e) {
  try {
    const payload = parsePayload_(e);
    const sheet = getSheet_();
    const ip = String(payload.ip || "unknown").trim() || "unknown";

    if (countSubmissionsTodayForIp_(sheet, ip) >= MAX_SUBMISSIONS_PER_IP_PER_DAY) {
      return json_({
        ok: false,
        error: "Daily submission limit reached for this network. Try again tomorrow."
      });
    }

    // H = raw user input (issue type is in issue_type / issue_label).
    const colH = String(
      (payload.user_value != null && String(payload.user_value).trim() !== "")
        ? payload.user_value
        : (payload.other_student != null && String(payload.other_student).trim() !== ""
          ? payload.other_student
          : (payload.related_student != null
            ? payload.related_student
            : (payload.related_student_id != null ? payload.related_student_id : "")))
    ).trim();

    sheet.appendRow([
      new Date(),
      payload.issue_type || "",
      payload.issue_label || "",
      payload.student_id || "",
      payload.student_name || "",
      payload.student_state || "",
      payload.student_grade || "",
      colH,
      payload.page_url || "",
      payload.user_agent || "",
      ip,
      payload.submitted_at || ""
    ]);

    return json_({ ok: true });
  } catch (err) {
    return json_({ error: String(err && err.message ? err.message : err) });
  }
}

function parsePayload_(e) {
  const raw = (e && e.postData && e.postData.contents) ? String(e.postData.contents) : "";
  if (raw) {
    try {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === "object") return parsed;
    } catch (_) {
      // Not JSON; fall through to form parsing.
    }
    const fromRawForm = {};
    raw.split("&").forEach((pair) => {
      if (!pair) return;
      const idx = pair.indexOf("=");
      const rawKey = idx >= 0 ? pair.slice(0, idx) : pair;
      const rawVal = idx >= 0 ? pair.slice(idx + 1) : "";
      if (!rawKey) return;
      const key = decodeURIComponent(rawKey.replace(/\+/g, " "));
      const val = decodeURIComponent(rawVal.replace(/\+/g, " "));
      fromRawForm[key] = val;
    });
    if (Object.keys(fromRawForm).length > 0) return fromRawForm;
  }
  const out = {};
  const params = (e && e.parameter) ? e.parameter : {};
  for (const key in params) {
    if (Object.prototype.hasOwnProperty.call(params, key)) {
      out[key] = params[key];
    }
  }
  return out;
}

function getSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  if (!ss) {
    throw new Error("No active spreadsheet. Open this script from a Google Sheet (bound script).");
  }
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow([
      "server_received_at",
      "issue_type",
      "issue_label",
      "student_id",
      "student_name",
      "student_state",
      "student_grade",
      "user_value",
      "page_url",
      "user_agent",
      "ip",
      "client_submitted_at"
    ]);
  }
  return sheet;
}

/**
 * IP is column K (index 10); server time is column A. Same calendar day in script timezone.
 */
function countSubmissionsTodayForIp_(sheet, ip) {
  const want = String(ip).trim() || "unknown";
  const tz = Session.getScriptTimeZone() || "UTC";
  const now = new Date();
  const todayStr = Utilities.formatDate(now, tz, "yyyy-MM-dd");
  const data = sheet.getDataRange().getValues();
  let count = 0;
  for (let r = 1; r < data.length; r++) {
    const rowIp = String(data[r][10] != null ? data[r][10] : "").trim() || "unknown";
    if (rowIp !== want) {
      continue;
    }
    const cellDate = data[r][0];
    if (cellDate == null || cellDate === "") {
      continue;
    }
    const d = cellDate instanceof Date ? cellDate : new Date(cellDate);
    if (isNaN(d.getTime())) {
      continue;
    }
    if (Utilities.formatDate(d, tz, "yyyy-MM-dd") === todayStr) {
      count++;
    }
  }
  return count;
}

function json_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
