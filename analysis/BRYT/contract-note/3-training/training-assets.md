# Estimate 3a: Training & Enablement Assets

## Overview

This deliverable covers the non-software assets needed to enable the BRYT team to self-serve the contract note template management system built in Estimates 1 & 2. The focus is on documentation, walkthroughs, and reference material that gets the team productive without ongoing developer support.

## Audience

Business users responsible for managing contract note templates — likely a small team (2-5 people) who will:
- Create and modify templates for different contract types
- Update Terms & Conditions when new versions are issued
- Configure rules to match templates to contract data
- Attach data sources for additional fields (Estimate 3b)

## Deliverables

### 1. Quick-Start Guide

**Purpose:** Get a new user from zero to "I've created my first template" in under 30 minutes.

**Contents:**
- Logging into the Admin Portal
- Navigating to Contract Note Template Management
- Creating a template (name, description)
- Adding a section and opening the designer
- Placing a few fields on the canvas
- Saving and previewing
- Setting up a basic rule

**Format:** Step-by-step written guide with annotated screenshots. PDF + internal wiki.

---

### 2. How-To Guides (Task-Based)

**Purpose:** Reference guides for specific tasks users will perform repeatedly.

| Guide | Covers |
|-------|--------|
| Create a new template | End-to-end: create → add sections → configure rule → test |
| Modify an existing template | Edit metadata, add/remove/reorder sections |
| Update Terms & Conditions | Edit a shared T&C section, understand propagation to all templates |
| Create a shared section | When to share, how to create, how to attach to multiple templates |
| Configure a selection rule | Building AND/OR/NOT trees, common patterns, testing |
| Reorder template priority | How priority affects rule evaluation, drag-to-reorder |
| Add a data source to a template | Browse available data sources, attach to template, use fields in sections (Estimate 3b) |

**Format:** Individual guides (1-2 pages each), written with screenshots. Internal wiki with PDF exports.

---

### 3. Data Field Reference

**Purpose:** A catalogue of all available fields so template designers know what they can use.

**Contents:**
- **Core contract fields** — all fields from the contract JSON payload, grouped by category:
  - Offer details (offer ID, reference, dates, product info)
  - Customer details (name, address, type, BrytNumber)
  - Pricing (charge types, rates, totals by timeband)
  - MPANs (meter details, consumption, capacity)
  - Sites (addresses, contacts)
- **Data source fields** — dynamically discovered from subscribed Glue tables (Estimate 3b)
- For each field: field name (as used in template), data type, description, example value

**Format:** Searchable table (internal wiki) + exported spreadsheet for offline reference.

---

### 4. Rules Engine Cheat Sheet

**Purpose:** One-page reference for building selection rules.

**Contents:**
- Operator reference: AND, OR, NOT, EQUALS, LESS_THAN, MORE_THAN, IN
- Common patterns:
  - "Fixed product" → `EQUALS: producttype = "Fixed"`
  - "HH meter type" → `EQUALS: metertype = "HH"`
  - "Multiple MPANs" → `MORE_THAN: numberofmpans > 1`
  - "North or South region" → `IN: region IN ["North", "South"]`
  - Combined: "Fixed AND HH AND > 1 MPAN" (nested tree example)
- Priority ordering explanation (first match wins)
- Tips: start specific (high priority), end with a catch-all

**Format:** Single-page PDF / laminated desk reference.

---

### 5. Template Design Patterns

**Purpose:** Best practices for structuring templates.

**Contents:**
- When to use shared sections vs template-specific sections
- Section ordering: header → body → pricing → T&Cs
- Handling dynamic-length content (tables that span pages)
- Font and alignment consistency
- Testing templates with sample data before going live

**Format:** Written guide (2-3 pages). Internal wiki.

---

### 6. Troubleshooting Guide

**Purpose:** Self-service resolution for common issues.

**Contents:**
- "My template isn't being selected" → check rule, check priority order
- "A field shows blank on the rendered PDF" → check field name matches payload, check data source is attached
- "T&Cs changes aren't showing" → shared section propagation, cache/timing
- "I can't delete a shared section" → referenced by templates, how to unlink
- "The designer won't load" → browser compatibility, retry

**Format:** FAQ-style. Internal wiki.

---

### 7. Screen Recordings (optional, post-build)

**Purpose:** Visual walkthroughs for people who learn better by watching.

**Suggested recordings:**
- Creating a template end-to-end (5 min)
- Using the pdf-me designer to position fields (3 min)
- Building a selection rule (3 min)
- Updating T&Cs (2 min)
- Adding a data source and using its fields (3 min)

**Format:** MP4, hosted on internal video platform or SharePoint.

---

## Delivery Approach

These assets should be produced **after** Estimates 1 and 3b are implemented, using the actual UI. Draft versions can be written earlier based on the wireframes/mockups, then updated with real screenshots once the system is live.

Suggested phasing:
1. **During build:** Draft quick-start guide and data field reference from wireframes + payload structure
2. **Post-build:** Finalise all guides with real screenshots, produce screen recordings
3. **Handover:** Run a live training session (1-2 hours) walking through the guides, then leave the team to self-serve

## Estimation Notes

This is primarily a documentation/training effort, not software development. Estimate should cover:
- Technical writer time (or developer time if writing in-house)
- Screenshot/recording production
- Review cycle with BRYT stakeholders
- Optional: live training session delivery
