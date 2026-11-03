# Current Engineering Context

Last updated: 2026-11-03

## Active problem

- Problem: Parking Lot (#4)
- Stage: Contract and initial design discussed; ready for learner implementation
- Mode: Interviewer presentation; no timer started
- Source: ashishps1/awesome-low-level-design/problems/parking-lot.md, accessed
  2026-11-03 on main; exact commit unavailable. Requirements inspected.
- Scope: Multiple levels, car/motorcycle/truck compatibility, entry allocation,
  exit release, availability, concurrent operations across entry/exit points.
- Design: Spot/floor/ticket records, ParkingLot orchestration, numeric level/spot
  ordering, ticket and vehicle maps, per-type free-spot heaps, direct spot lookup.
- Implementation/tests: Not started; no solution scaffolding created
- Hints used: Identity/lifecycle corrections, duplicate request examples,
  free-spot index prompt; learner proposed heaps and vehicle tracking.
- Next: Learner implements enums and data classes, then ParkingLot constructor;
  review small checkpoints before entry/exit/availability. See progress for contract.
- Detailed checkpoint: problems/04_parking_lot/progress.md
- Previous: LRU, LFU, Stock Exchange completed with guidance; independence not
  demonstrated. Favor small hints and learner attempts before code assistance.

All notes below are session history. Prior active timers, deadlines, pending
Stock Exchange next actions, and earlier exercise checkpoints are superseded.

Stock Exchange session override: learner confirmed this is their actual
90-minute machine-coding interview challenge. Run it as Stage 4 timed mock,
not guided pair coding. Timer started on learner's start signal on 2026-11-02;
requirements clarification is within the 90 minutes. Learner drives all work;
no unsolicited hints, solution code, or fixes. Record requested assistance and
assess the state at the deadline separately from any later fixes. See Stock
Exchange progress for time budget and assessment. Added defaults remain open
clarification points rather than source requirements.

Completion checkpoint: learner wrapped up LFU on 2026-10-31. Seven pytest cases
passed, including two concurrency cases. Mentor supplied several operation fixes,
locking, and tests at explicit request; independent readiness is not demonstrated.
See LFU progress for end-of-problem assessment. Notes below are session history;
earlier pending-fix and next-action statements are superseded.

Latest concurrency checkpoint: at explicit learner request, one per-instance Lock
now protects each complete get/put, including value return and promotion.
Promotion helper requires caller-held lock; internal maps/DLL are not independently
synchronized and external mutation is outside the contract. Added seven focused
pytest cases (five sequential, two concurrent); LFU pytest file: 7 passed.
Concurrent checks cover exact hot-key frequency increments plus shared-key
get/put/eviction invariants. Stress tests do not prove all interleavings.
Next: learner reviews lock scope and tests, then design/complexity defense.

Previous checkpoint: learner explicitly requested
all corrections and explanatory comments. Mentor fixed promotion/map types,
conditional minimum updates, zero-capacity handling, update return, victim
lookup deletion, group cleanup, and common frequency-1 insertion. Preserved
tail/LRU -> next -> head/MRU convention. Verified 20,000 seeded operations
against an independent frequency/recency model over capacities 0, 1, 2, 5,
checking list/map invariants after every operation; negative capacity rejected.
No permanent tests added. Single-threaded contract; no concurrency claim.
Next: learner reviews explanation and writes focused tests; independent
implementation readiness has not been demonstrated.

Latest manual review: first insertion and existing-key update raise
UnboundLocalError for dll. Promotion stores a Node in frequency_map and changes
minimum unconditionally; second get raises AttributeError on Node.remove.
Zero-capacity get returns None; put stores an entry. Eviction retains victim
lookup and stores a DLL instead of Node. Seeded fixtures isolate operations.
Solution code unchanged; no permanent tests added.
- Hints used: frequency grouping prompt; explained constant-time minimum update;
  corrected tail-removal boundary logic. Independent readiness not assessed.

LFU began at learner request on 2026-10-31. Track details in
problems/02_lfu_cache/progress.md. LRU remains completed with guidance;
the LRU notes below are historical and do not describe active LFU work.

## Latest pair-coding checkpoint

LRU wrapped up at learner request on 2026-10-30. This completion checkpoint
supersedes earlier pending-work notes below. See active problem progress.md for
end-of-problem assessment. No independent readiness claim: mentor wrote several
fixes and tests. Next: LFU when learner asks; prefer compact assertions/demos in
future rounds, with concurrency testing proportional to requirements/time.

Latest demo: checked upstream lru_cache_demo.py (sequential put/get printing).
Added and ran local lru_cache_demo.py for capacity 3, read recency, eviction,
and value update with integer keys/-1 contract. Output matched expectations.
Entry uses main() plus __name__ guard; no extra Demo class needed. Demo shows
usage, not concurrent verification; existing pytest covers verification.

Latest concurrency verification: at explicit request added one pytest stress test
with 4 ThreadPoolExecutor workers, Barrier start, overlapping keys, 500 iterations
each, and periodic sleep(0) between operations. future.result propagates worker
errors. Accepts legitimate misses; checks final capacity, endpoints, no cycles,
reciprocal links, and identical dictionary/list nodes after workers complete.
Full pytest file: 4 passed. Stress evidence is not proof of all interleavings.
Next: brief design/complexity defense and end-of-problem review, then independent
reimplementation later to assess readiness.

Latest authorized lock fix: complete put body now uses with self.lock, and get's
return is inside its lock. Existing pytest suite: 3 passed. Shared per-cache Lock
protects both operations; direct external mutation of lookup/DLL is outside this
contract. Concurrency verification still pending. User asks how with manages lock:
acquire on entry, release on exit including return/exception (try/finally).

Latest thread-safety review: learner imported Lock, created one per cache, and
wrapped get's membership/lookup/list changes. put remains entirely unprotected,
so synchronization is incomplete. get reads node.value after leaving lock;
requested move return inside to protect that read too. No solution changes.
Next: learner wraps complete put in same lock and indents get return inside.

Latest test consolidation at learner request: reduced six tests to three focused
scenarios. Empty miss folded into read-recency test; update test verifies no
eviction plus value/recency using a second update after checking the other entry;
capacity-1 test retained. Dropped redundant repeated-eviction test. Full file:
3 passed. Prefer compact, distinct coverage in future mentoring.

Latest testing update: at explicit request, mentor added empty-cache miss,
capacity-1 replacement, and repeated-eviction tests. Full test file run via
venv/bin/python -m pytest problems/01_lru_cache/test_lru_cache.py -q: 6 passed.
Basic coverage is in place; thread-safety implementation/testing remains pending.

Latest testing checkpoint: learner added read-recency and existing-value update
tests. At explicit request, mentor added test_updating_existing_key_changes_eviction_order,
with no get between update and insertion. Ran venv/bin/python -m pytest
problems/01_lru_cache/test_lru_cache.py -q: 3 passed. Next learner cases: empty
cache miss, capacity 1, repeated evictions. Thread safety still pending.

Recheck requested: current file again lacked eviction. Reapplied commented
capacity enforcement to the current put and removed redundant node=None.
Manual checks passed capacities 1, 2, 3 for misses, update/read recency, eviction,
and consistency between links and lookup. Thread safety and learner tests pending.

Latest put fix: learner corrected dictionary assignment and moved removal into
existing-key branch. Missing capacity enforcement remained. At explicit request,
mentor added commented tail/LRU eviction from both DLL and lookup before new
insertion, and removed redundant node=None. Manual assertions passed misses,
insertions, read/update recency, no eviction on update, repeated evictions, and
capacity 1, checking dictionary/list consistency and reciprocal links.
Basic single-threaded behavior now checked for positive capacities. Permanent
learner-written tests and repository-required thread safety remain outstanding.

Latest put review (learner attempt, no fixes applied): existing-key update is
correct. New-key path uses invalid dict.set; should use item assignment. Shared
remove(node) is invalid for a new node not in the DLL; remove only existing
nodes. Capacity/eviction handling is missing entirely. Next: learner fixes these
three issues, using tail/LRU for eviction and removing its key from lookup.

Latest authorized fix: constructor now creates DoublyLinkedList(), and get uses
lookup[key] after its membership check. Manual assertions passed missing get,
middle/head/tail accesses, and singleton access, including recency links. Setup
populated list/dictionary manually because put is not implemented. No permanent
tests added. Earlier dll=None defect is resolved. Next: learner implements put.

Latest get review: constructor now has cap and lookup dictionary, but dll=None
instead of a DoublyLinkedList instance. get miss returns -1 correctly; hit logic
uses remove/append then returns value, valid once dll is initialized. Reproduced
AttributeError on a populated lookup because dll is None. Requested learner fix
initialization. Moving an already-head node is valid, just optional extra work.
No solution code modified.

Latest constructor review: learner added LRUcache.__init__(capcacity) storing
self.cap only. Capacity storage is correct; dictionary and DoublyLinkedList
instance are still missing. Suggested spelling capacity and class name LRUCache
as readability improvements, not Python correctness errors. No code edited or
tests run. Next: learner completes constructor before implementing get.

Latest implementation update: at explicit learner request, fixed remove and added
comments. Preserved separate singleton/tail/head/middle cases and the learner's
link convention; all cases now reach shared prev/next cleanup. Manual assertions
passed all six removal positions for lists of sizes 1–3 plus reinsertion each
time. No permanent tests added. This supersedes prior unresolved remove issues.

Latest remove review: learner handles tail, head, middle. Endpoint updates work
for lists with at least two nodes; middle reconnection is correct. Two issues:
sole-node removal sets tail=None then accesses tail.prev (AttributeError), and
no branch clears removed node links, violating append's cleared-node contract.
Manual checks reproduced sole-node failure and stale links after middle removal
and reinsertion. No code modified. Next: learner handles singleton and clears
both links on all removal paths (early returns must not skip cleanup).

Latest append simplification: at learner request removed redundant node.next=None.
Contract: append receives a fresh node or a detached node with both links cleared.
Future removal must clear both links. node.prev=old head remains necessary.

AUTHORITATIVE LINK CONVENTION (learner clarified): tail/LRU -> next -> head/MRU;
prev points toward tail/LRU. head.next=None and tail.prev=None. Mentor had
incorrectly assumed the opposite link direction; the learner's original
nonempty insertion was correct. At explicit request, restored append to set
node.next=None, node.prev=old head, old head.next=node when nonempty, head=node.
Empty insertion sets both endpoints. Manual assertions passed for one, two,
and three nodes in both directions. This supersedes all contrary notes below.

Latest correction supersedes previous append feedback: learner chose insertion
at head (MRU), tail is LRU. At explicit request, mentor corrected only append:
node.prev=None, node.next=old head, old head.prev=node when nonempty, head=node;
first insertion sets both endpoints. Kept existing method name. Contract assumes
a detached node. Manual assertions passed for first insertion and three nodes,
including reciprocal links and unchanged tail. No permanent tests added.
Next: learner implements removal of a known node using the new convention.

The learner chose Node + DoublyLinkedList + LRUCache. The list owns head, tail,
and pointer operations; the cache owns capacity, dictionary, and eviction policy.
Learner codes first; mentor validates each part for machine-coding preparation.
Node now accepts value, key and stores both, with next/prev initialized to None.
DoublyLinkedList constructor correctly initializes head and tail to None.
The value, key argument order is valid; keep calls consistent. No solution code
changed or tests run for this static review.
Reference node.py was inspected on 2026-10-30 and stores key, value, prev, next.
Latest append review: empty-list branch is correct for detached nodes. Nonempty
branch uses head.next, node.prev=head, and head=node; it must append using tail
and preserve head under the chosen convention. After two nodes, current code
makes head the new node and leaves tail at the old node; later appends are wrong.
Next: learner corrects nonempty append to link through tail and update tail.
List owns links; cache will own eviction policy. Static review; no tests run.

## Repository reset

The previous Parking Lot, Job Scheduler, and Vending Machine problem statements,
implementations, tests, notes, and generated artifacts were removed at the
learner's explicit request. Unrelated repository content was preserved. The new
curriculum begins from scratch with LRU Cache.

## Current assignment

Requirements have been clarified. The learner proposed a dictionary for lookup,
then a deque for recency, and correctly identified O(n) arbitrary removal.
The mentor introduced doubly linked list nodes and O(1) removal given a node
reference. The learner then requested a short deque/linked-list revision.

The learner connected the dictionary to node references, explained removing an
evicted key from the dictionary, chose left/LRU and right/MRU, and reasoned
through get, existing-key put, and new-key put. Needed guidance on reciprocal
links, tail updates, and empty state after evicting the sole node.
An initial Node stub is present; no completed implementation or tests reviewed.
Next: learner implements Node and
LRUCache, then tests normal operations, eviction, updates, misses, and capacity 1.
The learner asked to wrap up the lengthy discussion: use consolidated guidance
and avoid further pointer-by-pointer questioning.

## Mentoring constraints

- On 2026-10-30 the learner selected ashishps1/awesome-low-level-design as the
  source of truth. The merged sequence and source policy are in root progress.md.
- For LRU, the repository also requires thread safety: cover it after the basic
  implementation. Use the learner's updated head/MRU, tail/LRU convention.
- The reference requirements say missing get returns -1, while explanatory text
  says null. Keep the agreed -1 contract and flag this inconsistency.

- The learner owns all solution and test code.
- No solution files or design artifacts should be created before the learner
  decides the design.
- Use progressive hints only when needed.
- Stay in interviewer mode unless the learner says "mentor help me".
- Use representative company-style interview briefs, without claiming exact
  FAANG, Stripe, or Atlassian provenance. Allow clarification one question at a time.
- Record progress in `problems/01_lru_cache/progress.md` after each meaningful
  LRU session.

Latest Stock Exchange steering: learner removed file/CLI input and proposed
OrderMatchingEngine accepting Order objects directly. Core matching rules remain;
trade output interface not yet chosen. Track this as changed scope from original
interview. Learner still choosing state/data structures. Conceptual guidance has
been supplied; do not assess this as an unassisted round. Deadline remains the
recorded one unless learner changes timing.

Latest next action: use problems/03_stock_exchange/current_attempt.md for the
consolidated current scope (one stock, direct orders, sequential arrival FIFO).
Learner requested requirements, then happy-flow tracing before data structures.
Per-submit returned trade records are proposed, still to confirm. Original
file-based interview brief remains in problem.md for reference.

Latest Stock Exchange coding checkpoint: learner explicitly requested help
implementing. Mentor added submit_order and Trade records in
problems/03_stock_exchange/order_matching_machine.py with explanatory comments.
Manual assertions pass original sample, both-side price/FIFO priority, partial
fills, noncrossing/equal prices, sell-price execution and remainders. No permanent
tests yet. Engine assumes valid unique-ID orders for one stock and sequential
calls; pending Order objects must not be externally mutated or resubmitted.
Next: learner traces code and writes tests. Attempt is assisted; revised deadline
remains 2026-11-02 17:44:04 IST.

Latest test checkpoint: at learner request added min-quantity takeaway comments
under order_matching_machine.py and separate test_order_matching_machine.py.
Four focused tests pass: original sample/remainders, ask price/FIFO/partial-fill
priority, bid price/FIFO/seller price, and noncrossing/equality/incoming remainder.
Both implementation and tests include explicit mentor coding assistance.

Latest Parking Lot checkpoint: learner explicitly requested code correction.
Mentor fixed data model and constructor in problems/04_parking_lot/parking_lot.py,
implemented direct spot lookup and per-type free heaps; manual setup checks pass.
Entry/exit/availability remain unimplemented and no synchronization added yet.
Next: learner reviews initialization, then implements entry incrementally.
Off-record question: sorting a copy of config by level and each spot list by ID;
sorting config is independent of heap-maintained allocation priority.

Latest Parking Lot implementation: at explicit learner request mentor added
enter/exit with one per-lot Lock. Per-type heaps, spots, tickets and active-vehicle
map updated under it; duplicate/full/unknown/closed cases fail explicitly.
Monotonic ticket IDs, timezone-aware UTC issue times, closed tickets retained.
Manual sequential and concurrent checks passed, including duplicate registration
race. availability remains unimplemented; next learner task is consistent
per-level/type counts under the same lock. No permanent Parking Lot tests yet.

Latest Parking Lot checkpoint: availability implemented at learner request, with
optional type filter and lock-protected fresh per-level/type count dictionaries;
zero counts included. Restored enter's missing vehicle-type validation and fixed
minor formatting. Sequential snapshot/filter/isolation/empty cases and concurrent
entry/exit/read checks passed. No permanent tests yet. Next: learner reviews
code, then focused test cases and complexity/invariant defense.

Latest Parking Lot test checkpoint: learner requested permanent tests. Added
problems/04_parking_lot/test_parking_lot.py; 9 pytest cases passed (including
three concurrency cases). Covers allocation, compatibility, lifecycle, explicit
failures, availability and config boundaries, contention and final invariants.
Implementation unchanged; git diff --check passed. Next: review complexity and
lock scope, then completion assessment when learner requests wrap-up.
