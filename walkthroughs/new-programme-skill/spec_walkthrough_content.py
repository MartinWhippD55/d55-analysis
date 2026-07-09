"""
Content for the New Programme skill spec walkthrough.

Drawn from .kiro/specs/new-programme-skill/design.md + diagram.md.
CSS-rendered diagrams (pipeline/layers) carry the in-doc flow; the rendered
mermaid critique-loop PNG is embedded as a figure. Images are embedded as
base64 by the engine so the document stays self-contained.
"""
from pathlib import Path

# The rendered mermaid PNGs live next to diagram.md in the spec folder.
_SPEC = Path(__file__).resolve().parents[2] / ".kiro" / "specs" / "new-programme-skill"
OVERVIEW_PNG = str(_SPEC / "diagram-overview.png")
S1_PNG = str(_SPEC / "diagram-s1-scope.png")
S2_PNG = str(_SPEC / "diagram-s2-modules.png")
S3_PNG = str(_SPEC / "diagram-s3-assets.png")
S4_PNG = str(_SPEC / "diagram-s4-verify.png")
CRITIQUE_LOOP_PNG = str(_SPEC / "diagram-critique-loop.png")

DOC = {
    "slug": "new-programme-skill-walkthrough",
    "title": "New Programme Skill",
    "subtitle": "Service Catalog — Technical Design Walkthrough",
    "effort": "Design-first spec · pre-requirements",
    "date": "July 2026",
    "blocks": [
        {
            "type": "section",
            "heading": "Background",
            "body": [
                "D55 wants a repeatable way to add a new service Programme to its Service Catalog. Every "
                "programme is built around a free assessment that determines a prospective client's current "
                "capability, then recommends the paid modules that close their gaps — Assess, Teach, Prove, "
                "Scale.",
                "The AI-DLC programme was built by hand and became the reference for the pattern. Reproducing "
                "that by hand for each new programme is slow and inconsistent. The New Programme skill "
                "automates it: from a rough idea (and optionally a client's scores) it produces the whole "
                "asset set — assessment dimensions, a module library, per-module HTML and PDF assets, an "
                "internal runbook spreadsheet, an assessment questionnaire spreadsheet, an interactive "
                "questionnaire that renders a radar chart and recommends modules, and an elevator-pitch deck.",
                "The defining feature is a six-persona sub-agent critique loop that refines each major "
                "artefact against internal (D55) and external (client) viewpoints before it reaches a human "
                "gate — so the user reviews a strong draft, not a first pass.",
            ],
        },
        {
            "type": "callout",
            "heading": "What changes, in one line",
            "body": [
                "A hand-built, one-off programme becomes a manifest-driven skill that scaffolds, authors, "
                "critiques, and renders a complete programme — reusing the existing render engine and "
                "deliverables skills rather than reinventing them.",
            ],
        },
        {
            "type": "section",
            "heading": "How it works",
            "pageBreak": True,
            "body": [
                "Three layers. An orchestrator (the new-programme skill) owns the phase flow and the human "
                "gates. Producer sub-skills each build one artefact type, mostly reusing what already exists "
                "(programme_engine.py, deliverables-toolkit, summary-presentation). A critique panel of six "
                "sub-agents refines artefacts between production and each human gate.",
                "Everything is driven from a single machine-readable manifest (programme.yaml) generated at "
                "scaffold time. Docs, spreadsheets, and the interactive questionnaire all render from it, so "
                "the tooling never drifts from the content.",
                "The skill runs in one of two modes: template mode maintains the canonical, reusable catalog "
                "entry; client-instance mode clones the template and scopes it to one client's assessment "
                "scores.",
            ],
        },
        {
            "type": "diagram",
            "heading": "The programme build flow — overview",
            "body": [
                "Nine phases (A–I), grouped into four stages. The overview shows how the stages connect; each "
                "of stages 1–3 runs the six-persona critique loop and a human gate internally (the dotted "
                "self-loops). The stage-by-stage detail follows.",
            ],
            "image": OVERVIEW_PNG,
            "caption": "High-level flow: Scope & Frame -> Build Modules -> Generate Assets -> Verify & Ship.",
        },
        {
            "type": "diagram",
            "heading": "Stage 1 — Scope & Frame (Phases A–B)",
            "pageBreak": True,
            "body": [
                "Establish the programme context, then the assessment dimensions. Each is refined by the "
                "critique panel and confirmed at a human gate before advancing.",
            ],
            "image": S1_PNG,
            "caption": "Context (CEO/Marketing/C-Suite critique) then Dimensions (CTO/Tech/Middle-Mgmt critique).",
        },
        {
            "type": "diagram",
            "heading": "Stage 2 — Build Modules (Phases C–D)",
            "pageBreak": True,
            "body": [
                "Scaffold the modules and manifest, validate the join keys, then author each in-scope module "
                "through the critique loop and a per-module human gate.",
            ],
            "image": S2_PNG,
            "caption": "Join keys are validated before authoring; the loop repeats per in-scope module.",
        },
        {
            "type": "diagram",
            "heading": "Stage 3 — Generate Assets (Phases E–H)",
            "pageBreak": True,
            "body": [
                "Produce the per-module assets, the runbook and questionnaire spreadsheets, the interactive "
                "questionnaire, and the elevator-pitch deck — with a final critique pass on the client-facing set.",
            ],
            "image": S3_PNG,
            "caption": "Assets -> spreadsheets -> interactive questionnaire -> pitch (Marketing/CEO/C-Suite critique).",
        },
        {
            "type": "diagram",
            "heading": "Stage 4 — Verify & Ship (Phase I)",
            "pageBreak": True,
            "body": [
                "Verify every output (measure the DOM, check PDFs and spreadsheets); fix and regenerate any "
                "failures until all checks pass.",
            ],
            "image": S4_PNG,
            "caption": "The programme is only 'ready' once all verification checks pass.",
        },
        {
            "type": "layers",
            "heading": "Architecture",
            "body": [
                "The orchestrator delegates rendering to producer sub-skills and refinement to the critique "
                "panel. A shared programme workspace (files on disk) is the single source of truth every "
                "sub-agent reads from and writes to.",
            ],
            "lanes": [
                {"label": "Orchestrator", "nodes": ["new-programme skill (phase state machine + gates)"]},
                {"label": "Producer sub-skills",
                 "nodes": ["scaffold", "dimensions-author", "module-author", "runbook + questionnaire sheets",
                           "interactive-questionnaire", "module-assets", "summary-presentation"]},
                {"label": "Critique panel (sub-agents)",
                 "nodes": ["CEO Jonathan", "CTO Rhys", "Marketing", "Client C-Suite", "Middle-Mgmt", "Tech Teams"]},
                {"label": "Engine + contracts",
                 "nodes": ["programme_engine.build()", "programme.yaml manifest", "MODULE-SCHEMA + manual TOC"]},
            ],
            "caption": "Producer sub-skills reuse the config-driven render engine; contracts keep the layers consistent.",
        },
        {
            "type": "table",
            "heading": "The six critique personas",
            "pageBreak": True,
            "intro": "Each persona is a sub-agent with its own lens and scorecard. Internal personas hold a higher bar (>= 4/5); external personas check credibility (>= 3/5).",
            "columns": ["Persona", "Lens", "Cares most about"],
            "rows": [
                ["Jonathan — D55 CEO", "Internal / commercial", "Strategic fit, brand, margin, is this a sellable programme"],
                ["Rhys — D55 CTO", "Internal / delivery", "Technical credibility, can a consultant run this, delivery risk"],
                ["Marketing", "Internal / GTM", "Elevator pitch, funnel, the free-assessment hook, differentiation"],
                ["Client C-Suite", "External / buyer", "ROI, risk, why you / why now, board-defensibility"],
                ["Client Middle-Management", "External / feasibility", "Disruption to my team, workload, what this means on Monday"],
                ["Client Technical Teams", "External / credibility", "Is this real or vendor fluff, depth, respect for how engineers work"],
            ],
        },
        {
            "type": "section",
            "heading": "The critique loop",
            "body": [
                "Each critiqued phase runs an autonomous refine loop before the human gate. Relevant personas "
                "critique the draft in parallel; the aggregator dedupes and ranks their findings and splits "
                "them into addressable-now (fix in-file) versus parked (needs a person or decision — never "
                "counted against the score).",
                "Three guards guarantee the loop terminates: a maximum iteration cap (default 3, matching the "
                "established process), pass gates (primary personas meet their threshold and there are zero "
                "open blockers), and stall detection (if the backlog stops shrinking, the loop escalates "
                "rather than spinning). On pass or escalation the refined artefact — plus a critique summary — "
                "goes to the human 'Happy?' gate.",
            ],
            "bullets": [
                "PASS — thresholds met, no blockers -> hand to the human gate",
                "ITERATE — apply the top-ranked addressable findings, then re-critique",
                "ESCALATE — cap hit or backlog stalled -> stop, surface open items to the human",
            ],
        },
        {
            "type": "diagram",
            "heading": "The critique loop (rendered)",
            "image": CRITIQUE_LOOP_PNG,
            "caption": "Relevant personas critique in parallel; the aggregator triages addressable vs parked; "
                       "gates and an iteration cap guarantee the loop terminates before the human review.",
        },
        {
            "type": "table",
            "heading": "Which personas critique which phase",
            "intro": "Primary personas (score gates) vs contributing vs light-touch, per artefact.",
            "columns": ["Artefact (phase)", "Primary (gates)", "Contributing"],
            "rows": [
                ["A. Context / positioning", "CEO, Marketing, C-Suite", "CTO"],
                ["B. Dimensions / questions", "CTO, Tech Teams, Middle-Mgmt", "C-Suite"],
                ["D. Module content", "CTO, Middle-Mgmt, Tech Teams", "CEO, Marketing, C-Suite"],
                ["G. Interactive questionnaire", "Marketing, C-Suite", "CEO, Middle-Mgmt, Tech"],
                ["H. Elevator pitch", "CEO, Marketing, C-Suite", "—"],
            ],
        },
        {
            "type": "section",
            "heading": "Self-sufficiency & portability",
            "pageBreak": True,
            "body": [
                "A hard constraint: the unit of portability is the skill directory. Any skill in this feature "
                "must run after being zipped and dropped into another repo — no reach-back into analysis/, no "
                "shared repo-root modules, no absolute paths. Portability wins over DRY: if two skills need the "
                "same engine, each vendors its own copy (or they ship together as one skill-set).",
                "So a skill stops being a lone .kiro/skills/<name>.md file and becomes a bundle directory that "
                "carries everything it needs:",
            ],
            "bullets": [
                "engine/ — the vendored, self-contained render + spreadsheet + questionnaire engines",
                "templates/ — manifest, module, dimensions, and manual-TOC skeletons",
                "personas/ — the six critique rubrics",
                "assets/brand/ — default D55 logo + background (overridable per programme)",
                "examples/ai-dlc/ — a trimmed worked example (patterns, not full prose)",
                "requirements.txt — bundle-local Python deps (openpyxl, playwright, pypdf, hypothesis)",
            ],
        },
        {
            "type": "callout",
            "heading": "How we prove it",
            "body": [
                "A portability check (Property 13) copies a bundle to a temp dir outside the repo, runs it on "
                "its bundled example, and asserts nothing resolves into analysis/, the repo root, or an "
                "absolute path. Paths resolve relative to the bundle; the output location is a parameter.",
            ],
        },
        {
            "type": "table",
            "heading": "Key design decisions",
            "pageBreak": True,
            "intro": "A handful of choices shape the rest of the build.",
            "columns": ["Decision", "Choice", "Why"],
            "rows": [
                ["Source of truth", "Manifest-first (programme.yaml)", "Docs and tools render from one machine-readable spine; keeps the interactive tool in sync"],
                ["Quality mechanism", "Six-persona critique loop before the human gate", "The user reviews a refined draft; captures external client viewpoints the offering is sold into"],
                ["External thresholds", "Lower than internal (3 vs 4)", "External audiences stress credibility; holding them to 5/5 would loop forever on pilot-only fixes"],
                ["Build vs reuse", "Thin producer sub-skills over vendored engine", "programme_engine, deliverables-toolkit and summary-presentation patterns do the heavy rendering"],
                ["Modes", "Template library + client-instance clone", "Maintain one canonical programme; scope per client by scores without editing the template"],
                ["Portability over DRY", "Self-sufficient skill bundles", "Vendor engine/schema/assets/example so a skill zips and runs elsewhere with no external-folder deps"],
            ],
        },
        {
            "type": "table",
            "heading": "The manifest, at a glance",
            "intro": "programme.yaml ties every artefact together and is validated on write.",
            "columns": ["Section", "Holds", "Notes"],
            "rows": [
                ["programme", "Slug, name, one-liner, phases, commercial model", "The programme's identity and pitch"],
                ["brand", "Palette, logo, background", "Feeds BrandConfig for the render engine"],
                ["dimensions", "The radar axes (name + short + rubric ref)", "Join key: names must match module dimensions_covered"],
                ["modules", "id, title, dimensions_covered, manual_section, trigger", "Mirrors module.md frontmatter for fast consumption"],
            ],
        },
        {
            "type": "table",
            "heading": "Join-key contracts",
            "intro": "The programme is only tooling-consumable if three joins hold; a validator hard-stops the build on any violation.",
            "columns": ["Join", "Authority", "Must match"],
            "rows": [
                ["Dimension coverage", "dimensions[].name", "dimensions_covered[] in each module.md"],
                ["Manual mapping", "manual TOC section titles", "manual_section in each module.md"],
                ["Scoring", "dimensions[].name", "DimensionScore.dimension (bijection — scored once)"],
                ["Criticality", "a module's dimensions_covered", "trigger.critical_dimensions[]"],
            ],
        },
        {
            "type": "callout",
            "heading": "Testing note",
            "body": [
                "The design defines 13 correctness properties — manifest integrity, scoring bijection, "
                "recommendation monotonicity, loop termination, gate integrity, self-containment, bundle "
                "portability, and more. "
                "These drive unit tests, property-based tests (hypothesis), and rendered-output verification "
                "(measure the DOM with Playwright; read PDFs back with pypdf). Loop termination and "
                "recommendation monotonicity are the highest-value properties to prove.",
            ],
        },
        {
            "type": "table",
            "heading": "Open questions",
            "pageBreak": True,
            "intro": "Carried into requirements for confirmation.",
            "columns": ["Question", "Working assumption"],
            "rows": [
                ["First-build scope", "Ship critique-loop + manifest against AI-DLC first, then generalise the engine"],
                ["Critique cost / latency", "Cap iterations; make panel membership per-phase configurable"],
                ["Runbook spreadsheet shape", "Stages, activities, owners, inputs/outputs, decision points — confirm columns"],
                ["Interactive questionnaire hosting", "Self-contained HTML only for now; hosted/booking version later"],
                ["External programme name", "Skill prompts for it but allows deferral (AI-DLC's is still TBD)"],
            ],
        },
    ],
}
