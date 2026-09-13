# Weisone Personal Intelligence

Personal Intelligence infrastructure for a person-owned continuity layer that coordinates multiple AI models, tools, and local intelligence systems.

## Core Principle

> The person owns the continuity. The models are replaceable components.

This project is intended to separate personal identity, continuity, permissions, resource management, and orchestration from any single AI provider.

## v0.1 Objective

Prove the core loop:

```text
Task
  -> Identity
  -> Permission Check
  -> Resource Check
  -> Intelligence Router
  -> Provider / Local Model
  -> Result
  -> Telemetry
  -> Continuity Update
```

## Initial Components

- Identity & continuity
- Permission boundary
- Resource manager
- Intelligence router
- Provider adapters
- Local-model adapters
- Telemetry
- Tests

## Security

This repository is currently public. Do not commit API keys, credentials, personal data, private research, proprietary kernel code, or other secrets.

## Relationship to Weisone R&D

Personal Intelligence is an infrastructure layer. Wison Kernel and Glyphin remain separate systems and should integrate through explicit interfaces rather than being collapsed into this project.
