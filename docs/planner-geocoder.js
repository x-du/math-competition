/* Independent coordinates for the custom map. Google is used only for directions links. */
(function () {
  let zipData, sequence = 0;
  function lastZip(address) {
    const matches = address.match(/\b(\d{5})(?:-\d{4})?\b/g);
    return matches ? matches[matches.length - 1].slice(0, 5) : null;
  }
  function looksLikeStreet(address) {
    return /^\d+\s+\S/.test(address.trim());
  }
  async function loadZips() {
    if (!zipData) {
      zipData = fetch('us-zip-locations.json').then(r => {
        if (!r.ok) throw new Error('ZIP data unavailable'); return r.json();
      }).catch(error => { zipData = null; throw error; });
    }
    return zipData;
  }
  async function lookupZip(zip) {
    const entry = (await loadZips())[zip];
    if (!entry) return [];
    return [{ label: `${entry[0]}, ${entry[1]} ${zip}`, position: { lat: entry[2], lng: entry[3] }, approximate: true }];
  }
  function lookupCensus(address) {
    return new Promise((resolve, reject) => {
      const callback = 'plannerCensus' + (++sequence);
      const script = document.createElement('script');
      let timer;
      const cleanup = () => {
        clearTimeout(timer); script.remove();
        window[callback] = () => {};
        setTimeout(() => { delete window[callback]; }, 60000);
      };
      window[callback] = response => {
        cleanup();
        const matches = response?.result?.addressMatches || [];
        resolve(matches.filter(m => Number.isFinite(m.coordinates?.x) && Number.isFinite(m.coordinates?.y)).map(m => ({
          label: m.matchedAddress,
          position: { lat: m.coordinates.y, lng: m.coordinates.x }, approximate: true
        })));
      };
      script.onerror = () => { cleanup(); reject(new Error('Address lookup unavailable')); };
      timer = setTimeout(() => { cleanup(); reject(new Error('Address lookup timed out')); }, 18000);
      script.src = 'https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?' + new URLSearchParams({
        address, benchmark: 'Public_AR_Current', format: 'jsonp', callback
      });
      document.head.append(script);
    });
  }
  async function lookup(address) {
    const trimmed = address.trim();
    if (/^\d{5}(?:-\d{4})?$/.test(trimmed)) return lookupZip(trimmed.slice(0, 5));
    const zip = lastZip(trimmed);
    // City + state + ZIP has no street; Census oneline usually returns nothing.
    if (zip && !looksLikeStreet(trimmed)) return lookupZip(zip);
    try {
      const matches = await lookupCensus(trimmed);
      if (matches.length) return matches;
    } catch (_) { /* Fall back to a ZIP in the query when Census is unavailable. */ }
    return zip ? lookupZip(zip) : [];
  }
  window.PlannerGeocoder = { lookup };
})();
