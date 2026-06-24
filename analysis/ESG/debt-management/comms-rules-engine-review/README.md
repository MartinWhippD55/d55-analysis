# Comms-Hub Rules Engine — Design Comparison

**Date:** 2026-06-24
**Subject:** Communications-Hub rules engine (`com.esgglobal.service.communications.rule`)
**Context:** Initial implementation used a recursive Specification-pattern design; subsequent refactors collapsed it into a tree-walking evaluator. Both perspectives are valid — this document captures an even-handed comparison so the team can converge on a position without it becoming a dispute.

## Versions under comparison

| Version | Reference | Shape |
|---|---|---|
| **Initial (Specification pattern)** | `Communications-Hub` @ `203e1da` (UBT-15534) | ~35 classes in `service/communications/rule/` |
| **Refactor (tree-walking evaluator)** | `Communications-Hub` @ `origin/feature/debt/main` (HEAD is `7c523c5`) | 3 classes: `RuleEvaluator`, `RuleValidator`, `RuleEvaluation` |

Pivot commit: `c273c22 UBT-15517: replace Specification engine with a tree-walking evaluator` — 1,742 LOC deleted / 773 added, net −969.

## At-a-glance shape

| Metric | Initial spec design | Post-refactor |
|---|---|---|
| Source files in `rule/` | ~35 | 3 |
| Runtime IR | Parse `Rule` → `Specification<JsonNode>` tree, then evaluate | Walk the `JsonNode` tree directly |
| Validator strategy | `@Primary` over a stub; reuses the deserialiser to validate | Independent structural walker |
| Trace mechanism | Thread-local `LeafEvaluationCollector` + `LoggingSpecification` decorator | `RuleEvaluation` record returned from `explain()` |
| Public abstractions in `rule/` | `Specification<T>`, `PathResolver`, `RuleValidator`, `CommunicationFireDecisionStrategy` | None (concrete classes only) |
| Wire contract | Unchanged across the refactor | Unchanged |

## Cyclomatic complexity

Summing per-method CC across the runtime evaluation path:

- **Initial:** ~90–110 CC, distributed ~2.5 per class. Hotspots: `SpecificationDeserialiser.buildGroup` and `buildLeaf` (CC ≈ 7–8), `ValueCoercionService.coerce` (CC ≈ 6), `RuleBasedCommunicationFireDecisionStrategy.shouldFire` (CC ≈ 6–7).
- **Refactor:** ~85–95 CC, concentrated in two files. Hotspots: `RuleEvaluator.matchGroup` (switch, CC ≈ 6), `matchLeaf` (CC ≈ 4), `asInstant` (CC ≈ 6–7 across 4 try/catches), `RuleValidator.validateLeaf` (CC ≈ 7).

**Total CC is essentially a wash.** Neither version has a method that breaches an ESG-style ≤10/≤11 per-method budget. What differs is concentration: many small classes (avg ~2.5 CC each) vs. two larger classes (avg ~30 CC each, but every method still under budget). PMD/JaCoCo per-method gates pass on both.

## SOLID scorecard

| Principle | Initial | Refactor | Notes |
|---|---|---|---|
| **S** — Single Responsibility | Strong | Weak | Each `Specification` does one thing (~15 LOC). `RuleEvaluator` (215 LOC) conflates operator dispatch, tree walking, value coercion, and trace formatting. |
| **O** — Open/Closed | Edge | — | New leaf in the initial = new class + one `registry.put` line. Refactor = modify the `OPERATORS` map. Both *modify* — initial is closer to the textbook ideal but the edge is smaller than the spec-pattern marketing suggests. |
| **L** — Liskov Substitution | Applies | n/a | Initial exercises real polymorphism with substitutable subtypes. Refactor has no hierarchy — LSP barely applies. |
| **I** — Interface Segregation | Tiny interfaces | n/a | `Specification`, `PathResolver`, `RuleValidator`, `CommunicationFireDecisionStrategy` are all single-method. Refactor has no interfaces in the package. |
| **D** — Dependency Inversion | Strong | Weak | `CommunicationGeneratorService` → `CommunicationFireDecisionStrategy` (interface) became `CommunicationGeneratorService` → `CommunicationEventRuleService` (concrete) → `RuleEvaluator` (concrete) → `JsonPathExtractor` (concrete). Every abstraction in the path was removed. |

