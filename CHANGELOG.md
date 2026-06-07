# Changelog

## [Unreleased]

### Added
- Support for the `disable-model-invocation: true` SKILL.md frontmatter key: hides a skill from the system-prompt advertisement and `list_skills` while keeping it loadable via `load_skill` and accessible via `toolset.get_skill()` for application-driven (user-invoked) workflows (#PR_NUMBER)
