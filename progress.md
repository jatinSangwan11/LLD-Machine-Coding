# Machine-Coding Curriculum Progress

Last updated: 2026-11-02

## Source of truth and scope

The learner selected [ashishps1/awesome-low-level-design](https://github.com/ashishps1/awesome-low-level-design) as the
source of truth for repository-covered requirements and solution comparisons.
This is the consolidated curriculum checked on 2026-10-30; it is not a live sync.

Coverage: 33 problem documents, 3 additional solution-only topics, 5 original-only
problems, 1 user-provided Stock Exchange challenge, and 9 README-linked
concurrency exercises: 51 unique exercises plus
one final random mock. The original first ten problems retain their relative order; the learner added
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
| 4 | Parking Lot | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/parking-lot.md) + original curriculum | Not started |
| 5 | Elevator System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/elevator-system.md) + original curriculum | Not started |
| 6 | Job Scheduler | Original curriculum | Not started |
| 7 | Notification System | Original curriculum | Not started |
| 8 | Rate Limiter | Original curriculum | Not started |
| 9 | Meeting Room Scheduler | Original curriculum | Not started |
| 10 | Vending Machine | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/vending-machine.md) + original curriculum | Not started |
| 11 | Splitwise | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/splitwise.md) + original curriculum | Not started |
| 12 | Stack Overflow | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/stack-overflow.md) | Not started |
| 13 | Logging Framework | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/logging-framework.md) | Not started |
| 14 | Traffic Signal Control System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/traffic-signal.md) | Not started |
| 15 | Coffee Vending Machine | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/coffee-vending-machine.md) | Not started |
| 16 | Task Management System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/task-management-system.md) | Not started |
| 17 | ATM | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/atm.md) | Not started |
| 18 | LinkedIn | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/linkedin.md) | Not started |
| 19 | Tic Tac Toe | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/tic-tac-toe.md) | Not started |
| 20 | Pub Sub System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/pub-sub-system.md) | Not started |
| 21 | Car Rental System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/car-rental-system.md) | Not started |
| 22 | Online Auction System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/online-auction-system.md) | Not started |
| 23 | Hotel Management System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/hotel-management-system.md) | Not started |
| 24 | Digital Wallet Service | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/digital-wallet-service.md) | Not started |
| 25 | Airline Management System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/airline-management-system.md) | Not started |
| 26 | Library Management System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/library-management-system.md) | Not started |
| 27 | Social Network (Facebook) | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/social-networking-service.md) | Not started |
| 28 | Restaurant Management System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/restaurant-management-system.md) | Not started |
| 29 | Concert Ticket Booking System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/concert-ticket-booking-system.md) | Not started |
| 30 | CricInfo | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/cricinfo.md) | Not started |
| 31 | Chess | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/chess-game.md) | Not started |
| 32 | Snake and Ladder | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/snake-and-ladder.md) | Not started |
| 33 | Ride-Sharing Service (Uber) | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/ride-sharing-service.md) | Not started |
| 34 | Course Registration System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/course-registration-system.md) | Not started |
| 35 | Movie Ticket Booking System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/movie-ticket-booking-system.md) | Not started |
| 36 | Online Shopping System (Amazon) | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/online-shopping-service.md) | Not started |
| 37 | Online Stock Brokerage System | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/online-stock-brokerage-system.md) | Not started |
| 38 | Music Streaming Service (Spotify) | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/music-streaming-service.md) | Not started |
| 39 | Food Delivery Service (Swiggy) | [Repository problem](https://github.com/ashishps1/awesome-low-level-design/blob/main/problems/food-delivery-service.md) | Not started |
| 40 | Voting System | [Repository solution](https://github.com/ashishps1/awesome-low-level-design/tree/main/solutions/python/votingsystem) | Not started |
| 41 | File and Directory System | [Repository solution](https://github.com/ashishps1/awesome-low-level-design/tree/main/solutions/java/src/filedirectory) | Not started |
| 42 | Online Learning Platform | [Repository solution](https://github.com/ashishps1/awesome-low-level-design/tree/main/solutions/java/src/onlinelearningplatform) | Not started |
| 43 | Print FooBar Alternately | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 44 | Print Zero Even Odd | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 45 | Fizz Buzz Multithreaded | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 46 | Building H2O Molecule | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 47 | Thread-Safe Cache with TTL | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 48 | Concurrent HashMap | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 49 | Thread-Safe Blocking Queue | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 50 | Concurrent Bloom Filter | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 51 | Multithreaded Merge Sort | [README concurrency exercise](https://github.com/ashishps1/awesome-low-level-design#-concurrency-and-multi-threading-problems) | Not started |
| 52 | Full random machine-coding mock | Original curriculum | Not started |

## Current readiness

LRU, LFU, and Stock Exchange completed with substantial guidance. Stock Exchange
used reduced scope and mentor-written matching/tests; independent interview
readiness is not demonstrated. Next problem: Parking Lot (#4).

## Cross-problem observations

The curriculum was expanded at the learner's request on 2026-10-30. Full
reference solutions remain withheld until requested.

On 2026-10-31 the learner inserted Stock Exchange — Order Matching as the next
problem, using their supplied challenge. Total: 51 exercises and one final mock.
