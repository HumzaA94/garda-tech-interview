# Submission — Shift Scheduling API

A small Flask REST API for booking security agents onto shifts, built in three iterations
against the sample `data.json`.

| Endpoint | What it does |
| --- | --- |
| `GET /api/shifts/{id}/available-agents` | Agents who can work the shift (qualified, not expired, not double-booked) |
| `POST /api/shifts/{id}/assignments` | Books an agent onto the shift and saves it to `data.json` |
| `GET /health` | Health check |

## Running it

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

flask --app shift_scheduling run --port 5000
```

The app loads `data.json` from the repo root at startup. Bookings write back to that file, so
to keep the sample data clean, point it at a copy:

```bash
cp data.json /tmp/data.json
DATA_PATH=/tmp/data.json flask --app shift_scheduling run --port 5000
```

### Trying the endpoints

```bash
# Who can work shf_2?  → [{"id": "agt_3", "name": "Marc Tremblay"}]
curl http://127.0.0.1:5001/api/shifts/shf_2/available-agents

# Book Marc onto shf_2  → 201 {"id": "asg_2", "shiftId": "shf_2", "agentId": "agt_3"}
curl -i -X POST http://127.0.0.1:5001/api/shifts/shf_2/assignments \
  -H "Content-Type: application/json" -d '{"agentId": "agt_3"}'

# shf_2 is now full  → 409 {"error": "shift is full"}
curl -i -X POST http://127.0.0.1:5001/api/shifts/shf_2/assignments \
  -H "Content-Type: application/json" -d '{"agentId": "agt_1"}'
```

## Testing

```bash
pytest -v
pre-commit run --all-files
```

CI (GitHub Actions) runs pre-commit (ruff lint and format) and the test suite on Python
3.11, 3.12 and 3.13 for every PR and every push to `main`.

Tests never touch the real `data.json`: fixtures copy it to a temporary directory, and
tests needing custom data build it with factory_boy factories and write it to `tmp_path`.

## Commit history

Each iteration was done on its own branch and merged by PR, in order:

| Iteration | PR |
| --- | --- |
| 0 — project scaffold, CI, health check | [#1](https://github.com/HumzaA94/garda-tech-interview/pull/1) |
| 1 — who is qualified? | [#2](https://github.com/HumzaA94/garda-tech-interview/pull/2) |
| 2 — who is actually available? | [#3](https://github.com/HumzaA94/garda-tech-interview/pull/3) |
| 3 — book an agent | [#4](https://github.com/HumzaA94/garda-tech-interview/pull/4) |

## How it's structured

```
shift_scheduling/
  routes/      HTTP only: parse the request, call a service, shape the response
  services/    business rules
    availability.py   the availability rules (qualification, expiry, double-booking)
    shifts.py         listing available agents, booking
    agents.py         agent lookup
  models/      dataclasses for data.json records, with from_dict / to_dict
  storage.py   loads data.json at startup, writes it back after a booking
  errors.py    domain errors (404/409/422/400) rendered as {"error": "..."}
  factories/   factory_boy factories used by the tests
```

Routes stay thin; services raise domain errors such as `NotFoundError` rather than building
HTTP responses, and one central handler turns every error into the same JSON shape.

### Availability rules

Each check is a `Rule` with a readable reason, collected in one list:

```python
RULES = [
    Rule("missing or expired qualification", ...),
    Rule("already booked on an overlapping shift", ...),
]
```

`unavailability_reasons(storage, agent, shift)` returns the reason for every failed rule;
`is_available` is simply "no reasons". The `GET` endpoint and the booking endpoint both use
these same rules, so Iteration 3's "exact same availability as Iteration 2" holds by
construction, and the `422` response says *why* an agent can't be booked.

## How the code coped with each iteration

- **Iteration 1 → 2.** The endpoint and response didn't change. Qualification became a rule
  that also checks expiry, and double-booking was added as a second rule next to it.
- **Iteration 2 → 3.** Booking reuses the availability rules unchanged. The new work was
  persistence (storage learned to save) and the headcount check.

## Assumptions and decisions

**Qualifications**

- A shift needs **every** code in `requiredQualifications`; extra qualifications don't
  matter. A missing, `null` or empty list means anyone qualifies.
- `expiresOn` is a date with no time, so a qualification counts **through the whole of its
  expiry day** (compared to the shift's start date in UTC). A licence expiring 2026-09-15
  still covers a shift starting at 22:00 UTC that day.
- Only required qualifications are checked for expiry; an expired qualification the shift
  doesn't need is irrelevant.
- Qualification codes are a fixed enum (`GUARD_LICENSE`, `FIRST_AID`, `CROWD_CONTROL`). An
  unknown code in `data.json` fails at startup rather than being silently ignored.

**Time and overlap**

- All times are parsed as timezone-aware UTC datetimes. Because start and end are full
  timestamps, an overnight 22:00→06:00 shift is naturally 8 hours and ends the next day.
- Two shifts overlap when each starts before the other ends. Shifts that only touch
  (06:00 end, 06:00 start) do **not** overlap.
- An agent already on a shift counts as double-booked for that same shift, since a shift
  overlaps itself.

**Booking**

- Checks run in this order: shift exists → agent exists → shift not full → agent available.
  So when a booking is **both** full and unavailable, it gets `409`, not `422`; the shift's
  own state is reported before problems with the particular agent.
- A body that isn't JSON with a non-empty string `agentId` is a `400` (not specified in the
  brief).
- A rejected booking changes nothing, in memory or on disk.
- New ids continue from the highest existing `asg_<n>`.
- `GET` reflects a booking immediately because both endpoints share one in-memory store,
  updated in the same step that writes the file.

**Persistence and concurrency**

- `data.json` is written to a temporary file and swapped in, so a crash mid-write can't
  corrupt it. If the write fails, the in-memory booking is rolled back too.
- Bookings hold a lock from check to write, so two simultaneous requests can't both pass the
  headcount check and overbook a shift. This is correct for a single process only.

## What I'd do next

- **A real database.** The JSON file and in-process lock are fine for this exercise but don't
  work across multiple server processes. A database with a transaction (or a unique
  constraint) around booking would replace both.
- **Faster availability checks at scale.** Every rule runs for every agent, and the
  double-booking check scans all assignments. With many rules or lots of data I'd:
  - build shared lookups once per request (for example each agent's booked shifts) and let
    `is_available` stop at the first failing rule;
  - run the checks asynchronously, so rules that wait on I/O (an external licence registry,
    a database, another service) run concurrently instead of one after another. Today's
    rules are fast in-memory checks, so async only pays off once rules like these exist.
- **Severity levels on rules.** Give each `Rule` a severity, for example:
  - **blocking** failures exclude the agent and reject a booking with `422`;
  - **warning** failures still allow the booking but are returned alongside it, such as a
    required qualification that expires within the next 30 days.

  This turns availability from a yes/no answer into "available, with these warnings", and
  lets the business tighten or relax a rule by changing its severity rather than its code.
- **Return reasons as a list** in the `422` body (for example `{"error": ..., "reasons": [...]}`)
  so clients don't need to parse the message.
- **Validate data at load time**, such as a shift's end being after its start, and a
  positive headcount.
