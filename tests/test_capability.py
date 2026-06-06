"""Tests for SkillsCapability."""

from __future__ import annotations

from pathlib import Path

import pytest

from pydantic_ai_skills import SkillsCapability, SkillsToolset


def test_skills_capability_get_toolset() -> None:
    """SkillsCapability should expose a SkillsToolset."""
    capability = SkillsCapability(skills=[], directories=[])
    toolset = capability.get_toolset()

    assert isinstance(toolset, SkillsToolset)
    assert capability.toolset is toolset


def test_skills_capability_init_with_minimal_params() -> None:
    """Constructor should work with only skills parameter."""
    capability = SkillsCapability(skills=[])
    assert isinstance(capability.get_toolset(), SkillsToolset)


def test_skills_capability_init_with_directories() -> None:
    """Constructor should accept directories parameter."""
    capability = SkillsCapability(directories=['./skills'])
    assert isinstance(capability.get_toolset(), SkillsToolset)


def test_skills_capability_init_with_all_params(tmp_path: Path) -> None:
    """Constructor should accept all parameters."""
    skills_dir = tmp_path / 'skills'
    skills_dir.mkdir()

    capability = SkillsCapability(
        skills=[],
        directories=[skills_dir],
        registries=[],
        validate=False,
        max_depth=5,
        id='test-toolset',
        instruction_template='Available skills: {skills_list}',
        exclude_tools={'run_skill_script'},
        auto_reload=True,
    )
    assert isinstance(capability.get_toolset(), SkillsToolset)
    toolset = capability.toolset
    assert toolset.id == 'test-toolset'


def test_skills_capability_toolset_property_is_same_as_get_toolset() -> None:
    """Toolset property should be the same instance as get_toolset()."""
    capability = SkillsCapability(skills=[])
    toolset_property = capability.toolset
    get_toolset_result = capability.get_toolset()
    assert toolset_property is get_toolset_result


def test_skills_capability_with_exclude_tools_as_list() -> None:
    """Constructor should accept exclude_tools as a list."""
    capability = SkillsCapability(
        skills=[],
        exclude_tools=['load_skill', 'run_skill_script'],
    )
    assert isinstance(capability.get_toolset(), SkillsToolset)


def test_skills_capability_init_with_custom_template() -> None:
    """Constructor should accept custom instruction template."""
    template = 'Use these skills: {skills_list}'
    capability = SkillsCapability(
        skills=[],
        instruction_template=template,
    )
    assert isinstance(capability.get_toolset(), SkillsToolset)


@pytest.mark.asyncio
async def test_skills_capability_get_instructions_returns_none() -> None:
    """get_instructions returns None — agent extracts instructions natively from the toolset."""
    capability = SkillsCapability(skills=[])
    assert capability.get_instructions() is None


@pytest.mark.asyncio
async def test_skills_capability_toolset_excludes_disabled_from_instructions() -> None:
    """Capability delegates to the toolset, so disable_model_invocation parity is automatic."""
    from unittest.mock import Mock

    from pydantic_ai_skills import Skill

    hidden = Skill(
        name='hidden-skill',
        description='A hidden skill',
        content='Hidden instructions',
        disable_model_invocation=True,
    )
    capability = SkillsCapability(skills=[hidden])

    assert await capability.toolset.get_instructions(Mock()) is None
    assert capability.toolset.get_skill('hidden-skill').content == 'Hidden instructions'
