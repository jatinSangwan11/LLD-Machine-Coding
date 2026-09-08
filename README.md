# LLD And Machine-Coding Interview Preparation

This repository is a hands-on workspace for Big Tech and YC-style
machine-coding interviews, backend SWE interviews, and practical object-oriented
design interviews. Python is the primary implementation language.

The emphasis is on doing the engineering: clarify ambiguous requirements, model
the domain, assign responsibilities, design useful interfaces, implement clean
Python, test behavior, respond to requirement changes, refactor, and defend the
trade-offs. Patterns and SOLID principles are introduced only when a real
problem creates a reason to use them.

## How Sessions Work

The mentor starts in interviewer mode. A typical problem moves through:

1. Requirements and clarification
2. Domain modeling, responsibilities, and interfaces
3. Initial design and Python implementation
4. Pytest coverage
5. A realistic requirement change
6. Refactoring, design review, and interview review

Hints are progressive. The first hint is a guiding question; later hints become
more explicit. A complete solution is provided only when requested.

## Repository Guide

- `agent.md` — permanent mentoring, interviewing, review, and teaching rules
- `current_context.md` — precise state of the active problem and session handoff
- `progress.md` — long-term attempts, scores, patterns, principles, weaknesses,
  hints, and recommendations
- `problems/` — problem statements, implementations, and tests as exercises begin
- `patterns/` — concise notes or reusable examples that emerge from completed
  engineering work; not a theory-first curriculum
- `OOPS/recap.py` — pre-existing file retained during repository setup

## Technical Baseline

- Python 3.12+
- modern type hints
- dataclasses, protocols, ABCs, and enums only when justified
- composition and dependency injection where they improve the design
- explicit exceptions and clean module boundaries
- pytest for every meaningful implementation

## State Management

Before a session, read `agent.md`, `current_context.md`, and `progress.md`. After
a meaningful session, update the current context. After a completed problem or
major session, update long-term progress using observable evidence rather than
generic ratings.

## Start

Ask the mentor: **Start my first problem.**

The mentor will provide the opening scenario and wait for your clarification
questions. No problem has been created during repository initialization.
