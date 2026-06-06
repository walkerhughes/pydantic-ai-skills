---
name: deploy
description: Generate a production deployment runbook for a release
disable-model-invocation: true
---

# Deploy

You are running the user-invoked deploy workflow. The user explicitly triggered
this skill; never run it on your own initiative.

Produce a deployment runbook for the requested release:

1. Confirm the release version from the user request (ask if it is missing).
2. List pre-deployment checks: tests green, changelog updated, migrations reviewed.
3. Provide the deployment steps in order.
4. Provide a rollback plan.

This is a planning skill: do not execute any commands. Output the runbook in markdown.
