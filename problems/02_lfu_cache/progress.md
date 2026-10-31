# LFU Cache Progress

Last updated: 2026-10-31

## Status

- Mode: Stage 1 — Guided; interviewer mode
- Stage: Thread-safe operations and seven tests verified; learner review next
- Source: Original curriculum; mentor-authored brief, no upstream LFU reference claimed
- Implementation/tests: Node/DLL, constructor, promotion/get/put corrected;
  seven permanent pytest cases pass (five sequential, two concurrent)
- Learner design decisions: Key-to-node map, frequency-to-DLL map, and
  lowest_frequency instance variable; node stores key/value/frequency/prev/next.
- Hints used: Prompted frequency grouping; explained why promotion of the last
  minimum-group node sets minimum to f+1; corrected tail-removal edge cases.

## Initial brief

Design a fixed-capacity, in-memory Python cache with integer keys and values.
Support get(key) and put(key, value). When inserting into a full cache, evict
the least frequently used entry. Target average O(1) get/put and O(capacity)
space.

## Agreed contract and design

- Keys and values are integers; keys are unique, values may repeat.
- Missing get returns -1 without state changes; stored -1 is accepted as an
  ambiguous return under this API.
- New entries start at frequency 1. Successful get and existing-key put increase
  frequency by 1 and make the entry MRU in its destination group.
- Existing-key put replaces the value without size growth or eviction.
- Eviction chooses lowest frequency, breaking ties by LRU.
- Reinsertion after eviction starts frequency at 1.
- Capacity zero: put is a no-op and get returns -1. Negative capacity raises
  ValueError. Other invalid input behavior and concurrency are not yet agreed.
- Per-group DLL: tail is LRU, head is MRU; next points toward head, prev toward
  tail. Empty endpoints are None; head.next and tail.prev are None.
- Dictionary maps each frequency to its DLL, rather than an independent LRU cache.
- Promotion detaches a known node and adds it at the destination group's head.
  Delete empty source groups. If promotion empties the minimum group f, set
  lowest_frequency to f+1, which contains the promoted node.
- Full-cache new-key put removes the minimum group's tail and its key-map entry,
  deletes an empty group, inserts at group 1's head, and resets minimum to 1.
- DLL owns links; LFU cache owns capacity, maps, frequency, and eviction policy.

## Learner evidence and review

Learner identified the scan problem in a single frequency-sorted DLL, then
described frequency groups with internal LRU order and direct key lookup.
Proposed tracking the minimum frequency but initially expected a linear update;
understood the f-to-f+1 argument after guidance. Correctly traced two entries
moving from frequency 4 to 5. Full-cache insertion outline was sound except
tail-removal boundary logic; mentor corrected it. No implementation reviewed.

## Next action

Latest authorized addition: learner requested locking before tests. Added one
per-cache threading.Lock around each complete get and put; promotion runs under
the caller's lock, avoiding nested acquisition. Documentation excludes direct
external mutation of internals. Added test_lfu_cache.py: five sequential cases
cover misses/LFU, promoted-group LRU ties/minimum updates, existing-key update
identity/size/frequency, zero/negative capacity, and capacity-one reinsertion,
stored -1, and empty-group cleanup. Two concurrent tests use Barrier starts and
scheduler yields: exact shared hot-key frequency and shared-key get/put/eviction
stress with final link/map/minimum invariants. future.result propagates failures.
Ran venv/bin/python -m pytest problems/02_lfu_cache/test_lfu_cache.py -q:
7 passed. git diff --check passed. Stress is evidence, not exhaustive proof.
Next: learner explains shared state/lock scope and complexity, then final review.

Latest checkpoint supersedes the pending fixes below: at learner's explicit
request, mentor corrected all current operations and added explanatory comments.
Map values now match their contracts; minimum changes only when its source group
empties; updates return; zero-capacity insertion does nothing; eviction removes
the victim lookup and empty group; new entries join actual group 1. Preserved
the learner's list convention and added return annotations/readable local names.
Manual verification: 20,000 reproducible operations (five seeds, capacities
0/1/2/5) against an independent scan-based frequency/recency model. Checked
return values, cache capacity, key/node identity, frequencies, minimum, reciprocal
links, per-group LRU order, and absence of empty groups after every operation.
Negative-capacity rejection also checked. No permanent tests or concurrency
support added. Mentor-written fixes do not establish independent readiness.
Next: learner understands corrections and writes focused behavioral tests.

