/* Independent coordinates for the custom map. Google is used only for routes. */
(function () {
  let zipData, sequence = 0;
  async function lookup(address) {
    const zip = address.trim().match(/^([0-9]{5})(?:-[0-9]{4})?$/);
    if (zip) {
      if (!zipData) zipData = fetch('us-zip-locations.json').then(r => {
        if (!r.ok) throw new Error('ZIP data unavailable'); return r.json();
      }).catch(error => { zipData = null; throw error; });
      const entry = (await zipData)[zip[1]];
      if (!entry) return [];
      return [{ label: `${entry[0]}, ${entry[1]} ${zip[1]}`, position: { lat: entry[2], lng: entry[3] }, approximate: true }];
    }
    // Census supports JSONP for static websites without cross-origin fetch access.
    return new Promise((resolve, reject) => {
      const callback = 'plannerCensus' + (++sequence);
      const script = document.createElement('script');
      let timer;
      const cleanup = () => {
        clearTimeout(timer); script.remove();
        // A no-op handles a late response that was already in flight at timeout.
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
  window.PlannerGeocoder = { lookup };
})();
