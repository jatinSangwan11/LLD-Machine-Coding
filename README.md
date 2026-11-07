# Python LLD and Machine-Coding Practice

This repository is a learner-owned workspace for SWE-1/2 LLD and 60–90 minute
machine-coding interview preparation.

## Working agreement

The learner designs, implements, tests, and defends every solution. The mentor
guides progressively, reviews like an interviewer, and does not reveal complete
designs or silently implement solutions.

Read:

- `MENTORING_PLAN.md` — teaching style, sequence, timing, and evaluation plan
- `agent.md` — mandatory operating rules for the mentor
- `current_context.md` — exact active-problem checkpoint
- `progress.md` — curriculum-level progress
- `problems/<problem>/progress.md` — detailed progress for each solution

## Current problem

LRU, LFU, and Stock Exchange completed with guidance. Stock Exchange covers a
single-stock in-memory engine with four passing tests; original file/CLI and
multi-stock scope was removed by the learner. Parking Lot (#4) was implemented with guidance; nine tests pass and its final
review is pending. Job Scheduler (#5) was implemented with guidance; manual checks pass and
permanent tests are pending. Current problem: Elevator System (#6), compact reduced-scope solution with
guidance; six tests pass. See problems/06_elevator_system/INTERVIEW_SCOPE.md.

## Curriculum reference

[ashishps1/awesome-low-level-design](https://github.com/ashishps1/awesome-low-level-design)
is the source of truth for covered requirements and reference solution reviews.
The merged curriculum has 52 exercises and one final mock.
See `progress.md` for the complete sequence, source links, and reference policy.

## Technical baseline

- Python
- pytest when implementation begins
- simple designs before abstractions
- SOLID principles and patterns only when justified by actual design pressure