Fix promotion first: register new destination DLL and update minimum only when
the old minimum group empties, setting it to old frequency+1. Then fix put with
zero-capacity guard, existing-key update/return, full-cache eviction of node and
lookup entry plus empty-group cleanup, and common insertion into actual group 1.
Store Node in key_to_node; do not reuse/relabel another frequency bucket.
Learner owns solution files; review did not modify implementation.

## First implementation review

Latest revision recheck: normal insertion and existing-key update both raise
UnboundLocalError for dll. Promotion unconditionally changes minimum and stores
a Node in frequency_map; second get raises AttributeError on Node.remove.
Zero-capacity get returns None instead of -1; zero-capacity put stores an entry.
Full-cache put retains the victim lookup and stores a DLL in key_to_node.
Existing-key update falls through into new insertion because it lacks return.
Manual seeded fixtures isolated operations. No implementation files edited.

Current recheck: promotion now sets minimum to node.freq when creating a
destination, but still fails to register that DLL. Minimum incorrectly becomes
2 while a source frequency-1 node remains; a second get raises KeyError(2).
When promotion empties group 1 into existing group 2, minimum incorrectly stays
1. Below-capacity put still does nothing; zero-capacity put inserts an entry.
Seeded full-cache eviction retains the victim lookup, stores a DLL instead of
a Node, and aliases frequency 1 and 2 to the same list. These are observed
manual failures, not just static concerns. No solution edits applied.

Latest operations review: seven isolated manual checks failed (below-capacity
insertion, zero-capacity put, destination registration, minimum with source
remaining, minimum with existing destination, eviction lookup cleanup, and
lookup Node type). Missing get passed. Seeded fixtures isolated promotion/get
and full-cache put, because normal insertion currently does nothing. Promotion
creates a DLL without saving it and resets minimum to 1 incorrectly. put lacks
normal insertion and zero-capacity guard, retains evicted keys, stores DLL in
key_to_node, and relabels/reuses eviction DLL as group 1, risking mixed groups
and aliasing. Indexed dictionary access cannot reach its missing-group None
branch: it raises KeyError first. No implementation edits or permanent tests.

Constructor recheck: negative-capacity ValueError guard is present. Manual checks
passed capacities 0, 1, 3, rejection of -1, empty dictionaries/minimum=0, and
separate dictionary ownership. Constructor accepted for agreed integer inputs;
get/put and promotion are not yet implemented. No implementation edits applied.

Latest constructor review: capacity, key_to_node, frequency_map, and minimum=0
initialized correctly. Manual assertions passed capacities 0 and 2 plus separate
dictionary ownership across instances. LFUCache(-1) incorrectly succeeds; agreed
ValueError guard is missing. Type annotations do not enforce validation.
No implementation edits applied.

Latest recheck: learner applied all three requested corrections. Six manual
removal/reinsertion cases for sizes 1–3 passed, including singleton. Checks
covered insertion, endpoints, reciprocal links, clearing detached links, and
initial frequency 1. DLL constructor no longer takes capacity. Verification
assumes append receives a detached node and remove receives a member node.
No solution files modified; no permanent tests added.

Manual assertions checked removal of every node position for sizes 1–3 and
reinsertion after successful removal. Five cases for sizes 2–3 passed, including
reciprocal links and endpoints. Singleton removal raises AttributeError because
the head branch sets head=None and dereferences head.next; the later singleton
branch is unreachable. Node starts at freq=0, contrary to the chosen initial
frequency of 1 unless later corrected by cache insertion. DLL takes an unused
capacity parameter; capacity belongs to LFUCache. Append preserves the learner's
correct next-toward-head convention for fresh/detached nodes. Removal must be
called only with a node belonging to that list; no membership validation promised.
