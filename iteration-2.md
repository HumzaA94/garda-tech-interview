# Iteration 2 — Who is *actually* available?

Same endpoint as before:

```
GET /api/shifts/{id}/available-agents
```

Two more things are now true about who counts as available. Being qualified
(Iteration 1) is necessary but no longer sufficient.

1. **Expired qualifications don't count.** A required qualification only counts if its
   `expiresOn` is on or after the shift's `start`. Priya's `GUARD_LICENSE` expired
   2026-08-31, so she isn't available for the September shifts.
2. **No double-booking.** Exclude any agent already assigned (in `assignments`) to a
   shift whose time window **overlaps** this one. Jordan is assigned to `shf_1`
   (22:00–06:00), which overlaps `shf_2` (23:00–03:00) — so Jordan is out for `shf_2`,
   and also out of `shf_1`'s own list, since he's already on it.

## Example

```
GET /api/shifts/shf_1/available-agents
```

```json
[
  { "id": "agt_3", "name": "Marc Tremblay" }
]
```

(Jordan is already assigned; Priya's licence is expired.)

## Rules

- Two shifts overlap if one starts before the other ends. Shifts that only touch (one
  ends exactly when the next starts) do **not** overlap.
- Handle overnight shifts correctly (a 22:00→06:00 shift is 8 hours, not −16).

## Done when

- Agents with an expired required qualification are excluded.
- Agents booked on an overlapping shift are excluded.
- `shf_1` and `shf_2` both return just Marc.

*When this works and is committed, move on to Iteration 3.*
