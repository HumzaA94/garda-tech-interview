# Iteration 3 — Book an agent

Now add a second endpoint that books an agent onto a shift.

```
POST /api/shifts/{id}/assignments
Content-Type: application/json

{ "agentId": "agt_3" }
```

On success, create an assignment, save it to `data.json`, and return it:

```json
201 Created

{ "id": "asg_2", "shiftId": "shf_2", "agentId": "agt_3" }
```

## Rules

A booking is only allowed when the agent is **available for that shift** — the exact
same availability from Iteration 2 (qualified, not expired, not double-booked). Reject
the booking and change nothing when:

- the shift or agent doesn't exist → `404`;
- the agent isn't available for the shift → `422`;
- the shift is already full (its `headcount` is reached) → `409`.

Two things must hold after a successful booking:

- the new assignment is persisted in `data.json`;
- calling `GET /api/shifts/{id}/available-agents` again reflects it straight away — the
  agent you just booked no longer appears as available, and neither do agents who now
  overlap it.

## Done when

- Booking Marc onto `shf_2` succeeds and appears in `data.json`.
- Booking an unqualified or double-booked agent is rejected and writes nothing.
- Booking onto a full shift returns `409`.
- A booking made through `POST` immediately changes what `GET` returns.
