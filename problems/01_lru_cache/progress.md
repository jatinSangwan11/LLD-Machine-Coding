# LRU Cache Progress

Last updated: 2026-10-30

## Status

- Mode: Stage 1 — Guided
- Current stage: Completed with guidance on 2026-10-30
- Problem statement presented: 2026-10-29
- Design: dictionary to node references plus doubly linked list; head MRU, tail LRU
- Implementation: Node, DLL append/remove, cache constructor/get/put implemented;
  basic single-threaded behavior checked for agreed positive capacities
- Tests: 4 passing pytest tests: 3 focused sequential cases plus 1 concurrent
  get/put stress test checking final dictionary/list consistency
- Concurrency: complete get/put protected by one per-cache Lock;
  concurrent stress test passes (not exhaustive interleaving proof)

## Learner evidence

## End-of-problem review

- Strengths: chose dictionary lookup, identified deque removal cost, connected
  dictionary keys to node references, and chose class responsibility boundaries.
- Revision: Python dictionary APIs, singleton/link cleanup cases, complete
  eviction logic, and applying one shared lock to complete get/put operations.
- Mentor correction: learner's next-toward-head convention was valid; mentor
  initially reversed it incorrectly. This is not a learner design defect.
- Validation: 3 focused sequential tests and 1 concurrent stress test passed;
  demo output matched expectations. Positive capacity remains the agreed input
  contract. Stress testing is not exhaustive concurrency proof.
- Independence: not demonstrated; several fixes and tests were mentor-written.
  Reimplement independently later to check retention.
- Complexity: O(1) average cache work per get/put and O(capacity) space; lock
  contention can increase elapsed operation time.
- Optional interviewer follow-ups: add TTL expiration; support capacity resizing.
- Session complete. Next curriculum topic: LFU, not started. Earlier incremental
  next-action notes below are historical rather than outstanding assignments.

## Learner evidence (session history)

The learner summarized capacity, key-value entries, and recency updates from
successful operations. Proposed a Python dictionary for O(1) average lookup.
Proposed a deque for recency and independently identified O(n) search/removal
of an arbitrary entry. Requested revision on deque versus doubly linked list.
Subsequently proposed storing node references in the dictionary, removing the
dictionary entry on eviction, and maintaining left/LRU and right/MRU order.
Explained get and existing-key updates, and insertion into a nonempty list.
Worked through pointer and boundary cases with mentor prompts.

## Decisions and assumptions

- Authoritative direction: tail/LRU -> next -> head/MRU; prev points toward
  tail/LRU. head.next=None, tail.prev=None. This supersedes prior assumptions
  about link direction; head/MRU and tail/LRU remain unchanged.

- Learner selected three classes: Node, DoublyLinkedList, and LRUCache.
  List owns links/head/tail; cache owns dictionary/capacity/eviction policy.
- Pair coding: learner implements each part first, mentor validates it.

- Caller supplies a positive integer capacity at construction; capacity is fixed
  and counts entries, not bytes. Keys and values are integers.
- Missing get returns -1 and does not change recency.
- Successful get and every put make the entry most recent.
- Updating an existing key changes its value without adding an entry.
- Inserting a new key beyond capacity evicts the least recently used entry.
- get and put target O(1) average time; storage targets O(capacity).
- Dictionary maps keys to nodes. Nodes hold key, value, left, and right.
- Learner changed convention: head tracks MRU and tail tracks LRU; both are None
  for an empty list. This supersedes earlier head/LRU guidance.

## Hints used


Used an update/eviction scenario to prompt clarification. Asked the learner to
reason about lookup and recency separately. After the deque proposal, introduced
a doubly linked list and explained O(1) detachment with a known node reference.
Asked what the dictionary could store to access that node directly; learner
answered node references. Guided reciprocal neighbor links, resetting the moved
node's right link, updating tail, and head handling. Explicitly explained that
evicting the sole node leaves head and tail both None before insertion.

## Feedback

Added runnable lru_cache_demo.py following upstream's sequential usage-demo
approach, adapted to integer keys and agreed -1 miss behavior. Ran via venv
Python: outputs 100, -1, 400, 150 as expected. Covers read recency/eviction and
value update. Demo is separate from assertions/concurrent pytest verification.

At explicit request added one concurrent stress test: 4 workers, synchronized
start, 500 iterations per worker, overlapping keys, periodic scheduler yields.
Checks worker exceptions, valid hit/miss values, final capacity and all list/map
invariants without assuming a final key order. Full suite: 4 passed. No claim
that stress testing proves race freedom; lock-scope reasoning remains essential.

At explicit request, mentor wrapped complete put in the existing lock and moved
get's return inside its with block. Existing 3 pytest tests passed; these tests
verify sequential behavior only. Concurrent invariant checks remain pending.

Thread-safety attempt: per-instance Lock and get lock placement around dict/list
changes are correct. put has no lock, so it can still race with get/put. Return
reads node.value outside get lock; requested move inside for complete operation
protection. Static review only; no solution edits or concurrency tests yet.

Learner requested concise tests with distinct coverage. Consolidated six to
three scenarios; removed standalone empty-miss, value-update, repeated-eviction
tests. Folded empty miss into read-recency scenario; combined update/value/no
eviction checks without letting a get mask update recency (second update before
insertion). Full pytest file: 3 passed. Thread safety still pending.

At explicit request, mentor added the three remaining discussed basic tests:
empty-cache miss, capacity-1 replacement, repeated evictions. Ran full file with
venv/bin/python -m pytest problems/01_lru_cache/test_lru_cache.py -q: 6 passed.
Thread safety is still outstanding; no claim of independent readiness yet.

