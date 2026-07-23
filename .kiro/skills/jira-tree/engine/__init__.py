"""jira-tree engine: render a spec-to-stories Jira plan as an editable markdown
tree (epic / stories / sub-tasks / links), parse it back, and validate it. The
tree is the human-review surface between `jira-plan.json` and live Jira; the agent
pushes it to Jira via the Atlassian MCP. This engine never touches Jira."""
