"""Tests for estimate parsing/classification/weighting (pure core)."""
import pytest

from engine.estimates import classify_task, parse_tasks_text, summarize, DEFAULT_WEIGHTS


@pytest.mark.parametrize("text,category", [
    ("Add a checkpoint review", "checkpoint"),
    ("Write property test for X", "testing"),
    ("Add integration test suite", "testing"),
    ("Provision CDK stack and IAM trust policy", "infrastructure"),
    ("Build the Angular component", "frontend"),
    ("Prompt iteration cycle for the model", "prompt_iteration"),
    ("Add navigation entry wiring", "integration"),
    ("Implement the REST handler", "api_backend"),
])
def test_classify_task(text, category):
    assert classify_task(text) == category


SAMPLE = """
# Tasks

- [ ] 1. Parent task
  - [ ] 1.1 Provision CDK stack
  - [ ] 1.2 Build the Angular component
  - [ ]* 1.3 Write property test for it
- [ ] 2. Another parent
  - [ ] 2.1 Implement the REST handler
"""


def test_parse_tasks_text_counts_and_optional():
    tasks = parse_tasks_text(SAMPLE, "Est 1")
    assert len(tasks) == 4
    ids = [t["task_id"] for t in tasks]
    assert ids == ["1.1", "1.2", "1.3", "2.1"]
    optional = [t for t in tasks if t["optional"]]
    assert len(optional) == 1 and optional[0]["task_id"] == "1.3"


def test_summarize_uses_default_weights():
    tasks = parse_tasks_text(SAMPLE, "Est 1")
    s = summarize(tasks)
    # 1.1 infra 1.0 + 1.2 frontend 0.75 + 2.1 api 0.5 = 2.25 required; 1.3 testing 0.5 optional
    assert s["required_days"] == 2.25
    assert s["optional_days"] == 0.5
    assert s["total_days"] == 2.75
    assert s["total_tasks"] == 4


def test_weights_override():
    tasks = parse_tasks_text(SAMPLE, "Est 1", weights={**DEFAULT_WEIGHTS, "frontend": 2.0})
    frontend = [t for t in tasks if t["category"] == "frontend"][0]
    assert frontend["days"] == 2.0


def test_non_task_lines_ignored():
    assert parse_tasks_text("just prose\n# heading\n", "Est 1") == []
