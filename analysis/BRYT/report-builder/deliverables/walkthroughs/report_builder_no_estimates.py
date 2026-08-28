"""
Estimate-scrubbed twin of report_builder.py.

Produces the same technical walkthrough with all commercial estimate figures
removed: no cover effort badge and no day figures in the delivery breakdown
(the phases and their scope are retained, just not the day counts). It reuses
the base content module by transforming a deep copy, so the two documents can
never drift apart - edit report_builder.py and both rebuild.

Build:
    python analysis/BRYT/report-builder/deliverables/walkthroughs/build_walkthrough.py report_builder_no_estimates
"""
import copy

import report_builder as base

DOC = copy.deepcopy(base.DOC)

# Different output file, and no cover effort badge.
DOC["slug"] = "report-builder-no-estimates"
DOC.pop("effort", None)

# Scrub day figures from the delivery breakdown: keep Phase + Scope, drop Days.
for block in DOC["blocks"]:
    if block.get("type") == "table" and block.get("heading") == "Delivery breakdown":
        block["intro"] = (
            "The build is grouped into eight phases. The security spine (Phase 2) "
            "is sequenced before any execution path - no query runs before the "
            "verifier exists and is property-tested."
        )
        block["columns"] = ["Phase", "Scope"]
        block["rows"] = [row[:2] for row in block["rows"]]
