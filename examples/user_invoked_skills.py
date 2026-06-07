"""Example of user-invoked skills hidden from the model via `disable-model-invocation`.

A skill with `disable-model-invocation: true` in its SKILL.md frontmatter (see
`skills-user-invoked/deploy/SKILL.md`) is excluded from the agent's system prompt
and the `list_skills` tool, but stays fully usable when the application invokes it
explicitly — the slash-command pattern used by tools like Claude Code.

Run from the repo root:

    python -m examples.user_invoked_skills

Then try:

    > what skills do you have available?   # the deploy skill is not advertised
    > /deploy v1.2.3                       # the app injects the hidden skill's content
"""

import asyncio
from pathlib import Path

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent

from pydantic_ai_skills import SkillsToolset

load_dotenv()

logfire.configure()
logfire.instrument_pydantic_ai()

# Load the regular (visible) skills alongside the hidden deploy skill
script_dir = Path(__file__).parent
skills_toolset = SkillsToolset(directories=[script_dir / 'skills', script_dir / 'skills-user-invoked'])

# Swap to model='openai:gpt-5.2' (with OPENAI_API_KEY set) if you are not using the gateway
agent = Agent(
    model='gateway/openai:gpt-5.2',
    instructions='You are a helpful research assistant.',
    toolsets=[skills_toolset],
)


def show_skill_visibility() -> None:
    """Print which skills the model sees vs. what the application can access."""
    visible = sorted(name for name, skill in skills_toolset.skills.items() if not skill.disable_model_invocation)
    hidden = sorted(name for name, skill in skills_toolset.skills.items() if skill.disable_model_invocation)
    print(f'Skills advertised to the model: {", ".join(visible)}')
    print(f'Hidden (user-invoked only):     {", ".join(hidden)}')


async def handle_user_input(user_input: str) -> str:
    """Dispatch slash commands to hidden skills; everything else goes straight to the agent."""
    if user_input.startswith('/'):
        command, _, args = user_input[1:].partition(' ')
        try:
            skill = skills_toolset.get_skill(command)  # works even though hidden from the model
        except KeyError:
            return f"Unknown command '/{command}'. Available: " + ', '.join(sorted(skills_toolset.skills))
        prompt = f'<skill name="{skill.name}">\n{skill.content}\n</skill>\n\nUser request: {args or "(none)"}'
    else:
        prompt = user_input
    result = await agent.run(prompt)
    return result.output


async def main() -> None:
    """Run an interactive loop demonstrating the slash-command pattern."""
    show_skill_visibility()
    print("\nType a question, or '/deploy <version>' to invoke the hidden skill. Empty line to exit.\n")
    while True:
        try:
            user_input = input('> ').strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input:
            break
        print(await handle_user_input(user_input))
        print()


if __name__ == '__main__':
    asyncio.run(main())
