"""
Estimate 4 walkthrough - "no estimates" variant.

Identical content to estimate_04.py (Bespoke Contracts) but with all
developer-day figures removed, so it can be shared with the delivery team
without applying schedule pressure:

  - the cover-page effort badge is dropped
  - the "Delivery breakdown" intro no longer states required/total days

Renders to a distinct slug (contract-note-bespoke) so the estimated version
in estimate_04.py is left untouched.

Usage:
    python analysis/BRYT/contract-note/walkthroughs/build_walkthrough.py estimate_04_no_estimates
"""
import copy

import estimate_04 as _base

DOC = copy.deepcopy(_base.DOC)

# Render to its own files, leaving estimate-4-walkthrough.* intact.
DOC["slug"] = "contract-note-bespoke"

# Drop the cover-page effort badge (build_walkthrough only renders it when present).
DOC.pop("effort", None)

# Rewrite the Delivery breakdown intro so it carries no day figures.
for block in DOC["blocks"]:
    if block.get("type") == "table" and block.get("heading") == "Delivery breakdown":
        block["intro"] = "Work on this estimate is grouped as follows."
        break
