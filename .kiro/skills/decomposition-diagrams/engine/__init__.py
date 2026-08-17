"""decomposition-diagrams engine.

Pure, testable helpers for turning a decomposition ``graph.yaml`` into per-story and
epic architecture diagrams (mermaid), plus the US-xx -> Jira-key rewrite used when
enriching issue descriptions. Rendering (mermaid -> PNG) is the only part that touches
the network / a browser and lives in ``render.py``.
"""
