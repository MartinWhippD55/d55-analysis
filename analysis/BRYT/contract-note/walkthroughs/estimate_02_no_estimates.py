"""
Estimate 2 walkthrough - "no estimates" variant.

Identical content to estimate_02.py (DocuSign Integration) but with all
developer-day figures removed, so it can be shared with the delivery team
without applying schedule pressure:

  - the cover-page effort badge is dropped
  - the "Delivery breakdown" intro no longer states required/total days

Renders to a distinct slug (estimate-2-walkthrough-no-estimates) so the
estimated version in estimate_02.py is left untouched.

Usage:
    python analysis/BRYT/contract-note/walkthroughs/build_walkthrough.py estimate_02_no_estimates
"""
import copy

import estimate_02 as _base

DOC = copy.deepcopy(_base.DOC)

# Render to its own files, leaving estimate-2-walkthrough.* intact.
DOC["slug"] = "contract-note-docusign"

# Drop the cover-page effort badge (build_walkthrough only renders it when present).
DOC.pop("effort", None)

# Rewrite the Delivery breakdown intro so it carries no day figures.
for block in DOC["blocks"]:
    if block.get("type") == "table" and block.get("heading") == "Delivery breakdown":
        block["intro"] = "Work on this estimate is grouped as follows."
        break

# Cap the two flow diagrams so the stakeholder-friendly "Simplified flow"
# fits on the same page as the "End-to-end sequence" (page 4) instead of
# spilling onto its own page.
for block in DOC["blocks"]:
    if block.get("type") == "diagram":
        if block.get("heading") == "End-to-end sequence":
            block["maxHeight"] = 60
        elif block.get("heading") == "Simplified flow":
            block["maxHeight"] = 100