**Textbook reading: the initial design follows SOLID more orthodoxly, on 5/5.** The refactor only "competes" on principles that don't apply because there's no hierarchy or interface to grade.

## Where the refactor genuinely wins

1. **One mental model, one screen.** "What does `in` mean?" is one grep in `RuleEvaluator`. In the spec design it spans `InSpecification` → `AbstractArrayComparisonSpecification` → `ValueCoercionService.coerce` → `CoercedPair.compareValues`.
2. **`anyOf` arrived cheaply.** The post-refactor `anyOf` composite (one switch arm + ~10-line helper in `matchAnyOf`, plus the array-aware `JsonPathExtractor.resolvePaths`) is a non-trivial feature the spec design would have needed: new `AnyOfSpecification`, deserialiser branch, validator branch, path-resolver overhaul. Empirical evidence that extensibility-via-classes wasn't paying its rent here.
3. **Trace is returned, not stashed.** `RuleEvaluation` is a record with the leaf list; no `ThreadLocal` to mis-thread under future async work.
4. **No Spring choreography.** Stub + `@Primary` real impl, plus the strategy interface with one real impl, are gone.

## Where the initial design has a real point

1. **Type safety at runtime.** `Specification<JsonNode>` is a typed runtime tree; the refactor walks raw `JsonNode` with `node.get("op")` returning null silently. Fail-closed depends entirely on `RuleValidator` gating *before* storage. Any future caller that bypasses validation (a migration, an admin tool, a re-import) hands the evaluator unvalidated JSON.
2. **Per-operator unit tests are cleaner.** `EqualsSpecificationTest` exists in isolation; in the refactor each operator is a lambda in a `Map.entry(...)` literal, only testable through `RuleEvaluator.evaluate`. Coverage is fine — granularity isn't.
3. **`asInstant` is exception-driven control flow.** Four `try/catch (DateTimeParseException ignored)` blocks chained as type-probes. CC of 6–7, harder to read than `ValueCoercionService.tryDate`, which probes once. Small but real smell.
4. **Each operator's branching is *its own*.** In the refactor every entry in `OPERATORS` re-states `comparable(resolved, value) && …` — the helper is shared, but the responsibility leaks into every lambda. A future predicate that doesn't want that gate (regex against null, presence check with bonus condition) would diverge from the table pattern.

## A behavioural shift worth flagging

The two designs coerce values differently:

- **Initial:** the *rule value's* type drives coercion (`if (ruleValue.isBoolean()) … else if (ruleValue.isNumber()) … else textual → date|string`).
- **Refactor:** both sides are coerced to whichever common type works, in `number → date/instant → string` order. The refactor commit message calls out the date improvement (number → date → string, and date-vs-date-time of the same instant compares equal) — a deliberate semantic improvement.

Worth confirming tests pin the edge cases (e.g. rule value `"5"` against resolved `5`, boolean-from-string) so neither design's behaviour is lost silently.

## SOLID compliance vs. ease of change

The honest tension: SOLID exists as a *means*; the end is code that's easier to change. The empirical evidence on this specific engine cuts against the textbook reading:

- **35 classes to cover 14 operators + 3 composites.** The variation between leaves is one expression each (`pair.compareValues() == 0` vs `< 0` vs `> 0` …). SRP rewards isolating *responsibilities*; it punishes you when there isn't enough variation to justify the isolation. "EqualsSpecification" and "LessThanSpecification" differ by an operator — that's a parameter, not a responsibility.
- **`anyOf` cost one switch arm post-refactor.** In the spec design that's a new composite class + deserialiser branch + validator branch + LSP-careful path-resolver overhaul. The more-SOLID design would have made the harder change harder.
- **The strategy indirection was load-bearing for one impl.** `CommunicationFireDecisionStrategy` had `Default` and `RuleBased` impls — the default was effectively dead once rules shipped. DIP rewarded a future flexibility that no client was buying.

Two positions, both coherent:

- *Initial design is more SOLID-compliant by orthodox reading.*
- *Refactor argues that SOLID was over-applied for this domain because abstraction count exceeded behavioural variation.*

