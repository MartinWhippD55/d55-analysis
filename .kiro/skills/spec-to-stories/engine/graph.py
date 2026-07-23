"""
Dependency graph construction, validation, topological sort and wave layering
for spec-to-stories.

Model recap: each Story `exports` components and `depends_on` components. An
edge `src --depends-on--> dst` means story `src` needs a component that story
`dst` exports, so `dst` must be implemented before `src`.

Everything here is deterministic: results are stably ordered by story id so the
same input always yields the same decomposition (Property: determinism).
"""
from __future__ import annotations

from collections import defaultdict

from .models import Decomposition, Edge, Issue, Story


def build_component_index(stories: list[Story]) -> tuple[dict[str, list[str]], list[Issue]]:
    """Map each exported component ref -> list of story ids that export it.

    A well-formed decomposition has exactly one exporter per component; more
    than one is reported as a `duplicate-exporter` issue.
    """
    index: dict[str, list[str]] = defaultdict(list)
    for story in stories:
        for comp in story.exports:
            index[comp.ref].append(story.id)

    issues: list[Issue] = []
    for ref, owners in sorted(index.items()):
        if len(owners) > 1:
            issues.append(
                Issue(
                    kind="duplicate-exporter",
                    detail=f"Component {ref} is exported by {len(owners)} stories: {', '.join(sorted(owners))}",
                    stories=sorted(owners),
                    components=[ref],
                )
            )
    return dict(index), issues


def resolve_edges(
    stories: list[Story], index: dict[str, list[str]]
) -> tuple[list[Edge], list[Issue]]:
    """Turn each story's dependencies into edges to the exporting story.

    Dependencies with no exporter are reported as `dangling-dependency`.
    A story depending on a component it exports itself is a `self-dependency`.
    Edges to the same target story are merged (collecting the `via` components).
    """
    issues: list[Issue] = []
    # (src, dst) -> set of component refs
    merged: dict[tuple[str, str], set[str]] = defaultdict(set)

    for story in sorted(stories, key=lambda s: s.id):
        for comp in sorted(story.depends_on, key=lambda c: c.ref):
            owners = index.get(comp.ref, [])
            if not owners:
                issues.append(
                    Issue(
                        kind="dangling-dependency",
                        detail=f"Story {story.id} depends on {comp.ref} which no story exports",
                        stories=[story.id],
                        components=[comp.ref],
                    )
                )
                continue
            for owner in owners:
                if owner == story.id:
                    issues.append(
                        Issue(
                            kind="self-dependency",
                            detail=f"Story {story.id} depends on {comp.ref} which it also exports",
                            stories=[story.id],
                            components=[comp.ref],
                        )
                    )
                    continue
                merged[(story.id, owner)].add(comp.ref)

    edges = [
        Edge(src=src, dst=dst, via=sorted(via))
        for (src, dst), via in sorted(merged.items())
    ]
    return edges, issues


def detect_cycles(story_ids: list[str], edges: list[Edge]) -> list[list[str]]:
    """Return a list of cycles (each a list of story ids) in the dependency
    graph. Uses iterative DFS colouring; deterministic by sorting adjacency."""
    adj: dict[str, list[str]] = {sid: [] for sid in story_ids}
    for e in edges:
        adj.setdefault(e.src, []).append(e.dst)
        adj.setdefault(e.dst, adj.get(e.dst, []))
    for sid in adj:
        adj[sid].sort()

    WHITE, GREY, BLACK = 0, 1, 2
    colour = {sid: WHITE for sid in adj}
    cycles: list[list[str]] = []

    def visit(start: str) -> None:
        stack: list[tuple[str, int]] = [(start, 0)]
        path: list[str] = []
        while stack:
            node, i = stack.pop()
            if i == 0:
                if colour[node] == BLACK:
                    continue
                colour[node] = GREY
                path.append(node)
            if i < len(adj[node]):
                stack.append((node, i + 1))
                nxt = adj[node][i]
                if colour.get(nxt, WHITE) == GREY:
                    # found a back-edge: extract the cycle from the path
                    if nxt in path:
                        cyc = path[path.index(nxt):] + [nxt]
                        cycles.append(cyc)
                elif colour.get(nxt, WHITE) == WHITE:
                    stack.append((nxt, 0))
            else:
                colour[node] = BLACK
                if path and path[-1] == node:
                    path.pop()

    for sid in sorted(adj):
        if colour[sid] == WHITE:
            visit(sid)
    return cycles


