# New Programme Skill — Orchestration Diagrams

The end-to-end flow is decomposed into a **high-level overview** (four stages and how they connect) plus a **per-stage detail** diagram for each. This keeps every diagram page-friendly and readable, instead of one very tall chart.

Rendered PNGs (mermaid.js + Playwright) sit alongside this file. Regenerate by serving `_render-diagrams.html` and screenshotting each SVG (see session notes).

Key structure over the original sketch:

- **Named stages (1–4)** grouping the nine phases (A–I).
- **A six-persona critique panel** runs before each human gate within stages 1–3.
- **Human "Happy?" gates** kept distinct from the autonomous critique loop.
- **A manifest** (`programme.yaml`) introduced at scaffold time as the single source of truth.

## Overview — how the stages interact

![Overview stage flow](diagram-overview.png)

```mermaid
flowchart LR
    S([Start]) --> M{Mode:<br/>template or client-instance}
    M --> S1[Stage 1<br/>Scope & Frame<br/>Phases A-B]
    S1 --> S2[Stage 2<br/>Build Modules<br/>Phases C-D]
    S2 --> S3[Stage 3<br/>Generate Assets<br/>Phases E-H]
    S3 --> S4[Stage 4<br/>Verify & Ship<br/>Phase I]
    S4 --> D([Programme ready])
    S1 -. critique + human gate .-> S1
    S2 -. critique + human gate .-> S2
    S3 -. critique + human gate .-> S3
```

## Stage 1 — Scope & Frame (Phases A–B)

![Stage 1 - Scope and Frame](diagram-s1-scope.png)

```mermaid
flowchart TD
    A[Phase A - Context<br/>positioning, ICP, phases, commercial model] --> CA[[Critique: CEO, Marketing, C-Suite]]
    CA --> GA{User gate: Happy?}
    GA -->|No| A
    GA -->|Yes| B[Phase B - Dimensions<br/>rubrics, scoring, questions]
    B --> CB[[Critique: CTO, Tech Teams, Middle-Mgmt]]
    CB --> GB{User gate: Happy?}
    GB -->|No| B
    GB -->|Yes| N([To Stage 2])
```

## Stage 2 — Build Modules (Phases C–D)

![Stage 2 - Build Modules](diagram-s2-modules.png)

```mermaid
flowchart TD
    C[Phase C - Scaffold modules + manifest] --> V[Validate join keys<br/>dimensions - manual TOC]
    V --> L[/For each in-scope module/]
    L --> D[Phase D - Author module.md]
    D --> CD[[Critique: role-weighted personas]]
    CD --> GD{User gate: Happy?}
    GD -->|No| D
    GD -->|Yes| More{More modules?}
    More -->|Yes| L
    More -->|No| N([To Stage 3])
```

## Stage 3 — Generate Assets (Phases E–H)

![Stage 3 - Generate Assets](diagram-s3-assets.png)

```mermaid
flowchart TD
    E[Phase E - Per-module assets<br/>HTML + PDF + starter templates] --> F[Phase F - Spreadsheets<br/>internal runbook + questionnaire]
    F --> G[Phase G - Interactive questionnaire<br/>radar chart + recommended modules]
    G --> H[Phase H - Elevator-pitch deck]
    H --> CH[[Critique: Marketing, CEO, C-Suite]]
    CH --> N([To Stage 4])
```

## Stage 4 — Verify & Ship (Phase I)

![Stage 4 - Verify and Ship](diagram-s4-verify.png)

```mermaid
flowchart TD
    I[Phase I - Verify all outputs<br/>DOM + PDF + xlsx checks] --> Q{All checks pass?}
    Q -->|No| Fix[Fix + regenerate affected]
    Fix --> I
    Q -->|Yes| Done([Programme ready])
```

## The critique loop (detail)

Runs inside stages 1–3 before each human gate.

![Critique loop](diagram-critique-loop.png)

```mermaid
flowchart LR
    Draft[Artefact draft] --> Fan{Fan out to relevant personas}
    Fan --> P1[CEO - Jonathan]
    Fan --> P2[CTO - Rhys]
    Fan --> P3[Marketing]
    Fan --> P4[Client C-Suite]
    Fan --> P5[Middle-Mgmt]
    Fan --> P6[Tech Teams]
    P1 --> Agg[Aggregate scores + triage addressable vs parked]
    P2 --> Agg
    P3 --> Agg
    P4 --> Agg
    P5 --> Agg
    P6 --> Agg
    Agg --> Gate{Gate met? or max iterations?}
    Gate -->|No - addressable| Fix2[Apply addressable fixes]
    Fix2 --> Draft
    Gate -->|Yes| Park[Log parked items] --> Out[Refined artefact -> human gate]
```
