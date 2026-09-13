# Architecture

## 1. Person-Owned Intelligence Layer

The Personal Intelligence layer is the stable system boundary around the person. AI models are interchangeable execution components.

```text
                         PERSON
                           |
                           v
                +----------------------+
                | PERSONAL INTELLIGENCE|
                |        CORE          |
                +----------+-----------+
                           |
        +------------------+------------------+
        |                  |                  |
        v                  v                  v
     Identity         Continuity         Permissions
        |                  |                  |
        +------------------+------------------+
                           |
                           v
                  RESOURCE MANAGER
                           |
                           v
                  INTELLIGENCE ROUTER
                    /       |       \
                   /        |        \
                  v         v         v
             Cloud AI    Local AI   Other AI
                   \        |        /
                    +-------+-------+
                            |
                            v
                         RESULT
                            |
                            v
                       TELEMETRY
                            |
                            v
                  CONTINUITY UPDATE
```

## 2. Core Boundaries

### Identity

Stores stable person-level information: goals, preferences, projects, relationships, permissions, and active context.

Identity must not depend on a particular model provider.

### Continuity

Provides the interface through which the system remembers, recalls, updates, and forgets information.

```python
class ContinuityStore:
    def remember(self, event): ...
    def recall(self, query): ...
    def update(self, state): ...
    def forget(self, item): ...
```

The initial implementation can be simple. Future Glyphin integration should occur through this boundary.

### Permissions

Controls what providers and tools can access. Access should be explicit, scoped, and revocable.

### Resource Manager

Tracks provider/model availability, quotas, context size, tokens when measurable, latency, failures, estimated cost, and task requirements.

### Intelligence Router

Selects an execution provider based on task requirements, availability, resource constraints, privacy requirements, and measured performance.

### Providers

Provider adapters expose a common interface without making the core dependent on one vendor.

### Telemetry

Records execution facts needed to evaluate routing, resource use, reliability, and quality.

## 3. System Relationship

Personal Intelligence is not the Wison Kernel and is not Glyphin.

```text
Personal Intelligence
        |
        +-- Continuity interface
        |
        +-- Resource orchestration
        |
        +-- Provider orchestration
        |
        +-- Security / permissions
        |
        +-- Telemetry
        |
        +-- Future Wison Kernel adapter
                    |
                    +-- Future Glyphin adapter
```

The separation is intentional. Each system should be independently testable.

## 4. First Engineering Target

PI-001 must demonstrate:

1. Receive a task.
2. Establish the task/person context.
3. Check permissions.
4. Inspect available resources/providers.
5. Route the task.
6. Execute it.
7. Record telemetry.
8. Update continuity.
9. Return the result.

The first implementation should favor deterministic interfaces and testability over feature volume.
