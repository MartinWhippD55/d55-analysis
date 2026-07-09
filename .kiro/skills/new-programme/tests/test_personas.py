"""Tests for persona rubrics, the relevance matrix, and the critic contract (Task 7)."""
from __future__ import annotations

from engine.critique import PRIMARY_PERSONAS, RELEVANCE_MATRIX, personas_for, primary_thresholds
from engine.models import Persona
from engine.personas import ALL_PERSONAS, PERSONA_META, CriticInput, load_rubric

SIX = {
    "d55_ceo", "d55_cto", "d55_marketing",
    "client_csuite", "client_middle_mgmt", "client_technical",
}


def test_all_six_personas_have_metadata():
    assert set(ALL_PERSONAS) == SIX
    for p in ALL_PERSONAS:
        assert PERSONA_META[p]["name"]
        assert PERSONA_META[p]["lens"]
        assert PERSONA_META[p]["cares"]


def test_every_persona_rubric_file_loads_and_names_itself():
    for p in ALL_PERSONAS:
        text = load_rubric(p)
        assert f"`{p}`" in text                     # rubric declares its persona id
        assert "Scoring rubric" in text
        assert "Addressable vs parked" in text


def test_relevance_matrix_covers_all_phases_and_personas():
    for phase, levels in RELEVANCE_MATRIX.items():
        assert set(levels.keys()) == SIX
        assert all(v in {"primary", "contributing", "light"} for v in levels.values())


def test_primary_personas_derived_from_matrix():
    for phase, levels in RELEVANCE_MATRIX.items():
        expected = tuple(p for p, lvl in levels.items() if lvl == "primary")
        assert PRIMARY_PERSONAS[phase] == expected
        # Every phase must have at least one gating persona.
        assert expected


def test_personas_for_excludes_light_by_default():
    for phase, levels in RELEVANCE_MATRIX.items():
        got = set(personas_for(phase))
        expected = {p for p, lvl in levels.items() if lvl in {"primary", "contributing"}}
        assert got == expected
        # Primary personas are always included among the critics to invoke.
        assert set(PRIMARY_PERSONAS[phase]).issubset(got)


def test_thresholds_internal_four_external_three():
    for phase in RELEVANCE_MATRIX:
        for persona, threshold in primary_thresholds(phase).items():
            internal = persona in {"d55_ceo", "d55_cto", "d55_marketing"}
            assert threshold == (4 if internal else 3)


def test_critic_input_build_loads_rubric():
    ci = CriticInput.build(
        persona="d55_cto",
        phase="D",
        artefact_paths=["modules/module-1-x/module.md"],
        programme_context="AI-DLC: assess to scale.",
    )
    assert ci.persona == "d55_cto"
    assert "`d55_cto`" in ci.rubric
    assert "addressable" in ci.scoring_guidance.lower()
