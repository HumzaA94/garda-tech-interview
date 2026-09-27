# Backend Take-Home — Shift Scheduling (Dev II)

Build a small **REST API** for scheduling security agents onto shifts. The work is
split into three short iterations, each in its own file. You'll be given a sample
database (`data.json`) to work from.

Suggested effort: **1–2 hours**. A clean Iteration 1 beats a broken Iteration 3.

## How to work through it

- Do the iterations **one at a time, in order** — [`iteration-1.md`](./iteration-1.md),
  then [`iteration-2.md`](./iteration-2.md), then [`iteration-3.md`](./iteration-3.md).
- Finish an iteration and **commit** before opening the next one.
- **Don't read ahead.** Don't build for requirements you haven't been given yet.

Each iteration changes the requirements, and part of what we're interested in is how
the code you've already written copes with the change. Reading ahead defeats the point,
so please keep to one iteration at a time.

## Ground rules

- **Python or TypeScript.** Pick whichever you're strongest in, and any framework you
  like within it (or none). We care about how you build a service, not the stack.
- **REST/HTTP returning JSON** — not tRPC, GraphQL, or RPC.
- **The data is the sample `data.json`** (see below). Load it at startup. Iterations 1–2
  only read it; Iteration 3 writes back to it.
- **Times are ISO-8601 (UTC).** Some shifts run overnight and cross midnight.
- Include a short **README in your submission** explaining how to run it and any
  assumptions you made.

## The data

`data.json` holds three lists:

- **agents** — `id`, `name`, and `qualifications` (each a `code` with an `expiresOn` date).
- **shifts** — `id`, `site`, `start`, `end`, `requiredQualifications` (list of codes), `headcount`.
- **assignments** — `id`, `shiftId`, `agentId` (an agent already booked on a shift).

The full sample file is in this repo as [`data.json`](./data.json).

## The two endpoints

1. `GET /api/shifts/{id}/available-agents` — who can work this shift (Iterations 1 &amp; 2).
2. `POST /api/shifts/{id}/assignments` — book an agent onto a shift (Iteration 3).

## Submitting

Push your work to a repo (or send us an archive) with your commit history intact —
we like to see the per-iteration commits — plus the short run/README notes described above.

Good luck, and have fun with it.
