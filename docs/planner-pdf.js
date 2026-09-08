/* Local, downloadable schedule PDFs; no print dialog or server required. */
(function (root) {
  function create(events, core, PDF) {
    const pdf = new PDF({ unit: 'pt', format: 'letter' });
    const margin = 44, width = 524, bottom = 735;
    let y = 0;
    const clean = value => String(value || '').replace(/[\u2010-\u2015]/g, '-').replace(/[‘’]/g, "'").replace(/[“”]/g, '"').replace(/[^\x20-\x7e\xa0-\xff]/g, ' ');
    function header() {
      pdf.setFont('helvetica', 'bold'); pdf.setFontSize(20); pdf.setTextColor(31, 54, 85);
      pdf.text('My competition schedule', margin, 48);
      pdf.setFont('helvetica', 'normal'); pdf.setFontSize(10); pdf.setTextColor(85);
      pdf.text('MathIntegrity  |  mathintegrity.org  |  Saved events and watchlist', margin, 68);
      y = 94;
    }
    function paragraph(text, size = 10, bold = false, url = null) {
      pdf.setFont('helvetica', bold ? 'bold' : 'normal'); pdf.setFontSize(size);
      const lines = pdf.splitTextToSize(clean(text), width);
      for (const line of lines) {
        if (y + size > bottom) { pdf.addPage(); header(); pdf.setFont('helvetica', bold ? 'bold' : 'normal'); pdf.setFontSize(size); }
        pdf.setTextColor(...(url ? [31, 85, 155] : [45, 49, 57]));
        pdf.text(line, margin, y);
        if (url && /^https?:\/\//i.test(url)) pdf.link(margin, y - size, pdf.getTextWidth(line), size + 3, { url });
        y += size * 1.4;
      }
      y += 5;
    }
    header();
    paragraph('Discover competitions across the US. Listings are not endorsements or verification of integrity. Confirm competition details and website policies with the organizer. Saving an event does not register you.', 9);
    y += 8;
    for (const event of [...events].sort(core.compareEvents)) {
      if (y + 135 > bottom) { pdf.addPage(); header(); }
      paragraph(event.name, 13, true);
      paragraph('Date: ' + core.dateLabel(event));
      paragraph(event.location?.city || (event.mode === 'online' ? 'Online' : 'Confirm testing host'));
      paragraph(core.deadlineLabel(event) + (event.registrationDeadline && event.registrationDeadline < core.todayISO() ? ' - Passed' : ''));
      paragraph(event.url, 9, false, event.url);
      if (event.dateTentative || event.dateKind !== 'fixed') paragraph('Watchlist - confirm your date or session with the organizer.', 9);
      for (const warning of core.conflicts(event, events)) paragraph(warning, 9);
      y += 6; pdf.setDrawColor(210); pdf.line(margin, y, margin + width, y); y += 22;
    }
    const pages = pdf.getNumberOfPages();
    for (let page = 1; page <= pages; page++) {
      pdf.setPage(page); pdf.setFont('helvetica', 'normal'); pdf.setFontSize(9); pdf.setTextColor(100);
      pdf.text(`${page} / ${pages}`, 568, 765, { align: 'right' });
    }
    pdf.setProperties({ title: 'MathIntegrity Competition Schedule', author: 'MathIntegrity' });
    return pdf;
  }
  if (typeof module === 'object' && module.exports) module.exports = { create };
  else root.PlannerPDF = { create };
})(typeof window !== 'undefined' ? window : globalThis);
