# Task 0.4 — Bedrock approach for the dry-run validation tool

**Decision:** roll our own **Converse API tool-use** loop inside a
`BrytReportBuilder` Lambda. Do **not** use managed Bedrock Agents (action groups
/ return-of-control) for this feature.

This note compares the two options against our actual requirements (R9 dry-run
validation, R10 data isolation, R12 prompt-injection defence, R4/R8 shared
Report_Design editing), cites the AWS docs, and records the rationale.

> _Content from AWS documentation below is paraphrased for compliance with
> licensing restrictions; follow the linked sources for exact wording._

---

## What the "dry-run validation tool" actually is

Per **R9.4** the Assistant must validate the generated query with a dry-run tool
before anything executes, and per **R9.9** that dry-run must return within 30s or
execution is blocked. The natural implementation of the dry-run itself is Athena
[`EXPLAIN`](https://docs.aws.amazon.com/athena/latest/ug/athena-explain-statement.html):
it validates the SQL and resolves table metadata **without scanning data**, and
Athena does not charge for `EXPLAIN` queries (Glue metadata calls may still count
against the Glue free tier). That makes it a cheap, side-effect-free syntax +
catalog check — exactly what a pre-execution "tool" should do.

So the real question in Task 0.4 is **not** "how do we dry-run" (that's Athena
`EXPLAIN`, decided) — it is **how the model is given access to that tool**:
managed Bedrock Agents, or our own Converse tool-use loop.

Note also this is not the only tool. Under **R4/R8** the Assistant reads and
writes the same Report_Design the canvas edits, so it needs
design-mutation tools (add table, add/remove column, add join, set filter/sort)
plus the validate tool. Whatever mechanism we pick has to carry all of them.

---

## Option A — Managed Bedrock Agents (action groups / return-of-control)

A managed orchestration service. You define an agent with instructions and
**action groups**; each action group is backed either by a Lambda executor or by
**return of control (RoC)**, where the agent hands the elicited action + params
back to your application instead of invoking a Lambda
([return of control docs](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-returncontrol.html),
[handle fulfillment](https://docs.aws.amazon.com/bedrock/latest/userguide/action-handle.html)).
With RoC, `InvokeAgent` returns the parameters in a `returnControl` field with an
`invocationId`; your app runs the logic and returns results in the `SessionState`
of the next `InvokeAgent` call
([InvokeAgent API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_InvokeAgent.html)).

What you get: managed prompt orchestration, managed session state/memory, and
built-in traces. What it costs us:

- **An AWS-managed orchestration prompt sits between us and the model.** For a
  security-critical flow (R12 prompt-injection defence, R10.7 "filter derived
  only from Trusted_Context") we want to own exactly what the model sees and
  precisely where the trusted bryt-number context is injected. The managed
  orchestration layer is harder to fully audit and constrain.
- **Managed session state duplicates our own store.** We already require a
  `Conversation_Store` in DynamoDB scoped to Bryt_Number (R14.2–R14.3). The
  agent's own session memory would compete with, not complement, that.
- **More moving parts.** Agent + action groups + versions + aliases, each with a
  prepare/deploy lifecycle and extra CDK, on top of the Lambda we'd write anyway.
- **RoC's headline benefit is moot for us.** RoC exists so you can skip Lambda
  executors and run the logic in your app — but Converse tool-use already runs
  the loop in our app *natively and more simply*. We'd be adding the agent
  scaffolding to get back to where Converse starts.

## Option B — Roll our own Converse API tool-use (recommended)

The [Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
is one message-based interface that works across all message-capable Bedrock
models; you swap `modelId` without rewriting the call. Tools are declared in the
[`toolConfig`](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ToolConfiguration.html)
parameter as an array of tool specs (name, description, JSON-schema input), and
[`toolChoice`](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-inference-call.html)
can force a specific tool. The loop is: model returns a `toolUse` request → our
code executes the tool → we return a `toolResult` in the next message → repeat
([tool use overview](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html),
[tool-use examples](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-examples.html)).
Calling `Converse` needs `bedrock:InvokeModel`
([using the Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference-call.html)).

Why it fits this feature:

- **We own the loop end-to-end.** Trusted_Context (Authorised_Bryt_Numbers) is
  injected by our Lambda, never surfaced to the model as something it can rewrite
  (R10.4, R10.7, R12.2). Every tool call — including ignored injection attempts —
  is ours to audit-log (R12.4).
- **Statelessness matches our persistence.** Converse holds no server-side
  session; we pass message history from our own `Conversation_Store` each turn,
  which is exactly the Bryt_Number-scoped store we already need (R14).
- **The independent verifier stays outside the model.** The `Query_Verifier`
  (R11, R12.5–R12.6) runs as ordinary backend code in our Step Functions pipeline,
  wholly independent of whatever the model emits — no managed agent in the path.
- **`toolChoice` gives us the R9.4 guarantee.** At finalisation we can force the
  validate tool so the model cannot skip the dry-run before we hand off to
  execution; our own code enforces the R9.9 30s timeout around the `EXPLAIN`.
- **Fewer moving parts, same pattern.** It's one API call inside a normal
  TypeScript Lambda — the established BrytBusinessServices pattern (R17) — with no
  agent/alias/version lifecycle to manage.
- **Model portability.** Assume Claude on Bedrock, but Converse lets us change
  `modelId` later without reworking the integration.

---

## Recommendation

Use **Converse API tool-use**. Implement the Assistant (Task 3.1) as a Converse
loop in a `BrytReportBuilder` Lambda with a `toolConfig` exposing:

1. **Report_Design mutation tools** — add/remove table, add/remove column, add
   join (Join_Manifest predicates only), set filter, set sort — operating on the
   shared model (R4, R8).
2. **`validate_query`** — generates Athena SQL from the current Report_Design and
   runs `EXPLAIN` against the workgroup, forced via `toolChoice` before
   finalisation, with a 30s timeout (R9.4, R9.9).

Trusted_Context (Authorised_Bryt_Numbers, selected Bryt_Number, Join_Manifest) is
assembled server-side and injected into the system prompt / tool inputs by the
Lambda — never taken from model output or user prompt (R10.4, R10.7). The
`Query_Verifier` remains an independent backend step, not a model tool (R11, R12.5).

### When we would revisit Agents

If the roadmap later needs managed multi-step orchestration, built-in Knowledge
Base/RAG grounding, or managed long-term memory across many tools, managed
orchestration becomes more attractive. In that case the current, more mature
landing spot would be **Amazon Bedrock AgentCore** — a managed agent harness
(orchestration loop, tool execution, memory, identity, observability) that you
drive from config
([AgentCore harness vs. runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-vs-runtime.html))
— rather than the original Agents action-group model. None of that is needed for
the tightly-scoped, security-critical single validate tool this feature requires,
so it stays out of scope for now.

---

## Sources

- Athena `EXPLAIN` (validate, no data scan, not charged): <https://docs.aws.amazon.com/athena/latest/ug/athena-explain-statement.html>
- Converse API inference: <https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html>
- Using the Converse API (permissions): <https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference-call.html>
- Tool use (function calling) overview: <https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html>
- Call a tool with the Converse API (`toolConfig`, `toolChoice`): <https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-inference-call.html>
- `ToolConfiguration` API reference: <https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ToolConfiguration.html>
- Converse tool-use examples: <https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-examples.html>
- Bedrock Agents return of control: <https://docs.aws.amazon.com/bedrock/latest/userguide/agents-returncontrol.html>
- Handle fulfillment of the action (Lambda vs RoC): <https://docs.aws.amazon.com/bedrock/latest/userguide/action-handle.html>
- `InvokeAgent` (`returnControl` field): <https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_InvokeAgent.html>
- Bedrock AgentCore harness vs. runtime: <https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-vs-runtime.html>
