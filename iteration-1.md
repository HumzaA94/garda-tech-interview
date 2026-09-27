# Iteration 1 — Who is qualified?

**Goal:** Return the agents qualified to work a given shift.

## Endpoint

```
GET /api/shifts/{id}/available-agents
```

An agent is qualified when they hold **every** qualification in the shift's
`requiredQualifications`.

## Example

```
GET /api/shifts/shf_2/available-agents
```

`shf_2` requires `GUARD_LICENSE` and `CROWD_CONTROL`, so only Marc holds both:

```json
[
  { "id": "agt_3", "name": "Marc Tremblay" }
]
```

For `shf_1` (requires only `GUARD_LICENSE`), all three agents qualify.

## Rules

- Unknown shift id → `404`.
- A shift with no `requiredQualifications` → every agent qualifies.
- The response is a JSON array — an empty array if nobody qualifies, not `404`.

## Done when

- Both seeded shifts return the correct agents.
- A missing shift returns `404`.

*When this works and is committed, move on to Iteration 2.*