def topological_order(story_ids: list[str], edges: list[Edge]) -> list[str]:
    """Kahn's algorithm. Returns a linear order where every dependency `dst`
    precedes the story `src` that depends on it. Ties are broken by story id
    for determinism. Raises ValueError if the graph has a cycle."""
    ids = sorted(set(story_ids))
    # indegree counts an edge src->dst as: src needs dst first, so dst -> src
    # in implementation order. We want dst before src, so treat dst as prereq.
    prereqs_done: dict[str, int] = {sid: 0 for sid in ids}
    dependents: dict[str, list[str]] = defaultdict(list)
    remaining_deps: dict[str, set[str]] = defaultdict(set)

    for e in edges:
        # src depends on dst
        remaining_deps[e.src].add(e.dst)
        dependents[e.dst].append(e.src)

    ready = sorted(sid for sid in ids if not remaining_deps.get(sid))
    order: list[str] = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for dep in sorted(dependents.get(node, [])):
            remaining_deps[dep].discard(node)
            if not remaining_deps[dep]:
                # insert keeping the ready list sorted
                ready.append(dep)
                ready.sort()
    if len(order) != len(ids):
        raise ValueError("Cannot topologically sort: dependency cycle present")
    return order


def partition_waves(story_ids: list[str], edges: list[Edge]) -> list[list[str]]:
    """Layer stories into waves. A story's wave is 1 + the max wave of the
    stories it depends on (longest-path layering). Stories in the same wave
    have no dependency between them and may be built in parallel.

    Assumes an acyclic graph (call detect_cycles first)."""
    order = topological_order(story_ids, edges)
    deps: dict[str, set[str]] = defaultdict(set)
    for e in edges:
        deps[e.src].add(e.dst)

    wave_of: dict[str, int] = {}
    for sid in order:  # order guarantees deps computed first
        d = deps.get(sid) or ()
        wave_of[sid] = 1 + max((wave_of[x] for x in d), default=0)

    max_wave = max(wave_of.values(), default=0)
    waves: list[list[str]] = []
    for w in range(1, max_wave + 1):
        members = sorted(sid for sid, wv in wave_of.items() if wv == w)
        waves.append(members)
    return waves


def check_requirement_coverage(
    stories: list[Story], all_requirement_ids: list[str]
) -> list[Issue]:
    """Report parent-spec requirements not covered by any story (warning-level)."""
    covered: set[str] = set()
    for s in stories:
        covered.update(str(r) for r in s.covers_requirements)
    issues: list[Issue] = []
    for req in all_requirement_ids:
        if str(req) not in covered:
            issues.append(
                Issue(
                    kind="uncovered-requirement",
                    detail=f"Requirement {req} is not covered by any story",
                    components=[],
                )
            )
    return issues


def build_decomposition(
    parent_spec: str,
    stories: list[Story],
    all_requirement_ids: list[str] | None = None,
) -> Decomposition:
    """Full pipeline: index -> edges -> cycle check -> waves -> coverage.

    Always returns a Decomposition; blocking problems are captured as issues
    and (for cycles) waves are left empty. Use `.ok` to gate downstream steps.
    """
    index, dup_issues = build_component_index(stories)
    edges, edge_issues = resolve_edges(stories, index)
    issues: list[Issue] = [*dup_issues, *edge_issues]

    story_ids = [s.id for s in stories]
    cycles = detect_cycles(story_ids, edges)
    for cyc in cycles:
        issues.append(
            Issue(
                kind="cycle",
                detail="Dependency cycle: " + " -> ".join(cyc),
                stories=cyc,
            )
        )

    waves: list[list[str]] = []
    if not cycles:
        waves = partition_waves(story_ids, edges)

    if all_requirement_ids:
        issues.extend(check_requirement_coverage(stories, all_requirement_ids))

    return Decomposition(
        parent_spec=parent_spec,
        stories=stories,
        edges=edges,
        waves=waves,
        issues=issues,
    )