Permanent tests now exist. At explicit request, mentor added update-recency
eviction test without intervening get; preserved learner's existing two tests.
Ran venv/bin/python -m pytest problems/01_lru_cache/test_lru_cache.py -q:
3 passed. Next cases: empty miss, capacity 1, repeated evictions. Thread safety
still pending; passing current tests does not imply full reference coverage.

Rechecked current file at learner request: prior eviction changes were absent.
Reapplied commented put eviction and removed node=None. Manual checks passed
capacities 1, 2, 3 for misses, updates, read recency, eviction, and DLL/dictionary
consistency. No permanent tests added; thread safety remains pending.

Latest put review/fix: learner correctly used dict assignment and removed only
existing nodes. At explicit request, mentor added missing capacity eviction
(save tail/LRU node, remove from DLL, delete its dictionary key) before new
insertion, with comments. Removed redundant node=None. Manual checks passed
misses, read/update recency, no eviction on updates, repeated evictions, and
capacity 1; checked list links and dictionary consistency. No permanent tests
added. Learner-written tests and thread safety are still pending.

put first attempt reviewed statically: existing-key retrieval/value update and
Node(value,key) order are correct. Python issue: dict has no .set method. Design
issues: remove is called on fresh nodes outside the DLL, and no capacity check
or eviction exists. No solution edits made. Next: learner separates existing/new
paths, uses dictionary assignment, and handles tail/LRU eviction in both stores.

At explicit request, fixed DLL initialization and used lookup[key] after the
membership guard. Manual assertions passed missing get, middle/head/tail access,
and singleton access. Fixtures manually populated lookup/DLL since put is absent.
The dll=None defect is resolved; no permanent tests added. Next: learner writes put.

get review: miss branch correct; hit flow remove/append/return is correct given
an initialized DLL. Constructor currently assigns self.dll=None; reproduced
AttributeError on get hit. Learner should construct DoublyLinkedList instead.
Head check optional, not required for correctness. No solution code modified.

LRU constructor review: stores capacity in self.cap; missing dictionary and DLL
instance. capcacity typo and LRUcache capitalization are style/readability issues,
not syntax errors. Static review only, no code changes. Next: learner completes
constructor and then proceeds to get.

At explicit request, mentor fixed remove with commented singleton handling and
shared link cleanup after the tail/head/middle branches. Preserved learner's
direction convention. Manual assertions passed six removal positions across
list sizes 1–3 and reinsertion of each removed node, checking both links and
endpoints. No permanent tests added. Earlier remove defects are resolved.

remove review: tail/head updates valid with at least two nodes, middle neighbors
reconnected correctly, O(1). Reproduced AttributeError for sole-node removal at
self.tail.prev after tail becomes None. All paths leave removed node links
uncleared; reproduced invalid head.next after remove-middle then append. Learner
should handle singleton and clear both links on every path. No solution edits.

Learner identified redundant node.next=None under the fresh/cleared-node contract.
Removed that assignment at explicit request; append still sets node.prev=old head.
Future removal should clear both links before a node is reinserted.

Latest correction: mentor had wrongly reversed the learner's valid next/prev
convention. At learner request, restored append using old head.next=node,
node.prev=old head, node.next=None, then head=node. Empty insertion sets both
endpoints. Manual assertions passed for one, two, and three nodes, including
both directions and stable tail. Prior contrary append feedback is superseded.

Latest: learner clarified head insertion and explicitly requested correction.
Mentor fixed append's pointer direction, retained its name, and initialized new
head.prev to None. Contract accepts detached nodes. Manual assertions passed for
empty insertion and three-node reciprocal links with stable tail. No permanent
tests added. Prior append feedback assumed the former orientation and is
superseded. Next learner task: removing a known node.

append review: empty-list branch correctly sets both ends for a detached node.
Nonempty branch incorrectly uses/reassigns head instead of tail, breaking the
head/LRU, tail/MRU convention. Learner should link through tail and update tail
while preserving head. O(1) work, but incorrect endpoint state. Static review;
no solution edits or tests run. Next: learner fixes the nonempty branch.

Follow-up review: learner added key correctly and implemented DoublyLinkedList
with head/tail both None. Constructor order (value, key) is valid if used
consistently. Static review only; no solution edits or tests run. Next incremental
action: implement append(node) for a detached node, handling empty/nonempty lists.

Node review on 2026-10-30: constructor stores value and sets next/prev to None
correctly. Missing key parameter/field is needed to delete an evicted node's
dictionary entry without searching. next/prev names are appropriate. Static
review only; no tests run and no learner solution edits made. Compared against
[reference node.py](https://github.com/ashishps1/awesome-low-level-design/blob/main/solutions/python/lrucache/node.py),
which stores key, value, prev, next. Next incremental action: learner adds key,
then implements the DoublyLinkedList constructor.

Correct dictionary lookup complexity and correct identification of deque's
arbitrary-removal bottleneck. Initially needed clarification that LRU tracks
recency rather than frequency. Needs implementation practice with boundary
conditions and reciprocal links. No implementation or readiness assessment yet.

## Next action

Reference alignment on 2026-10-30: the learner selected
[repository LRU requirements](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/lru-cache.md)
and its linked Python implementation as the reference. Requirements and Python
directory/README were inspected; implementation code has not yet been reviewed.
The reference adds thread safety, to cover after basic implementation. Its
requirements specify -1 for misses while explanatory prose says null; retain
our agreed -1 behavior. The learner's reverse list orientation is equivalent.
No solution code was modified during this curriculum update.

Learner implements Node and LRUCache, then writes tests for misses, recency,
updates without size growth, eviction, and capacity 1. Review the learner's code.
Learner requested wrapping up the lengthy discussion: consolidate next steps
instead of continuing pointer-by-pointer questions.
Stay in interviewer mode unless the learner says "mentor help me"; allow
clarification questions one at a time.