## Suggested middle ground

Rather than undo the refactor, two small additions close the genuine SOLID smells without bringing back 35 classes:

1. **Reintroduce `PathResolver` as an interface.** `RuleEvaluator` currently hard-depends on a concrete `JsonPathExtractor` that mixes rules-engine concerns (`resolvePaths`) with comms-data utilities (`extractContactLevelFilterCriteria`, `extractGroupReferenceNumberFromInvoiceJson`). That's a true SRP violation in `JsonPathExtractor` — modifying the comms-data side could accidentally break the engine. A two-method `PathResolver` interface with a thin impl would close that hole.
2. **Extract `OPERATORS` lambdas into named private methods.** Each operator becomes independently grep-able and unit-testable (`private static boolean opEquals(JsonNode, JsonNode)`) while the dispatch table stays a one-screen map. Recovers most of the spec design's per-operator clarity at near-zero cost.

Optionally:

3. **Have `RuleEvaluator.evaluate` defensively invoke `RuleValidator` once and throw on errors** (or assert at construction) so a future caller bypassing the storage-time validation gate doesn't silently misbehave. The validator already exists; this just plugs the only path where fail-closed semantics depend on caller discipline.

## TL;DR

- **Cyclomatic complexity:** roughly equal in total; differently distributed. Both pass per-method budgets.
- **SOLID:** initial wins clearly by textbook reading (5/5). The refactor's lost abstractions (`Specification`, `PathResolver`, `RuleValidator` interface, `CommunicationFireDecisionStrategy`) are the cost.
- **Ease of change in practice:** roughly equal for new operators; refactor slightly ahead for new composites (`anyOf` is the proof).
- **Net recommendation:** keep the refactor's shape, reintroduce one abstraction (`PathResolver` interface) to fix the genuine SRP/DIP smell at the path-extraction boundary, and consider extracting operator lambdas into named methods for testability. That's a position both sides can land on without anyone losing the argument.

## Appendix — key file references

**Initial design** (`Communications-Hub` @ `203e1da`, `src/main/java/com/esgglobal/service/communications/rule/`):

- `Specification.java` — single-method interface (`isSatisfiedBy(T)`)
- `AndSpecification.java`, `OrSpecification.java`, `NotSpecification.java` — composites
- `AbstractComparisonSpecification.java`, `AbstractArrayComparisonSpecification.java` — template-method bases
- 14 leaf classes (`EqualsSpecification`, `LessThanSpecification`, `InSpecification`, `IsNullSpecification`, …)
- `ComparisonSpecificationFactory.java` — `EnumMap<PredicateEnum, LeafFactory>` registry
- `SpecificationDeserialiser.java` — walks `Rule` DTO → `Specification<JsonNode>` tree with collected `RuleError`s
- `SpecificationDeserialiserRuleValidator.java` — `@Primary` validator delegating to the deserialiser
- `ValueCoercionService.java` — rule-value-driven coercion to `CoercedPair`
- `JsonPathResolver.java` — `PathResolver` impl via Jackson `JsonPointer`
- `LoggingSpecification.java` + `LeafEvaluationCollector.java` — thread-local trace decorator
- `RuleBasedCommunicationFireDecisionStrategy.java` — `@Primary` strategy impl

**Refactor** (`Communications-Hub` @ `origin/feature/debt/main`, `src/main/java/com/esgglobal/service/communications/rule/`):

- `RuleEvaluator.java` (~215 LOC) — `OPERATORS` dispatch table + tree walk + coercion (`compareValues`, `asNumber`, `asInstant`) + trace assembly
- `RuleValidator.java` (~100 LOC) — independent structural walker; uses `RuleEvaluator.SUPPORTED_PREDICATES` as the operator-vocabulary source of truth
- `RuleEvaluation.java` — record with nested `LeafEvaluation` record
- `util/JsonPathExtractor.java` — pre-existing utility extended with `resolvePaths(root, dotPath)` for array fan-out (`a.b[].c` semantics)
- `CommunicationEventRuleService.shouldFire(...)` — replaces the strategy; called directly from `CommunicationGeneratorService`
