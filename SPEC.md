# Product Specification

## Problem
Users overuse expensive agentic surfaces because Chat, Scheduled Chat, Work, Codex, apps, MCP and local compute overlap.

## Product
A router that classifies the task, inspects available capabilities, selects the cheapest sufficient surface, escalates only when necessary, and returns to Chat when the specialist phase is done.

## Routes
CHAT, SCHEDULED_CHAT, LOCAL_TOOL, CODEX, WORK, EXTERNAL_API, HYBRID.

## Requirements
- evidence-based capability detection
- versioned routing policy
- compact surface handoffs
- GitHub-backed skills
- MCP/local-tool delegation
- run manifests and metrics
- safe defaults
- no claim that indirection makes paid providers free

## Success targets
- >=60% reduction in Work/Codex usage after tuning
- <10% unnecessary escalations
- >90% routing agreement on canonical fixtures
- no material quality regression
- typical handoff <5 KB
