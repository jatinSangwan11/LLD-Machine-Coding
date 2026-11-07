# Machine-Coding Curriculum Progress

Last updated: 2026-11-07

## Source of truth and scope

The learner selected [ashishps1/awesome-low-level-design](https://github.com/ashishps1/awesome-low-level-design) as the
source of truth for repository-covered requirements and solution comparisons.
This is the consolidated curriculum checked on 2026-10-30; it is not a live sync.

Coverage: 33 problem documents, 3 additional solution-only topics, 5 original-only
problems, 1 user-provided Stock Exchange challenge, 1 Job Scheduler extension,
and 9 README-linked concurrency exercises: 52 exercises plus one final mock. The original first ten problems retain their relative order; the learner added
Stock Exchange as #3 on 2026-10-31, ahead of Parking Lot.

Duplicates across our list and the repository are counted once: LRU Cache,
Parking Lot, Elevator System, Vending Machine, and Splitwise. Language
implementations and alternate Hotel/Concert solution folders are not new problems.
Coffee Vending Machine remains a separate variant with its own requirements.
Task Management is distinct from Job Scheduler; Pub Sub is distinct from
Notification System; Course Registration is distinct from Online Learning.

## Reference workflow

- Before each problem, read its repository requirements; before judging an
  attempted solution, inspect the relevant actual implementation, preferring Python.
- The learner still derives and writes the solution. Reveal full reference
  designs/code only when explicitly requested. Guidance switches from interviewer
  mode when the learner says "mentor help me".
- Use the reference for behavior, design comparison, complexity, and concurrency;
  equivalent correct designs need not copy its class names or list orientation.
- Flag contradictory requirements, implementation bugs, or gaps explicitly.
  Record the agreed contract rather than silently copying a contradiction.
- Original-only topics have no verified answer in this repository; label their
  briefs and review reasoning as mentor-authored.
- Concurrency exercises are linked from the README to external pages. Inclusion
  does not imply a free solution exists in this repository. If unavailable, state
  that limitation and distinguish any mentor-authored guidance.
- Save the exact reference URL and accessed version/commit when available in each
  problem's progress file when that problem begins.

## Consolidated sequence

| # | Problem | Source | Status |
| --- | --- | --- | --- |
| 1 | LRU Cache | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/lru-cache.md) + original curriculum | Completed with guidance; 4 tests pass; demo runs |
| 2 | LFU Cache | Original curriculum | Completed with guidance; 7 tests pass; thread-safe get/put |
| 3 | Stock Exchange — Order Matching | [Learner's actual interview challenge](problems/03_stock_exchange/problem.md) | Completed with guidance; reduced scope; 4 tests pass |
| 4 | Parking Lot | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/parking-lot.md) + original curriculum | Implementation and 9 tests pass with guidance; final review pending |
| 5 | Job Scheduler | Original curriculum | Implemented with guidance; manual checks pass; permanent tests pending |
| 6 | Elevator System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/elevator-system.md) + original curriculum | Compact reduced-scope solution with guidance; 6 tests pass |
| 7 | Notification System | Original curriculum | Not started |
| 8 | Rate Limiter | Original curriculum | Not started |
| 9 | Meeting Room Scheduler | Original curriculum | Not started |
| 10 | Vending Machine | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/vending-machine.md) + original curriculum | Not started |
| 11 | Splitwise | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/splitwise.md) + original curriculum | Not started |
| 12 | Stack Overflow | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/stack-overflow.md) | Not started |
| 13 | Bounded Job Scheduler — Backpressure and ThreadPoolExecutor | Extension of #5 | Planned week of 2026-11-09; not started |
| 14 | Logging Framework | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/logging-framework.md) | Not started |
| 15 | Traffic Signal Control System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/traffic-signal.md) | Not started |
| 16 | Coffee Vending Machine | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/coffee-vending-machine.md) | Not started |
| 17 | Task Management System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/task-management-system.md) | Not started |
| 18 | ATM | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/atm.md) | Not started |
| 19 | LinkedIn | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/linkedin.md) | Not started |
| 20 | Tic Tac Toe | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/tic-tac-toe.md) | Not started |
| 21 | Pub Sub System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/pub-sub-system.md) | Not started |
| 22 | Car Rental System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/car-rental-system.md) | Not started |
| 23 | Online Auction System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/online-auction-system.md) | Not started |
| 24 | Hotel Management System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/hotel-management-system.md) | Not started |
| 25 | Digital Wallet Service | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/digital-wallet-service.md) | Not started |
| 26 | Airline Management System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/airline-management-system.md) | Not started |
| 27 | Library Management System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/library-management-system.md) | Not started |
| 28 | Social Network (Facebook) | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/social-networking-service.md) | Not started |
| 29 | Restaurant Management System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/restaurant-management-system.md) | Not started |
| 30 | Concert Ticket Booking System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/concert-ticket-booking-system.md) | Not started |
| 31 | CricInfo | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/cricinfo.md) | Not started |
| 32 | Chess | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/chess-game.md) | Not started |
| 33 | Snake and Ladder | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/snake-and-ladder.md) | Not started |
| 34 | Ride-Sharing Service (Uber) | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/ride-sharing-service.md) | Not started |
| 35 | Course Registration System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/course-registration-system.md) | Not started |
| 36 | Movie Ticket Booking System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/movie-ticket-booking-system.md) | Not started |
| 37 | Online Shopping System (Amazon) | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/online-shopping-service.md) | Not started |
| 38 | Online Stock Brokerage System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/online-stock-brokerage-system.md) | Not started |
| 39 | Music Streaming Service (Spotify) | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/music-streaming-service.md) | Not started |
| 40 | Food Delivery Service (Swiggy) | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/food-delivery-service.md) | Not started |
| 41 | Voting System | [Repository solution](https://github.com/ashishps1/awesome-low-level-design/tree/main/solutions/python/votingsystem) | Not started |
| 42 | File and Directory System | [Repository solution](https://github.com/ashishps1/awesome-low-level-design/tree/main/solutions/java/src/filedirectory) | Not started |
| 43 | Online Learning Platform | [Repository solution](https://github.com/ashishps1/awesome-low-level-design/tree/main/solutions/java/src/onlinelearningplatform) | Not started |
| 44 | Print FooBar Alternately | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 45 | Print Zero Even Odd | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 46 | Fizz Buzz Multithreaded | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 47 | Building H2O Molecule | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 48 | Thread-Safe Cache with TTL | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 49 | Concurrent HashMap | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 50 | Thread-Safe Blocking Queue | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 51 | Concurrent Bloom Filter | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 52 | Multithreaded Merge Sort | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 53 | Full random machine-coding mock | Original curriculum | Not started |

## Current readiness

LRU, LFU, and Stock Exchange completed with substantial guidance. Stock Exchange
used reduced scope and mentor-written matching/tests; independent interview
readiness is not demonstrated. Parking Lot (#4) implementation/tests are complete with guidance; final review
remains pending. Active problem: Elevator System (#6), requirement clarification. Job Scheduler
was implemented with guidance; manual checks pass, permanent tests pending.

## Cross-problem observations

The curriculum was expanded at the learner's request on 2026-10-30. Full
reference solutions remain withheld until requested.

On 2026-10-31 the learner inserted Stock Exchange — Order Matching as the next
problem, using their supplied challenge. Total: 51 exercises and one final mock.

On 2026-11-03 the learner moved Job Scheduler ahead of Elevator System. Job
Scheduler is #5, planned 2026-11-04; Elevator is #6. Earlier relative-order notes
are superseded by this explicit change.

On 2026-11-05 the learner added Bounded Job Scheduler — Backpressure and
ThreadPoolExecutor as #13 for the week of 2026-11-09. It extends #5 with a limit
of two accepted-but-unfinished jobs, bounded queue behavior, and an executor
variant. See the Job Scheduler progress file for the exercise scope.
