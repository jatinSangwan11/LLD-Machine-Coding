# Current Engineering Context

Last updated: 2026-10-30

## Active problem

- Problem: LRU Cache
- Mode: Stage 1 — Guided
- Stage: Completed with guidance; next scheduled problem LFU (not started)
- Implementation: Node, DLL, thread-safe LRUCache, and runnable demo complete
- Tests: 4 passing pytest cases (3 sequential, 1 concurrency stress test)
- Design decisions: dictionary maps keys to doubly linked list nodes; head is MRU,
  tail is LRU (learner changed convention); empty head and tail are None
- Hints used: introduced direct node references and doubly linked list operations

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
