---
inclusion: manual
description: Scrapes the top N vessels from VesselFinder and collects key AIS details from each vessel's page.
---

# Vessel Finder

Scrapes the top N vessels from VesselFinder and collects key details from each vessel's page.

## Parameters

- **N** — the number of vessels to fetch (default: 10). The user specifies this when invoking the skill, e.g. "get the top 5 vessels" or "fetch 20 vessels". If not specified, default to 10.

## Steps

### Step 1: Navigate and Handle Consent

1. Use Playwright MCP to navigate to `https://www.vesselfinder.com/vessels`
2. Take a snapshot of the page
3. If a consent/cookie dialog is present, click the "Consent" button to dismiss it — this is intermittent and may not appear
4. Proceed regardless of whether the dialog was shown

### Step 2: Identify Top N Vessel Links

1. Take a fresh snapshot of the page after consent is dismissed
2. From the vessels table, extract the first N vessel links (the `<a>` elements in the first column of each row)
3. Store the vessel name and URL for each
4. If N exceeds the number of vessels on the first page (typically 20), paginate using the "next page" link and continue collecting until N vessels are gathered

### Step 3: Visit Each Vessel Page

For each of the N vessels, in order:

1. Navigate to the vessel's detail page URL (e.g., `https://www.vesselfinder.com/vessels/details/<imo>`)
2. Extract AIS data using `browser_evaluate` with this JS pattern — it's faster and more reliable than parsing snapshots for tabular data:
   ```js
   () => {
     const rows = document.querySelectorAll('.aparams tr');
     const data = {};
     rows.forEach(row => {
       const cells = row.querySelectorAll('td');
       if (cells.length >= 2) {
         data[cells[0].textContent.trim()] = cells[1].textContent.trim();
       }
     });
     return JSON.stringify(data);
   }
   ```
3. From the returned JSON, extract:
   - IMO and MMSI — stored together in `"IMO / MMSI"` field, split on ` / `
   - Callsign — `"Callsign"`
   - AIS Type — `"AIS Type"`
   - AIS Flag — `"AIS Flag"`
   - Length — `"Length / Beam"` (includes beam, e.g. `"400 / 62 m"`)
   - Position received — `"Position received"`
4. The vessel name comes from the page title (format: `"NAME, Type - Details..."`)
5. Proceed directly to the next vessel URL (no need to navigate back)

### Step 4: Summarise Results

Present the collected data as a markdown table with columns:

| Vessel Name | IMO | MMSI | Callsign | AIS Type | Flag | Length | Position Received |
|---|---|---|---|---|---|---|---|

Include all N vessels. If any field was not available on the page, show `-` in that cell.

## Notes

- The page defaults to sorting by gross tonnage descending, so the top N are the world's largest vessels.
- Some vessels (e.g., offshore platforms) may have incomplete AIS data.
- If a vessel page fails to load or has a different layout, skip it and note the issue.
- Use accessibility snapshots for navigation/link discovery (Step 2), but use `browser_evaluate` for structured data extraction (Step 3) — it's significantly faster.
- The vessel listing table uses URLs of the form `/vessels/details/<imo>` — the IMO number is in the URL path.
- The consent dialog is served by a third-party and may not appear on every session. Don't block on it.
