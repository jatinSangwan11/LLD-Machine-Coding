# Stock Exchange Progress

Last updated: 2026-11-02

## Status

- Actual start: 2026-11-02 15:44:19 IST (10:14:19 UTC)
- Original deadline: 2026-11-02 17:14:19 IST (11:44:19 UTC), superseded by pause
- Resumed: 2026-11-02 17:06:04 IST
- Adjusted deadline: 2026-11-02 17:44:04 IST (12:14:04 UTC)
- Remaining time at resume: 38 minutes, using the approximate saved pause checkpoint
- Stage: Completed with guidance at learner request on 2026-11-02
- Closed: 17:36:41 IST; round ended early at learner request
- Original planned date was 2026-11-01; learner started on 2026-11-02.
- No automatic reminder created; compare wall clock with deadline at interactions.
- Source: Learner's actual 90-minute machine-coding interview challenge;
  employer not specified. See problem.md for refined requirements and sample.
- Mode: Started as timed mock; completed as assisted practice with reduced scope
- Design: Two price/arrival-priority heaps; matching implemented, four pytest tests pass
- Assistance: Conceptual guidance and concrete priority tuples supplied; assisted round

## Next action

Session closed at learner request. Next curriculum problem: Parking Lot (#4),
planned 2026-11-03 at learner request; not started. An independent reimplementation is a future retention exercise.
Earlier timer instructions, pending work, and original full-scope assessment
criteria below are historical, superseded by this completion checkpoint.

## End-of-problem review

- Completed scope: one-stock, sequential in-memory matching via direct Order
  submission; trade records returned. File/CLI and multi-stock support were
  explicitly removed by the learner, so this does not complete the original
  interview prompt's full scope.
- Strengths: learner proposed the Order entity and matching component, identified
  two heaps with tuple tie-breaking, and understood partial-quantity updates and
  min-based execution after discussion.
- Revision: independently tracing quantities, turning requirements into entities
  and operations, Enum/types versus modules, heap storage versus algorithms,
  price/time priority, and translating the matching loop into code.
- Mentor contribution: extensive conceptual guidance, concrete heap keys,
  complete submit_order implementation, Trade records, and four permanent tests
  at explicit request. Learner wrote Order and engine skeleton with corrections.
- Validation: four pytest cases passed, covering original sample and remaining
  quantities, ask/bid price priority, FIFO and retained partial-fill priority,
  incoming-seller pricing, noncrossing/equal prices, and incoming remainder.
- Complexity: best-price peek O(1), insertion/removal O(log n); upper bound
  O((k+1) log(n+1)) per submission generating k trades, O(n) book storage plus
  O(k) returned trades under standard arithmetic assumptions.
- Limitations: valid unique-ID inputs for one stock assumed, sequential calls,
  no validation or external mutation protection, timestamps informational.
- Independence: not demonstrated; record as guided completion, not a passed
  independent 90-minute interview. Timing included a pause restored from an
  approximate checkpoint and the learner ended before the adjusted deadline.
- Follow-ups: restore file/CLI input and multi-stock routing; add cancellation.

## Time budget and assessment

- 0–10 minutes: requirements and clarification
- 10–20 minutes: design and complexity
- 20–65 minutes: implementation, including file input and console output
- 65–80 minutes: testing and debugging
- 80–90 minutes: trade-offs and design defense

Assess the actual submitted state at the deadline: runnable CLI, correct matching,
price/time priority, partial quantities, money precision, test evidence,
maintainability, and time management. Record unfinished work and assistance;
post-deadline fixes are separate from the timed result. Do not force concurrency
or other extensions absent an agreed requirement.

## Clarifications during timed round

Learner asked about CLI arguments, stock types, previously unseen symbols,
functional requirements, price/time priority, and sell-price execution.
Interviewer clarified: input path passed after script name; stocks identified by
symbol, no predefined stock-category registry or inventory. First order for a
symbol starts its book; absence of a matching opposite order leaves it pending.
Price priority precedes time; FIFO breaks equal-price ties. Trade quantity is
minimum remaining quantity, execution price always seller's limit even for an
incoming seller. These are requirement explanations, not design/code assistance.

## Learner-directed scope change

Learner explicitly removed text-file input during the round. New boundary:
OrderMatchingEngine accepts an Order object and performs matching. CLI/file
parsing is no longer required for this attempt; original interview prompt remains
in problem.md for provenance. Output interface is still to clarify (return trade
records versus printing). Core price-time, partial-fill, and sell-price rules
remain. Learner proposed Order entity and OrderMatchingEngine; no solution code
has been generated. Session has included conceptual assistance on entities,
classes/objects, price-time matching, quantity scenarios, exact price types, and
arrival sequence; this attempt is assisted rather than an independent mock.

Latest scope refinement: learner narrowed the current implementation to one
asset, with multiple symbols a future extension. Uses bid (buy) and ask (sell)
terminology and requests low latency, suggesting O(1). Explain that reading the
best price can be O(1), but maintaining arbitrary dynamic prices generally needs
ordered updates; an incoming order causing k trades requires at least O(k) work.
No bounded price universe or specialized O(1) guarantees agreed.

Learner requested a consolidated refined statement before tracing a happy flow
and deriving storage. Saved current_attempt.md: one-stock engine, direct Order
input, sequential arrival priority, unchanged matching/partial-fill/sell-price
rules, valid input assumption, realistic complexity goals. Returning per-submit
trade records is explicitly proposed for confirmation. No data structures or
solution code supplied. Original problem.md retained for provenance.

## Data structure checkpoint

Learner correctly traced best-ask priority and FIFO order; needed correction on
remaining quantity in the equal-price example. Proposed two heaps and tuple
comparison for price/time ties. Interviewer supplied bid negation and concrete
priority tuples: asks (price, sequence, order), bids (-price, sequence, order).
Unique engine-assigned sequence avoids comparing Order objects. Learner stated
partial-fill remaining quantity should be updated; clarified that the resting
order remains in heap until filled because priority fields do not change.
Next: implement Order and OrderMatchingEngine state plus submit_order; generate
trade records and test the happy flows, noncrossing prices, incoming sells,
and partial remainders. No code generated by mentor. This is an assisted attempt.

## First code review (resumed round)

At 17:11 IST, inspected order_matching_machine.py. Order dataclass and engine
skeleton exist. Loading module fails: ORDERTYPE inherits enum module rather
than enum.Enum. Independently confirmed heapq() raises TypeError because heapq
is a module; heaps should be lists manipulated through heapq functions.
price: decimal and order_time: time annotate modules, not value types; use
Decimal and a suitable time type if retaining timestamp. Engine sequence counter
is missing. No matching code yet; no implementation modifications made.

Code recheck at 17:14 IST: Enum inheritance and heap storage corrected; module
loads and engine initializes empty ask/bid lists plus counter. Remaining quantity
field renamed correctly. price and order_time still annotate decimal/time modules;
correction to concrete types still pending. Counter spelled arrival_squence.
Explained heapq supplies algorithms over a list, analogous to C++ heap algorithms
over a vector; unlike deque it is not a container constructor. No code modified.

## Authorized coding assistance

At learner's explicit request for coding help, mentor implemented submit_order in
order_matching_machine.py, added immutable Trade records, typed heap tuples, fixed
arrival_sequence spelling, and documented valid-input/single-stock/ownership
assumptions. Method handles both incoming sides through buy/sell references,
compares real prices, matches minimum remaining quantities at seller's price,
pops only filled resting orders, and queues any incoming remainder with original
arrival sequence. Explanatory comments included. Removed an unfinished,
unreachable draft after return that caused a SyntaxError during verification.
Manual assertions passed original sample and final quantities, best ask and bid,
FIFO ties including identical timestamps, retained partial-fill priority,
incoming-seller pricing, noncrossing exact prices, equality, and incoming remainder.
git diff --check passed. No permanent tests added. This implementation is
mentor-written assistance and does not demonstrate independent timed readiness.
Next: learner traces method, then writes focused tests and defends complexity.

Latest authorized update: learner requested takeaway notes and only necessary
separate tests. Added bottom-of-file min-quantity takeaway: with positive inputs,
subtraction leaves nonnegative quantities and fills at least one side; min does
not validate input. Added test_order_matching_machine.py with four cases:
original sample/remainders; best ask and FIFO retained across partial fills;
best bid/FIFO/incoming sell price; exact noncrossing prices then equality and
incoming remainder. venv/bin/python -m pytest
problems/03_stock_exchange/test_order_matching_machine.py -q: 4 passed.
git diff --check passed. Tests are mentor-written at explicit request.
